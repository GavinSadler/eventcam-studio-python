
from typing import Callable, List
import numpy as np

class FrameBuffer:
    """
        Keeps a buffer which we can update
        Will update all subscribers when a new value is set
    """
    
    _buffer: np.ndarray
    _width: int
    _height: int
    _subscribers: List[Callable[[np.ndarray], None]]

    def __init__(self, width, height):
        """ Initializes a black frambuffer of given width and height """
        self._width = width
        self._height = height
        self._subscribers = []

        # Buffer should be black upon initialization
        self.setColor(0, 0, 0)
    
    def setColor(self, r: float, g: float, b: float, a = 1.0):
        data = []

        for i in range(0, self._width * self._height):
            data.append(r)  # Red
            data.append(g)  # Green
            data.append(b)  # Blue
            data.append(a)  # Alpha
        
        self.set(np.array(data, "f"))

    def set(self, newBuffer: np.ndarray):
        self._buffer = newBuffer
        self.notifySubscribers()

    def get(self):
        return self._buffer

    def registerCallback(self, callback: Callable[[np.ndarray], None]):
        self._subscribers.append(callback)
        
    def notifySubscribers(self):
        for s in self._subscribers:
            s(self._buffer)
