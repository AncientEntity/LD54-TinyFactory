import pygame
import time
from spritesheet import *

def LoadAssets():
    global assets, tileSize

    assets["world"] = SpriteSheet("art\\tilset.png", tileSize)

def Tick(deltaTime : int):
    pygame.event.clear()

    pass

def Draw():
    global assets, world

    mouseWorldPosition = pygame.mouse.get_pos()
    mouseTilePosition = (mouseWorldPosition[0] // 32, mouseWorldPosition[1] // 32)

    #Build World
    for x in range(16):
        for y in range(16):
            tileSprite : pygame.Surface = None
            if(mouseTilePosition[0] == x and mouseTilePosition[1] == y):
                tileSprite = assets["world"][world[x][y]].copy()
                tileSprite.fill((100,100,100,50),None,pygame.BLEND_RGBA_MULT)
            else:
                tileSprite = assets["world"][world[x][y]]
            screen.blit(tileSprite,(x*tileSize,y*tileSize))

    window.blit(pygame.transform.scale(screen,(512,512)),(0,0))
    pygame.display.update(pygame.Rect(0,0,640,640))

tileSize = 16
assets = {}
LoadAssets()

window = pygame.display.set_mode((512,512))
pygame.display.set_caption("LudumDare54 - AncientEntity")
pygame.display.set_icon(assets["world"][(1,0)])
screen = pygame.Surface((256,256))
world = []
for x in range(16):
    r = []
    for y in range(16):
        if(x == 0 or x == 15 or y == 0 or y == 15):
            r.append((0,1))
        else:
            r.append((0,0))
    world.append(r)

running = True
lastFrameTime = time.time()


while running:
    delta = time.time() - lastFrameTime
    lastFrameTime = time.time()

    Tick(delta)
    Draw()

