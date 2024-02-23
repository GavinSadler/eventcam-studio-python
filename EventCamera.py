from metavision_core.event_io import EventsIterator
from metavision_core.event_io.raw_reader import initiate_device
from metavision_sdk_core import PeriodicFrameGenerationAlgorithm
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

            for callback in self.callbacks.values():
                callback(cd_frame)

        self.frameGenerator = PeriodicFrameGenerationAlgorithm(
            sensor_width=self.width, sensor_height=self.height, fps=30
        )
        self.frameGenerator.set_output_callback(frame_gen_callback)
        
        self.connected = True

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
