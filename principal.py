import pygame
import sys
import os
from random import choice, randint

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
ancho_pantalla = 800
alto_pantalla = 600
pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Space Invaders')

# Directorio base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Clase Jugador
class Jugador(pygame.sprite.Sprite):
    def __init__(self, pos, limite, velocidad):
        super().__init__()
        self.image = pygame.image.load(os.path.join(BASE_DIR, 'graficos', 'jugador.png')).convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)
        self.velocidad = velocidad
        self.limite_x_max = limite
        self.listo = True
        self.tiempo_laser = 0
        self.enfriamiento_laser = 600
        self.lasers = pygame.sprite.Group()
        self.sonido_laser = pygame.mixer.Sound(os.path.join(BASE_DIR, 'sonidos', 'laser.wav'))
        self.sonido_laser.set_volume(0.5)

    def obtener_entrada(self, teclas):
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

    def update(self, teclas):
        self.obtener_entrada(teclas)
        self.limitar()
        self.recargar()
        self.lasers.update()


# Clase Laser
class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, velocidad, altura_pantalla):
        super().__init__()
        self.image = pygame.Surface((4, 20))
        self.image.fill('white')
        self.rect = self.image.get_rect(center=pos)
        self.velocidad = velocidad
        self.limite_altura_y = altura_pantalla

    def destruir(self):
        if self.rect.y <= -50 or self.rect.y >= self.limite_altura_y + 50:
            self.kill()

    def update(self):
        self.rect.y += self.velocidad
        self.destruir()


# Clase Alien
class Alien(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        ruta_archivo = os.path.join(BASE_DIR, 'graficos', f'{color}.png')
        self.image = pygame.image.load(ruta_archivo).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))

        if color == 'rojo':
            self.valor = 100
        elif color == 'verde':
            self.valor = 200
        else:
            self.valor = 300

    def update(self, direccion):
        self.rect.x += direccion


# Clase Extra
class Extra(pygame.sprite.Sprite):
    def __init__(self, lado, ancho_pantalla):
        super().__init__()
        self.image = pygame.image.load(os.path.join(BASE_DIR, 'graficos', 'extra.png')).convert_alpha()

        if lado == 'derecha':
            x = ancho_pantalla + 50
            self.velocidad = -3
        else:
            x = -50
            self.velocidad = 3

        self.rect = self.image.get_rect(topleft=(x, 80))

    def update(self):
        self.rect.x += self.velocidad


# Clase Bloque (para obstáculos)
class Bloque(pygame.sprite.Sprite):
    def __init__(self, tamano, color, x, y):
        super().__init__()
        self.image = pygame.Surface((tamano, tamano))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))


# Forma del obstáculo
forma_obstaculo = [
    '  xxxxxxx  ',
    ' xxxxxxxxx ',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxx     xxx',
    'xx       xx'
]


# Clase principal del juego
class Juego:
    def __init__(self):
        self.estado = "menu"
        self.modo = None
        self.fuente = pygame.font.Font(os.path.join(BASE_DIR, 'fuente', 'Pixeled.ttf'), 20)
        self.configurar_sonidos()
        self.reiniciar_juego()

    def configurar_sonidos(self):
        self.musica = pygame.mixer.Sound(os.path.join(BASE_DIR, 'sonidos', 'musica.wav'))
        self.musica.set_volume(0.2)
        self.sonido_laser = pygame.mixer.Sound(os.path.join(BASE_DIR, 'sonidos', 'laser.wav'))
        self.sonido_laser.set_volume(0.5)
        self.sonido_explosion = pygame.mixer.Sound(os.path.join(BASE_DIR, 'sonidos', 'explosion.wav'))
        self.sonido_explosion.set_volume(0.3)

    def reiniciar_juego(self):
        self.jugador1 = None
        self.jugador2 = None
        self.vidas1 = 3
        self.vidas2 = 3
        self.superficie_vida = pygame.image.load(os.path.join(BASE_DIR, 'graficos', 'jugador.png')).convert_alpha()
        self.pos_x_inicio_vida = ancho_pantalla - (self.superficie_vida.get_size()[0] * 2 + 20)
        self.puntuacion1 = 0
        self.puntuacion2 = 0
        self.bloques = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.lasers_alien = pygame.sprite.Group()
        self.extra = pygame.sprite.GroupSingle()
        self.tiempo_aparicion_extra = randint(40, 80)
        self.direccion_alien = 1
        self.crear_obstaculos()
        self.configurar_aliens()

    def crear_obstaculos(self):
        for indice_obstaculo in range(4):
            x_obstaculo = indice_obstaculo * (ancho_pantalla / 4) + 50
            self.crear_obstaculo(x_obstaculo, 480)

    def crear_obstaculo(self, x_inicio, y_inicio):
        for indice_fila, fila in enumerate(forma_obstaculo):
            for indice_columna, columna in enumerate(fila):
                if columna == 'x':
                    x = x_inicio + indice_columna * 40
                    y = y_inicio + indice_fila * 40
                    bloque = Bloque(40, 'blue', x, y)
                    self.bloques.add(bloque)

    def configurar_aliens(self):
        for fila in range(6):
            for columna in range(8):
                x = columna * 60 + 60
                y = fila * 40 + 100
                if fila == 0:
                    alien = Alien('rojo', x, y)
                elif fila == 1 or fila == 2:
                    alien = Alien('verde', x, y)
                else:
                    alien = Alien('azul', x, y)
                self.aliens.add(alien)

    def dibujar_menu(self):
        titulo = self.fuente.render('SPACE INVADERS', True, (255, 255, 255))
        instruccion = self.fuente.render('Presiona ESPACIO para comenzar', True, (255, 255, 255))

        pantalla.blit(titulo, (ancho_pantalla // 2 - titulo.get_width() // 2, alto_pantalla // 3))
        pantalla.blit(instruccion, (ancho_pantalla // 2 - instruccion.get_width() // 2, alto_pantalla // 2))

    def dibujar_seleccion_modo(self):
        titulo = self.fuente.render('SELECCIONA MODO', True, (255, 255, 255))
        opcion1 = self.fuente.render('1 - Un Jugador', True, (255, 255, 255))
        opcion2 = self.fuente.render('2 - Dos Jugadores', True, (255, 255, 255))

        pantalla.blit(titulo, (ancho_pantalla // 2 - titulo.get_width() // 2, alto_pantalla // 3))
        pantalla.blit(opcion1, (ancho_pantalla // 2 - opcion1.get_width() // 2, alto_pantalla // 2))
        pantalla.blit(opcion2, (ancho_pantalla // 2 - opcion2.get_width() // 2, alto_pantalla // 2 + 50))

    def configurar_jugadores(self):
        if self.modo == "individual":
            sprite_jugador = Jugador((ancho_pantalla / 2, alto_pantalla), ancho_pantalla, 5)
            self.jugador1 = pygame.sprite.GroupSingle(sprite_jugador)
            self.jugador2 = None
        elif self.modo == "multijugador":
            sprite_jugador1 = Jugador((ancho_pantalla / 3, alto_pantalla), ancho_pantalla, 5)
            sprite_jugador2 = Jugador((2 * ancho_pantalla / 3, alto_pantalla), ancho_pantalla, 5)
            self.jugador1 = pygame.sprite.GroupSingle(sprite_jugador1)
            self.jugador2 = pygame.sprite.GroupSingle(sprite_jugador2)

    def mostrar_puntuaciones(self):
        if self.modo == "individual":
            texto_puntuacion = self.fuente.render(f'Puntuación: {self.puntuacion1}', True, (255, 255, 255))
            pantalla.blit(texto_puntuacion, (10, 10))
        else:
            texto_p1 = self.fuente.render(f'P1: {self.puntuacion1}', True, (255, 255, 255))
            texto_p2 = self.fuente.render(f'P2: {self.puntuacion2}', True, (255, 255, 255))
            pantalla.blit(texto_p1, (10, 10))
            pantalla.blit(texto_p2, (ancho_pantalla - 150, 10))

    def mostrar_vidas(self):
        if self.modo == "individual":
            for i in range(self.vidas1):
                x = self.pos_x_inicio_vida + (i * 40)
                pantalla.blit(self.superficie_vida, (x, 10))
        else:
            for i in range(self.vidas1):
                x = 10 + (i * 40)
                pantalla.blit(self.superficie_vida, (x, 40))
            for i in range(self.vidas2):
                x = ancho_pantalla - 150 + (i * 40)
                pantalla.blit(self.superficie_vida, (x, 40))

    def run(self):
        clock = pygame.time.Clock()
        self.musica.play(loops=-1)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.estado == "menu" and event.key == pygame.K_SPACE:
                        self.estado = "seleccion_modo"
                    elif self.estado == "seleccion_modo" and event.key == pygame.K_1:
                        self.estado = "jugando"
                        self.modo = "individual"
                        self.configurar_jugadores()
                    elif self.estado == "seleccion_modo" and event.key == pygame.K_2:
                        self.estado = "jugando"
                        self.modo = "multijugador"
                        self.configurar_jugadores()
                    elif self.estado == "jugando" and event.key == pygame.K_p:
                        self.estado = "menu"
                        self.reiniciar_juego()

            pantalla.fill((30, 30, 30))

            if self.estado == "menu":
                self.dibujar_menu()
            elif self.estado == "seleccion_modo":
                self.dibujar_seleccion_modo()
            elif self.estado == "jugando":
                self.mostrar_puntuaciones()
                self.mostrar_vidas()
                self.jugador1.draw(pantalla)
                self.jugador2.draw(pantalla)
                self.bloques.draw(pantalla)
                self.aliens.draw(pantalla)
                self.lasers_alien.draw(pantalla)
                self.extra.draw(pantalla)

            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    juego = Juego()
    juego.run()