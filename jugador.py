import pygame
import os

DIR_BASE = os.path.dirname(os.path.abspath(__file__))

class Jugador(pygame.sprite.Sprite):
    def __init__(self, pos, limite, velocidad):
        super().__init__()
        self.image = pygame.image.load(os.path.join(DIR_BASE, 'graficos', 'jugador.png')).convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)
        self.velocidad = velocidad
        self.limite_x_max = limite
        self.listo = True
        self.tiempo_laser = 0
        self.enfriamiento_laser = 600

        self.lasers = pygame.sprite.Group()

        self.sonido_laser = pygame.mixer.Sound(os.path.join(DIR_BASE, 'sonidos', 'laser.wav'))
        self.sonido_laser.set_volume(0.5)

    def obtener_entrada(self):
        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidad
        elif teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidad

        if teclas[pygame.K_SPACE] and self.listo:
            self.disparar_laser()
            self.listo = False
            self.tiempo_laser = pygame.time.get_ticks()

    def recargar(self):
        if not self.listo:
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - self.tiempo_laser >= self.enfriamiento_laser:
                self.listo = True

    def limitar(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= self.limite_x_max:
            self.rect.right = self.limite_x_max

    def disparar_laser(self):
        self.lasers.add(Laser(self.rect.center, -8, self.rect.bottom))
        self.sonido_laser.play()

    def update(self):
        self.obtener_entrada()
        self.limitar()
        self.recargar()
        self.lasers.update()

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, velocidad, altura_pantalla):
        super().__init__()
        self.image = pygame.Surface((4,20))
        self.image.fill('white')
        self.rect = self.image.get_rect(center = pos)
        self.velocidad = velocidad
        self.limite_altura_y = altura_pantalla

    def destruir(self):
        if self.rect.y <= -50 or self.rect.y >= self.limite_altura_y + 50:
            self.kill()

    def update(self):
        self.rect.y += self.velocidad
        self.destruir()