
from time import sleep

import numpy as np
from FrameCamera import FrameCamera

frameCam = FrameCamera()
frameCam.connect()

numFrames = 0

def onFrameFrame(frame: np.ndarray):
    global numFrames
    numFrames += 1

frameCam.registerCallback("dearpygui", onFrameFrame)

frameCam.startStreaming()

delay = 10

sleep(delay)

print(f"{numFrames} in {delay} seconds, {numFrames / delay} fps")
print(f"{frameCam.device.ResultingFrameRate.Value} Fps from the camera")