import dearpygui.dearpygui as dpg
import numpy as np
from pypylon import pylon

# === GUI stuff === #

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

# === Connect to frame camera === #

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

camera.Width.SetValue(640)
camera.Height.SetValue(480)
camera.BslCenterX.Execute()
camera.BslCenterY.Execute()
camera.PixelFormat.SetValue("RGB8")
camera.AcquisitionFrameRate.SetValue(30)
camera.AcquisitionFrameRateEnable.SetValue(True)
# camera.TriggerMode.setValue("On" or "Off")
# camera.TriggerSource.setValue("Line 1" or "Line 2" or ...)

width = camera.Width.GetValue()
height = camera.Height.GetValue()

# === More GUI stuff === #

initialData = []
for i in range(0, height * width):
    initialData.append(0)
    initialData.append(255)
    initialData.append(255)

initialData = np.array(initialData)
initialData = initialData.ravel()
initialData = np.asfarray(initialData, "f")
initialData = np.true_divide(initialData, 255.0)

with dpg.texture_registry(show=True):
    dpg.add_raw_texture(
        width,
        height,
        initialData,
        format=dpg.mvFormat_Float_rgb,
        tag="frameFrameBuffer",
    )

with dpg.window(label="Example Window"):
    dpg.add_image("frameFrameBuffer")

# === Frame camera event handler === #

class ImageGrabHandler(pylon.ImageEventHandler):
    def __init__(self):
        super().__init__()
    def OnImageGrabbed(self, camera, grabResult: pylon.GrabResult):
        frame = grabResult.GetArray().ravel()
        frame = np.asfarray(frame, "f")
        frame = np.true_divide(frame, 255.0)
        dpg.set_value("frameFrameBuffer", frame)

handler = ImageGrabHandler()
camera.RegisterImageEventHandler(handler, pylon.RegistrationMode_ReplaceAll, pylon.Cleanup_None)

camera.StartGrabbing(pylon.GrabStrategy_LatestImages, pylon.GrabLoop_ProvidedByInstantCamera) # === Frame Camera, start grabbing! ===

# === More GUI stuff === #

dpg.show_metrics()
dpg.show_viewport()

while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

camera.StopGrabbing() # === Frame Camera, stop grabbing! ===

dpg.destroy_context()
