import numpy as np

class Memory:
    def __init__(self, size):
        self.data = np.zeros(size)

    def write(self, address, byte):
        self.data[address] = byte

    def read(self, adress):
        return self.data[adress]
