import threading

import dearpygui.dearpygui as dpg
import numpy as np
from metavision_core.event_io import EventsIterator
from metavision_core.event_io.raw_reader import initiate_device
from metavision_sdk_core import PeriodicFrameGenerationAlgorithm

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

device = initiate_device("")

device.get_i_ll_biases().set("bias_fo", 1600)

mv_iterator = EventsIterator.from_device(device=device)
height, width = mv_iterator.get_size()

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
        tag="eventFrameBuffer",
    )


def frame_gen_callback(ts, cd_frame):
    cd_frame = cd_frame.ravel()
    cd_frame = np.asfarray(cd_frame, "f")
    cd_frame = np.true_divide(cd_frame, 255.0)
    dpg.set_value("eventFrameBuffer", cd_frame)


periodic_frame_gen = PeriodicFrameGenerationAlgorithm(
    sensor_width=width, sensor_height=height, fps=30
)
periodic_frame_gen.set_output_callback(frame_gen_callback)

with dpg.window(label="Example Window"):
    dpg.add_image("eventFrameBuffer")

dpg.show_metrics()
dpg.show_viewport()

quit = threading.Event()

def processEventCam(mv_iterator, periodic_frame_gen, quitEvent):
    for evs in mv_iterator:

        if quitEvent.is_set():
            break

        periodic_frame_gen.process_events(evs)


eventCamThread = threading.Thread(
    target=processEventCam, args=(mv_iterator, periodic_frame_gen, quit)
)
eventCamThread.start()

while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

dpg.destroy_context()

quit.set()
