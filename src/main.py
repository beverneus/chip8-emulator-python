import time
import math
import numpy as np
import pygame

from memory import Memory
from registry import Registry, ProgramCounter
from stack import Stack
from display import Display
from timer import Timer

class CPU:
    def __init__(self, memory, PC, I, registers, display, stack):
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
        self.stack = stack

    def fetch(self):
        PC_value = self.PC.get()
        a = f"{self.memory.read(PC_value):08b}"
        b = f"{self.memory.read(PC_value+1):08b}"
        self.PC.increment(2)
        self.opcode = a + b

    def decode(self):
        # DECODE/EXECUTE
        self.category = int(self.opcode[:4], 2) # Get first 4 binary digits
        self.X = int(self.opcode[4:8], 2) # Get second 4 binary digits
        self.Y = int(self.opcode[8:12], 2) # Get third 4 binary digits
        self.N = int(self.opcode[12:], 2) # Get last 4 binary digits
        self.NN = int(self.opcode[8:], 2) # Get second byte
        self.NNN = int(self.opcode[4:], 2) # Get everything except first 4 binary digits

        match self.category:
            case 0x0000:
                match self.NN:
                    case 0x00:  # CLEAR SCREEN
                        self.display.clear()
                    case 0xEE:  # RETURN FROM SUBROUTINE
                        address = self.stack.pop()
                        self.PC.set(adress)
            case 0x1: # SET PC TO NNN
                self.PC.set(self.NNN)
            case 0x2:  # START SUBROUTINE AT NNN
                self.stack.push(self.PC.get())
                self.PC.set(self.NNN)
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
                I_value = self.I.get()
                sprite = [self.memory.read(i) for i in range(I_value, I_value+self.N)]
                for i, line in enumerate(sprite):
                    assert i < self.N, 'Sprite lines go further than N'
                    byte = f'{line:08b}'
                    for j in range(8):
                        if int(byte[j]) == 1:
                            self.display.flip_pixel(x + j, y + i)
                self.display.blit()
            case 0xE:
                pass
            case 0xF:
                pass


memory = Memory(4096)
stack = Stack()

PC = ProgramCounter()
I = Registry(16)

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
rom_location = 'assets/roms/test_opcode.ch8'
with open(rom_location, 'rb') as rom:
    rom_hex = rom.read().hex()
for i in range(0, len(rom_hex), 2):
    A = rom_hex[i]
    B = rom_hex[i+1]
    memory.write(0x200+i//2, int(f'0x{A}{B}', 16))

cpu = CPU(memory=memory, PC=PC, I=I, registers=registers, display=display, stack=stack)

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            display.flip_pixel(13,13)
    cpu.fetch()
    cpu.decode()
    
    timer.update()
    buzzer.update()
        
    clock.tick(700)
    display.blit()
