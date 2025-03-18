import time
import math
import numpy as np
import pygame

from memory import Memory
from registry import Registry
from stack import Stack
from display import Display
from timer import Timer

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
            case 0xD: # DISPLAY SPRITE LOCATED IN MEMORY LOCATION I AT VX AND VY WITH N VERTICAL LINES
                x = self.registers[self.X].get() % (self.display.width - 1)
                y = self.registers[self.Y].get()
                sprite = [memory[i] for i in range(self.I, self.I+self.N)]
                for i, line in enumerate(sprite):
                    assert i < self.N, 'Sprite lines go further than N'
                    byte = bin(line)[2:]
                    for j in range(8):
                        if byte[j] == 1:
                            self.display.flip(x + j, y + i)
                self.display.blit()
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
