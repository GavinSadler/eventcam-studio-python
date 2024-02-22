from typing import Callable

import numpy as np


class Camera:

    # Stores the width of the camera upon connect() being called
    width = -1
    
    # Stores the height of the camera upon connect() being called
    height = -1

    # Stores the last frame generated by the camera
    lastFrame: np.ndarray = None

    callbacks: dict[str, Callable[[np.ndarray], None]] = {}

    def registerCallback(self, callbackName: str, callback: Callable[[np.ndarray], None]):
        self.callbacks[str] = callback

    def deregisterCallback(self, callbackName: str):
        self.callbacks.pop(str)