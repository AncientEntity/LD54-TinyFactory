import pygame
import time
from spritesheet import *
from item import *

def LoadAssets():
    global assets, tileSize

    assets["world"] = SpriteSheet("art\\tilset.png", tileSize)
    assets["items"] = SpriteSheet("art\\items.png", tileSize)

def Tick(deltaTime : int):
    global assets, world
    for event in pygame.event.get():
        if(event.type == pygame.KEYDOWN):
            if(event.key == pygame.K_r):
                global placementRotation
                placementRotation += 90
                placementRotation = placementRotation % 360

    mouseWorldPosition = pygame.mouse.get_pos()
    mouseTilePosition = (mouseWorldPosition[0] // 32, mouseWorldPosition[1] // 32)

    #Simulate Items
    for item in items:
        itemTilePosition = (round(item.position[0] / 16), round(item.position[1] / 16))
        onBlockType = world[int(itemTilePosition[0])][int(itemTilePosition[1])]

        #Handle conveyor movement
        if(onBlockType[0] == 1 and onBlockType[1] == 0):
            #block it is on is conveyor.
            rot = onBlockType[2]
            moveSpeed = [0,0]
            targetX = False
            targetY = False

            #Configure rotation targets based on rotation of block
            if(rot == 0): #Move right
                moveSpeed[0] = 90
                targetY = True
            elif(rot == 180): #Move left
                moveSpeed[0] = -90
                targetY = True
            elif(rot == 270): #Move down
                moveSpeed[1] = 90
                targetX = True
            elif(rot == 90): #Move up
                moveSpeed[1] = -90
                targetX = True

            #Movement
            item.position[0] += moveSpeed[0] * deltaTime
            item.position[1] += moveSpeed[1] * deltaTime

            #Center on belt lerp
            if(targetY != -1):
                item.position[1] = item.position[1] - (8 * deltaTime) * (item.position[1] - itemTilePosition[1]*16)
            if(targetX != -1):
                item.position[0] = item.position[0] - (8 * deltaTime) * (item.position[0] - itemTilePosition[0]*16)

        #Clamp final positions within the world!
        if(item.position[0] < 0):
            item.position[0] = 0
        elif(item.position[0] > 498):
            item.position[0] = 498
        if(item.position[1] < 0):
            item.position[1] = 0
        elif(item.position[1] > 498):
            item.position[1] = 498


    #Render World
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

    #Render Items
    for item in items:
        screen.blit(assets["items"][item.spriteIdent], (item.position[0],item.position[1]))

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
items = [Item((0,0),[100,100])]
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

    if(delta >= 1.0 / 30.0): #We clamp delta time to prevent issues with things going too far. Not the best solution but for this project it'll do the trick!
        delta = 1.0 / 30.0

    Tick(delta)