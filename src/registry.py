class Registry:
    def __init__(self, bits=8):
        self.value = 0
        if bits is not None:
            self.max_value = 2**bits
        else:
            self.max_value = None
    def set(self, value):
        if self.max_value is not None:
            self.value = value % self.max_value
        else:
            self.value = value

    def get(self):
        return self.value

class ProgramCounter(Registry):
    def __init__(self):
        Registry.__init__(self)
        self.value = 0x200
        self.max_value = None
    
    def increment(self, amount):
        self.value += amount
