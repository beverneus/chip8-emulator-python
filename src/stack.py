class Stack:
    def __init__(self):
        stack = []

    def push(self, data):
        self.stack.append(data)

    def pop(self):
        return self.stack.pop()
