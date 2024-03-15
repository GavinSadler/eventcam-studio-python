import cv2
import numpy as np
from pypylon import pylon
import threading
from Camera import Camera
import time


# Needed by pylon API in order to facilitate callback functionality
class _ImageGrabHandler(pylon.ImageEventHandler):

    _thread = None
    imgageHandler = pylon.PylonImage()
    record = False

    def __init__(self, callbacks):
        super().__init__()
        self.callbacks = callbacks

    def _processFrame(self, frame: np.ndarray):
        frame = cv2.cvtColor(frame, cv2.COLOR_BayerBG2RGB)
        frame = np.asfarray(frame, "f")
        frame = np.true_divide(frame, 255.0)

        for callback in self.callbacks.values():
            callback(frame)

    def startRecording(self, baseFilename: str):
        self.baseFilename = baseFilename
        self.frameNumber = 0
        self.record = True
        
    def stopRecording(self):
        self.record = False

    def OnImageGrabbed(self, camera: pylon.InstantCamera, grabResult: pylon.GrabResult):
        if self.record:
            self.imgageHandler.AttachGrabResultBuffer(grabResult)
            self.imgageHandler.Save(pylon.ImageFileFormat_Raw, f"{self.baseFilename}_{self.frameNumber}.png")
            # print(grabResult.GetImageFormat())
            # print(self.imgageHandler.CanSaveWithoutConversion(grabResult.GetImageFormat()))
            self.imgageHandler.Release()
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
        self.device.Height.SetValue(480 * 3) # 1440
        self.device.BslCenterX.Execute()
        self.device.BslCenterY.Execute()
        self.device.PixelFormat.SetValue("BayerRG8")
        self.device.TriggerSource.SetValue("Line1")
        # self.device.TriggerSource.SetValue("Line 1")
        # self.device.AcquisitionFrameRate.SetValue(30)
        # self.device.AcquisitionFrameRateEnable.SetValue(True)

        self.width = self.device.Width.GetValue()
        self.height = self.device.Height.GetValue()

        # Initialize self.lastFrame with a random frame
        rng = np.random.default_rng()
        self.lastFrame = rng.standard_normal(
            self.width * self.height * 3, dtype=np.float32
        )

        self.imageGrabHandler = _ImageGrabHandler(self.callbacks)
        self.device.RegisterImageEventHandler(
            self.imageGrabHandler, pylon.RegistrationMode_ReplaceAll, pylon.Cleanup_None
        )

        def onFrameGrab(frame):
            self.lastFrame = frame

        self.registerCallback("_internal", onFrameGrab)

        self.connected = True

    # Starts the event camera stream
    def startStreaming(self, triggeredInput = False):
                
        self.device.TriggerMode.SetValue("On" if triggeredInput else "Off")
        
        self.device.StartGrabbing(
            pylon.GrabStrategy_LatestImageOnly, pylon.GrabLoop_ProvidedByInstantCamera
        )
        self.streaming = True

    # Stops the event camera stream
    def stopStreaming(self):
        self.device.StopGrabbing()
        self.streaming = False
    
    def startRecording(self, recordingFileName = "output"):
        if not self.streaming or self.recording:
            return
        
        self.imageGrabHandler.startRecording(recordingFileName)
        
        self.recording = True
        
    def stopRecording(self):        
        self.imageGrabHandler.record = False
        self.recording = False
        
