import numpy as np

class Memory:
    def __init__(self, size):
        self.data = list(np.zeros(size))

    def write(self, address, byte):
        self.data[address] = byte

    def read(self, adress):
        return int(self.data[adress])
