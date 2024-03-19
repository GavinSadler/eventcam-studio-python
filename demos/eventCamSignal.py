
import time
import os
from EventCamera import EventCamera
from FrameCamera import FrameCamera

# This program lets the event camera drive the sync signal

ec = EventCamera()
fc = FrameCamera()

ec.connect()
fc.connect()

ec.startStreaming()
fc.startStreaming(triggeredInput=True)

outputPath = "./out"

if not os.path.exists(outputPath):
    os.mkdir(outputPath)

timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

ec.stopExternalClock()

fc.startRecording(f"{outputPath}/{timestamp}")
ec.startRecording(f"{outputPath}/{timestamp}.raw")

ec.startExternalClock(period=(1/15))

while True:
    input()
    break

ec.stopRecording()
fc.stopRecording()

fc.stopStreaming()
ec.stopStreaming()

print(f"All done, recordings in {outputPath}")
