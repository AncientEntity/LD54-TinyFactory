import pygame
import time
from spritesheet import *
from item import *

def LoadAssets():
    global assets, tileSize

    print("[Assets] Loading Assets Started")

    #Spritesheets
    assets["world"] = SpriteSheet("art\\tilset.png", tileSize)
    assets["items"] = SpriteSheet("art\\items.png", tileSize)

    #Fonts
    assets["fpsFont"] = pygame.font.Font("art\\FreeSansBold.ttf",10)


    print("[Assets] Loading Assets Completed")

def Tick(deltaTime : int):
    global assets, world, placementIdent
    for event in pygame.event.get():
        if(event.type == pygame.KEYDOWN):
            if(event.key == pygame.K_r):
                global placementRotation
                placementRotation += 90
                placementRotation = placementRotation % 360

            #TEMP FOR DEBUG SHOULD GET REMOVED BEFORE RELEASE :))))
            elif(event.key == pygame.K_1):
                placementIdent = (1,0)
            elif(event.key == pygame.K_2):
                placementIdent = (2,0)

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

    #Render Items
    for item in items:
        screen.blit(assets["items"][item.spriteIdent], (item.position[0],item.position[1]))


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
items = [Item((0,0),[32,32]),Item((0,0),[64,32])]
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
trueDelta = 0

while running:
    delta = time.time() - lastFrameTime
    lastFrameTime = time.time()

    trueDelta = delta
    if(delta >= 1.0 / 30.0): #We clamp delta time to prevent issues with things going too far. Not the best solution but for this project it'll do the trick!
        delta = 1.0 / 30.0

    Tick(delta)