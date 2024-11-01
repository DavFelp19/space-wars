import pygame

class Bloque(pygame.sprite.Sprite):
    def __init__(self, tamano, color, x, y):
        super().__init__()
        self.image = pygame.Surface((tamano, tamano))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft = (x,y))

forma = [
    '  xxxxxxx  ',
    ' xxxxxxxxx ',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxx     xxx',
    'xx       xx'
]