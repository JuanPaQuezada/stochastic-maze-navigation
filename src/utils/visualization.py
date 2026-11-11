import os
import sys
import pygame

from src.mazeMapping import Map as GeneradorMapa
from src.pathfinding_engine import a_star

# ==========================================
# 1. GESTOR DE RECURSOS (CON TILESETS ORDENADOS Y SPRITES)
# ==========================================

class GestorSprites:
    """
    Carga imágenes individuales para Frisk, Sans y recorta texturas 
    consistentes para muros y suelos desde la carpeta assets/Tilesets/.
    """
    def __init__(self, celda_px=48):
        self.celda_px = celda_px
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
        self.ruta_assets = os.path.join(base_dir, "assets")
   
        self.fondo_castillo = None
        self.texturas = {}
        self.anim_frisk = {}
        self.anim_sans = {}

        print(f"[INFO] Buscando assets en: {self.ruta_assets}")
        self.cargar_recursos()

    def _cargar_img(self, nombre_base, subcarpeta=""):
        carpetas = [self.ruta_assets]
        if subcarpeta:
            carpetas.append(os.path.join(self.ruta_assets, subcarpeta))

        for carpeta in carpetas:
            for ext in [".png", ".jpg", ".jpeg", ".PNG", ".JPG"]:
                path = os.path.join(carpeta, nombre_base + ext)
                if os.path.exists(path):
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        print(f"  [ÉXITO] Cargado: {path}")
                        return img
                    except Exception as e:
                        print(f"  [ERROR] Al leer {path}: {e}")
        print(f"  [AVISO] No se encontró la imagen: {nombre_base}")
        return None

    def _crear_color(self, color):
        s = pygame.Surface((self.celda_px, self.celda_px))
        s.fill(color)
        return s

    def cargar_recursos(self):
        print("\n--- INICIANDO CARGA DE RECURSOS ---")
        
        # 1. Fondo
        path_fondo = os.path.join(self.ruta_assets, "fondo_castillo.png")
        if os.path.exists(path_fondo):
            self.fondo_castillo = pygame.transform.scale(pygame.image.load(path_fondo).convert(), (800, 500))

        # 2. Carga del Tileset desde la carpeta assets/Tilesets/
        print("\n[Cargando Tileset]")
        tileset_img = (
            self._cargar_img("bg_ruinseasynam1", subcarpeta="Tilesets") or 
            self._cargar_img("tileset", subcarpeta="Tilesets")
        )

        if tileset_img:
            try:
                # Coordenadas exactas para mantener un orden lógico y limpio
                rect_muro = pygame.Rect(40, 0, 20, 20)  # Textura de ladrillos de pared
                rect_piso = pygame.Rect(0, 40, 20, 20)  # Textura de suelo liso

                muro_sub = tileset_img.subsurface(rect_muro)
                piso_sub = tileset_img.subsurface(rect_piso)

                self.texturas["muro"] = pygame.transform.scale(muro_sub, (self.celda_px, self.celda_px))
                self.texturas["piso"] = pygame.transform.scale(piso_sub, (self.celda_px, self.celda_px))
                print("  [ÉXITO] Tileset recortado con orden lógico (muros y pisos).")
            except Exception as e:
                print(f"  [ERROR] Al recortar el tileset: {e}. Usando colores de respaldo.")
                self.texturas["muro"] = self._crear_color((55, 40, 75))
                self.texturas["piso"] = self._crear_color((20, 15, 30))
        else:
            self.texturas["muro"] = self._crear_color((55, 40, 75))
            self.texturas["piso"] = self._crear_color((20, 15, 30))

        self.texturas["meta"] = self._crear_color((255, 215, 0))

        # 3. Frisk (Carpeta assets/Frisk/)
        print("\n[Cargando sprites de Frisk]")
        self.anim_frisk["DOWN"] = [self._escala(self._cargar_img(f"spr_f_maincharad_{i}", "Frisk")) for i in range(4)]
        self.anim_frisk["UP"] = [self._escala(self._cargar_img(f"spr_maincharau_{i}", "Frisk")) for i in range(4)]
        self.anim_frisk["LEFT"] = [self._escala(self._cargar_img(f"spr_f_maincharal_{i}", "Frisk")) for i in range(2)]
        self.anim_frisk["RIGHT"] = [self._escala(self._cargar_img(f"spr_f_maincharar_{i}", "Frisk")) for i in range(2)]

        for d in ["DOWN", "UP", "LEFT", "RIGHT"]:
            self.anim_frisk[d] = [img for img in self.anim_frisk[d] if img is not None]
            if not self.anim_frisk[d]:
                self.anim_frisk[d] = [self._crear_color((255, 0, 0))]

        # 4. Sans (Carpeta assets/Sans/)
        print("\n[Cargando sprites de Sans]")
        self.anim_sans["DOWN"] = [self._escala(self._cargar_img(f"spr_sans_d_{i}", "Sans")) for i in range(4)]
        self.anim_sans["UP"] = [self._escala(self._cargar_img(f"spr_sans_stool_buttscratch_{i}", "Sans")) for i in range(4)]
        self.anim_sans["LEFT"] = [self._escala(self._cargar_img(f"spr_sans_l_{i}", "Sans")) for i in range(4)]
        self.anim_sans["RIGHT"] = [self._escala(self._cargar_img(f"spr_sans_r_{i}", "Sans")) for i in range(4)]

        for d in ["DOWN", "UP", "LEFT", "RIGHT"]:
            self.anim_sans[d] = [img for img in self.anim_sans[d] if img is not None]
            if not self.anim_sans[d]:
                self.anim_sans[d] = [self._crear_color((235, 60, 150))]

        print("-----------------------------------\n")

    def _escala(self, img):
        if img:
            return pygame.transform.scale(img, (self.celda_px, self.celda_px))
        return None


# ==========================================
# 2. PUNTO DE INTEGRACIÓN DE LA IMPLEMENTACIÓN DEL EQUIPO
# ==========================================

class Map:
    """Contenedor de datos del mapa."""

    def __init__(self, width=35, height=35):
        self.width = width
        self.height = height
        self.start = (1, 1)
        self.goal = (width - 2, height - 2)
        self.ocupancy_grid = None


class Implementation:

    def generar_laberinto(self, ancho, alto, inicio, meta):
        mapa_backend = GeneradorMapa(
            width=ancho, height=alto, density_rate=0.3, hardness_rate=0.5, start=inicio, goal=meta
        )
        return mapa_backend.generate_map()

    def encontrar_ruta(self, mapa, inicio, meta):
        ruta = a_star(cost_map=mapa, start=inicio, goal=meta)
        return ruta if ruta else []


# ==========================================
# 3. CÁMARA Y JUEGO PRINCIPAL
# ==========================================

class Camera:
    def __init__(self, viewport_width, viewport_height, cell_size):
        self.viewport_w = viewport_width
        self.viewport_h = viewport_height
        self.cell_size = cell_size
        self.offset_x = 0
        self.offset_y = 0

    def update(self, target_pos, map_width, map_height):
        target_pixel_x = target_pos[0] * self.cell_size
        target_pixel_y = target_pos[1] * self.cell_size

        self.offset_x = target_pixel_x - (self.viewport_w // 2)
        self.offset_y = target_pixel_y - (self.viewport_h // 2)

        max_offset_x = (map_width * self.cell_size) - self.viewport_w
        max_offset_y = (map_height * self.cell_size) - self.viewport_h

        self.offset_x = max(0, min(self.offset_x, max_offset_x))
        self.offset_y = max(0, min(self.offset_y, max_offset_y))


class undertaleGUI:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() #Motor de audio
        
        self.ANCHO_PANTALLA = 800
        self.ALTO_PANTALLA = 500
        self.CELL_SIZE = 48
        
        self.screen = pygame.display.set_mode((self.ANCHO_PANTALLA, self.ALTO_PANTALLA))
        pygame.display.set_caption("Laberinto - Undertale Edition")
        self.clock = pygame.time.Clock()

        self.sprites = GestorSprites(celda_px=self.CELL_SIZE)

        self.sfx_ganar = pygame.mixer.Sound(os.path.join(self.sprites.ruta_assets, "victory.wav"))
        self.sfx_perder = pygame.mixer.Sound(os.path.join(self.sprites.ruta_assets, "gameover.wav"))
        pygame.mixer.music.load(os.path.join(self.sprites.ruta_assets, "menu.mp3"))
        pygame.mixer.music.play(-1)
        
        self.C_NEGRO = (0, 0, 0)
        self.C_BLANCO = (255, 255, 255)
        self.C_ROJO = (255, 0, 0)
        self.C_AMARILLO = (255, 215, 0)

        self.estado = "MENU_PRINCIPAL"
        self.modo_previo = "JUEGO_VS"

        self.opcion_menu = 0
        self.opciones_menu = ["CPU VS CPU", "CONTRA CPU", "1V1", "OPCIONES", "SALIR"]

        self.opcion_config = 0
        self.vel_bot_idx = 1
        self.vel_bot_lista = [171, 200, 110]
        self.vel_bot_etiquetas = ["LENTO", "NORMAL", "RÁPIDO"]

        self.opcion_game_over = 0
        self.opciones_game_over = ["REINICIAR", "MENU PRINCIPAL"]
        self.mensaje_game_over = "PERDISTE"

        self.mapa = Map(width=35, height=35)
        self.implementacion = Implementation()

        self.pos_jugador = list(self.mapa.start)
        self.pos_bot = list(self.mapa.start)
        self.dir_jugador = "DOWN"
        self.dir_bot = "DOWN"
        self.frame_jugador = 0
        self.frame_bot = 0

        self.ruta_bot = []
        self.ruta_jugador = []
        self.paso_jugador_idx = 0
        self.paso_bot_idx = 0
        
        self.timer_bot = 0
        self.timer_jugador = 0
        self.speed_jugador_ms = 130
        
        self.esperando_inicio = False
        self.tiempo_inicio_cuenta = 0

        self.camera = Camera(self.ANCHO_PANTALLA, self.ALTO_PANTALLA, self.CELL_SIZE)
        self.minimap_size = 100
        self.minimap_surface = pygame.Surface((self.minimap_size, self.minimap_size))

    def reiniciar_procesos_completos(self):
        grid = self.implementacion.generar_laberinto(
            self.mapa.width,
            self.mapa.height,
            self.mapa.start,
            self.mapa.goal
        )

        # Mientras no se agregue la implementación, no se inicia la partida.
        if grid is None:
            self.mapa.ocupancy_grid = None
            self.ruta_bot = []
            return False

        self.mapa.ocupancy_grid = grid
        self.ruta_bot = self.implementacion.encontrar_ruta(
            self.mapa.ocupancy_grid,
            self.mapa.start,
            self.mapa.goal
        ) or []
        self.ruta_jugador = list(self.ruta_bot)
        self.paso_jugador_idx = 0

        self.pos_jugador = list(self.mapa.start)
        self.pos_bot = list(self.mapa.start)
        self.dir_jugador = "DOWN"
        self.dir_bot = "DOWN"
        self.frame_jugador = 0
        self.frame_bot = 0

        self.paso_bot_idx = 0
        self.timer_bot = 0
        self.timer_jugador = 0
        return True

    def procesar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if self.estado == "MENU_PRINCIPAL":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.opcion_menu = (self.opcion_menu - 1) % len(self.opciones_menu)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.opcion_menu = (self.opcion_menu + 1) % len(self.opciones_menu)
                    elif event.key in (pygame.K_z, pygame.K_RETURN):
                        if self.opcion_menu == 0:
                            if self.reiniciar_procesos_completos():
                                self.modo_previo = "JUEGO_CPU"
                                self.estado = "JUEGO_CPU"
                                pygame.mixer.music.load(os.path.join(self.sprites.ruta_assets, "Juego2.mp3"))
                                pygame.mixer.music.play(-1)
                        elif self.opcion_menu == 1:
                            if self.reiniciar_procesos_completos():
                                self.modo_previo = "JUEGO_VS"
                                self.estado = "JUEGO_VS"
                                # --- INICIAR CUENTA REGRESIVA ---
                                self.esperando_inicio = True
                                self.tiempo_inicio_cuenta = pygame.time.get_ticks()
                                pygame.mixer.music.load(os.path.join(self.sprites.ruta_assets, "Juego1.mp3"))
                                pygame.mixer.music.play(-1)
                        elif self.opcion_menu == 2:
                            if self.reiniciar_procesos_completos():
                                self.modo_previo = "JUEGO_1V1"
                                self.estado = "JUEGO_1V1"
                                self.esperando_inicio = True
                                self.tiempo_inicio_cuenta = pygame.time.get_ticks()
                                pygame.mixer.music.load(os.path.join(self.sprites.ruta_assets, "Juego1.mp3"))
                                pygame.mixer.music.play(-1)
                        elif self.opcion_menu == 3:
                            self.estado = "OPCIONES"
                        elif self.opcion_menu == 4:
                            pygame.quit(); sys.exit()

            elif self.estado == "OPCIONES":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                        self.opcion_config = (self.opcion_config + 1) % 2
                    elif event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                        if self.opcion_config == 0:
                            self.vel_bot_idx = (self.vel_bot_idx + 1) % len(self.vel_bot_lista)
                    elif event.key in (pygame.K_x, pygame.K_ESCAPE, pygame.K_z, pygame.K_RETURN):
                        self.estado = "MENU_PRINCIPAL"

            elif "JUEGO" in self.estado:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_x, pygame.K_ESCAPE):
                        self.reiniciar_procesos_completos()
                        self.estado = "MENU_PRINCIPAL"
                        pygame.mixer.music.load(os.path.join(self.sprites.ruta_assets, "Menu.mp3"))
                        pygame.mixer.music.play(-1)

            elif self.estado == "GAME_OVER":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.opcion_game_over = (self.opcion_game_over - 1) % len(self.opciones_game_over)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.opcion_game_over = (self.opcion_game_over + 1) % len(self.opciones_game_over)
                    elif event.key in (pygame.K_z, pygame.K_RETURN):
                        if self.opcion_game_over == 0:
                            if self.reiniciar_procesos_completos():
                                # --- INICIAR CUENTA REGRESIVA ---
                                self.esperando_inicio = True
                                self.tiempo_inicio_cuenta = pygame.time.get_ticks()
                                self.estado = self.modo_previo
                                self.sfx_ganar.stop()
                                self.sfx_perder.stop()
                                pygame.mixer.music.load(os.path.join(self.sprites.ruta_assets, "Juego2.mp3"))
                                pygame.mixer.music.play(-1)
                        elif self.opcion_game_over == 1:
                            self.reiniciar_procesos_completos()
                            self.estado = "MENU_PRINCIPAL"
                            self.sfx_ganar.stop()
                            self.sfx_perder.stop()
                            pygame.mixer.music.load(os.path.join(self.sprites.ruta_assets, "Menu.mp3"))
                            pygame.mixer.music.play(-1)

    def actualizar_jugador(self):
        # Permitir movimiento en ambos modos multijugador
        if self.estado not in ["JUEGO_VS", "JUEGO_1V1"] or self.mapa.ocupancy_grid is None: return
        if getattr(self, 'esperando_inicio', False): return 

        now = pygame.time.get_ticks()
        if now - self.timer_jugador >= self.speed_jugador_ms:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0

            # Controles exclusivos de J1 (Flechas)
            if keys[pygame.K_UP]: dy = -1; self.dir_jugador = "UP"
            elif keys[pygame.K_DOWN]: dy = 1; self.dir_jugador = "DOWN"
            elif keys[pygame.K_LEFT]: dx = -1; self.dir_jugador = "LEFT"
            elif keys[pygame.K_RIGHT]: dx = 1; self.dir_jugador = "RIGHT"

            if dx != 0 or dy != 0:
                px = self.pos_jugador[0] + dx
                py = self.pos_jugador[1] + dy

                if 0 <= px < self.mapa.width and 0 <= py < self.mapa.height:
                    if self.mapa.ocupancy_grid[py][px] < float('inf'):
                        self.pos_jugador = [px, py]
                        frames_disp = len(self.sprites.anim_frisk.get(self.dir_jugador, [1]))
                        self.frame_jugador = (self.frame_jugador + 1) % max(1, frames_disp)
                        self.timer_jugador = now

                        if tuple(self.pos_jugador) == self.mapa.goal:
                            if self.estado == "JUEGO_1V1":
                                self.mensaje_game_over = "¡FRISK (J1) GANA!"
                            else:
                                self.mensaje_game_over = "¡HAS GANADO!"
                            self.opcion_game_over = 0
                            self.estado = "GAME_OVER"
                            pygame.mixer.music.stop()
                            self.sfx_ganar.play()

    def actualizar_bot(self):
        # El bot únicamente recorre la ruta que ya ha calculado el algoritmo A* importado
        if "JUEGO" not in self.estado: return
        if getattr(self, 'esperando_inicio', False): return
        now = pygame.time.get_ticks()
        intervalo_bot = self.vel_bot_lista[self.vel_bot_idx]
        
        if self.ruta_bot and self.paso_bot_idx < len(self.ruta_bot):
            if now - self.timer_bot >= intervalo_bot:
                siguiente = self.ruta_bot[self.paso_bot_idx]
                
                if siguiente[0] > self.pos_bot[0]: self.dir_bot = "RIGHT"
                elif siguiente[0] < self.pos_bot[0]: self.dir_bot = "LEFT"
                elif siguiente[1] > self.pos_bot[1]: self.dir_bot = "DOWN"
                elif siguiente[1] < self.pos_bot[1]: self.dir_bot = "UP"

                self.pos_bot = list(siguiente)
                frames_disp = len(self.sprites.anim_sans.get(self.dir_bot, [1]))
                self.frame_bot = (self.frame_bot + 1) % max(1, frames_disp)
                self.paso_bot_idx += 1
                self.timer_bot = now

                if tuple(self.pos_bot) == self.mapa.goal:
                    # Mensaje dinámico según el modo
                    if self.estado == "JUEGO_VS":
                        self.mensaje_game_over = "¡PERDISTE!"
                    elif self.estado == "JUEGO_CPU":
                        self.mensaje_game_over = "¡SANS CPU 2 GANA!"
                    else:
                        self.mensaje_game_over = "¡BOT HA LLEGADO!"
                        
                    self.opcion_game_over = 0
                    self.estado = "GAME_OVER"
                    
                    # Detener música de fondo
                    pygame.mixer.music.stop()
                    
                    # En modo espectador (CPU vs CPU) reproducir victoria, si juegas contra él reproducir derrota
                    if self.estado == "JUEGO_CPU":
                        if hasattr(self, 'sfx_ganar'): self.sfx_ganar.play()
                    else:
                        if hasattr(self, 'sfx_perder'): self.sfx_perder.play()
    
    def actualizar_bot_frisk(self):
        if self.estado != "JUEGO_CPU": return
        if getattr(self, 'esperando_inicio', False): return
        now = pygame.time.get_ticks()
        
        # Velocidad fija de Frisk bot para que no se superponga con Sans
        intervalo_frisk = 150 
        
        if self.ruta_jugador and self.paso_jugador_idx < len(self.ruta_jugador):
            if now - self.timer_jugador >= intervalo_frisk:
                siguiente = self.ruta_jugador[self.paso_jugador_idx]
                
                if siguiente[0] > self.pos_jugador[0]: self.dir_jugador = "RIGHT"
                elif siguiente[0] < self.pos_jugador[0]: self.dir_jugador = "LEFT"
                elif siguiente[1] > self.pos_jugador[1]: self.dir_jugador = "DOWN"
                elif siguiente[1] < self.pos_jugador[1]: self.dir_jugador = "UP"

                self.pos_jugador = list(siguiente)
                frames_disp = len(self.sprites.anim_frisk.get(self.dir_jugador, [1]))
                self.frame_jugador = (self.frame_jugador + 1) % max(1, frames_disp)
                self.paso_jugador_idx += 1
                self.timer_jugador = now

                if tuple(self.pos_jugador) == self.mapa.goal:
                    self.mensaje_game_over = "¡FRISK CPU 1 GANA!"
                    self.opcion_game_over = 0
                    self.estado = "GAME_OVER"
                    pygame.mixer.music.stop()
                    if hasattr(self, 'sfx_ganar'): self.sfx_ganar.play()
                                    
    def actualizar_jugador2(self):
        if self.estado != "JUEGO_1V1" or self.mapa.ocupancy_grid is None: return
        if getattr(self, 'esperando_inicio', False): return

        now = pygame.time.get_ticks()
        # Usamos la misma velocidad que el jugador 1 para que sea justo
        if now - self.timer_bot >= self.speed_jugador_ms: 
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0

            # Controles exclusivos de J2 (WASD)
            if keys[pygame.K_w]: dy = -1; self.dir_bot = "UP"
            elif keys[pygame.K_s]: dy = 1; self.dir_bot = "DOWN"
            elif keys[pygame.K_a]: dx = -1; self.dir_bot = "LEFT"
            elif keys[pygame.K_d]: dx = 1; self.dir_bot = "RIGHT"

            if dx != 0 or dy != 0:
                px = self.pos_bot[0] + dx
                py = self.pos_bot[1] + dy

                if 0 <= px < self.mapa.width and 0 <= py < self.mapa.height:
                    if self.mapa.ocupancy_grid[py][px] < float('inf'):
                        self.pos_bot = [px, py]
                        frames_disp = len(self.sprites.anim_sans.get(self.dir_bot, [1]))
                        self.frame_bot = (self.frame_bot + 1) % max(1, frames_disp)
                        self.timer_bot = now

                        if tuple(self.pos_bot) == self.mapa.goal:
                            self.mensaje_game_over = "¡SANS (J2) GANA!"
                            self.opcion_game_over = 0
                            self.estado = "GAME_OVER"
                            pygame.mixer.music.stop()
                            self.sfx_ganar.play()

    def _dibujar_corazon_cursor(self, x, y):
        pygame.draw.polygon(self.screen, self.C_ROJO, [
            (x, y + 6), (x + 6, y), (x + 12, y + 6), (x + 6, y + 16)
        ])

    def renderizar_menu_principal(self):
        self.screen.fill(self.C_NEGRO)
        if self.sprites.fondo_castillo:
            self.screen.blit(self.sprites.fondo_castillo, (0, 0))

        font_titulo = pygame.font.SysFont("impact", 40)
        texto = "LABERINTO INTELIGENTE \n  (UNDERTALE EDITION)"
        x_tit = self.ANCHO_PANTALLA // 2
        y_tit = 70

        for dx, dy in [(-3,0),(3,0),(0,-3),(0,3),(-3,-3),(3,3),(-3,3),(3,-3)]:
            surf_b = font_titulo.render(texto, True, self.C_ROJO)
            self.screen.blit(surf_b, (x_tit - surf_b.get_width() // 2 + dx, y_tit + dy))
        
        surf_f = font_titulo.render(texto, True, self.C_NEGRO)
        self.screen.blit(surf_f, (x_tit - surf_f.get_width() // 2, y_tit))

        font_opc = pygame.font.SysFont("monospace", 22, bold=True)
        y_inicio = 240

        for i, opc_text in enumerate(self.opciones_menu):
            y_pos = y_inicio + i * 40
            surf_t = font_opc.render(opc_text, True, self.C_BLANCO)
            x_pos = self.ANCHO_PANTALLA // 2 - surf_t.get_width() // 2

            if i == self.opcion_menu:
                self._dibujar_corazon_cursor(x_pos - 30, y_pos + 2)
            self.screen.blit(surf_t, (x_pos, y_pos))

    def renderizar_opciones(self):
        self.screen.fill(self.C_NEGRO)
        if self.sprites.fondo_castillo:
            self.screen.blit(self.sprites.fondo_castillo, (0, 0))

        font_t = pygame.font.SysFont("monospace", 36, bold=True)
        font_o = pygame.font.SysFont("monospace", 20, bold=True)

        surf_t = font_t.render("CONFIGURACIÓN", True, self.C_BLANCO)
        self.screen.blit(surf_t, (self.ANCHO_PANTALLA // 2 - surf_t.get_width() // 2, 60))

        txt_vel = f"VELOCIDAD BOT: < {self.vel_bot_etiquetas[self.vel_bot_idx]} >"
        surf_1 = font_o.render(txt_vel, True, self.C_BLANCO if self.opcion_config == 0 else (120, 120, 120))
        self.screen.blit(surf_1, (self.ANCHO_PANTALLA // 2 - surf_1.get_width() // 2, 200))

        surf_2 = font_o.render("VOLVER AL MENÚ", True, self.C_BLANCO if self.opcion_config == 1 else (120, 120, 120))
        self.screen.blit(surf_2, (self.ANCHO_PANTALLA // 2 - surf_2.get_width() // 2, 260))

        y_sel = 200 if self.opcion_config == 0 else 260
        self._dibujar_corazon_cursor(self.ANCHO_PANTALLA // 2 - 180, y_sel + 2)

    def renderizar_minimapa(self):
        self.minimap_surface.fill((0, 0, 0))
        if self.mapa.ocupancy_grid is None:
            return

        cell_w = self.minimap_size / self.mapa.width
        cell_h = self.minimap_size / self.mapa.height

        for y in range(self.mapa.height):
            for x in range(self.mapa.width):
                if self.mapa.ocupancy_grid[y][x] == float('inf'):
                    pygame.draw.rect(self.minimap_surface, (80, 80, 80), (x * cell_w, y * cell_h, cell_w + 1, cell_h + 1))

        gx, gy = self.mapa.goal
        pygame.draw.rect(self.minimap_surface, self.C_AMARILLO, (gx * cell_w, gy * cell_h, cell_w * 2, cell_h * 2))

        bx, by = self.pos_bot
        pygame.draw.rect(self.minimap_surface, (235, 60, 150), (bx * cell_w, by * cell_h, cell_w * 2, cell_h * 2))

        if self.estado in ["JUEGO_VS", "JUEGO_1V1", "JUEGO_CPU"]:
            jx, jy = self.pos_jugador
            pygame.draw.rect(self.minimap_surface, self.C_ROJO, (jx * cell_w, jy * cell_h, cell_w * 2, cell_h * 2))

    def renderizar_juego(self):
        self.screen.fill(self.C_NEGRO)

        if self.mapa.ocupancy_grid is None:
            font = pygame.font.SysFont("monospace", 20, bold=True)
            mensaje = font.render("IMPLEMENTACIÓN DEL LABERINTO PENDIENTE", True, self.C_BLANCO)
            self.screen.blit(
                mensaje,
                (self.ANCHO_PANTALLA // 2 - mensaje.get_width() // 2, self.ALTO_PANTALLA // 2)
            )
            return

        if self.estado == "JUEGO_VS":
            target_focus = self.pos_jugador
        elif self.estado in ["JUEGO_1V1", "JUEGO_CPU"]:
            # Promedia la posición para mantener a ambos a la vista
            target_focus = ((self.pos_jugador[0] + self.pos_bot[0]) // 2, (self.pos_jugador[1] + self.pos_bot[1]) // 2)
        else:
            target_focus = self.pos_bot
        self.camera.update(target_focus, self.mapa.width, self.mapa.height)

        for y in range(self.mapa.height):
            for x in range(self.mapa.width):
                draw_x = x * self.CELL_SIZE - self.camera.offset_x
                draw_y = y * self.CELL_SIZE - self.camera.offset_y

                if -self.CELL_SIZE <= draw_x <= self.ANCHO_PANTALLA and -self.CELL_SIZE <= draw_y <= self.ALTO_PANTALLA:
                    if self.mapa.ocupancy_grid[y][x] == float('inf'):
                        self.screen.blit(self.sprites.texturas["muro"], (draw_x, draw_y))
                    else:
                        self.screen.blit(self.sprites.texturas["piso"], (draw_x, draw_y))

        gx, gy = self.mapa.goal
        self.screen.blit(self.sprites.texturas["meta"], (gx * self.CELL_SIZE - self.camera.offset_x, gy * self.CELL_SIZE - self.camera.offset_y))

        # Bot (Sans)
        bx, by = self.pos_bot
        anim_sans = self.sprites.anim_sans.get(self.dir_bot, [])
        if anim_sans:
            img_sans = anim_sans[self.frame_bot % len(anim_sans)]
            self.screen.blit(img_sans, (bx * self.CELL_SIZE - self.camera.offset_x, by * self.CELL_SIZE - self.camera.offset_y))

        # Jugador (Frisk)
        if self.estado in ["JUEGO_VS", "JUEGO_1V1", "JUEGO_CPU"]:
            jx, jy = self.pos_jugador
            anim_frisk = self.sprites.anim_frisk.get(self.dir_jugador, [])
            if anim_frisk:
                img_frisk = anim_frisk[self.frame_jugador % len(anim_frisk)]
                self.screen.blit(img_frisk, (jx * self.CELL_SIZE - self.camera.offset_x, jy * self.CELL_SIZE - self.camera.offset_y))
        
        self.renderizar_minimapa()
        # Calcular posición en la esquina superior derecha
        padding = 8
        panel_size = self.minimap_size + (padding * 2)
        panel_x = self.ANCHO_PANTALLA - panel_size - 15  # 15 píxeles de separación del borde derecho
        panel_y = 15  # 15 píxeles de separación del techo
        
        # Dibujar el marco negro con borde blanco
        panel_rect = pygame.Rect(panel_x, panel_y, panel_size, panel_size)
        pygame.draw.rect(self.screen, (0, 0, 0), panel_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, 3)

        # Dibujar directamente el minimapa dentro del panel
        self.screen.blit(self.minimap_surface, (panel_x + padding, panel_y + padding))
        
        # --- DIBUJAR CUENTA REGRESIVA EN EL CENTRO DE LA PANTALLA ---
        if getattr(self, 'esperando_inicio', False):
            tiempo_actual = pygame.time.get_ticks()
            segundos_transcurridos = (tiempo_actual - self.tiempo_inicio_cuenta) // 1000
            
            if segundos_transcurridos < 3:
                numero = str(3 - segundos_transcurridos) # Mostrará 3, 2, 1
            elif segundos_transcurridos == 3:
                numero = "¡YA!"
            else:
                self.esperando_inicio = False # Apagar bloqueo y permitir movimiento
                numero = None
                
            if numero:
                # Oscurecer ligeramente el fondo para resaltar los números
                overlay = pygame.Surface((self.ANCHO_PANTALLA, self.ALTO_PANTALLA))
                overlay.set_alpha(100)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))
                
                # Fuente gigante estilo Undertale
                font_cuenta = pygame.font.SysFont("impact", 120)
                surf_num = font_cuenta.render(numero, True, self.C_BLANCO)
                surf_borde = font_cuenta.render(numero, True, self.C_NEGRO)
                
                cx = self.ANCHO_PANTALLA // 2
                cy = self.ALTO_PANTALLA // 2
                
                # Renderizar sombra gruesa y texto
                for dx, dy in [(-4,0),(4,0),(0,-4),(0,4),(-4,-4),(4,4),(-4,4),(4,-4)]:
                    self.screen.blit(surf_borde, (cx - surf_borde.get_width() // 2 + dx, cy - surf_borde.get_height() // 2 + dy))
                
                self.screen.blit(surf_num, (cx - surf_num.get_width() // 2, cy - surf_num.get_height() // 2))

    def renderizar_game_over(self):
        self.renderizar_juego()

        overlay = pygame.Surface((self.ANCHO_PANTALLA, self.ALTO_PANTALLA))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        box_w, box_h = 360, 220
        box_x = (self.ANCHO_PANTALLA - box_w) // 2
        box_y = (self.ALTO_PANTALLA - box_h) // 2

        pygame.draw.rect(self.screen, (0, 0, 0), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, self.C_BLANCO, (box_x, box_y, box_w, box_h), 4)

        font_titulo = pygame.font.SysFont("monospace", 32, bold=True)
        surf_titulo = font_titulo.render(self.mensaje_game_over, True, self.C_ROJO)
        self.screen.blit(surf_titulo, (box_x + (box_w - surf_titulo.get_width()) // 2, box_y + 30))

        font_opciones = pygame.font.SysFont("monospace", 20, bold=True)
        for i, opc in enumerate(self.opciones_game_over):
            color = self.C_BLANCO if i == self.opcion_game_over else (120, 120, 120)
            surf_opc = font_opciones.render(opc, True, color)
            x_pos = box_x + (box_w - surf_opc.get_width()) // 2
            y_pos = box_y + 110 + i * 40

            if i == self.opcion_game_over:
                self._dibujar_corazon_cursor(x_pos - 30, y_pos + 2)
            self.screen.blit(surf_opc, (x_pos, y_pos))

    def ejecutar(self):
        while True:
            self.procesar_eventos()
            self.actualizar_jugador()
            if self.estado == "JUEGO_1V1":
                self.actualizar_jugador2()
            elif self.estado == "JUEGO_CPU":
                self.actualizar_bot()
                self.actualizar_bot_frisk()
            else:
                self.actualizar_bot()

            if self.estado == "MENU_PRINCIPAL":
                self.renderizar_menu_principal()
            elif self.estado == "OPCIONES":
                self.renderizar_opciones()
            elif "JUEGO" in self.estado:
                self.renderizar_juego()
            elif self.estado == "GAME_OVER":
                self.renderizar_game_over()

            pygame.display.flip()
            self.clock.tick(60)
