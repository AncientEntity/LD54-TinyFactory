import pygame
import time, random

from itemgen import ItemGen
from spritesheet import *
from item import *

def LoadAssets():
    global assets, tileSize

    print("[Assets] Loading Assets Started")

    #Spritesheets
    assets["world"] = SpriteSheet("art\\tilset.png", tileSize)
    assets["items"] = SpriteSheet("art\\items.png", tileSize)
    assets["ritems"] = SpriteSheet("art\\ryanitems.png", 10)

    #Fonts
    assets["fpsFont"] = pygame.font.Font("art\\FreeSansBold.ttf",10)


    print("[Assets] Loading Assets Completed")

def Tick(deltaTime : int):
    global assets, world, placementIdent
    for event in pygame.event.get():
        if(event.type == pygame.KEYDOWN):
            if(event.key == pygame.K_r):
                global placementRotation
                placementRotation -= 90
                placementRotation = placementRotation % 360

            #TEMP FOR DEBUG SHOULD GET REMOVED BEFORE RELEASE :))))
            elif(event.key == pygame.K_1):
                placementIdent = (1,0)
            elif(event.key == pygame.K_2):
                placementIdent = (2,0)

    mouseWorldPosition = pygame.mouse.get_pos()
    mouseTilePosition = (mouseWorldPosition[0] // 32, mouseWorldPosition[1] // 32)

    #Simulate Generators
    for gen in generators:
        result = gen.AttemptNewItem()
        if(result != False):
            items.append(result)

    #Simulate Items
    for item in items[:]:
        itemTilePosition = item.GetTilePosition()
        onBlockType = item.GetOnBlockType(world)

        #Handle input
        if(onBlockType[0] == 0 and onBlockType[1] == 3):
            items.remove(item)
            item.active = False


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
            if(world[x][y] != (0,1,0) and world[x][y] != (0,3,0) and mouseTilePosition[0] == x and mouseTilePosition[1] == y):
                if(pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]):

                    #preview : pygame.Surface = assets["world"][(2,1)].copy()
                    #preview.set_alpha(100,32)
                    #screen.blit(preview,(x*tileSize,y*tileSize))
                    screen.blit(assets["world"][(2,1)],(x*tileSize,y*tileSize))
                    if(pygame.mouse.get_pressed()[0]):
                        world[x][y] = (placementIdent[0],placementIdent[1],placementRotation)
                    else:
                        world[x][y] = (0,0,0)
                else:
                    preview : pygame.Surface = assets["world"][placementIdent].copy()
                    preview.convert_alpha()
                    preview.set_alpha(80)
                    preview = pygame.transform.rotate(preview,placementRotation)
                    screen.blit(preview,(x*tileSize,y*tileSize))

    #Render Generators
    for gen in generators:
        screen.blit(assets["world"][0,2], gen.position)

    #Render Items
    for item in items:
        screen.blit(assets["ritems"][item.spriteIdent], (item.position[0] + 2.5,item.position[1] + 2.5))


    #ENGINE RENDERING FINISH

    window.blit(pygame.transform.scale(screen,(512,512)),(0,0))

    #FPS Counter
    if(trueDelta != 0):
        fpsText = assets["fpsFont"].render("FPS: "+str(int(1.0 / trueDelta)),False,(250,250,250))
        window.blit(fpsText,(3,3))

    pygame.display.update(pygame.Rect(0,0,640,640))

#Engine Setup
pygame.init()

tileSize = 16
assets = {}
LoadAssets()

#Game Setup

placementRotation = 0
placementIdent = (1,0)

window = pygame.display.set_mode((512,512))
pygame.display.set_caption("LudumDare54 - AncientEntity")
pygame.display.set_icon(assets["world"][(1,0)])
screen = pygame.Surface((256,256))
world = []
items = []
generators = []
for x in range(16):
    r = []
    for y in range(16):
        if(x == 0 or x == 15 or y == 0 or y == 15):
            r.append((0,1,0))
        else:
            chance = random.randint(0,100)
            if(chance <= 90):
                r.append((0, 0, 0))
            elif(chance <= 95):
                r.append((0, 3, 0))
            else:
                r.append((0, 0, 0))
                generators.append(ItemGen((random.randint(0,9),random.randint(0,1)),[x*16,y*16]))
    world.append(r)

running = True
lastFrameTime = time.time()
trueDelta = 0

while running:
    delta = time.time() - lastFrameTime
    lastFrameTime = time.time()

    trueDelta = delta
    if(delta >= 1.0 / 30.0): #We clamp delta time to prevent issues with things going too far. Not the best solution but for this project it'll do the trick!
        delta = 1.0 / 30.0

    Tick(delta)