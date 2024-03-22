import time
from metavision_core.event_io import EventsIterator
from metavision_core.event_io.raw_reader import initiate_device
from metavision_sdk_core import PeriodicFrameGenerationAlgorithm
import metavision_hal
import numpy as np

import threading

from Camera import Camera


class EventCamera(Camera):

    device = None
    eventsIterator = None
    frameGenerator = None

    stopStreamingEvent = threading.Event()

    def __init__(self) -> None:
        super().__init__()

    def connect(self):

        self.device = initiate_device("")

        # === Device configuration ===

        self.device.get_i_ll_biases().set("bias_fo", 1600)

        self.eventsIterator = EventsIterator.from_device(self.device)
        self.height, self.width = self.eventsIterator.get_size()

        # Initialize self.lastFrame with a random frame
        rng = np.random.default_rng()
        self.lastFrame = rng.standard_normal(self.width * self.height * 3, dtype=np.float32)

        def frame_gen_callback(ts, cd_frame):
            cd_frame = np.asfarray(cd_frame, "f")
            cd_frame = np.true_divide(cd_frame, 255.0)

            self.lastFrame = cd_frame

            self.frameBuffer.set(cd_frame)

        self.frameGenerator = PeriodicFrameGenerationAlgorithm(
            sensor_width=self.width, sensor_height=self.height, fps=30
        )
        self.frameGenerator.set_output_callback(frame_gen_callback)
        
        # Just to make sure the external clock isn't running from a previous instance of the camera being connected
        self.stopExternalClock()
        
        self.connected = True
        
    def startExternalClock(self, dutyCycle=0.5, period=(1/30)):
        i_trigger_in = self.device.get_i_trigger_in()
        i_trigger_in.enable(metavision_hal.I_TriggerIn.Channel.LOOPBACK)
        
        i_trigger_out = self.device.get_i_trigger_out()
        i_trigger_out.set_duty_cycle(dutyCycle) # 50% duty cycle
        i_trigger_out.set_period(int(1 * 10**6 * period)) # Period in us, so multiply duration in seconds by 10^6
        i_trigger_out.enable()
    
    def stopExternalClock(self):
        i_trigger_in = self.device.get_i_trigger_in()
        i_trigger_in.disable(metavision_hal.I_TriggerIn.Channel.LOOPBACK)
        
        i_trigger_out = self.device.get_i_trigger_out()
        i_trigger_out.disable()
        
    def enableTriggerInput(self):
        # Enable electronic trigger in signals
        i_trigger_in = self.device.get_i_trigger_in()
        i_trigger_in.enable(metavision_hal.I_TriggerIn.Channel.MAIN)
        
    def disableTriggerInput(self):
        # Disable electronic trigger in signals
        i_trigger_in = self.device.get_i_trigger_in()
        i_trigger_in.disable(metavision_hal.I_TriggerIn.Channel.MAIN)

    def startRecording(self, recordingFileName = "output.raw"):
        if not self.streaming or self.recording:
            return
        
        self.device.get_i_events_stream().log_raw_data(recordingFileName)
        self.recording = True
    
    def stopRecording(self):
        self.device.get_i_events_stream().stop_log_raw_data()
        self.recording = False

    # Starts the event camera stream
    def startStreaming(self):
        self._thread = threading.Thread(target=self._processEvents)
        self._thread.start()
        self.streaming = True

    # Stops the event camera stream
    def stopStreaming(self):
        self.stopStreamingEvent.set()
        self.streaming = False

    # For internal use only
    # Processes event camera's events in a threa
    def _processEvents(self):

        for event in self.eventsIterator:

            if self.stopStreamingEvent.is_set():
                break

            # This sends streamed events to the PeriodicFrameGenerator so we have some sort of output from the camera
            self.frameGenerator.process_events(event)
