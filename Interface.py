import numpy as np
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo


dpg.create_context()

demo.show_demo()


# === Theme for disabled elements ===
with dpg.theme() as disabled_theme:
    with dpg.theme_component(dpg.mvMenuItem, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, [100, 100, 100])
        dpg.add_theme_color(dpg.mvThemeCol_Button, [100, 100, 100])

dpg.bind_theme(disabled_theme)

# === Export footage dialog ===
with dpg.window(
    label="Export footage", modal=True, show=False, tag="exportFootageDialog"
):
    dpg.add_text("Start timestamp (us):")
    dpg.add_input_double()
    dpg.add_text("End timestamp (us):")
    dpg.add_input_double()
    dpg.add_separator()
    dpg.add_text("Accumulation time (us) (?)")
    dpg.add_input_int(default_value=10000)
    dpg.add_text("Frames per second (?)")
    dpg.add_input_float(default_value=0.0)
    with dpg.group(horizontal=True):
        dpg.add_button(
            label="Export",
            width=75,
            callback=lambda: dpg.configure_item("exportFootageDialog", show=False),
        )
        dpg.add_button(
            label="Cancel",
            width=75,
            callback=lambda: dpg.configure_item("exportFootageDialog", show=False),
        )

# === Configure Frame Camera Dialog ===
with dpg.window(
    label="Configure frame camera", modal=True, show=False, tag="configureFrameCameraDialog"
):
    dpg.add_text("Target FPS: (?)")
    dpg.add_input_double(default_value=15.0)
    dpg.add_text("Resolution Width:")
    dpg.add_input_int(default_value=(640 * 3))
    dpg.add_text("Resolution Height:")
    dpg.add_input_int(default_value=(480 * 3))
    dpg.add_separator()
    with dpg.group(horizontal=True):
        dpg.add_button(
            label="Confirm",
            width=75,
            callback=lambda: dpg.configure_item("configureFrameCameraDialog", show=False),
        )
        dpg.add_button(
            label="Cancel",
            width=75,
            callback=lambda: dpg.configure_item("configureFrameCameraDialog", show=False),
        )

ecTexture = []
for i in range(0, 640 * 480):
    ecTexture.append(1)  # red
    ecTexture.append(0)  # green
    ecTexture.append(0)  # blue
    ecTexture.append(1)  # alpha
ecTexture = np.array(ecTexture)

fcTexture = []
for i in range(0, 640 * 480):
    fcTexture.append(0)  # red
    fcTexture.append(1)  # green
    fcTexture.append(0)  # blue
    fcTexture.append(1)  # alpha
fcTexture = np.array(fcTexture)

blendedTexture = ecTexture * (50 / 100) + fcTexture * (100 - 50) / 100

def updateOverlayTexture(_, blendPercentage):
    blendedTexture = ecTexture * (blendPercentage / 100) + fcTexture * (100 - blendPercentage) / 100
    dpg.set_value("blendedBuffer", blendedTexture)

# === Texture registry (used to setup camera framebuffers) ===
with dpg.texture_registry(show=True):
    
    dpg.add_dynamic_texture(640, 480, ecTexture, tag="eventCameraFrameBuffer")
    dpg.add_dynamic_texture(640, 480, fcTexture, tag="frameCameraFrameBuffer")
    dpg.add_dynamic_texture(640, 480, blendedTexture, tag="blendedBuffer")

# === Camera viewports window ===
with dpg.window(tag="viewportWindow", label="Viewports", no_close=True, no_collapse=True):
    dpg.add_image("eventCameraFrameBuffer", tag="eventCameraViewport", pos=(0, 0))
    dpg.add_image("frameCameraFrameBuffer", tag="frameCameraViewport", pos=(640, 0))
    dpg.add_text(
        "No viewports visible (Change view mode in Display > Stream view)",
        tag="noViewportsMessage",
        show=False,
    )

# === Seeking scrubber window ===
with dpg.window(tag="scrubberWindow"):
    dpg.add_slider_double(width=-1)
    
    with dpg.table(width=-1, header_row=False):
        dpg.add_table_column(width_stretch=True)
        dpg.add_table_column(width_stretch=False)
        dpg.add_table_column(width_stretch=True)
        with dpg.table_row():
            dpg.add_table_cell()
            with dpg.group(horizontal=True):
                dpg.add_button(label="Seek back")
                dpg.add_button(label="Pause/play")
                dpg.add_button(label="Seek forwared")
            dpg.add_table_cell()

def setViewportMode(_, mode):
    if mode == "None":
        dpg.hide_item("eventCameraViewport")
        dpg.hide_item("frameCameraViewport")
        dpg.set_item_pos("frameCameraViewport", (0, 0))
        dpg.configure_item("viewportWindow", width=640, height=30)
        dpg.show_item("noViewportsMessage")
    elif mode == "Event camera only":
        dpg.show_item("eventCameraViewport")
        dpg.hide_item("frameCameraViewport")
        dpg.set_item_pos("frameCameraViewport", (0, 0))
        dpg.configure_item("viewportWindow", width=640, height=480)
        dpg.hide_item("noViewportsMessage")
    elif mode == "Frame camera only":
        dpg.hide_item("eventCameraViewport")
        dpg.show_item("frameCameraViewport")
        dpg.set_item_pos("frameCameraViewport", (0, 0))
        dpg.configure_item("viewportWindow", width=640, height=480)
        dpg.hide_item("noViewportsMessage")
    elif mode == "Side-by-side":
        dpg.show_item("eventCameraViewport")
        dpg.show_item("frameCameraViewport")
        dpg.set_item_pos("frameCameraViewport", (640, 0))
        dpg.configure_item("viewportWindow", width=(640 * 2), height=480)
        dpg.hide_item("noViewportsMessage")
    elif mode == "Overlay":
        dpg.show_item("eventCameraViewport")
        dpg.show_item("frameCameraViewport")
        dpg.set_item_pos("frameCameraViewport", (0, 0))
        dpg.configure_item("viewportWindow", width=640, height=480)
        dpg.hide_item("noViewportsMessage")


# === Menu bar ===
with dpg.viewport_menu_bar():
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Open recording", tag="openRecordingButton")
        dpg.add_menu_item(
            label="Close recording", tag="closeRecordingButton", enabled=False
        )
        dpg.add_separator()
        dpg.add_menu_item(
            label="Connect to cameras",
            tag="connectCamerasButton",
        )
        dpg.add_menu_item(
            label="Disconnect from cameras",
            tag="disconnectCamerasButton",
            enabled=False,
        )
        dpg.add_separator()
        dpg.add_menu_item(
            label="Export footage",
            callback=lambda: dpg.configure_item("exportFootageDialog", show=True),
        )
        dpg.add_separator()
        dpg.add_menu_item(label="Exit")

    with dpg.menu(label="Display"):
        with dpg.menu(label="Stream view"):
            dpg.add_radio_button(
                (
                    "None",
                    "Side-by-side",
                    "Event camera only",
                    "Frame camera only",
                    "Overlay",
                ),
                callback=setViewportMode,
                default_value="Side-by-side",
            )
            dpg.add_slider_float(callback=updateOverlayTexture)

        with dpg.menu(label="Event stream"):
            with dpg.menu(label="Color scheme"):
                dpg.add_radio_button(("Light", "Dark", "CoolWarm", "Gray"))
            with dpg.menu(label="Frame generation"):
                dpg.add_text("Accumulation time (us) (?)", tag="accumulationTimeLabel")
                dpg.add_input_int(default_value=10000)
                dpg.add_text("Frames per second (?)", tag="eventFpsLabel")
                dpg.add_input_float(default_value=0.0)

                with dpg.tooltip("accumulationTimeLabel"):
                    dpg.add_text(
                        "The window of time which we display events from in the event stream"
                    )
                with dpg.tooltip("eventFpsLabel"):
                    dpg.add_text(
                        "If set to 0, accumulation time is used to compute frames per second"
                    )

    with dpg.menu(label="Settings"):
        dpg.add_menu_item(label="Event camera configuration", enabled=False)
        dpg.add_menu_item(label="Frame camera configuration", callback=lambda: dpg.configure_item("configureFrameCameraDialog", show=True))

    dpg.add_menu_item(label="Help")

# dpg.show_metrics() # Shows performance stats
dpg.show_imgui_demo()

dpg.create_viewport(title="Eventcam Studio", width=1280, height=720)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
