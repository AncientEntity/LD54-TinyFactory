import pygame
import time, random, threading, math

from itemgen import ItemGen
from spritesheet import *
from button import *

def LoadAssets():
    global assets, tileSize

    print("[Assets] Loading Assets Started")

    #Spritesheets
    assets["world"] = SpriteSheet("art\\tilset.png", tileSize)
    assets["items"] = SpriteSheet("art\\items.png", tileSize)
    assets["ritems"] = SpriteSheet("art\\ryanitems.png", 10)

    #Fonts
    assets["fpsFont"] = pygame.font.Font("art\\FreeSansBold.ttf",10)
    assets["moneyFont"] = pygame.font.Font("art\\PixeloidMono-d94EV.ttf",20)

    pygame.mixer.init()
    #Music
    assets["trackA"] = pygame.mixer.Sound("sound\\A Loop.wav")
    assets["trackB"] = pygame.mixer.Sound("sound\\B Loop.wav")
    assets["backMusic"] = pygame.mixer.Sound("sound\\backgroundmusic.wav")


    print("[Assets] Loading Assets Completed")

def GetValidPosition(worldRef):
    for i in range(200):
        xRand = random.randint(1, 14)
        yRand = random.randint(1, 14)

        #Block if input/output
        if(worldRef[xRand][yRand][0] == 0 and worldRef[xRand][yRand][1] == 3):
            continue
        if(worldRef[xRand][yRand][0] == 0 and worldRef[xRand][yRand][1] == 2):
            continue

        #Valid spot if it's an empty spot or a side wall
        if((worldRef[xRand][yRand][0] == 0 and worldRef[xRand][yRand][1] == 0)):
            return [xRand,yRand]
    return False

def ThreadSubsystemHandler():
    global items, running
    while running:

        #Music Handler
        if(musicChannel.get_sound() == None):
            musicChannel.set_volume(0.1)
            musicChannel.play(random.choice([assets["trackA"],assets["trackB"]]))


        #Handle Delayed Items
        for itemDelay in delayedItems: #timeStarted, delay, item
            if(time.time() - itemDelay[0] >= itemDelay[1]):
                items.append(itemDelay[2])
                delayedItems.remove(itemDelay)
        time.sleep(0.1)

def PlaceNewObjective():
    global levelCount
    targetItem = [random.randint(0,8),random.randint(0,1)]
    validIn = GetValidPosition(world)

    if(validIn == False):
        return False
    previous = world[validIn[0]][validIn[1]]
    world[validIn[0]][validIn[1]] = [0,3,targetItem]
    validOut = GetValidPosition(world)

    if(validOut == False):
        world[validIn[0]][validIn[1]] = previous
        return False

    generators.append(ItemGen(targetItem,[validOut[0] * 16,validOut[1] * 16]))
    print("[Generators] New generator with item: ",targetItem)
    levelCount += 1

    if(levelCount >= 5):
        global underExitButton, underEntranceButton
        underEntranceButton.originalIconSprite = assets["world"][[2, 0]]
        underExitButton.originalIconSprite = assets["world"][[3, 0]]
        underEntranceButton.ChangeScale(underEntranceButton.scale)
        underExitButton.ChangeScale(underExitButton.scale)

    return generators[len(generators)-1]

def HandleObjectives():
    global lastObjectivePlaced
    if(time.time() - lastObjectivePlaced >= 15):
        lastObjectivePlaced = time.time()
        result = PlaceNewObjective()
        if(result == False):
            print("Failed to spawn new objective, not enough space.")

def SetPlacementIdent(ident,minLevel):
    global placementIdent
    if(levelCount < minLevel):
        return
    placementIdent = ident

def Tick(deltaTime : int):
    global assets, world, placementIdent, money, items, running
    for event in pygame.event.get():
        if(event.type == pygame.QUIT):
            pygame.quit()
            running = False
            return

        if(event.type == pygame.KEYDOWN):
            if(event.key == pygame.K_r):
                global placementRotation
                placementRotation -= 90
                placementRotation = placementRotation % 360

            #TEMP FOR DEBUG SHOULD GET REMOVED BEFORE RELEASE :))))
            elif(event.key == pygame.K_1):
                SetPlacementIdent((1,0),0)
            elif (event.key == pygame.K_2):
                SetPlacementIdent((2,0),5)
            elif (event.key == pygame.K_3):
                SetPlacementIdent((3,0),5)

    mouseWorldPosition = pygame.mouse.get_pos()
    mouseTilePosition = (mouseWorldPosition[0] // 32, mouseWorldPosition[1] // 32)

    HandleObjectives()

    #Simulate Generators
    for gen in generators:
        result = gen.AttemptNewItem()
        if(result != False):
            items.append(result)

    #Simulate Items
    for item in items[:]:
        if(item.active == False):
            continue
        itemTilePosition = item.GetTilePosition()
        onBlockType = item.GetOnBlockType(world)

        #Handle input
        if(onBlockType[0] == 0 and onBlockType[1] == 3):
            items.remove(item)
            item.active = False
            if(onBlockType[2] == item.spriteIdent):
                money += 1

        #Handle underground belts, if on entrance
        if(onBlockType[0] == 2 and onBlockType[1] == 0):
            # Try to locate underground exit based on entrance rotation
            rot = world[itemTilePosition[0]][itemTilePosition[1]][2]
            lookDirection = [0,0]
            if(rot == 0): #Move right
                lookDirection = [1,0]
            elif(rot == 180): #Move left
                lookDirection = [-1, 0]
            elif(rot == 270): #Move down
                lookDirection = [0, 1]
            elif(rot == 90): #Move up
                lookDirection = [0, -1]
            curPos = list(itemTilePosition[:]) #Convert from tuple
            for i in range(3): #Max underground of 3
                curPos[0] += lookDirection[0]
                curPos[1] += lookDirection[1]
                curBlock = world[curPos[0]][curPos[1]]
                if(curBlock[0] == 3 and curBlock[1] == 0 and curBlock[2] == world[itemTilePosition[0]][itemTilePosition[1]][2]): #If exit and same rotation as entrance
                    #FOUND EXIT
                    item.position = [curPos[0]*16,curPos[1]*16]
                    items.remove(item)
                    delayedItems.append([time.time(),(i+1)*0.5,item])
                    #asyncio.run(AsyncItemAdd(item,i+1))

                    #asyncLoop = asyncio.get_event_loop()
                    #asyncLoop.run_until_complete(AsyncItemAdd(item,i+1))

                    break



        #Handle conveyor movement
        if((onBlockType[0] == 1 and onBlockType[1] == 0) or (onBlockType[0] == 3 and onBlockType[1] == 0)): #if conveyor or underground exit
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
    for x in range(len(world)):
        for y in range(len(world[0])):
            screen.blit(assets["world"][world[0][0]],(x*tileSize,y*tileSize))
            if(x != 0 and y != 0):
                tileSprite = None
                if(type(world[x][y][2]) == int or type(world[x][y][2]) == float):
                    tileSprite = pygame.transform.rotate(assets["world"][world[x][y]],world[x][y][2])
                else:
                    tileSprite = assets["world"][world[x][y]]
                screen.blit(tileSprite,(x*tileSize,y*tileSize))

                #Handle preview of the item certain things want
                if(world[x][y][0] == 0 and world[x][y][1] == 3):
                    preview: pygame.Surface = assets["ritems"][world[x][y][2]].copy()
                    preview.convert_alpha()
                    preview.set_alpha(150)
                    screen.blit(preview, (x * tileSize + 3, y * tileSize + 3))

            if(world[x][y] != (0,1,0) and (world[x][y][0] != 0 or world[x][y][1] != 3) and mouseTilePosition[0] == x and mouseTilePosition[1] == y):
                if(pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]):

                    screen.blit(assets["world"][(2,1)],(x*tileSize,y*tileSize))
                    if(pygame.mouse.get_pressed()[0]):
                        if(world[x][y][0] != placementIdent[0] or world[x][y][1] != placementIdent[1]):
                            #Placing underground belt entrance
                            if(placementIdent[0] == 2 and placementIdent[1] == 0):
                                if(money < 10):
                                    continue
                                money -= 5
                            #Placing underground belt exit
                            elif(placementIdent[0] == 3 and placementIdent[1] == 0):
                                if(money < 10):
                                    continue
                                money -= 5
                            else:
                                if(money < 5):
                                    continue

                            world[x][y] = (placementIdent[0],placementIdent[1],placementRotation)
                            money -= 5

                    elif(world[x][y] != (0,0,0)):
                        world[x][y] = (0,0,0)
                        money += 5
                else:
                    preview : pygame.Surface = assets["world"][placementIdent].copy()
                    preview.convert_alpha()
                    preview.set_alpha(80)
                    preview = pygame.transform.rotate(preview,placementRotation)
                    screen.blit(preview,(x*tileSize,y*tileSize))

    #Placing undergrounds, so do the underground preview
    if((placementIdent[0] == 2 or placementIdent[0] == 3) and placementIdent[1] == 0):
        for x in range(len(world)):
            for y in range(len(world[0])):
                # Handle 'underground' preview if placing underground belt
                if (world[x][y][1] == 0 and (world[x][y][0] == 2)):
                    rot = world[x][y][2]
                    lookDirection = [0, 0]
                    if (rot == 0):  # Move right
                        lookDirection = [1, 0]
                    elif (rot == 180):  # Move left
                        lookDirection = [-1, 0]
                    elif (rot == 270):  # Move down
                        lookDirection = [0, 1]
                    elif (rot == 90):  # Move up
                        lookDirection = [0, -1]
                    curPos = [x, y]  # Convert from tuple
                    for i in range(3):  # Max underground of 3
                        curPos[0] += lookDirection[0]
                        curPos[1] += lookDirection[1]
                        rotatedPreview = pygame.transform.rotate(assets["world"][[1, 1]],rot)
                        screen.blit(rotatedPreview, (curPos[0] * tileSize, curPos[1] * tileSize))


    #Render Generators
    for gen in generators:
        screen.blit(assets["world"][0,2], gen.position)

    #Render Items
    for item in items:
        screen.blit(assets["ritems"][item.spriteIdent], (item.position[0] + 3,item.position[1] + 3))


    #ENGINE RENDERING FINISH

    window.blit(pygame.transform.scale(screen,(512,544)),(0,0))
    #pygame.draw.arc(window,(255,0,0),pygame.Rect(450,10,20,20),0,math.pi)

    #FPS Counter
    #if(trueDelta != 0):
    #    fpsText = assets["fpsFont"].render("FPS: "+str(int(1.0 / trueDelta)),False,(250,250,250))
    #    window.blit(fpsText,(100,3))

    moneyText = assets["moneyFont"].render("$" + str(money), False, (250, 250, 250))
    window.blit(moneyText,(40,5))
    currentLevelText = assets["moneyFont"].render("Level: " + str(levelCount), False, (250, 250, 250))
    untilNextObjectiveText = assets["moneyFont"].render("Next Level: " + str(int(15 - (time.time() - lastObjectivePlaced))) + "s", False, (250, 250, 250))
    window.blit(currentLevelText,(130,5))
    window.blit(untilNextObjectiveText,(280,5))

    #Select Buttons
    for button in buttons:
        clickResult = button.Tick()
        if(clickResult == True):
            button.ChangeScale([45,45])
        else:
            button.ChangeScale([40,40])
        button.Render(window)
    #Current Placmeent Ident Preview
    currentPreview = pygame.transform.scale(assets["world"][placementIdent],[32,32])
    currentPreview = pygame.transform.rotate(currentPreview, placementRotation)
    window.blit(currentPreview,(448,490))


    pygame.display.update(pygame.Rect(0,0,640,640))

#Engine Setup
pygame.init()

tileSize = 16
assets = {}
LoadAssets()

#Game Setup

placementRotation = 0
placementIdent = (1,0)

window = pygame.display.set_mode((512,544))
pygame.display.set_caption("Tiny Factory - LD54 - AncientEntity")
pygame.display.set_icon(assets["world"][(1,0)])
screen = pygame.Surface((256,272))
world = []
items = []
delayedItems = []
generators = []

#Initialize buttons
buttons = []

conveyorButton = Button(assets["world"][[1,3]],assets["world"][[1,0]],[32,490])
conveyorButton.onClick.append(lambda : SetPlacementIdent((1,0),0))
buttons.append(conveyorButton)
underEntranceButton = Button(assets["world"][[1,3]],assets["world"][[0,0]],[77,490])
underEntranceButton.onClick.append(lambda : SetPlacementIdent((2,0),5))
buttons.append(underEntranceButton)
underExitButton = Button(assets["world"][[1,3]],assets["world"][[0,0]],[122,490])
underExitButton.onClick.append(lambda : SetPlacementIdent((3,0),5))
buttons.append(underExitButton)




money = 160
for x in range(16):
    r = []
    for y in range(18):
        if(x == 0 or x == 15 or y == 0 or y >= 15):
            r.append((0,1,0))
        else:
            r.append((0,0,0))
    world.append(r)

running = True
lastFrameTime = time.time()
trueDelta = 0

lastObjectivePlaced = 0
levelCount = 0

musicChannel = pygame.mixer.Channel(1)

subsystemThread = threading.Thread(target=ThreadSubsystemHandler)
subsystemThread.start()

while running:
    delta = time.time() - lastFrameTime
    lastFrameTime = time.time()

    trueDelta = delta
    if(delta >= 1.0 / 30.0): #We clamp delta time to prevent issues with things going too far. Not the best solution but for this project it'll do the trick!
        delta = 1.0 / 30.0

    Tick(delta)

print("[Engine] Loop has ended. Engine/Game shutting down.")