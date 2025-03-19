import time
import math
import numpy as np
import pygame
from typing import Type
import random

from memory import Memory
from registry import Registry, ProgramCounter
from stack import Stack
from display import Display
from timer import Timer

MODERN_SHIFT = True # SHIFT VX in place instead of MOVING VY to VX and then SHIFT
MODERN_JUMP_WITH_OFFSET = False

class CPU:
    def __init__(self, memory, PC: Type[ProgramCounter], I, registers, display, stack, timer, buzzer):
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
        self.timer = timer
        self.buzzer = buzzer

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
                        self.PC.set(address)
            case 0x1: # SET PC TO NNN
                self.PC.set(self.NNN)
            case 0x2:  # START SUBROUTINE AT NNN
                self.stack.push(self.PC.get())
                self.PC.set(self.NNN)
            case 0x3: # VX == NN
                if self.registers[self.X].get() == self.NN:
                    self.PC.increment(2)
            case 0x4: # VX != NN
                if self.registers[self.X].get() != self.NN:
                    self.PC.increment(2)
            case 0x5: # VX == VY
                if self.registers[self.X].get() == self.registers[self.Y].get():
                    self.PC.increment(2)
            case 0x6: # SET VX to NN
                self.registers[self.X].set(self.NN)
            case 0x7: # ADD NN to VX
                register = self.registers[self.X]
                value = register.get()
                register.set(value + self.NN)
            case 0x8:
                match self.N:
                    case 0x0:  # SET VX to VY
                        VY = self.registers[self.Y].get()
                        self.registers[self.X].set(VY)
                    case 0x1: # SET VX to BINARY OR of VX and VY
                        VX = self.registers[self.X].get()
                        VY = self.registers[self.Y].get()
                        VX = VX | VY
                        self.registers[self.X].set(VX)
                    case 0x2: # SET VX to BINARY AND of VX and VY
                        VX = self.registers[self.X].get()
                        VY = self.registers[self.Y].get()
                        VX = VX & VY
                        self.registers[self.X].set(VX)
                    case 0x3: # SET VX to LOGICAL XOR of VX and VY
                        VX = self.registers[self.X].get()
                        VY = self.registers[self.Y].get()
                        VX = VX ^ VY
                        self.registers[self.X].set(VX)
                    case 0x4: # SET VX to SUM of VX and VY, IF VX overflows SET VF to 1 ELSE SET VF to 0
                        VX = self.registers[self.X].get()
                        VY = self.registers[self.Y].get()
                        VX += VY
                        if VX >= 255:
                            self.registers[0xF].set(1)
                        else:
                            self.registers[0xF].set(0)
                        self.registers[self.X].set(VX)
                    case 0x5: # SET VX to VX - VY
                        VX = self.registers[self.X].get()
                        VY = self.registers[self.Y].get()
                        VX -= VY
                        self.registers[self.X].set(VX)
                    case 0x6: # (OPTIONALLY SET VX TO VY) SHIFT VX RIGHT by 1
                        if not MODERN_SHIFT:
                            VX = self.registers[self.Y].get() >> 1
                        else:
                            VX = self.registers[self.X].get() >> 1
                        self.registers[self.X].set(VX)
                    case 0x7: # SET VX to VY - VX
                        VX = self.registers[self.X].get()
                        VY = self.registers[self.Y].get()
                        VX = VY - VX
                        self.registers[self.X].set(VX)
                    case 0xE: # (OPTIONALLY SET VX TO VY) SHIFT VX LEFT by 1
                        if not MODERN_SHIFT:
                            VX = self.registers[self.Y].get() << 1
                        else:
                            VX = self.registers[self.X].get() << 1
                        self.registers[self.X].set(VX)
            case 0x9: # VX != VY
                if self.registers[self.X].get() != self.registers[self.Y].get():
                    self.PC.increment(2)
            case 0xA: # SET INDEX TO NNN
                self.I.set(self.NNN)
            case 0xB: # JUMP to NNN +  V0 (or with modern switch jump to XNN + VX)
                if MODERN_JUMP_WITH_OFFSET:
                    X = self.X
                else:
                    X = 0
                address = self.NNN + self.registers[X].get()
                self.PC.set(address)
            case 0xC: # GENERATE RANDOM NUMBER and BITWISE AND with NN put result in VX
                result = random.randint(0, 255) & self.NN
                self.registers[self.X].set(result)
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
            case 0xE: # SKIP if key
                VX = self.registers[self.X].get()
                pressed = SCANCODES[VX] in keys_pressed
                match self.NN:
                    case 0x9E:  # is PRESSED
                        if pressed:
                            self.PC.increment(2)
                    case 0xA1: # is NOT PRESSED
                        if not pressed:
                            self.PC.increment(2)
            case 0xF:
                match self.NN:
                    case 0x07:  # GET time remaining in TIMER and put in VX
                        time_left = timer.get()
                        self.registers[self.X].set(time_left)
                    case 0x15: # SET TIMER to VX
                        VX = self.registers[X].get()
                        timer.set(VX)
                    case 0x18: # SET BUZZER to VX
                        VX = self.registers[X].get()
                        buzzer.set(VX)
                    case 0x1E: # ADD VX to I, SETTING VF if I OVERFLOWS above 0x1000
                        VI = self.I.get() 
                        VX = self.registers[self.X].get()
                        VI += VX
                        if VI > 0x1000:
                            self.registers[0xF].set(1)
                        else:
                            self.registers[0xF].set(0)
                        self.I.set(VI)
                    case 0x0A: # BREAK until KEY PRESSED
                        if len(keys_pressed) == 0:
                            self.PC.increment(-2)
                    case 0x29: # SET I to ADRESS of FONT_CHARACTER in VX
                        VX = self.registers[self.X].get()
                        character = VX & 0b00001111
                        character_adress = 0x50 + character
                        self.I.set(character_adress)


memory = Memory(4096)
stack = Stack()

PC = ProgramCounter()
I = Registry(16)

registers = [Registry(8) for i in range(16)]

pygame.init()
pygame.mixer.init()
display = Display(64, 32, 10)

timer = Timer()
buzzer = Timer(True)

# LOAD FONT
with open('assets/fonts/font.txt', 'r', encoding='UTF-8') as font:
    content = font.read().replace('\n', ' ').strip()
    data = map(lambda t: int(t, 16), content.split(', '))
    for address, code in zip(range(int(0x50), int(0x9F)+1), data):
        memory.write(address, code)

# LOAD ROM
rom_location = 'assets/roms/3-corax+.ch8'
with open(rom_location, 'rb') as rom:
    rom_hex = rom.read().hex()
for i in range(0, len(rom_hex), 2):
    A = rom_hex[i]
    B = rom_hex[i+1]
    memory.write(0x200+i//2, int(f'0x{A}{B}', 16))

cpu = CPU(memory=memory, PC=PC, I=I, registers=registers, display=display, stack=stack, timer=timer, buzzer=buzzer)

SCANCODES = (0x02, 0x03, 0x04, 0x05, # 1, 2, 3, 4
             0x10, 0x11, 0x12, 0x13, # Q, W, E, R
             0x1E, 0x1F, 0x20, 0x21, # A, S, D, F
             0x2C, 0x2D, 0x2E, 0x2F  # Z, X, C, V
             )
keys_pressed = set()

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            keys_pressed.add(event.scancode)
        elif event.type == pygame.KEYUP:
            if event.scancode in keys_pressed:
                keys_pressed.remove(event.scancode)
            
    cpu.fetch()
    cpu.decode()
    
    timer.update()
    buzzer.update()
        
    clock.tick(700)
    display.blit()
