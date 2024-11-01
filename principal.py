import pygame
import sys
import os
import random
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
    def __init__(self, pos, limite, velocidad, controles):
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
        self.controles = controles

    def obtener_entrada(self):
        teclas = pygame.key.get_pressed()
        if teclas[self.controles['derecha']]:
            self.rect.x += self.velocidad
        elif teclas[self.controles['izquierda']]:
            self.rect.x -= self.velocidad
        if teclas[self.controles['disparo']] and self.listo:
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

    def configurar_jugadores(self):
        if self.modo == "individual":
            controles_jugador1 = {
                'izquierda': pygame.K_a,
                'derecha': pygame.K_d,
                'disparo': pygame.K_w
            }
            sprite_jugador = Jugador((ancho_pantalla / 2, alto_pantalla - 100), ancho_pantalla, 5, controles_jugador1)
            self.jugador1 = pygame.sprite.GroupSingle(sprite_jugador)
            self.jugador2 = None
        elif self.modo == "multijugador":
            controles_jugador1 = {
                'izquierda': pygame.K_a,
                'derecha': pygame.K_d,
                'disparo': pygame.K_w
            }
            controles_jugador2 = {
                'izquierda': pygame.K_LEFT,
                'derecha': pygame.K_RIGHT,
                'disparo': pygame.K_SPACE
            }
            sprite_jugador1 = Jugador((ancho_pantalla / 3, alto_pantalla - 100), ancho_pantalla, 5, controles_jugador1)
            sprite_jugador2 = Jugador((2 * ancho_pantalla / 3, alto_pantalla - 100), ancho_pantalla, 5,
                                      controles_jugador2)
            self.jugador1 = pygame.sprite.GroupSingle(sprite_jugador1)
            self.jugador2 = pygame.sprite.GroupSingle(sprite_jugador2)
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
            self.crear_obstaculo(x_obstaculo)

            def crear_obstaculo(self, x_obstaculo):
                for indice_fila, fila in enumerate(forma_obstaculo):
                    for indice_columna, columna in enumerate(fila):
                        if columna == 'x':
                            x = x_obstaculo + (indice_columna * 30)
                            y = alto_pantalla - (indice_fila * 30 + 50)
                            self.bloques.add(Bloque(30, 'grey', x, y))

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

            def dibujar_vidas(self):
                vida_imagen = pygame.image.load(os.path.join(BASE_DIR, 'graficos', 'vida.png')).convert_alpha()
                vida_rect = vida_imagen.get_rect()

                # Vidas del jugador 1 (arriba a la derecha)
                for i in range(self.vidas1):
                    pantalla.blit(vida_imagen, (ancho_pantalla - 100 + i * 30, 10))

                if self.modo == "multijugador":
                    # Vidas del jugador 2 (debajo de las vidas del jugador 1)
                    for i in range(self.vidas2):
                        pantalla.blit(vida_imagen, (ancho_pantalla - 100 + i * 30, 50))

            def dibujar_puntuaciones(self):
                puntuacion1_texto = self.fuente.render(f'Puntuación 1: {self.puntuacion1}', True, 'white')
                pantalla.blit(puntuacion1_texto, (10, 10))

                if self.modo == "multijugador":
                    puntuacion2_texto = self.fuente.render(f'Puntuación 2: {self.puntuacion2}', True, 'white')
                    pantalla.blit(puntuacion2_texto, (10, 30))

            def dibujar_elementos(self):
                self.bloques.draw(pantalla)
                self.aliens.draw(pantalla)
                self.lasers_alien.draw(pantalla)
                self.extra.draw(pantalla)
                self.jugador1.lasers.draw(pantalla)
                if self.modo == "multijugador":
                    self.jugador2.lasers.draw(pantalla)

            def revisar_colisiones(self):
                # Colisiones de láser jugador con aliens
                for jugador in [self.jugador1, self.jugador2]:
                    if jugador:
                        for laser in jugador.lasers:
                            aliens_golpeados = pygame.sprite.spritecollide(laser, self.aliens, True)
                            if aliens_golpeados:
                                laser.kill()
                                if jugador == self.jugador1:
                                    self.puntuacion1 += 100 * len(aliens_golpeados)
                                else:
                                    self.puntuacion2 += 100 * len(aliens_golpeados)
                                self.sonido_explosion.play()

                # Colisiones de láser alien con jugadores
                for laser in self.lasers_alien:
                    if self.jugador1 and pygame.sprite.spritecollide(self.jugador1.sprite, [laser], True):
                        self.vidas1 -= 1
                        self.sonido_explosion.play()
                    if self.jugador2 and pygame.sprite.spritecollide(self.jugador2.sprite, [laser], True):
                        self.vidas2 -= 1
                        self.sonido_explosion.play()

            def revisar_bordes_aliens(self):
                for alien in self.aliens:
                    if alien.rect.right >= ancho_pantalla or alien.rect.left <= 0:
                        self.direccion_alien *= -1
                        self.aliens.update(self.direccion_alien)

            def disparar_laser_alien(self):
                if self.aliens:
                    alien = choice(list(self.aliens))
                    self.lasers_alien.add(Laser(alien.rect.center, 4, alto_pantalla))

            def jugar(self):
                self.jugador1.update()
                if self.modo == "multijugador":
                    self.jugador2.update()

                self.aliens.update(self.direccion_alien)
                self.lasers_alien.update()
                self.extra.update()
                self.bloques.update()

                self.dibujar_elementos()
                self.revisar_colisiones()
                self.revisar_bordes_aliens()
                self.disparar_laser_alien()

            def mostrar_pantalla_victoria(self):
                victoria_texto = self.fuente.render('¡Victoria!', True, 'white')
                pantalla.blit(victoria_texto, (ancho_pantalla / 2 - 50, alto_pantalla / 2 - 20))

            def mostrar_pantalla_derrota(self):
                derrota_texto = self.fuente.render('¡Derrota!', True, 'white')
                pantalla.blit(derrota_texto, (ancho_pantalla / 2 - 50, alto_pantalla / 2 - 20))

            def run(self):
                if self.estado == "menu":
                    self.menu()
                elif self.estado == "juego":
                    self.jugar()
                elif self.estado == "victoria":
                    self.mostrar_pantalla_victoria()
                elif self.estado == "derrota":
                    self.mostrar_pantalla_derrota()

                pygame.display.update()
                pygame.time.Clock().tick(60)

            def menu(self):
                self.musica.play(-1)
                self.estado = "menu"
                self.modo = None
                self.jugador1 = None
                self.jugador2 = None
                self.vidas1 = 3
                self.vidas2 = 3
                self.puntuacion1 = 0
                self.puntuacion2 = 0

                while self.estado == "menu":
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_1:
                                self.estado = "juego"
                                self.modo = "individual"
                                self.jugador1 = Jugador((ancho_pantalla / 2, alto_pantalla - 100), ancho_pantalla, 5,
                                                        {'derecha': pygame.K_d, 'izquierda': pygame.K_a,
                                                         'disparo': pygame.K_w})
                            elif event.key == pygame.K_2:
                                self.estado = "juego"
                                self.modo = "multijugador"
                                self.jugador1 = Jugador((ancho_pantalla / 2 - 100, alto_pantalla - 100), ancho_pantalla,
                                                        5, {'derecha': pygame.K_d, 'izquierda': pygame.K_a,
                                                            'disparo': pygame.K_w})
                                self.jugador2 = Jugador((ancho_pantalla / 2 + 100, alto_pantalla - 100), ancho_pantalla,
                                                        5, {'derecha': pygame.K_RIGHT, 'izquierda': pygame.K_LEFT,
                                                            'disparo': pygame.K_SPACE})

                    pantalla.fill('black')
                    menu_texto = self.fuente.render(
                        'Presiona 1 para jugar en modo individual o 2 para jugar en modo multijugador', True, 'white')
                    pantalla.blit(menu_texto, (ancho_pantalla / 2 - 200, alto_pantalla / 2 - 20))
                    pygame.display.update()
                    pygame.time.Clock().tick(60)

                self.musica.stop()

        if __name__ == "__main__":
            juego = Juego()
            while True:
                juego.run()