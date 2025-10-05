import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dungeon Runner")
clock = pygame.time.Clock()

jump_sound = pygame.mixer.Sound("game/jump.mp3")
collect_sound = pygame.mixer.Sound("game/collect.mp3")
death_sound = pygame.mixer.Sound("game/death.mp3")
web_sound = False
dash_sound = False

player_image = None
enemy_image = None
collectible_image = None
platform_image = None

try:
    player_image = pygame.image.load('game/player.png')
except:
    pass

try:
    enemy_image = pygame.image.load('game/enemy.png')
except:
    pass

try:
    collectible_image = pygame.image.load('game/collectible.png')
except:
    pass

try:
    platform_image = pygame.image.load('platform.png')
except:
    pass

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 220, 0)
PINK = (255, 105, 180)
GRAY = (80, 80, 80)
DARK_GRAY = (50, 50, 50)
RED = (255, 50, 50)
BG_COLOR = (20, 20, 40)

class Player:
    def __init__(self):
        self.x = 200
        self.y = 400
        self.w = 30
        self.h = 30
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.direction = 1
        self.web_attached = False
        self.web_x = 0
        self.web_y = 0
        self.health = 3
        self.invincible = 0
        
    def jump(self):
        if self.on_ground and not self.web_attached:
            self.vy = -16
            self.on_ground = False
            if jump_sound:
                jump_sound.play()
    
    def attach_web(self, mouse_x, mouse_y, camera_x, roof_segments):
        if not self.web_attached:
            world_mouse_x = mouse_x + camera_x
            world_mouse_y = mouse_y
            
            for segment in roof_segments:
                if segment['x1'] <= world_mouse_x <= segment['x2']:
                    self.web_attached = True
                    self.web_x = world_mouse_x
                    self.web_y = segment['y']
                    if web_sound:
                        web_sound.play()
                    break
    
    def detach_web(self):
        if self.web_attached:
            self.web_attached = False
            self.vy = -12
    
    def update(self, platforms, roof_segments):
        self.invincible = max(0, self.invincible - 1)
        
        if self.web_attached:
            dx = self.web_x - (self.x + self.w // 2)
            dy = self.web_y - (self.y + self.h // 2)
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist > 5:
                pull_strength = 0.015
                self.vx += dx * pull_strength
                self.vy += dy * pull_strength
            
            self.vy += 0.4
            
            self.vx *= 0.985
            self.vy *= 0.985
        else:
            move_speed = 5 * self.direction
            self.vx = move_speed
            
            self.vy += 0.7
            if self.vy > 18:
                self.vy = 18
        
        self.x += self.vx
        self.y += self.vy
        
        self.on_ground = False
        
        for plat in platforms:
            if (self.x + self.w > plat.x and self.x < plat.x + plat.w and
                self.y + self.h >= plat.y and self.y + self.h <= plat.y + plat.h + 20 and self.vy >= 0):
                self.y = plat.y - self.h
                self.vy = 0
                self.on_ground = True
                break
        
        for segment in roof_segments:
            if (self.x + self.w > segment['x1'] and self.x < segment['x2'] and
                self.y <= segment['y'] + 10):
                self.y = segment['y'] + 10
                if self.vy < 0:
                    self.vy = 0
                break
    
    def take_damage(self):
        if self.invincible == 0:
            self.health -= 1
            self.invincible = 90
            return True
        return False
    
    def draw(self, camera_x):
        screen_x = int(self.x - camera_x)
        
        if self.invincible > 0 and (self.invincible // 5) % 2 == 0:
            color = (200, 200, 200)
        else:
            color = WHITE
        
        if player_image:
            img = player_image.convert_alpha()
            img = pygame.transform.scale(img, (self.w, self.h))
            if self.invincible > 0 and (self.invincible // 5) % 2 == 0:
                img.set_alpha(128)
            screen.blit(img, (screen_x, int(self.y)))
        else:
            pygame.draw.rect(screen, color, (screen_x, int(self.y), self.w, self.h))
            pygame.draw.rect(screen, BLACK, (screen_x, int(self.y), self.w, self.h), 2)
        
        if self.web_attached:
            web_screen_x = int(self.web_x - camera_x)
            pygame.draw.line(screen, (180, 180, 180), 
                           (screen_x + self.w // 2, int(self.y + self.h // 2)),
                           (web_screen_x, int(self.web_y)), 2)
            pygame.draw.circle(screen, WHITE, (web_screen_x, int(self.web_y)), 4)

class Platform:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def draw(self, camera_x):
        screen_x = int(self.x - camera_x)
        if -200 < screen_x < WIDTH + 200:
            if platform_image:
                img = platform_image.convert_alpha()
                img = pygame.transform.scale(img, (self.w, self.h))
                screen.blit(img, (screen_x, int(self.y)))
            else:
                pygame.draw.rect(screen, GRAY, (screen_x, int(self.y), self.w, self.h))
                pygame.draw.rect(screen, DARK_GRAY, (screen_x, int(self.y), self.w, self.h), 2)

class Particle:
    def __init__(self, x, y, color, vx=None, vy=None):
        self.x = x
        self.y = y
        self.vx = vx if vx else random.uniform(-6, 6)
        self.vy = vy if vy else random.uniform(-8, -2)
        self.life = 45
        self.color = color
        self.size = random.randint(6, 12)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.life -= 1
    
    def draw(self, camera_x):
        if self.life > 0:
            screen_x = int(self.x - camera_x)
            alpha = int(255 * (self.life / 45))
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
            screen.blit(s, (screen_x - self.size, int(self.y) - self.size))

class Collectible:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 14
        self.collected = False
        self.pulse = 0
    
    def update(self):
        self.pulse += 0.15
    
    def check_collect(self, player, particles):
        if not self.collected:
            if (abs(player.x + player.w // 2 - self.x - self.size // 2) < (player.w + self.size) // 2 and
                abs(player.y + player.h // 2 - self.y - self.size // 2) < (player.h + self.size) // 2):
                self.collected = True
                if collect_sound:
                    collect_sound.play()
                for _ in range(25):
                    particles.append(Particle(self.x + self.size // 2, self.y + self.size // 2, PINK))
                return True
        return False
    
    def draw(self, camera_x):
        if not self.collected:
            screen_x = int(self.x - camera_x)
            if -100 < screen_x < WIDTH + 100:
                size_mod = int(2 * math.sin(self.pulse))
                draw_size = self.size + size_mod
                
                if collectible_image:
                    img = collectible_image.convert_alpha()
                    img = pygame.transform.scale(img, (draw_size, draw_size))
                    screen.blit(img, (screen_x - size_mod // 2, int(self.y - size_mod // 2)))
                else:
                    pygame.draw.rect(screen, PINK, (screen_x - size_mod // 2, int(self.y - size_mod // 2), draw_size, draw_size))
                    pygame.draw.rect(screen, BLACK, (screen_x - size_mod // 2, int(self.y - size_mod // 2), draw_size, draw_size), 2)

class Enemy:
    def __init__(self, x, y, min_x, max_x):
        self.x = x
        self.y = y
        self.w = 28
        self.h = 28
        self.vx = 0
        self.min_x = min_x
        self.max_x = max_x
        self.dash_cooldown = 0
        self.patrol_dir = random.choice([-1, 1])
        self.patrol_speed = 2
    
    def update(self, player, particles):
        self.dash_cooldown = max(0, self.dash_cooldown - 1)
        
        dist = abs(player.x - self.x)
        
        if dist < 250 and abs(player.y - self.y) < 100 and self.dash_cooldown == 0:
            dash_dir = 1 if player.x > self.x else -1
            self.vx = dash_dir * 11
            self.dash_cooldown = 110
            if dash_sound:
                dash_sound.play()
        else:
            self.vx = self.patrol_dir * self.patrol_speed
        
        self.x += self.vx
        
        if self.x <= self.min_x:
            self.x = self.min_x
            self.patrol_dir = 1
            self.vx = self.patrol_speed
        elif self.x >= self.max_x - self.w:
            self.x = self.max_x - self.w
            self.patrol_dir = -1
            self.vx = -self.patrol_speed
        
        if (abs(player.x + player.w // 2 - self.x - self.w // 2) < (player.w + self.w) // 2 and
            abs(player.y + player.h // 2 - self.y - self.h // 2) < (player.h + self.h) // 2):
            if player.take_damage():
                push = 1 if player.x > self.x else -1
                player.vx = push * 12
                player.vy = -8
                for _ in range(20):
                    particles.append(Particle(player.x + player.w // 2, player.y + player.h // 2, RED))
    
    def draw(self, camera_x):
        screen_x = int(self.x - camera_x)
        if -100 < screen_x < WIDTH + 100:
            color = (255, 255, 100) if self.dash_cooldown > 80 else YELLOW
            
            if enemy_image:
                img = enemy_image.convert_alpha()
                img = pygame.transform.scale(img, (self.w, self.h))
                if self.dash_cooldown > 80:
                    tinted = img.copy()
                    tinted.fill((255, 255, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
                    screen.blit(tinted, (screen_x, int(self.y)))
                else:
                    screen.blit(img, (screen_x, int(self.y)))
            else:
                pygame.draw.rect(screen, color, (screen_x, int(self.y), self.w, self.h))
                pygame.draw.rect(screen, BLACK, (screen_x, int(self.y), self.w, self.h), 2)

def generate_roof_segments(start_x, count=20):
    segments = []
    x = start_x
    y = 80
    
    for i in range(count):
        width = random.randint(150, 300)
        y_change = random.randint(-30, 30)
        new_y = max(50, min(150, y + y_change))
        
        segments.append({'x1': x, 'x2': x + width, 'y': y})
        
        x += width
        y = new_y
    
    return segments

def generate_dungeon_section(start_x, last_y):
    platforms = []
    collectibles = []
    enemies = []
    
    x = start_x
    y = last_y
    
    num_platforms = random.randint(6, 10)
    
    for i in range(num_platforms):
        plat_w = random.randint(100, 200)
        plat_h = 20
        
        x_gap = random.randint(150, 280)
        y_change = random.randint(-80, 80)
        
        plat_x = x + x_gap
        plat_y = max(300, min(600, y + y_change))
        
        platforms.append(Platform(plat_x, plat_y, plat_w, plat_h))
        
        if random.random() > 0.3:
            col_x = plat_x + random.randint(20, plat_w - 30) if plat_w > 50 else plat_x + plat_w // 2
            col_y = plat_y - 35
            collectibles.append(Collectible(col_x, col_y))
        
        if random.random() > 0.5 and plat_w > 120:
            enemy_x = plat_x + 20
            enemy_y = plat_y - 33
            enemies.append(Enemy(enemy_x, enemy_y, plat_x, plat_x + plat_w))
        
        x = plat_x
        y = plat_y
    
    return platforms, collectibles, enemies, y

def draw_hearts(health):
    for i in range(3):
        x = WIDTH - 40 - i * 35
        y = 20
        if i < health:
            pygame.draw.circle(screen, RED, (x, y), 12)
        else:
            pygame.draw.circle(screen, (80, 80, 80), (x, y), 12)
        pygame.draw.circle(screen, BLACK, (x, y), 12, 2)

def main():
    player = Player()
    camera_x = 0
    
    platforms = [Platform(100, 500, 150, 20)]
    collectibles = []
    enemies = []
    particles = []
    
    roof_segments = generate_roof_segments(0)
    
    last_y = 500
    new_p, new_c, new_e, last_y = generate_dungeon_section(250, last_y)
    platforms.extend(new_p)
    collectibles.extend(new_c)
    enemies.extend(new_e)
    
    score = 0
    last_gen_x = platforms[-1].x if platforms else 0
    last_roof_x = roof_segments[-1]['x2'] if roof_segments else 0
    
    font = pygame.font.Font(None, 40)
    running = True
    
    while running:
        clock.tick(60)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if player.web_attached:
                        player.detach_web()
                    else:
                        player.jump()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.direction *= -1
                elif event.button == 3:
                    if player.web_attached:
                        player.detach_web()
                    else:
                        player.attach_web(mouse_x, mouse_y, camera_x, roof_segments)
        
        player.update(platforms, roof_segments)
        
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)
        
        for col in collectibles:
            col.update()
            if col.check_collect(player, particles):
                score += 10
        
        for enemy in enemies:
            enemy.update(player, particles)
        
        if player.health <= 0:
            if death_sound:
                death_sound.play()
            screen.fill(BG_COLOR)
            game_over_text = font.render("GAME OVER!", True, RED)
            score_text = font.render(f"Final Score: {score}", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (WIDTH // 2 - 120, HEIGHT // 2 - 60))
            screen.blit(score_text, (WIDTH // 2 - 140, HEIGHT // 2))
            screen.blit(restart_text, (WIDTH // 2 - 150, HEIGHT // 2 + 60))
            pygame.display.flip()
            
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            main()
                            return
            continue
        
        if player.y > HEIGHT + 100:
            player.health = 0
            continue
        
        target_camera_x = player.x - WIDTH // 3
        camera_x += (target_camera_x - camera_x) * 0.1
        
        if player.x > last_gen_x - 1000:
            new_p, new_c, new_e, last_y = generate_dungeon_section(last_gen_x + 200, last_y)
            platforms.extend(new_p)
            collectibles.extend(new_c)
            enemies.extend(new_e)
            last_gen_x = platforms[-1].x if platforms else last_gen_x
        
        if player.x > last_roof_x - 1500:
            new_roof = generate_roof_segments(last_roof_x)
            roof_segments.extend(new_roof)
            last_roof_x = roof_segments[-1]['x2'] if roof_segments else last_roof_x
        
        platforms = [p for p in platforms if p.x > camera_x - 300]
        collectibles = [c for c in collectibles if c.x > camera_x - 300]
        enemies = [e for e in enemies if e.x > camera_x - 300]
        roof_segments = [s for s in roof_segments if s['x2'] > camera_x - 300]
        
        screen.fill(BG_COLOR)
        
        for segment in roof_segments:
            x1 = int(segment['x1'] - camera_x)
            x2 = int(segment['x2'] - camera_x)
            y = int(segment['y'])
            if x2 > -100 and x1 < WIDTH + 100:
                pygame.draw.rect(screen, DARK_GRAY, (x1, 0, x2 - x1, y))
                pygame.draw.line(screen, (100, 100, 100), (x1, y), (x2, y), 3)
        
        for plat in platforms:
            plat.draw(camera_x)
        
        for particle in particles:
            particle.draw(camera_x)
        
        for col in collectibles:
            col.draw(camera_x)
        
        for enemy in enemies:
            enemy.draw(camera_x)
        
        player.draw(camera_x)
        
        score_surf = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surf, (10, 10))
        
        dir_text = "→" if player.direction == 1 else "←"
        dir_surf = font.render(f"Dir: {dir_text}", True, WHITE)
        screen.blit(dir_surf, (10, 50))
        
        draw_hearts(player.health)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()