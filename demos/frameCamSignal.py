
import os
import time

from EventCamera import EventCamera
from FrameCamera import FrameCamera

# This program lets the frame camera drive the sync signal

OUTPUT_DIRECTORY = "./output"
OUTPUT_NAME = time.strftime("%Y-%m-%d_%H-%M-%S")

if not os.path.exists(OUTPUT_DIRECTORY):
    os.mkdir(OUTPUT_DIRECTORY)

ec = EventCamera()
fc = FrameCamera()

ec.connect()
fc.connect()

ec.startStreaming()
fc.startStreaming(targetFramerate=10.0)

fc.device.LineInverter.SetValue(True)
fc.device.LineMode.SetValue("Output")
fc.device.LineSource.SetValue("ExposureActive")

fc.device.AcquisitionFrameRate.SetValue(10.0)
fc.device.AcquisitionFrameRateEnable.SetValue(True)

ec.startRecording(f"{OUTPUT_DIRECTORY}/EVENT_DATA_{OUTPUT_NAME}.raw")
fc.startRecording(f"{OUTPUT_DIRECTORY}/{OUTPUT_NAME}")

time.sleep(3)

fc.stopRecording()
ec.stopRecording()

fc.stopStreaming()
ec.stopStreaming()

print(f"All done, recordings in {OUTPUT_DIRECTORY}")
