#!/usr/bin/env python

from enum import Enum
from bitstream import BitStream

#MAJOR.MINOR.PATCH
__version__ = "1.0.0"

#Buffer
class DataBufferState(Enum):
    BUFFER_ENABLED = 33
    BUFFER_DISABLED = 55

class DataBuffer:
    """
    Buffer data and control class
    state = used to control data in buffer are valid for use
    flush = used to control if new data is written to buffer
    watch = used to take an action if size data in buffer at some value
    """

    def __init__(self, 
            buffer=BitStream(), 
            state=DataBufferState.BUFFER_ENABLED, 
            flush=False, 
            watch=False):
        self.buffer = buffer
        self.state = state
        self.flush = flush
        self.watch = watch
    
    def Enable(self):
        self.state = DataBufferState.BUFFER_ENABLED
    
    def Disable(self):
        self.state = DataBufferState.BUFFER_DISABLED

    def isEnabled(self):
        return self.state == DataBufferState.BUFFER_ENABLED

    def isDisabled(self):
        return self.state == DataBufferState.BUFFER_DISABLED

    def GetState(self):
        return self.state

    def ResetBuffer(self):
        self.buffer = BitStream()
    
    def GetSizeInBits(self):
        return len(self.buffer.buffer)

    def GetSizeInBytes(self):
        return int(len(self.buffer)/8)

databuffer = DataBuffer()
