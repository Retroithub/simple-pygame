# this is simple pygame this is made by me and i am not a part of making pygame and this is a module

import pygame

class MainLoader:
    # you need this to load the game and create a window
    def __init__(self, screen_width=640, screen_height=480, name="Simple Pygame", fullscreen=False, resizable=False):
        pygame.init()
        if fullscreen:
            self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
        elif resizable:
            self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        else:
            self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(name)
        self.running = True
        self.mouse_clicked = None 

    def poll_events(self):
        self.mouse_clicked = None  
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_clicked = event.button

    def get_mouse_pos(self):
        return pygame.mouse.get_pos()

    def is_mouse_pressed(self, button=0):
        return pygame.mouse.get_pressed()[button]

    def was_mouse_clicked(self, button=0):
        return self.mouse_clicked == button + 1

    def fps(self, fps=60):
        self.clock.tick(fps)

    def screencolor(self, color=(0, 0, 0)):
        self.screen.fill(color)

    def update(self):
        pygame.display.flip()

    def is_key_pressed(self, key):
        keys = pygame.key.get_pressed()
        return keys[key]

    def quit(self):
        pygame.quit()

class PhysicsObject:
    # physics on pygame :O
    def __init__(self, x, y, width, height, gravity=0.5, friction=0.85):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx = 0
        self.vy = 0
        self.gravity = gravity
        self.friction = friction
        self.on_ground = False
        self.image = None

    def load_image(self, path):
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def draw(self, screen, color=(255, 255, 255), camera=None):
        if camera:
            draw_x, draw_y = camera.apply(self)
        else:
            draw_x, draw_y = self.x, self.y

        if self.image is not None:
            screen.blit(self.image, (draw_x, draw_y))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(draw_x, draw_y, self.width, self.height))

    def update(self):
        self.vy += self.gravity
        self.vx *= self.friction

        
        if abs(self.vx) < 0.01:
            self.vx = 0
        if abs(self.vy) < 0.01:
            self.vy = 0

        self.x += self.vx
        self.y += self.vy

    def jump(self, force=10):
        if self.on_ground:
            self.vy = -force  
            self.on_ground = False

    def resolve_floor(self, floor_y):
        if self.y + self.height >= floor_y:
            self.y = floor_y - self.height  
            self.vy = 0                     
            self.on_ground = True
        else:
            self.on_ground = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with(self, other):
        return self.get_rect().colliderect(other.get_rect())
    
    def resolve_walls(self, screen_width, screen_height):
        if self.x <= 0:
            self.x = 0
            self.vx = 0

        if self.x + self.width >= screen_width:
            self.x = screen_width - self.width
            self.vx = 0

        if self.y <= 0:
            self.y = 0
            self.vy = 0

    def resolve_collision(self, other):
        if not self.collides_with(other):
            return

        overlap = self.get_rect().clip(other.get_rect())

        if overlap.width < overlap.height:
            if self.x < other.x:
                self.x -= overlap.width
            else:
                self.x += overlap.width
            self.vx = 0
        else:
            if self.y < other.y:
                self.y -= overlap.height
                self.on_ground = True
            else:
                self.y += overlap.height
            self.vy = 0

class StaticObject:
    # object you code youself since im lazy jk but it's in the name
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = None 

    def load_image(self, path):
            self.image = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, color=(100, 100, 100), camera=None):
        if camera:
            draw_x, draw_y = camera.apply(self)
        else:
            draw_x, draw_y = self.x, self.y

        if self.image is not None:
            screen.blit(self.image, (draw_x, draw_y))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(draw_x, draw_y, self.width, self.height))


class Spritesheet:
    # no doc
    def __init__(self, path):
        self.sheet = pygame.image.load(path).convert_alpha()

    def get_frame(self, x, y, width, height):
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(self.sheet, (0, 0), (x, y, width, height))
        return frame

    def get_row(self, y, frame_width, frame_height, count):
        frames = []
        for i in range(count):
            frame = self.get_frame(i * frame_width, y, frame_width, frame_height)
            frames.append(frame)
        return frames
    
class Animation:
    # no doc
    def __init__(self, frames, speed=0.1):
        self.frames = frames
        self.speed = speed    
        self.current = 0        

    def update(self):
        self.current += self.speed
        if self.current >= len(self.frames):
            self.current = 0    
    def get_frame(self):
        return self.frames[int(self.current)]
    
class Camera:
    # simple camera :)
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.screen_width = screen_width
        self.screen_height = screen_height

    def follow(self, target, smoothing=0.1, deadzone=5):
        target_x = target.x - self.screen_width // 2
        target_y = target.y - self.screen_height // 2

        if abs(target_x - self.x) > deadzone:
            self.x += (target_x - self.x) * smoothing
        if abs(target_y - self.y) > deadzone:
            self.y += (target_y - self.y) * smoothing

        self.x = round(self.x)
        self.y = round(self.y)

    def apply(self, obj):
        return (round(obj.x - self.x), round(obj.y - self.y))

    def apply_rect(self, obj):
        return pygame.Rect(obj.x - self.x, obj.y - self.y, obj.width, obj.height)
    
class Keys:
    A = pygame.K_a
    B = pygame.K_b
    C = pygame.K_c
    D = pygame.K_d
    E = pygame.K_e
    F = pygame.K_f
    G = pygame.K_g
    H = pygame.K_h
    I = pygame.K_i
    J = pygame.K_j
    K = pygame.K_k
    L = pygame.K_l
    M = pygame.K_m
    N = pygame.K_n
    O = pygame.K_o
    P = pygame.K_p
    Q = pygame.K_q
    R = pygame.K_r
    S = pygame.K_s
    T = pygame.K_t
    U = pygame.K_u
    V = pygame.K_v
    W = pygame.K_w
    X = pygame.K_x
    Y = pygame.K_y
    Z = pygame.K_z
 
    N0 = pygame.K_0
    N1 = pygame.K_1
    N2 = pygame.K_2
    N3 = pygame.K_3
    N4 = pygame.K_4
    N5 = pygame.K_5
    N6 = pygame.K_6
    N7 = pygame.K_7
    N8 = pygame.K_8
    N9 = pygame.K_9
    
    NUMPAD_0 = pygame.K_KP0
    NUMPAD_1 = pygame.K_KP1
    NUMPAD_2 = pygame.K_KP2
    NUMPAD_3 = pygame.K_KP3
    NUMPAD_4 = pygame.K_KP4
    NUMPAD_5 = pygame.K_KP5
    NUMPAD_6 = pygame.K_KP6
    NUMPAD_7 = pygame.K_KP7
    NUMPAD_8 = pygame.K_KP8
    NUMPAD_9 = pygame.K_KP9
    NUMPAD_PLUS = pygame.K_KP_PLUS
    NUMPAD_MINUS = pygame.K_KP_MINUS
    NUMPAD_MULTIPLY = pygame.K_KP_MULTIPLY
    NUMPAD_DIVIDE = pygame.K_KP_DIVIDE
    NUMPAD_ENTER = pygame.K_KP_ENTER
    NUMPAD_PERIOD = pygame.K_KP_PERIOD
 
    LEFT = pygame.K_LEFT
    RIGHT = pygame.K_RIGHT
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN
 
    F1 = pygame.K_F1
    F2 = pygame.K_F2
    F3 = pygame.K_F3
    F4 = pygame.K_F4
    F5 = pygame.K_F5
    F6 = pygame.K_F6
    F7 = pygame.K_F7
    F8 = pygame.K_F8
    F9 = pygame.K_F9
    F10 = pygame.K_F10
    F11 = pygame.K_F11
    F12 = pygame.K_F12
 
    LEFT_SHIFT = pygame.K_LSHIFT
    RIGHT_SHIFT = pygame.K_RSHIFT
    LEFT_CTRL = pygame.K_LCTRL
    RIGHT_CTRL = pygame.K_RCTRL
    LEFT_ALT = pygame.K_LALT
    RIGHT_ALT = pygame.K_RALT
 
    SPACE = pygame.K_SPACE
    ENTER = pygame.K_RETURN
    ESCAPE = pygame.K_ESCAPE
    BACKSPACE = pygame.K_BACKSPACE
    TAB = pygame.K_TAB
    CAPS_LOCK = pygame.K_CAPSLOCK
    DELETE = pygame.K_DELETE
    INSERT = pygame.K_INSERT
    HOME = pygame.K_HOME
    END = pygame.K_END
    PAGE_UP = pygame.K_PAGEUP
    PAGE_DOWN = pygame.K_PAGEDOWN
    PRINT_SCREEN = pygame.K_PRINT
    SCROLL_LOCK = pygame.K_SCROLLOCK
    PAUSE = pygame.K_PAUSE
 
    MINUS = pygame.K_MINUS
    EQUALS = pygame.K_EQUALS
    LEFT_BRACKET = pygame.K_LEFTBRACKET
    RIGHT_BRACKET = pygame.K_RIGHTBRACKET
    BACKSLASH = pygame.K_BACKSLASH
    SEMICOLON = pygame.K_SEMICOLON
    QUOTE = pygame.K_QUOTE
    COMMA = pygame.K_COMMA
    PERIOD = pygame.K_PERIOD
    SLASH = pygame.K_SLASH
    BACKQUOTE = pygame.K_BACKQUOTE

class Mouse:
    # no doc
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2

class Sound:
    # .mp3 .wav and .ogg support
    def __init__(self):
        pygame.mixer.init()
        self.music_volume = 1.0
        self.sfx_volume = 1.0
        self.sounds = {} 

    def load_music(self, path):
        pygame.mixer.music.load(path)

    def play_music(self, loop=True):
        pygame.mixer.music.play(-1 if loop else 0)

    def stop_music(self):
        pygame.mixer.music.stop()

    def pause_music(self):
        pygame.mixer.music.pause()

    def resume_music(self):
        pygame.mixer.music.unpause()

    def set_music_volume(self, volume):
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume)

    def load_sound(self, name, path):
        self.sounds[name] = pygame.mixer.Sound(path)

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].set_volume(self.sfx_volume)
            self.sounds[name].play()

    def set_sfx_volume(self, volume):
        self.sfx_volume = volume