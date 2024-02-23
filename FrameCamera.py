import numpy as np
from pypylon import pylon

from Camera import Camera

# Needed by pylon API in order to facilitate callback functionality
class _ImageGrabHandler(pylon.ImageEventHandler):
    def __init__(self, callbacks):
        super().__init__()
        self.callbacks = callbacks
    def OnImageGrabbed(self, camera: pylon.InstantCamera, grabResult: pylon.GrabResult):
        frame = np.asfarray(grabResult.GetArray(), "f")
        frame = np.true_divide(frame, 255.0)

        for callback in self.callbacks.values():
            callback(frame)

class FrameCamera(Camera):

    device: pylon.InstantCamera = None
    imageGrabHandler: _ImageGrabHandler = None

    def __init__(self) -> None:
        super().__init__()

    def connect(self):
        self.device = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.device.Open()

        self.device.Width.SetValue(640 * 4)
        self.device.Height.SetValue(480 * 4)
        self.device.BslCenterX.Execute()
        self.device.BslCenterY.Execute()
        self.device.PixelFormat.SetValue("RGB8")
        self.device.AcquisitionFrameRate.SetValue(30)
        self.device.AcquisitionFrameRateEnable.SetValue(True)
        # camera.TriggerMode.setValue("On" or "Off")
        # camera.TriggerSource.setValue("Line 1" or "Line 2" or ...)

        self.width = self.device.Width.GetValue()
        self.height = self.device.Height.GetValue()
        
        # Initialize self.lastFrame with a random frame
        rng = np.random.default_rng()
        self.lastFrame = rng.standard_normal(self.width * self.height * 3, dtype=np.float32)
        
        self.imageGrabHandler = _ImageGrabHandler(self.callbacks)
        self.device.RegisterImageEventHandler(self.imageGrabHandler, pylon.RegistrationMode_ReplaceAll, pylon.Cleanup_None)
        
        def onFrameGrab(frame):
            self.lastFrame = frame
        
        self.registerCallback("_internal", onFrameGrab)
        
        self.connected = True
    
    # Starts the event camera stream
    def startStreaming(self):
        self.device.StartGrabbing(pylon.GrabStrategy_LatestImages, pylon.GrabLoop_ProvidedByInstantCamera)
        self.streaming = True

    # Stops the event camera stream
    def stopStreaming(self):
        self.device.StopGrabbing()
        self.streaming = False
