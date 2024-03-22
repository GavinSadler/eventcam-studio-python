
import numpy as np

class Framebuffer:
    
    _buffer: np.ndarray
    _width: int
    _height: int

    def __init__(self, width, height):
        
        self._width = width
        self._height = height

        # Buffer should be black upon initialization
        self.setColor(0, 0, 0)
    
    def setColor(self, r: float, g: float, b: float, a = 1.0):
        data = []

        for i in range(0, self._width * self._height):
            data.append(r)  # Red
            data.append(g)  # Green
            data.append(b)  # Blue
            data.append(a)  # Alpha
        
        self._buffer = np.array(data, "f")

    def set(self, newBuffer):
        self._buffer = newBuffer

    def get(self):
        return self._buffer
