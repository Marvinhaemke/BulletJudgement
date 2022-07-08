# Bullet Judgement
#
# @author Marvin Hämke
# Mtr. Nr.: 20202316

from statistics import mode
from tkinter import S
from numpy import double
import pygame
from pygame.locals import *
import sys
import random
import time
import math
from os.path import exists

pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional

HEIGHT = 600
WIDTH = 600
ACC = 2
FPS = 60
RUN = True

FramePerSec = pygame.time.Clock()

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

# Anfangs Spielstatus (Startbildschirm)
gameState = 1

# Standardmäßig ausgewählter Spielmudus (Hell)
mode = 1

# Sprite Gruppen für Bullets bzw. Gegners
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# prevState zum Anzeigen des vorherigen Spielstatuses (Startbildschirm, Pause, etc.)
prevState = 0

# einige globale Variablen
pauseTime = 0
upgradeCooldown = 0
spawntimer = 0
maxspawntimer = 60
enemyHp = 1
explosions = False

# Musik Laden und auf repeat abspielen
pygame.mixer.music.load('musik/gameMusic.mp3')
pygame.mixer.music.play(-1)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Spieler Größe und Farbe
        self.surf = pygame.Surface((10, 10))
        self.surf.fill((0, 255, 0))
        # Die Hitboox ist wie in Bullet Hell Spielen üblich kleiner als der Sprite
        self.hitbox = pygame.Surface((6, 6))
        self.rect = pygame.Rect(0, 0, 6, 6)
        
        self.hp = 3
        self.pos = vec((WIDTH/2, HEIGHT/2+HEIGHT/4))
        
        self.acc = vec(0, 0)
        self.vel = vec(0, 0)
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y 
        self.surf.blit(self.hitbox, self.pos)

        

    def update(self):
        
        #Bewegung (evtl. mit events neu schreiben)
        # Spieler bleibt immer im Bildschirm
        pressed_keys = pygame.key.get_pressed()
        self.acc = vec(0, 0)
        if pressed_keys[K_LEFT] or pressed_keys[K_a]:
            if self.pos.x > 0 - 5:
                self.acc.x += -ACC
        if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
            if self.pos.x < WIDTH - 5:
                self.acc.x += ACC
        if pressed_keys[K_DOWN] or pressed_keys[K_s]:
            if self.pos.y < HEIGHT-5:
                self.acc.y += ACC
        if pressed_keys[K_UP] or pressed_keys[K_w]:
            if self.pos.y > 0-5:
                self.acc.y += -ACC

        self.pos += self.acc
        
        '''
        # unendlicher Raum (Alternative)
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        
        if self.pos.y > HEIGHT:
            self.pos.y = 0
        if self.pos.y < 0:
            self.pos.y = HEIGHT
        '''
        self.rect.center = self.pos
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

    
class PlayerHeaven(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        #self.image = pygame.image.load("character.png")
        self.surf = pygame.Surface((10, 10))
        self.surf.fill((0, 255, 0))
        self.hitbox = pygame.Surface((6, 6))
        #self.hitbox.fill((255, 50, 50))
        self.rect = pygame.Rect(0, 0, 6, 6)

        self.maxHp = 3
        self.hp = 3
        self.speed = 2
        self.fireRate = 1
        self.bullets = 1
        self.size = 1
        self.dmg = 1
        self.piercing = 1
        self.bltSize = 1
        self.range = 50

        self.pos = vec((WIDTH/2, HEIGHT/2+HEIGHT/4))

        self.cooldown = 0
        self.maxcooldown = 30

        self.acc = vec(0, 0)
        self.vel = vec(0, 0)
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        self.surf.blit(self.hitbox, self.pos)

    def getPos(self):
        return self.pos

    def update(self):

        # Bewegung
        pressed_keys = pygame.key.get_pressed()
        self.acc = vec(0, 0)
        if pressed_keys[K_LEFT] or pressed_keys[K_a]:
            if self.pos.x > 0 - 5:
                self.acc.x += -self.speed
        if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
            if self.pos.x < WIDTH - 5:
                self.acc.x += self.speed
        if pressed_keys[K_DOWN] or pressed_keys[K_s]:
            if self.pos.y < HEIGHT-5:
                self.acc.y += self.speed
        if pressed_keys[K_UP] or pressed_keys[K_w]:
            if self.pos.y > 0-5:
                self.acc.y += -self.speed
        # Bei Mausklick wird geschossen
        if pygame.mouse.get_pressed()[0]:
            if self.cooldown <= 0:
                self.shoot()
                self.cooldown = self.maxcooldown
        self.cooldown -= self.fireRate

        

        self.pos += self.acc
        self.rect.center = self.pos
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
    # shoot method

    def shoot(self):
        for i in range(self.bullets):
            if i % 3 == 0:
                self.addAngle = 0
            elif i % 3 == 1:
                self.addAngle = i*0.1
            elif i % 3 == 2:
                self.addAngle = (-i+1)*0.1
            bullet = BulletHeaven(self.pos, self.addAngle, self.dmg, self.piercing, self.bltSize, self.range)
            bullets.add(bullet)

class Boss(pygame.sprite.Sprite):
    
    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load('images/auge.png')
        self.rect = self.surf.get_rect()
        self.pos = vec((WIDTH/2, HEIGHT/2))
        self.angle = 0
        
        self.counter = 0
        
        self.rotDirection = 0
        self.moveDirection = 0

        self.pattern = 0
        self.patternCooldown = 900

        # Parameter zur Kontrolle der Schwierigkeit
        self.maxCooldown = 20
        self.cooldown = 0

        self.type = 0
        self.gap = 13377331

        self.numPatterns = 5
        #Geschwindigkeit der Kugeln
        self.bulletSpeed = 2
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        self.center = vec((self.rect.x + self.rect.width/4, self.rect.y + self.rect.height/4))
        

    def update(self):
        self.bulletSpeed = self.pattern/7 + 2
        if self.pattern > 6:
            self.maxCooldown = 15
        if self.pattern > 12:
            self.maxCooldown = 10
        self.shoot()
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        self.center = vec((self.rect.x + self.rect.width/4, self.rect.y + self.rect.height/4))
        
        if self.patternCooldown <= 0:
            if self.pattern == 4:
                self.gap = 0
            if self.pattern < self.numPatterns -1:
                self.pattern += 1
            else:
                self.pattern = 0
            
            
            self.patternCooldown = 900
        else:
            self.patternCooldown -= 1
    
    def shoot(self):
        
        # Bullet Patterns (viele andere Patterns, durch Anpassung des Bullettypes möglich)
        
        #pattern 1 Circle (numPatterns nutzlos?)
        if self.pattern%self.numPatterns == 0:
            if self.cooldown < self.maxCooldown:
                self.cooldown += 2
            else:
                for x in range(18):
                    #bullets.append(Bullet(self.pos.x, self.pos.y, self.angle, self.bulletSpeed, 0))
                    bullets.add(Bullet(self.center.x, self.center.y, self.angle, self.bulletSpeed, 0, self.type))
                    self.angle += 20
                if self.rotDirection == 0:
                    self.angle += 3
                else:
                    self.angle -= 3
                self.cooldown = 0
                if self.counter < 20:
                    self.counter += 1
                else:
                    if self.rotDirection == 0:
                        self.rotDirection = 1
                    else:
                        self.rotDirection = 0
                    self.counter = 0
        #pattern 2 Großer Kreis
        elif self.pattern%self.numPatterns == 1:
            if self.cooldown < self.maxCooldown:
                self.cooldown += 1
            else:
                for x in range(9):
                    #bullets.append(Bullet(self.pos.x, self.pos.y, self.angle, self.bulletSpeed, 0))
                    bullets.add(Bullet(self.center.x, self.center.y, self.angle, self.bulletSpeed, 0, self.type))
                    self.angle += 40
                if self.rotDirection == 0:
                    self.angle += 24
                else:
                    self.angle -= 24
                self.cooldown = 0
                if self.counter < 10:
                    self.counter += 1
                else:
                    if self.rotDirection == 0:
                        self.rotDirection = 1
                    else:
                        self.rotDirection = 0
                    self.counter = 0
        #pattern 3 circle walls
        if self.pattern%self.numPatterns == 2:
            if self.cooldown < self.maxCooldown:
                self.cooldown += 1
            else:
                for x in range(18):
                    #bullets.append(Bullet(self.pos.x, self.pos.y, self.angle, self.bulletSpeed, 0))
                    bullets.add(Bullet(self.center.x, self.center.y, self.angle, self.bulletSpeed, 0, self.type))
                    
                    self.angle += 3
                if self.rotDirection == 0:
                    self.angle += 6
                else:
                    self.angle -= 6
                self.cooldown = 0
                if self.counter < 60:
                    self.counter += 1
                else:
                    if self.rotDirection == 0:
                        self.rotDirection = 1
                    else:
                        self.rotDirection = 0
                    self.counter = 0
        #pattern 3 circle with gaps  (Überarbeiten)
        if self.pattern%self.numPatterns == 3:
            if self.cooldown < self.maxCooldown:
                self.cooldown += 1
            else:
                if self.gap == 0:
                    self.gap = math.atan2(P1.pos.y - self.pos.y, P1.pos.x - self.pos.x) + 90
                for x in range(68):
                    
                    bullets.add(Bullet(self.center.x, self.center.y, self.angle, self.bulletSpeed, 0, self.type))
                    if self.angle%360 < (self.gap%360)-20 or self.angle%360 > (self.gap%360)+20:
                        self.angle += 5
                    
                    else:
                        self.angle += 20
                self.gap += 10

                if self.rotDirection == 0:
                    self.angle += 6
                else:
                    self.angle -= 5
                self.cooldown = 0
                #Rotierungsrichtung
                if self.counter < 60:
                    self.counter += 1
                else:
                    if self.rotDirection == 0:
                        self.rotDirection = 1
                    else:
                        self.rotDirection = 0
                    self.counter = 0
        #pattern 3 Kreis mit links/rechts Bewegung (kaotisch) (Überarbeiten, muss zur Mitte zurück kehren)
        elif self.pattern%self.numPatterns == 4:
            if self.moveDirection == 0:
                if self.pos.x > 240:
                    self.pos.x -= 2
                else:
                    self.moveDirection = 1
                    self.pos.x += 2
            else:
                if self.pos.x < 360:
                    self.pos.x += 2
                else:
                    self.moveDirection = 0
                    self.pos.x -= 2

            if self.cooldown < self.maxCooldown * 1.5:
                self.cooldown += 1
            else:
                for x in range(9):
                    
                    bullets.add(Bullet(self.center.x, self.center.y, self.angle, self.bulletSpeed, 0, self.type))
                    self.angle += 40
                if self.rotDirection == 0:
                    self.angle += 11
                else:
                    self.angle -= 5
                self.cooldown = 0
                if self.counter < 60:
                    self.counter += 1
                else:
                    if self.rotDirection == 0:
                        self.rotDirection = 1
                    else:
                        self.rotDirection = 0
                    self.counter = 0

#Gegner Klasse für den Bullet Hell Modus (1 Boss)
class Enemy(pygame.sprite.Sprite):
    def __init__(self, hp, explosions):
        super().__init__()
        self.surf = pygame.Surface((10, 10))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        randPos = random.randint(0, 3)
        if randPos == 0:
            self.pos = vec((WIDTH + 50, random.randint(0, HEIGHT)))
        elif randPos == 1:
            self.pos = vec((-50, random.randint(0, HEIGHT)))
        elif randPos == 2:
            self.pos = vec((random.randint(0, WIDTH), HEIGHT+50))
        elif randPos == 3:
            self.pos = vec((random.randint(0, WIDTH), -50))
        self.angle = 0
        self.hp = hp
        self.explosions = explosions

        self.moveDirection = 0

        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        self.center = vec((self.rect.x + self.rect.width/4,
                          self.rect.y + self.rect.height/4))

    def update(self):
        # holt sich die Position des Spielers
        playerPos = P1.getPos()
        # Bewegt sich auf den Spieler zu
        self.pos += (playerPos - self.pos).normalize()
        # Gegner hält Abstand von anderen Gegnern
        for enemy in enemies:
            if self.pos != enemy.pos:
                if self.rect.colliderect(enemy.rect):
                    self.pos += (self.pos - enemy.pos).normalize()
        if self.hp <= 0:
            # Falls explosions Upgrade ausgewählt wurde explodieren sterbende Gegner in einen Kreis aus Kugeln mit kurzer Reichweite
            if self.explosions:
                angle = random.randint(0, 360)
                for x in range(10):
                    bullet = BulletHeaven(self.pos, angle, 1, 1, 1, 10)
                    bullets.add(bullet)
                    angle += 10
            enemies.remove(self)
        # Rect Center wird geupdatet, sodass es mit der neuen Position übereinstimmt
        self.rect.center = self.pos

# Heaven Mode Bullet
class BulletHeaven(pygame.sprite.Sprite):
    def __init__(self, pos, addAngle, dmg, piercing, size, range):
        super().__init__()
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        self.surf = pygame.Surface((10*size, 10*size))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect()
        self.hp = piercing
        self.pos = vec((pos.x, pos.y))
        self.range = range

        # Gruppe mit getroffenen Gegnern, damit diese nicht mehrmals von der gleichen Kugel getroffen werden
        self.hits = pygame.sprite.Group()

        # Winkel zu Maus wird berechnet
        self.angle = math.atan2(self.mouse_y - self.pos.y,
                                self.mouse_x - self.pos.x) + addAngle
        
        self.speed = 3
        self.type = type
        
        # Geschwindigkeit wird berechnet
        self.vel = vec(self.speed * math.cos(self.angle),
                       self.speed * math.sin(self.angle))
        self.beschleunigung = 0
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

    def update(self):
        # Falls sich die Kugel im Fenster befindet bewegt sie sich weiter, ist sie außerhalb wird sie gelöscht
        self.rect.center = self.pos
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        print((self.angle * 180/math.pi)+180)

        self.range -= 1
        if self.range <= 0:
            bullets.remove(self)

        if self.hp <= 0:
            bullets.remove(self)

        if (self.pos.x < WIDTH and self.pos.x > -10 and self.pos.y < HEIGHT and self.pos.y > -10):
            # Die Kugel bewegt sich in Richtung maus
            self.pos += self.vel
            self.rect.center = self.pos
        else:
            # bullets.remove(self)
            bullets.remove(self)

# Hell Mode Bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, angle, speed, beschleunigung, type):
        super().__init__()
        # Größe und Farbe der Bullet
        self.surf = pygame.Surface((10, 10))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect()

        self.hp = 3
        self.pos = vec((pos_x, pos_y))
        self.angle = angle
        self.speed = speed
        self.type = type
        self.vel = pygame.math.Vector2()
        self.vel.from_polar((speed, self.angle))
        self.beschleunigung = beschleunigung
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y 

    def update(self):
        
        self.rect.center = self.pos
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
        #Falls sich die Kugel im Fenster befindet bewegt sie sich weiter, ist sie außerhalb wird sie gelöscht
        if (self.pos.x < WIDTH and self.pos.x > -10 and self.pos.y < HEIGHT and self.pos.y > -10):
            #Die Kugel bewegt sich in einer geraden Linie
            if self.type == 0:
                self.pos.x += float(self.vel.x)
                self.pos.y += float(self.vel.y)
            #Die Kugel wird schneller
            if self.type == 1:
                if self.vel.x > 0:
                    self.pos.x += float(self.vel.x) - self.beschleunigung
                else:
                    self.pos.x += float(self.vel.x) + self.beschleunigung
                if self.vel.y > 0:
                    self.pos.y += float(self.vel.y) - self.beschleunigung
                else:
                    self.pos.y += float(self.vel.y) + self.beschleunigung
                self.beschleunigung += 0.007
            #Die Kugel wird langsamer
            if self.type == 2:
                pass
            #Die Kugel wird abwechselnd langsamer und schneller
            if self.type == 3:
                pass
            #Die Kugel bewegt sich hin und her
            if self.type == 4:
                pass
            #Die Kugel wird langsamer, kehrt um und wird dann schneller
            if self.type == 5:
                self.pos.x += float(self.vel.x) * self.x
                self.pos.y -= float(self.vel.y) * self.x
                self.x -= 0.01
            #Die Kugel fliegen seitwärts, dan runter und hoch (muss noch angepasst werden)
            if self.type == 6:
                if self.vel.x > 0:
                    self.pos.x += float(self.vel.x) + self.x
                else:
                    self.pos.x += float(self.vel.x) - self.x
                if self.vel.y > 0:
                    self.pos.y += float(self.vel.y) + self.x
                else:
                    self.pos.y += float(self.vel.y) - self.x
                self.x += 0.001
        else:
            #bullets.remove(self)
            bullets.remove(self)



class Score(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = vec((WIDTH/2, HEIGHT/12))
        self.score = 0
        self.startTime = time.time()

        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.surf = self.font.render(str(self.score), False, (255, 255, 255))

    def getScore(self):
        return int(self.score)

    def update(self):
        # Score

        self.score = time.time() - self.startTime
        self.surf = self.font.render(
            str(int(self.score)), False, (255, 255, 255))
        self.pos = vec(WIDTH/2 - self.surf.get_width()/2, (HEIGHT/12))





while True:
    
    # Events
    click = False
    for event in pygame.event.get():

        # Escape beendet das Spiel
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                print("Ende")
                pygame.quit()
                sys.exit()

        if event.type == QUIT:
            print("Ende")
            pygame.quit()
            sys.exit()

        # Space startet bzw, pausiert das Spiel
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                print("Start")
                if prevState == 0:
                    gameState = 3
                else:
                    gameState = 0
        # M mutet die Musik
        if event.type == KEYDOWN:
            if event.key == K_m:
                print(pygame.mixer.music.get_volume())
                if pygame.mixer.music.get_volume() > 0:
                    print("Mute")
                    pygame.mixer.music.set_volume(0)
                else:
                    pygame.mixer.music.set_volume(1)
                   
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            click = True

    # Hintergrund jeden Frame überschreiben
    SCREEN.fill((0, 0, 0))
    
    # Spielablauf
    if gameState == 0:
        if mode == 0:
            if prevState == 1 or prevState == 2:
                P1 = PlayerHeaven()
                S1 = Score()
                all_sprites = pygame.sprite.Group()
                all_sprites.add(P1)
                all_sprites.add(S1)
    
            if prevState != 0 and prevState != 3 and prevState != 4:
                bullets.empty()
                enemies.empty()
                P1.__init__()
                S1.__init__()
                maxspawntimer = 60
            
            if prevState == 3 or prevState == 4:  
                S1.startTime += (time.time() - pauseTime)

            prevState = 0

            # Gegner Spawnen
            if maxspawntimer > 2:
                maxspawntimer -= (S1.score/10000)

            if spawntimer <= 0:
                enemy = Enemy(enemyHp, explosions)
                enemies.add(enemy)
                spawntimer = maxspawntimer
            else:
                spawntimer -= 1
        
            for entity in all_sprites:
                entity.update()
                SCREEN.blit(entity.surf, entity.pos)
               

            # collision von Bullets mit Enemy
            for entity in bullets:
                entity.update()
                for enemy in enemies:
                    if entity.rect.colliderect(enemy.rect):
                        # check if enemy is in entity.hits
                        if enemy not in entity.hits:
                            entity.hits.add(enemy)
                            entity.hp -= 1
                            enemy.hp -= P1.dmg

                SCREEN.blit(entity.surf, entity.pos)

            for entity in enemies:
                entity.update()
                if entity.rect.colliderect(P1.rect):
                    P1.hp -= 1
                    if P1.hp == 2:
                        P1.surf.fill((255, 255, 0))
                    elif P1.hp == 1:
                        P1.surf.fill((255, 155, 0))
                    elif P1.hp == 0:
                        gameState = 2
                    # destroy enemy
                    enemies.remove(entity)
                SCREEN.blit(entity.surf, entity.pos)
            if upgradeCooldown > 0:
                upgradeCooldown -= 1
            # Leben der Gegner alle 100 Punkte erhöhen
            if int(S1.score) % 100 == 0 and int(S1.score) != 0 and upgradeCooldown == 0:
                enemyHp += 1
            # Alle 20 Punkte wird ein Upgrade Bildschirm angezeigt
            if int(S1.score) % 20 == 0 and int(S1.score) != 0 and upgradeCooldown == 0:
                gameState = 4
                upgradeCooldown = 100

        # Hell Mode Spielablauf
        elif mode == 1:
            if prevState == 1 or prevState == 2:
                # Klassen Instanzieren und in all_sprites Gruppe einfügen
                P1 = Player()
                S1 = Score()
                B1 = Boss()
                all_sprites = pygame.sprite.Group()
                all_sprites.add(P1)
                all_sprites.add(S1)
                all_sprites.add(B1)
          
                
            if prevState != 0 and prevState != 3:
                bullets.empty()
                P1.__init__()
                B1.__init__()
                S1.__init__()
            prevState = 0
            
            # Alle Objekte (außer Bullets) updaten
            for entity in all_sprites:
                entity.update()
                SCREEN.blit(entity.surf, entity.pos)
            
            # Bullets updaten
            for entity in bullets:
                entity.update()
                if entity.rect.colliderect(P1.rect):
                    bullets.remove(entity)
                    P1.hp -= 1
                    if P1.hp == 2:
                        P1.surf.fill((255, 255, 0))
                    elif P1.hp == 1:
                        P1.surf.fill((255, 155, 0))
                    elif P1.hp == 0:
                        gameState = 2
                SCREEN.blit(entity.surf, entity.pos)
        
            
        
        
        

    # Startbildschirm
    elif gameState == 1:

        if prevState == 0:

            # Font und Text erstellen
            font = pygame.font.SysFont('Comic Sans MS', 30)
            text = font.render('Press Space to Start', False, (255, 255, 255))
            tutorial = font.render(
                'Space: Pause                    M = Mute', False, (255, 255, 255))
            heavenMode = font.render('Heaven', False, (255, 255, 255))
            hellMode = font.render('Hell', False, (255, 255, 255))
            # neuen prevState setzen
            prevState = 1

        # Highlight the selected mode
        if mode == 0:
            heavenMode = font.render('Heaven', False, (0, 255, 0))
            hellMode = font.render('Hell', False, (255, 255, 255))
        elif mode == 1:
            hellMode = font.render('Hell', False, (255, 0, 0))
            heavenMode = font.render('Heaven', False, (255, 255, 255))

        # Text anzeigen
        SCREEN.blit(text, (WIDTH/2 - text.get_width() /
                    2, HEIGHT/2 - text.get_height()/2))
        SCREEN.blit(heavenMode, (WIDTH/2 - heavenMode.get_width()/2 - 150 , HEIGHT/2 - text.get_height()/2 + 100))
        SCREEN.blit(hellMode, (WIDTH/2 + hellMode.get_width()/2 + 100, HEIGHT/2 - text.get_height()/2 + 100))
        SCREEN.blit(tutorial, (WIDTH/2 - tutorial.get_width()/2,
                    (HEIGHT/2 - tutorial.get_height()/2) + 250))

        

        # Check if Hell or Heaven Mode is selected
        if click == True:
            if pygame.mouse.get_pos()[0] > WIDTH/2 - heavenMode.get_width()/2 - 150 and pygame.mouse.get_pos()[0] < WIDTH/2 - heavenMode.get_width()/2 - 150 + heavenMode.get_width() and pygame.mouse.get_pos()[1] > HEIGHT/2 - text.get_height()/2 + 100 and pygame.mouse.get_pos()[1] < HEIGHT/2 - text.get_height()/2 + 100 + heavenMode.get_height():
                mode = 0
                click = False
            elif pygame.mouse.get_pos()[0] > WIDTH/2 + hellMode.get_width()/2 + 100 and pygame.mouse.get_pos()[0] < WIDTH/2 + hellMode.get_width()/2 + 100 + hellMode.get_width() and pygame.mouse.get_pos()[1] > HEIGHT/2 - text.get_height()/2 + 100 and pygame.mouse.get_pos()[1] < HEIGHT/2 - text.get_height()/2 + 100 + hellMode.get_height():
                mode = 1
                click = False

    # Gameoverbildschirm
    elif gameState == 2:

        if prevState == 0:
            # Fonts
            font = pygame.font.SysFont('Comic Sans MS', 30)
            font2 = pygame.font.SysFont('Comic Sans MS', 50)
            # Game Over Text
            text = font2.render('Game Over', False, (255, 255, 255))
            # Score Text
            finalscore = int(S1.score)
            score = font.render('Score: ' + str(finalscore),
                                False, (255, 255, 255))
            if mode == 0:
                # Highscore speichern
                if exists('highscoreHeaven.txt'):     
                    if finalscore > int(open('highscoreHeaven.txt', 'r').read()):
                        open('highscoreHeaven.txt', 'w').write(str(finalscore))
                    highscoreText = font.render(
                        'Highscore: ' + str(int(open('highscoreHeaven.txt', 'r').read())), False, (255, 255, 255))
                else:
                    open('highscoreHeaven.txt', 'w').write(str(finalscore))
                    highscoreText = font.render(
                        'Highscore: ' + str(int(open('highscoreHeaven.txt', 'r').read())), False, (255, 255, 255))

            elif mode == 1:
                # Highscore speichern
                if exists('highscoreHell.txt'):         
                    if finalscore > int(open('highscoreHell.txt', 'r').read()):
                        open('highscoreHell.txt', 'w').write(str(finalscore))
                    highscoreText = font.render(
                        'Highscore: ' + str(int(open('highscoreHell.txt', 'r').read())), False, (255, 255, 255))
                else:
                    open('highscoreHell.txt', 'w').write(str(finalscore))
                    highscoreText = font.render(
                        'Highscore: ' + str(int(open('highscoreHell.txt', 'r').read())), False, (255, 255, 255))

            # Restart Text
            restartText = font.render(
                'Press Space to Restart', False, (255, 255, 255))

            heavenMode = font.render('Heaven', False, (255, 255, 255))
            hellMode = font.render('Hell', False, (255, 255, 255))

            # neuen prevState setzen
            prevState = 2
        
        # Ausgewählten Modus einfärben
        if mode == 0:
            heavenMode = font.render('Heaven', False, (0, 255, 0))
            hellMode = font.render('Hell', False, (255, 255, 255))
        elif mode == 1:
            hellMode = font.render('Hell', False, (255, 0, 0))
            heavenMode = font.render('Heaven', False, (255, 255, 255))
        
        # Prüfen welcher Modus ausgewählt ist
        if click == True:
            if pygame.mouse.get_pos()[0] > WIDTH/2 - heavenMode.get_width()/2 - 150 and pygame.mouse.get_pos()[0] < WIDTH/2 - heavenMode.get_width()/2 - 150 + heavenMode.get_width() and pygame.mouse.get_pos()[1] > HEIGHT/2 - text.get_height()/2 + 200 and pygame.mouse.get_pos()[1] < HEIGHT/2 - text.get_height()/2 + 200 + heavenMode.get_height():
                mode = 0
                click = False
            elif pygame.mouse.get_pos()[0] > WIDTH/2 + hellMode.get_width()/2 + 100 and pygame.mouse.get_pos()[0] < WIDTH/2 + hellMode.get_width()/2 + 100 + hellMode.get_width() and pygame.mouse.get_pos()[1] > HEIGHT/2 - text.get_height()/2 + 200 and pygame.mouse.get_pos()[1] < HEIGHT/2 - text.get_height()/2 + 200 + hellMode.get_height():
                mode = 1
                click = False
        
        # Text rendern
        SCREEN.blit(restartText, (WIDTH/2 - restartText.get_width() /
                    2, (HEIGHT/2 - restartText.get_height()/2) + 50))
        SCREEN.blit(highscoreText, (WIDTH/2 - highscoreText.get_width() /
                    2, (HEIGHT/2 - highscoreText.get_height()/2 -100)))
        SCREEN.blit(score, (WIDTH/2 - score.get_width()/2,
                    (HEIGHT/2 - score.get_height()/2) - 150))
        SCREEN.blit(text, (WIDTH/2 - text.get_width()/2,
                    (HEIGHT/2 - text.get_height()/2) - 250))
        SCREEN.blit(heavenMode, (WIDTH/2 - heavenMode.get_width()/2 - 150 , HEIGHT/2 - text.get_height()/2 + 200))
        SCREEN.blit(hellMode, (WIDTH/2 + hellMode.get_width()/2 + 100, HEIGHT/2 - text.get_height()/2 + 200))

    # Pausenbildschirm
    elif gameState == 3:
        if prevState == 0:
            # Fonts
            font = pygame.font.SysFont('Comic Sans MS', 30)

            # Restart Text
            resumeText = font.render(
                'Press Space to Resume', False, (255, 255, 255))

            # neuen prevState setzen
            prevState = 3

            pauseTime = time.time()

        # Text rendern
        SCREEN.blit(resumeText, (WIDTH/2 - resumeText.get_width() /
                    2, (HEIGHT/2 - resumeText.get_height()/2)))
        SCREEN.blit(S1.surf, S1.pos)

    # Upgradebildschirm
    elif gameState == 4:
        if prevState != 4:
            # Fonts
            font = pygame.font.SysFont('Comic Sans MS', 30)
            # Upgrades
            dmgUp = font.render('Damage Up', False, (255, 255, 255))
            fireUp = font.render('Fire Rate Up', False, (255, 255, 255))
            heal = font.render('Heal', False, (255, 255, 255))
            spdUp = font.render('Speed Up', False, (255, 255, 255))
            bltUp = font.render('Bullets Up', False, (255, 255, 255))
            sizeDown = font.render('Size Down', False, (255, 255, 255))
            piercing = font.render('Piercing Up', False, (255, 255, 255))
            bltSize = font.render('Bullet Size Up', False, (255, 255, 255))
            rangeUp = font.render('Range Up', False, (255, 255, 255))

            # seltene Optionen
            explosionsUp = font.render('Explosions', False, (255, 215, 0))

            # zufällig 3 Upgrades aus der Liste auswählen
            upgradeList = [dmgUp, fireUp, heal, spdUp, bltUp, sizeDown, piercing, bltSize, rangeUp]
            random.shuffle(upgradeList)
            upgradeList = upgradeList[:3]

            # pauseTime setzen
            pauseTime = time.time()

            # neuen prevState setzen
            prevState = 4

            # ab und zu gibt es ein seltenes Upgrade
            if random.randint(0, 50) < 5:
                selteneOption = True
            else:
                selteneOption = False

        # Optionen werden angezeigt
        for i in range(len(upgradeList)):
            SCREEN.blit(upgradeList[i], (WIDTH/2 - upgradeList[i].get_width() /
                        2, (HEIGHT/2 - upgradeList[i].get_height()/2) + i*100))

        # Seltene Option wird angezeigt
        if selteneOption == True:          
            if explosions == False:
                SCREEN.blit(explosionsUp, (WIDTH/2 - explosionsUp.get_width() /
                            2, (HEIGHT/2 - explosionsUp.get_height()/2) - 100))

        # prüfen ob eine Option geklickt wurde
        if click == True:
            
            
            # überprüft ob die 1. Option geklickt wurde
            if pygame.mouse.get_pos()[0] > WIDTH/2 - upgradeList[0].get_width()/2 and pygame.mouse.get_pos()[0] < WIDTH/2 + upgradeList[0].get_width()/2 and pygame.mouse.get_pos()[1] > HEIGHT/2 - upgradeList[0].get_height()/2 and pygame.mouse.get_pos()[1] < HEIGHT/2 + upgradeList[0].get_height()/2:
                chosenUpgrade = upgradeList[0]
            # überprüft ob die 2. Option geklickt wurde
            elif pygame.mouse.get_pos()[0] > WIDTH/2 - upgradeList[1].get_width()/2 and pygame.mouse.get_pos()[0] < WIDTH/2 + upgradeList[1].get_width()/2 and pygame.mouse.get_pos()[1] > HEIGHT/2 - upgradeList[1].get_height()/2 + 100 and pygame.mouse.get_pos()[1] < HEIGHT/2 + upgradeList[1].get_height()/2 + 100:
                chosenUpgrade = upgradeList[1]
            # überprüft ob die 3. Option geklickt wurde
            elif pygame.mouse.get_pos()[0] > WIDTH/2 - upgradeList[2].get_width()/2 and pygame.mouse.get_pos()[0] < WIDTH/2 + upgradeList[2].get_width()/2 and pygame.mouse.get_pos()[1] > HEIGHT/2 - upgradeList[2].get_height()/2 + 200 and pygame.mouse.get_pos()[1] < HEIGHT/2 + upgradeList[2].get_height()/2 + 200:
                chosenUpgrade = upgradeList[2]
            # überprüft ob die seltene Option geklickt wurde
            elif pygame.mouse.get_pos()[0] > WIDTH/2 - explosionsUp.get_width()/2 and pygame.mouse.get_pos()[0] < WIDTH/2 + explosionsUp.get_width()/2 and pygame.mouse.get_pos()[1] > HEIGHT/2 - explosionsUp.get_height()/2 - 100 and pygame.mouse.get_pos()[1] < HEIGHT/2 + explosionsUp.get_height()/2 -100 and selteneOption == True:
                chosenUpgrade = explosionsUp
            # wenn keine gelickt wurde, bleibt chosenUpgrade leer
            else:
                chosenUpgrade = None


            # Upgrade anwenden
            # Schaden wird erhöht
            if chosenUpgrade == dmgUp:
                P1.dmg += 1
            # Feuerrate wird erhöht
            elif chosenUpgrade == fireUp:
                P1.fireRate += 1
            # Spieler wird voll geheilt
            elif chosenUpgrade == heal:
                P1.hp = P1.maxHp
                # Spieler wird wieder grün
                P1.surf.fill((0, 255, 0))
            # Geschwindigkeit wird erhöht
            elif chosenUpgrade == spdUp:
                P1.speed += 1
            # Anzahl der Schüsse wird erhöht
            elif chosenUpgrade == bltUp:
                P1.bullets += 1
            # Größe der Schüsse wird erhöht
            elif chosenUpgrade == bltSize:
                P1.bltSize += 1
            # Größe des Spielers wird verringert
            elif chosenUpgrade == sizeDown:
                P1.surf = pygame.transform.scale(P1.surf, (P1.surf.get_width() - 2, P1.surf.get_height() - 2))
            # Schüsse gehen durch einen weiteren Gegner
            elif chosenUpgrade == piercing:
                P1.piercing += 1
            elif chosenUpgrade == rangeUp:
                P1.range += (P1.range * 0.5)
            # Seltene Upgrades
            # Gegner explodieren in Schüsse
            elif chosenUpgrade == explosionsUp:
                explosions = True
            # wenn ein Upgrade ausgewählt wurde, wird der Upgradebildschirm beendet
            if chosenUpgrade != None:
                gameState = 0

    pygame.display.update()
    FramePerSec.tick(FPS)
