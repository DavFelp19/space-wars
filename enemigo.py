import pygame
import os

class Alien(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        ruta_archivo = os.path.join(BASE_DIR, 'graficos', f'{color}.png')
        self.image = pygame.image.load(ruta_archivo).convert_alpha()
        self.rect = self.image.get_rect(topleft = (x, y))

        if color == 'rojo': self.valor = 100
        elif color == 'verde': self.valor = 200
        else: self.valor = 300

    def update(self, direccion):
        self.rect.x += direccion


class Extra(pygame.sprite.Sprite):
    def __init__(self, lado, ancho_pantalla):
        super().__init__()
        self.image = pygame.image.load('./graphics/extra.png').convert_alpha()

        if lado == 'derecha':
            x = ancho_pantalla + 50
            self.velocidad = -3
        else:
            x = -50
            self.velocidad = 3

        self.rect = self.image.get_rect(topleft=(x, 80))

    def update(self):
        self.rect.x += self.velocidad