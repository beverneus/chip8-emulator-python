import pygame
import numpy as np

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
        pygame.display.set_caption("CHIP-8")

        self.canvas = pygame.Surface((self.width, self.height))
        self.canvas.fill(BLACK)

    def clear(self):
        self.state = np.zeros((self.width, self.height))
        self.canvas.fill(BLACK)

    def flip_pixel(self, x, y):
        color = BLACK if self.state[x, y] else WHITE
        self.canvas.set_at((x, y), color)
        self.state[x, y] = (self.state[x, y] + 1) % 2

    def blit(self):
        scaled_canvas = pygame.transform.scale(self.canvas, (self.dwidth, self.dheight))
        self.screen.blit(scaled_canvas, (0, 0))
