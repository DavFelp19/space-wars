import pygame, sys
from jugador import Jugador
import obstaculo
from enemigo import Alien, Extra
from laser import Laser
from random import choice, randint
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Juego:
    def __init__(self):
        # Configuración del jugador
        sprite_jugador = Jugador((ancho_pantalla / 2, alto_pantalla), ancho_pantalla, 5)
        self.jugador = pygame.sprite.GroupSingle(sprite_jugador)

        # Configuración de la salud y puntuación
        self.vidas = 3
        self.superficie_vida = pygame.image.load(os.path.join(BASE_DIR, 'graficos', 'jugador.png')).convert_alpha()
        self.pos_x_inicio_vida = ancho_pantalla - (self.superficie_vida.get_size()[0] * 2 + 20)
        self.puntuacion = 0
        self.fuente = pygame.font.Font(os.path.join(BASE_DIR, 'fuente', 'Pixeled.ttf'), 20)

        # Configuración de obstáculos
        self.forma = obstaculo.forma
        self.tamano_bloque = 6
        self.bloques = pygame.sprite.Group()
        self.cantidad_obstaculos = 4
        self.posiciones_x_obstaculo = [num * (ancho_pantalla / self.cantidad_obstaculos) for num in range(self.cantidad_obstaculos)]
        self.crear_multiples_obstaculos(*self.posiciones_x_obstaculo, x_inicio=ancho_pantalla / 15, y_inicio=480)

        # Configuración de aliens
        self.aliens = pygame.sprite.Group()
        self.configurar_aliens(filas=6, columnas=8)
        self.direccion_alien = 1
        self.lasers_alien = pygame.sprite.Group()

        # Configuración de extra
        self.extra = pygame.sprite.GroupSingle()
        self.tiempo_aparicion_extra = randint(40, 80)

        # Audio
        musica = pygame.mixer.Sound(os.path.join(BASE_DIR, 'sonidos', 'musica.wav'))
        musica.set_volume(0.2)
        musica.play(loops=-1)
        self.sonido_laser = pygame.mixer.Sound(os.path.join(BASE_DIR, 'sonidos', 'laser.wav'))
        self.sonido_laser.set_volume(0.5)
        self.sonido_explosion = pygame.mixer.Sound(os.path.join(BASE_DIR, 'sonidos', 'explosion.wav'))
        self.sonido_explosion.set_volume(0.3)

    def crear_obstaculo(self, x_inicio, y_inicio, desplazamiento_x):
        for indice_fila, fila in enumerate(self.forma):
            for indice_col, col in enumerate(fila):
                if col == 'x':
                    x = x_inicio + indice_col * self.tamano_bloque + desplazamiento_x
                    y = y_inicio + indice_fila * self.tamano_bloque
                    bloque = obstaculo.Bloque(self.tamano_bloque, (241, 79, 80), x, y)
                    self.bloques.add(bloque)

    def crear_multiples_obstaculos(self, *desplazamiento, x_inicio, y_inicio):
        for desplazamiento_x in desplazamiento:
            self.crear_obstaculo(x_inicio, y_inicio, desplazamiento_x)

    def configurar_aliens(self, filas, columnas, distancia_x=60, distancia_y=48, desplazamiento_x=70, desplazamiento_y=100):
        for indice_fila, fila in enumerate(range(filas)):
            for indice_col, col in enumerate(range(columnas)):
                x = indice_col * distancia_x + desplazamiento_x
                y = indice_fila * distancia_y + desplazamiento_y

                if indice_fila == 0:
                    sprite_alien = Alien('amarillo', x, y)
                elif 1 <= indice_fila <= 2:
                    sprite_alien = Alien('verde', x, y)
                else:
                    sprite_alien = Alien('rojo', x, y)
                self.aliens.add(sprite_alien)

    def verificar_posicion_alien(self):
        todos_aliens = self.aliens.sprites()
        for alien in todos_aliens:
            if alien.rect.right >= ancho_pantalla:
                self.direccion_alien = -1
                self.mover_aliens_abajo(2)
            elif alien.rect.left <= 0:
                self.direccion_alien = 1
                self.mover_aliens_abajo(2)

    def mover_aliens_abajo(self, distancia):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distancia

    def disparo_alien(self):
        if self.aliens.sprites():
            alien_aleatorio = choice(self.aliens.sprites())
            sprite_laser = Laser(alien_aleatorio.rect.center, 6, alto_pantalla)
            self.lasers_alien.add(sprite_laser)
            self.sonido_laser.play()

    def temporizador_alien_extra(self):
        self.tiempo_aparicion_extra -= 1
        if self.tiempo_aparicion_extra <= 0:
            self.extra.add(Extra(choice(['derecha', 'izquierda']), ancho_pantalla))
            self.tiempo_aparicion_extra = randint(400, 800)

    def verificar_colisiones(self):
        # colisiones de láser del jugador
        if self.jugador.sprite.lasers:
            for laser in self.jugador.lasers:
                # colisión con obstáculos
                if pygame.sprite.spritecollide(laser, self.obstaculos, True):
                    laser.kill()

                # colisión con aliens
                aliens_golpeados = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_golpeados:
                    for alien in aliens_golpeados:
                        self.puntuacion += alien.valor
                    laser.kill()
                    self.sonido_explosion.play()

                # colisión con extra
                if pygame.sprite.spritecollide(laser, self.extra, True):
                    self.puntuacion += 500
                    laser.kill()

        # colisiones de láser alien
        if self.lasers_alien:
            for laser in self.lasers_alien:
                # colisión con obstáculos
                if pygame.sprite.spritecollide(laser, self.obstaculos, True):
                    laser.kill()

                # colisión con jugador
                if pygame.sprite.spritecollide(laser, self.jugador, False):
                    laser.kill()
                    self.vidas -= 1
                    if self.vidas <= 0:
                        pygame.quit()
                        sys.exit()

        # colisiones de aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.obstaculos, True)

                if pygame.sprite.spritecollide(alien, self.jugador, False):
                    pygame.quit()
                    sys.exit()

    def mostrar_vidas(self):
        for vida in range(self.vidas - 1):
            x = self.pos_x_inicio_vida + (vida * (self.superficie_vida.get_size()[0] + 10))
            pantalla.blit(self.superficie_vida, (x, 8))

    def mostrar_puntuacion(self):
        superficie_puntuacion = self.fuente.render(f'puntuación: {self.puntuacion}', False, 'white')
        rect_puntuacion = superficie_puntuacion.get_rect(topleft=(10, -10))
        pantalla.blit(superficie_puntuacion, rect_puntuacion)

    def mensaje_victoria(self):
        if not self.aliens.sprites():
            superficie_victoria = self.fuente.render('Has ganado', False, 'white')
            rect_victoria = superficie_victoria.get_rect(center=(ancho_pantalla / 2, alto_pantalla / 2))
            pantalla.blit(superficie_victoria, rect_victoria)

    def ejecutar(self):
        self.jugador.update()
        self.lasers_alien.update()
        self.extra.update()

        self.aliens.update(self.direccion_alien)
        self.verificar_posicion_alien()
        self.temporizador_alien_extra()
        self.verificar_colisiones()

        self.jugador.sprite.lasers.draw(pantalla)
        self.jugador.draw(pantalla)
        self.bloques.draw(pantalla)
        self.aliens.draw(pantalla)
        self.lasers_alien.draw(pantalla)
        self.extra.draw(pantalla)
        self.mostrar_vidas()
        self.mostrar_puntuacion()
        self.mensaje_victoria()


if __name__ == '__main__':
    pygame.init()
    ancho_pantalla = 600
    alto_pantalla = 600
    pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
    reloj = pygame.time.Clock()
    juego = Juego()

    LASER_ALIEN = pygame.USEREVENT + 1
    pygame.time.set_timer(LASER_ALIEN, 800)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == LASER_ALIEN:
                juego.disparo_alien()

        pantalla.fill((30, 30, 30))
        juego.ejecutar()

        pygame.display.flip()
        reloj.tick(60)

