import pygame
from pygame.locals import *
import random
import sys
from tkinter import filedialog
from tkinter import *

pygame.init()

vec = pygame.math.Vector2
height = 350
width = 700
acc = 0.3
fric = -0.1
fps = 60
fps_clock = pygame.time.Clock()
count = 0
run_animation_right = (pygame.image.load("Player_Sprite_R.png"), pygame.image.load("Player_Sprite2_R.png"),
                       pygame.image.load("Player_Sprite3_R.png"), pygame.image.load("Player_Sprite4_R.png"),
                       pygame.image.load("Player_Sprite5_R.png"), pygame.image.load("Player_Sprite6_R.png"),
                       pygame.image.load("Player_Sprite_R.png"))
run_animation_left = (pygame.image.load("Player_Sprite_L.png"), pygame.image.load("Player_Sprite2_L.png"),
                      pygame.image.load("Player_Sprite3_L.png"), pygame.image.load("Player_Sprite4_L.png"),
                      pygame.image.load("Player_Sprite5_L.png"), pygame.image.load("Player_Sprite6_L.png"),
                      pygame.image.load("Player_Sprite_L.png"))
attack_animation_right = (pygame.image.load("Player_Sprite_R.png"), pygame.image.load("Player_Attack_R.png"),
                          pygame.image.load("Player_Attack2_R.png"), pygame.image.load("Player_Attack2_R.png"),
                          pygame.image.load("Player_Attack3_R.png"), pygame.image.load("Player_Attack3_R.png"),
                          pygame.image.load("Player_Attack4_R.png"), pygame.image.load("Player_Attack4_R.png"),
                          pygame.image.load("Player_Attack5_R.png"), pygame.image.load("Player_Attack5_R.png"),
                          pygame.image.load("Player_Sprite_R.png"))
attack_animation_left = (pygame.image.load("Player_Sprite_L.png"), pygame.image.load("Player_Attack_L.png"),
                         pygame.image.load("Player_Attack2_L.png"), pygame.image.load("Player_Attack2_L.png"),
                         pygame.image.load("Player_Attack3_L.png"), pygame.image.load("Player_Attack3_L.png"),
                         pygame.image.load("Player_Attack4_L.png"), pygame.image.load("Player_Attack4_L.png"),
                         pygame.image.load("Player_Attack5_L.png"), pygame.image.load("Player_Attack5_L.png"),
                         pygame.image.load("Player_Sprite_L.png"))
hit_cooldown = pygame.USEREVENT + 1


display = pygame.display.set_mode((width, height))
pygame.display.set_caption("RPG MASTA")


class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.bgimage = pygame.image.load("Background.png")
        self.bgY = 0
        self.bgX = 0

    def render(self):
        display.blit(self.bgimage, (self.bgX, self.bgY))


class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Ground.png")
        self.rect = self.image.get_rect(center=(350, 350))

    def render(self):
        display.blit(self.image, (self.rect.x, self.rect.y))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player_Sprite_R.png")
        self.rect = self.image.get_rect()
        self.vx = 0
        self.pos = vec((340, 240))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.direction = "RIGHT"
        self.jumping = False
        self.running = False
        self.move_frame = 0
        self.attacking = False
        self.combat_frame = 0
        self.cooldown = False

    def correction(self):
        if self.combat_frame == 1:
            self.pos.x -= 20
        if self.combat_frame == 10:
            self.pos.x += 20

    def move(self):
        self.acc = vec(0, 0.5)
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:
            self.acc.x = -acc
        if pressed_keys[K_RIGHT]:
            self.acc.x = acc
        if abs(self.vel.x) > 0.3:
            self.running = True
        else:
            self.running = False
        self.acc.x += self.vel.x * fric
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        if self.pos.x > width:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = width
        self.rect.midbottom = self.pos

    def update(self):
        if self.move_frame > 6:
            self.move_frame = 0
            return
        if not self.jumping and self.running:
            if self.vel.x > 0:
                self.image = run_animation_right[self.move_frame]
                self.direction = "RIGHT"
            else:
                self.image = run_animation_left[self.move_frame]
                self.direction = "LEFT"
            self.move_frame += 1
        if abs(self.vel.x) < 0.2 and self.move_frame != 0:
            self.move_frame = 0
            if self.direction == "RIGHT":
                self.image = run_animation_right[self.move_frame]
            if self.direction == "LEFT":
                self.image = run_animation_left[self.move_frame]

    def attack(self):
        if self.combat_frame > 10:
            self.combat_frame = 0
            self.attacking = False
        if self.direction == "RIGHT":
            self.image = attack_animation_right[self.combat_frame]
        elif self.direction == "LEFT":
            self.correction()
            self.image = attack_animation_left[self.combat_frame]
        self.combat_frame += 1

    def jump(self):
        self.rect.x += 1
        hits = pygame.sprite.spritecollide(self, ground_group, False)
        self.rect.x -= 1
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -13

    def gravity_check(self):
        hits = pygame.sprite.spritecollide(player, ground_group, False)
        if self.vel.y > 0:
            if hits:
                lowest = hits[0]
                if self.pos.y < lowest.rect.bottom:
                    self.pos.y = lowest.rect.top + 1
                    self.vel.y = 0
                    self.jumping = False

    def player_hit(self):
        if not self.cooldown:
            self.cooldown = True
            pygame.time.set_timer(hit_cooldown, 1000)
            print("HIT!")
            pygame.display.update()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.pos = vec(0, 0)
        self.vel = vec(0, 0)
        self.direction = random.randint(0, 1)
        self.vel.x = random.randint(2, 6) / 2
        if self.direction == 0:
            self.pos.x = 0
            self.pos.y = 235
        if self. direction == 1:
            self.pos.x = 700
            self.pos.y = 235

    def move(self):
        if self.pos.x > width - 20:
            self.direction = 1
        if self.pos.x < 20:
            self.direction = 0
        if self.direction == 1:
            self.pos.x -= self.vel.x
        if self.direction == 0:
            self.pos.x += self.vel.x
        self.rect.center = self.pos

    def render(self):
        display.blit(self.image, (self.pos.x, self.pos.y))

    def update(self):
        hits = pygame.sprite.spritecollide(self, player_group, False)
        if hits and player.attacking:
            self.kill()
            print("GOT 'EM")
        elif hits and not player.attacking:
            player.player_hit()


class Castle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hide = False
        self.image = pygame.image.load("castle.png")

    def update(self):
        if not self.hide:
            display.blit(self.image, (400, 80))


class EventHandler:
    def __init__(self):
        self.enemy_count = 0
        self.battle = False
        self.enemy_generation = pygame.USEREVENT + 1
        self.stage_enemies = []
        self.stage = 1
        for x in range(1, 21):
            self.stage_enemies.append(int(x ** 2 / 2) + 1)
        self.root = Tk()

    def stage_handler(self):
        self.root.geometry('200x170')
        button1 = Button(self.root, text="Twilight Dungeon", width=16, height=2, command=self.world1)
        button2 = Button(self.root, text="skyward Dungeon", width=16, height=2, command=self.world2)
        button3 = Button(self.root, text="Hell Dungeon", width=16, height=2, command=self.world3)

        button1.place(x=40, y=15)
        button2.place(x=40, y=65)
        button3.place(x=40, y=115)

        self.root.mainloop()

    def world1(self):
        self.root.destroy()
        pygame.time.set_timer(self.enemy_generation, 2000)
        castle.hide = True
        self.battle = True

    def world2(self):
        self.battle = True

    def world3(self):
        self.battle = True

    def next_stage(self):
        self.stage += 1
        self.enemy_count = 0
        print("Stage " + str(self.stage))
        pygame.time.set_timer(self.enemy_generation, 1500 - (50 * self.stage))


background = Background()
ground = Ground()
player = Player()
ground_group = pygame.sprite.Group()
ground_group.add(ground)
player_group = pygame.sprite.Group()
player_group.add(player)
Enemies = pygame.sprite.Group()
castle = Castle()
handler = EventHandler()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_RETURN:
                if not player.attacking:
                    player.attack()
                    player.attacking = True
            if event.key == pygame.K_z and 450 < player.rect.x < 550:
                handler.stage_handler()
            if event.key == pygame.K_x:
                if handler.battle and len(Enemies) == 0:
                    handler.next_stage()
        if event.type == hit_cooldown:
            player.cooldown = False
            pygame.time.set_timer(hit_cooldown, 0)
        if event.type == handler.enemy_generation:
            if handler.enemy_count < handler.stage_enemies[handler.stage - 1]:
                enemy = Enemy()
                Enemies.add(enemy)
                handler.enemy_count += 1

    background.render()
    ground.render()
    castle.update()
    player.move()
    player.gravity_check()
    player.update()
    if player.attacking:
        player.attack()
    for entity in Enemies:
        entity.update()
        entity.move()
        entity.render()
    display.blit(player.image, player.rect)
    pygame.display.update()
    fps_clock.tick(fps)
