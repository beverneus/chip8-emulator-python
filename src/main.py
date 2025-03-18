import time
import math
import numpy as np
import pygame

class Memory:
    def __init__(self, size):
        self.data = np.zeros(size)
    
    def write(self, address, byte):
        self.data[address] = byte
    
    def read(self, adress):
        return self.data[adress]


class Registry:
    def __init__(self):
        self.value = None
    
    def set(self, value):
        self.value = value
    
    def get(self):
        return self.value


class Stack:
    def __init__(self):
        stack = []
    
    def push(self, data):
        self.stack.append(data)
    
    def pop(self):
        return self.stack.pop()

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)

class Display:
    def __init__(self, width, height, scale):
        self.width = width
        self.height = height
        
        self.scale = scale
        self.dwidth = self.scale * self.width
        self.dheight = self.scale * self.height
        
        self.state = np.zeros((self.width, self.height))
        
        self.screen = pygame.display.set_mode((self.dwidth, self.dheight))
        pygame.display.set_caption('CHIP-8')
        
        self.canvas = pygame.Surface((self.width, self.height))
        self.canvas.fill(BLACK)
    
    def clear(self):
        self.state = np.zeros((self.width, self.height))
        self.canvas.fill(BLACK)
    
    def flip_pixel(self, x, y):
        color = BLACK if self.state[x, y] else WHITE
        self.canvas.set_at((x, y), color)
        self.state[x, y] = (self.state[x,y] + 1) % 2
        
    def blit(self):
        scaled_canvas = pygame.transform.scale(self.canvas, (self.dwidth, self.dheight))
        self.screen.blit(scaled_canvas, (0, 0))


class Timer:
    def __init__(self, buzzer=False, beep_sound=None):
        self.time = 0
        self.last_set = 0
        self.buzzer = buzzer
        self.beep_sound = pygame.mixer.Sound("assets/audio/beep.wav")

    def set(self, amount):
        self.time=amount
        self.last_set = time.time()

    def update(self):
        if self.time != 0:
            current_time = time.time()
            diff = math.floor((current_time - self.last_set) / (1 / 60))
            self.time -= diff
            self.last_set = current_time if diff != 0 else self.last_set
            if self.buzzer and diff and self.time%30 == 0:
                self.beep_sound.play()


    def get(self):
        return self.time

class CPU:
    def __init__(self, memory, PC, I, registers, display):
        self.opcode = 0
        self.category = 0
        self.X = 0
        self.Y = 0
        self.N = 0
        self.NN = 0
        self.NNN = 0
        self.memory = memory
        self.PC = PC
        self.I = I
        self.registers = registers
        self.display = display

    def fetch(self):
        PC_value = self.PC.get()
        a = f"{self.memory.read(PC_value):07b}"
        b = f"{self.memory.read(PC_value):07b}"
        self.PC.set(PC_value + 2)
        self.opcode = int(a + b)
        
    def decode(self):
        #DECODE/EXECUTE
        self.category = self.opcode & 61440 # Get first 4 binary digits
        self.X = self.opcode & 3840 # Get second 4 binary digits
        self.Y = self.opcode & 240 # Get third 4 binary digits
        self.N = self.opcode & 15 # Get last 4 binary digits
        self.NN = self.opcode & 255 # Get second byte
        self.NNN = self.opcode & 4095 # Get everything except first 4 binary digits

        match self.category:
            case 0x0:
                if self.NNN == 0x0E0: # CLEAR SCREEN
                    self.display.clear()
            case 0x1: # SET PC TO NNN
                self.PC.set(self.NNN)
            case 0x2:
                pass
            case 0x3:
                pass
            case 0x4:
                pass
            case 0x5:
                pass
            case 0x6: # Set VX to NN
                self.registers[self.X].set(self.NN)
            case 0x7: # ADD NN to VX
                register = self.registers[self.X]
                value = register.get()
                register.set(value + self.NN)
            case 0x8:
                pass
            case 0x9:
                pass
            case 0xA: # SET INDEX TO NNN
                self.I.set(self.NNN)
            case 0xB:
                pass
            case 0xC:
                pass
            case 0xD: # DISPLAY SPRITE LOCATED IN MEMORY LOCATION I AT VX AND VY
                x = self.registers[self.X].get() % self.display.width
                y = self.registers[self.Y].get()
                pass
                
                
            case 0xE:
                pass
            case 0xF:
                pass


memory = Memory(4096)

PC = Registry()
I = Registry()

registers = [Registry() for i in range(16)]

pygame.init()
pygame.mixer.init()
display = Display(64, 32, 10)

timer = Timer()
buzzer = Timer(True)

# LOAD FONT
with open('assets/fonts/font.txt', 'r', encoding='UTF-8') as font:
    content = font.read().replace('\n', ' ').strip()
    data = map(lambda t: int(t, 16), content.split(', '))
    for adress, code in zip(range(int(0x50), int(0x9F)+1), data):
        memory.write(adress, code)

# LOAD ROM
pass

cpu = CPU(memory=memory, PC=PC, I=I, registers=registers, display=display)

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            display.flip_pixel(10, 10)

    timer.update()
    buzzer.update()
    
    display.blit()
    pygame.display.flip()
    
    clock.tick(700)
