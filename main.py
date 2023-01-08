import pygame
import random

# Initialising font
pygame.font.init()

# Initialize the pygame
pygame.init()

# Game Constants
WIDTH = 512
HEIGHT = 512
COLOR = (255, 255, 255)
SIZE = 64
MIN_GRASS_HEIGHT = 288
# PLAYER_VELOCITY = 4
# ENEMY_VELOCITY = 1

# Game Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Title and Icon
pygame.display.set_caption("Crop Wars")
icon = pygame.image.load('assets/imgs/icon.png')
pygame.display.set_icon(icon)

# Load Images
# PLAYER = pygame.transform.scale(pygame.image.load('assets/imgs/air_blower.png'), (64, 64))
PLAYER = pygame.transform.rotate(pygame.transform.scale(pygame.image.load('assets/imgs/robo.png'), (64, 64)), 0)
ENEMY_CLOUD_1 = pygame.transform.scale(pygame.image.load('assets/imgs/thunder.png'), (64, 64))
ACID_DROP = pygame.transform.scale(pygame.image.load('assets/imgs/acid_drop.png'), (24, 24))
LASER = pygame.transform.rotate(pygame.image.load('assets/imgs/laser_32.png'), -90)
GRASS_PATCH = pygame.transform.scale(pygame.image.load('assets/imgs/grass_patch.png'), (32, 32))
GRASS_1 = pygame.transform.scale(pygame.image.load('assets/imgs/grass_1.png'), (32, 32))
GAME_OVER = pygame.image.load('assets/imgs/game_over.png')
BACKGROUND = pygame.transform.scale(pygame.image.load(
    'assets/imgs/plains.png'), (WIDTH, HEIGHT))

GRASS_1_POSITIONS = [
    [40, 410],
    [120, 310],
    [140, 480],
    [150, 370],
    [250, 300],
    [325, 360],
    [395, 430],
    [400, 300],
    [350, 480]
]

GRASS_PATCH_POSITIONS = [
    [36, 290],
    [460, 380]
]

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Entity:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 5

    def get_width(self):
        return self.img.get_width()

    def get_height(self):
        return self.img.get_height()

# Class Player
class Player(Entity):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.img = PLAYER
        self.laser_img = LASER
        self.mask = pygame.mask.from_surface(self.img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.img.get_height() + 10, self.img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.img.get_height() + 10, self.img.get_width() * (self.health/self.max_health), 10))

class Clouds(Entity):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.img, self.laser_img = ENEMY_CLOUD_1, ACID_DROP
        self.mask = pygame.mask.from_surface(self.img)

    def move(self, vel):
        if self.y < 100:
            self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+12, self.y+12, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 3

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# Game Loop
def main():
    running = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 25)
    lost_font = pygame.font.SysFont("comicsans", 60)
    clouds = []
    wave_length = 5
    cloud_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(WIDTH//2-SIZE//2, HEIGHT-SIZE-30)
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def draw_grass():
        for i in GRASS_1_POSITIONS:
            screen.blit(GRASS_1, (i[0], i[1]))

    def draw_grass_patch():
        for i in GRASS_PATCH_POSITIONS:
            screen.blit(GRASS_PATCH, (i[0], i[1]))

    def draw_screen():
        screen.fill(COLOR)
        screen.blit(BACKGROUND, (0, 0))
        # screen.blit(GRASS_PATCH, (20, MIN_GRASS_HEIGHT))
        draw_grass()
        draw_grass_patch()
        # screen.blit(WEED, (180, MIN_GRASS_HEIGHT+140))
        # screen.blit(ENEMY_CLOUD_1, (100, 50))
        # screen.blit(PLAYER, (WIDTH//2-SIZE//2, HEIGHT-SIZE-50))

    # Function to redraw window
    def redraw_window():
        draw_screen()
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (0,0,0))
        level_label = main_font.render(f"Level: {level}", 1, (0,0,0))

        screen.blit(lives_label, (10, 10))
        screen.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for cloud in clouds:
            cloud.draw(screen)

        player.draw(screen)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            draw_screen()
            screen.blit(GAME_OVER, (WIDTH/2 - GAME_OVER.get_width()/2, 20))
            screen.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
            
        pygame.display.update()

    while running:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                running = False
            else:
                continue

        if len(clouds) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                cloud = Clouds(random.randrange(10, WIDTH-64), random.randrange(-1500, -100))
                clouds.append(cloud)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        
        for cloud in clouds[:]:
            cloud.move(cloud_vel)
            cloud.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                cloud.shoot()

            if collide(cloud, player):
                player.health -= 10
                clouds.remove(cloud)
            elif cloud.y + cloud.get_height() > HEIGHT:
                lives -= 1
                clouds.remove(cloud)

        player.move_lasers(-laser_vel, clouds)
    
def main_menu():
    title_font_1 = pygame.font.SysFont("comicsans", 20)
    title_font_2 = pygame.font.SysFont("comicsans", 30)
    running = True
    while running:
        screen.fill(COLOR)
        screen.blit(BACKGROUND, (0,0))
        # screen.blit(GAME_OVER, (0, 0))
        instr_label_1 = title_font_1.render("USE LEFT AND RIGHT KEYS TO MOVE", 1, (0,0,0))
        instr_label_2 = title_font_1.render("SPACEBAR FOR SHOOTING AWAY THE CLOUDS", 1, (0,0,0))
        title_label = title_font_2.render("Press the mouse to begin...", 1, (0,0,0))
        screen.blit(instr_label_1, (WIDTH/2 - instr_label_1.get_width()/2, 50)) 
        screen.blit(instr_label_2, (WIDTH/2 - instr_label_2.get_width()/2, 100))
        screen.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


if __name__ == "__main__":
    main_menu()
