import dearpygui.dearpygui as dpg
import numpy as np
from EventCamera import EventCamera
from FrameCamera import FrameCamera

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

# === Setup Event Camera ===

eventCam = EventCamera()
eventCam.connect()

def onEventFrame(frame: np.ndarray):
    frame = frame.ravel()
    dpg.set_value("eventCameraFrameBuffer", frame)

eventCam.registerCallback("dearpygui", onEventFrame)

# === Setup Frame Camera ===

frameCam = FrameCamera()
frameCam.connect()

def onFrameFrame(frame: np.ndarray):
    frame = frame.ravel()
    dpg.set_value("frameCameraFrameBuffer", frame)

frameCam.registerCallback("dearpygui", onFrameFrame)

# === DPG

with dpg.texture_registry(show=True):
    dpg.add_raw_texture(
        eventCam.width,
        eventCam.height,
        eventCam.lastFrame,
        format=dpg.mvFormat_Float_rgb,
        tag="eventCameraFrameBuffer",
    )
    dpg.add_raw_texture(
        frameCam.width,
        frameCam.height,
        frameCam.lastFrame,
        format=dpg.mvFormat_Float_rgb,
        tag="frameCameraFrameBuffer",
    )

with dpg.window():
    dpg.add_image("eventCameraFrameBuffer")
    dpg.add_image("frameCameraFrameBuffer")
    # pass

frameCam.beginStreaming()
eventCam.beginStreaming()

dpg.show_metrics()
dpg.show_viewport()

while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

dpg.destroy_context()
