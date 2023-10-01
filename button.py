import pygame

class Button:
    def __init(self, backSprite, iconSprite, rect : pygame.Rect):
        self.backSprite = backSprite
        self.iconSprite = iconSprite
        self.rect = rect