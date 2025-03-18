import time
import math
import pygame

class Timer:
    def __init__(self, buzzer=False, beep_sound=None):
        self.time = 0
        self.last_set = 0
        self.buzzer = buzzer
        self.beep_sound = pygame.mixer.Sound("assets/audio/beep.wav") if beep_sound is None else beep_sound

    def set(self, amount):
        self.time = amount
        self.last_set = time.time()

    def update(self):
        if self.time != 0:
            current_time = time.time()
            diff = math.floor((current_time - self.last_set) / (1 / 60))
            self.time -= diff
            self.last_set = current_time if diff != 0 else self.last_set
            if self.buzzer and diff and self.time % 30 == 0:
                self.beep_sound.play()

    def get(self):
        return self.time
