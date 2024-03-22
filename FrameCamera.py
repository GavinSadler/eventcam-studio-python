import cv2
import numpy as np
from pypylon import pylon
import threading
from Camera import Camera
import time

from FrameBuffer import FrameBuffer


# Needed by pylon API in order to facilitate callback functionality
class _ImageGrabHandler(pylon.ImageEventHandler):

    _thread: threading.Thread = None
    _record: bool
    _frameBuffer: FrameBuffer

    _imgageHandler = pylon.PylonImage()

    def __init__(self, fb: FrameBuffer):
        super().__init__()
        self._record = False
        self._thread = None
        self._frameBuffer = fb

    def _processFrame(self, frame: np.ndarray):
        frame = cv2.cvtColor(frame, cv2.COLOR_BayerBG2RGB)
        frame = np.asfarray(frame, "f")
        frame = np.true_divide(frame, 255.0)

        self._frameBuffer.set(frame)

    def startRecording(self, baseFilename: str):
        self.baseFilename = baseFilename
        self.frameNumber = 0
        self._record = True

    def stopRecording(self):
        self._record = False

    def OnImageGrabbed(self, camera: pylon.InstantCamera, grabResult: pylon.GrabResult):
        if self._record:
            self._imgageHandler.AttachGrabResultBuffer(grabResult)
            self._imgageHandler.Save(
                pylon.ImageFileFormat_Bmp, f"{self.baseFilename}_{self.frameNumber}.bmp"
            )
            # print(grabResult.GetImageFormat())
            # print(self.imgageHandler.CanSaveWithoutConversion(grabResult.GetImageFormat()))
            self._imgageHandler.Release()
            self.frameNumber += 1

        self._thread = threading.Thread(
            target=self._processFrame, args=(grabResult.GetArray(),)
        )
        self._thread.start()


class FrameCamera(Camera):

    device: pylon.InstantCamera = None
    imageGrabHandler: _ImageGrabHandler = None

    def __init__(self) -> None:
        super().__init__()

    def connect(self):
        self.device = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice()
        )
        self.device.Open()

        self.device.Width.SetValue(640 * 3)  # 1920
        self.device.Height.SetValue(480 * 3)  # 1440
        self.device.BslCenterX.Execute()
        self.device.BslCenterY.Execute()
        self.device.PixelFormat.SetValue("BayerRG8")

        # If the device is configured to send signals out on frame capture, make sure the output line is configured correctly
        self.device.LineSource.SetValue("ExposureActive")

        self.width = self.device.Width.GetValue()
        self.height = self.device.Height.GetValue()

        # Initialize self.lastFrame with a random frame
        rng = np.random.default_rng()
        self.lastFrame = rng.standard_normal(
            self.width * self.height * 3, dtype=np.float32
        )

        self.imageGrabHandler = _ImageGrabHandler(self.frameBuffer)
        self.device.RegisterImageEventHandler(
            self.imageGrabHandler, pylon.RegistrationMode_ReplaceAll, pylon.Cleanup_None
        )

        def onFrameGrab(frame):
            self.lastFrame = frame

        self.connected = True

    # Starts the event camera stream
    def startStreaming(self):
        
        # Uncap camera framerate
        self.device.TriggerMode.SetValue("Off")
        self.device.AcquisitionFrameRateEnable.SetValue(False)
        
        # Make sure camera is not triggering from external source
        self.device.TriggerSource.SetValue("Software")
        self.device.LineSource.SetValue("Off")
        self.device.TriggerMode.SetValue("Off")

        self.device.StartGrabbing(
            pylon.GrabStrategy_LatestImageOnly, pylon.GrabLoop_ProvidedByInstantCamera
        )
        self.streaming = True

    # Stops the event camera stream
    def stopStreaming(self):
        self.device.StopGrabbing()
        self.streaming = False

    def startRecording(
        self, recordingFileName="output", triggeredInput=False, framerateTarget=-1.0
    ):
        """Starts recording from the frame camera

        Args:
            recordingFileName (str, optional): The name of the file to be saved to disk. Defaults to "output".
            
            triggeredInput (bool, optional): Whether or not the camera should capture frames from some external trigger signal. Defaults to False.
            
            framerateTarget (float, optional): The target framerate of the camera if it is not being triggered by an external signal, so only effective if
            triggeredInput == False. If negative, the camera will maximize its framerate. Defaults to -1.0.
        """
        if not self.streaming or self.recording:
            return

        if triggeredInput:
            self.device.LineMode.SetValue("Input")
            self.device.TriggerSource.SetValue("Line1")
            self.device.TriggerMode.SetValue("On")
        else:
            if framerateTarget < 0:
                self.device.AcquisitionFrameRateEnable.SetValue(False)
            else:
                self.device.AcquisitionFrameRateEnable.SetValue(True)
                self.device.AcquisitionFrameRate.SetValue(framerateTarget)

            self.device.TriggerSource.SetValue("Software")
            self.device.LineMode.SetValue("Output")
            self.device.LineSource.SetValue("Line1")
            self.device.TriggerMode.SetValue("Off")

        self.imageGrabHandler.startRecording(recordingFileName)

        self.recording = True

    def stopRecording(self):
        self.imageGrabHandler._record = False
        self.recording = False
        
        # Uncap camera framerate
        self.device.TriggerMode.SetValue("Off")
        self.device.AcquisitionFrameRateEnable.SetValue(False)
        
        # Make sure camera is not triggering from external source
        self.device.TriggerSource.SetValue("Software")
        self.device.LineSource.SetValue("Off")
        self.device.TriggerMode.SetValue("Off")
