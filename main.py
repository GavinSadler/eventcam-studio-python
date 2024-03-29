import dearpygui.dearpygui as dpg
import numpy as np
from Camera import Camera
from EventCamera import EventCamera
from FrameCamera import FrameCamera

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

# === Setup Event Camera ===

eventCam = EventCamera()
eventCam.connect()

def onEventFrame(frame: np.ndarray):
    dpg.set_value("eventCameraFrameBuffer", frame.ravel())

eventCam.registerCallback("dearpygui", onEventFrame)

# === Setup Frame Camera ===

frameCam = FrameCamera()
frameCam.connect()

def onFrameFrame(frame: np.ndarray):
    dpg.set_value("frameCameraFrameBuffer", frame.ravel())

frameCam.registerCallback("dearpygui", onFrameFrame)

# === DPG

# Viewport textures
with dpg.texture_registry():
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

with dpg.window(no_close=True, no_collapse=True):

    with dpg.group(horizontal=True):
        dpg.add_image("eventCameraFrameBuffer")
        dpg.add_image("frameCameraFrameBuffer", width=640, height=480)

    with dpg.group(horizontal=True):
        dpg.add_text("Event Camera Stream: ")
        dpg.add_button(label="Start", callback=lambda: eventCam.startStreaming())
        dpg.add_button(label="Stop", callback=lambda: eventCam.stopStreaming())
        
    with dpg.group(horizontal=True):
        dpg.add_text("Frame Camera Stream: ")
        dpg.add_button(label="Start", callback=lambda: frameCam.startStreaming())
        dpg.add_button(label="Stop", callback=lambda: frameCam.stopStreaming())
    
    with dpg.group(horizontal=True):
        dpg.add_text("Event Camera Record: ")
        dpg.add_button(label="Start", callback=lambda: eventCam.startRecording())
        dpg.add_button(label="Stop", callback=lambda: eventCam.stopRecording())
        
    with dpg.group(horizontal=True):
        dpg.add_text("Frame Camera Record: ")
        dpg.add_button(label="Start", callback=lambda: frameCam.startRecording())
        dpg.add_button(label="Stop", callback=lambda: frameCam.stopRecording())

dpg.show_metrics() # Shows performance stats
dpg.show_imgui_demo()

# eventCam.startStreaming()
# frameCam.startStreaming()

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
