import pygame
import time
from spritesheet import *

def LoadAssets():
    global assets, tileSize

    assets["world"] = SpriteSheet("art\\tilset.png", tileSize)

def Tick(deltaTime : int):
    global assets, world
    for event in pygame.event.get():
        if(event.type == pygame.KEYDOWN):
            if(event.key == pygame.K_r):
                global placementRotation
                placementRotation += 90

    mouseWorldPosition = pygame.mouse.get_pos()
    mouseTilePosition = (mouseWorldPosition[0] // 32, mouseWorldPosition[1] // 32)

    #Build World
    for x in range(16):
        for y in range(16):
            screen.blit(assets["world"][world[0][0]],(x*tileSize,y*tileSize))
            if(x != 0 and y != 0):
                tileSprite = pygame.transform.rotate(assets["world"][world[x][y]],world[x][y][2])
                screen.blit(tileSprite,(x*tileSize,y*tileSize))
            if(world[x][y] != (0,1,0) and mouseTilePosition[0] == x and mouseTilePosition[1] == y):
                if(pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]):
                    screen.blit(assets["world"][(2,1)],(x*tileSize,y*tileSize))
                    if(pygame.mouse.get_pressed()[0]):
                        world[x][y] = (1,0,placementRotation)
                    else:
                        world[x][y] = (0,0,0)
                else:
                    screen.blit(assets["world"][(1,1)],(x*tileSize,y*tileSize))


    window.blit(pygame.transform.scale(screen,(512,512)),(0,0))
    pygame.display.update(pygame.Rect(0,0,640,640))

#Engine Setup

tileSize = 16
assets = {}
LoadAssets()

#Game Setup

placementRotation = 0

window = pygame.display.set_mode((512,512))
pygame.display.set_caption("LudumDare54 - AncientEntity")
pygame.display.set_icon(assets["world"][(1,0)])
screen = pygame.Surface((256,256))
world = []
for x in range(16):
    r = []
    for y in range(16):
        if(x == 0 or x == 15 or y == 0 or y == 15):
            r.append((0,1,0))
        else:
            r.append((0,0,0))
    world.append(r)

running = True
lastFrameTime = time.time()


while running:
    delta = time.time() - lastFrameTime
    lastFrameTime = time.time()

    Tick(delta)