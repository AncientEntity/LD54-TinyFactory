import pygame
import time, random, threading, math, pickle

from os import path, mkdir
from sys import platform
from itemgen import ItemGen
from spritesheet import *
from button import *


DEBUGGAME = False

def LoadAssets():
    global assets, tileSize, displayScaleFactor

    print("[Assets] Loading Assets Started")

    #Spritesheets
    assets["world"] = SpriteSheet("art\\tilset.png", tileSize)
    assets["items"] = SpriteSheet("art\\items.png", tileSize)
    assets["ritems"] = SpriteSheet("art\\ryanitems.png", 10)

    #Fonts
    assets["fpsFont"] = pygame.font.Font("art\\PixeloidMono-d94EV.ttf",int(10*displayScaleFactor))
    assets["moneyFont"] = pygame.font.Font("art\\PixeloidMono-d94EV.ttf",int(20*displayScaleFactor))
    assets["titleFont"] = pygame.font.Font("art\\PixeloidMono-d94EV.ttf",int(40*displayScaleFactor))
    assets["descFont"] = pygame.font.Font("art\\PixeloidMono-d94EV.ttf",int(30*displayScaleFactor))
    assets["infoFont"] = pygame.font.Font("art\\PixeloidMono-d94EV.ttf",int(15*displayScaleFactor))

    pygame.mixer.init()
    #Music
    assets["trackA"] = pygame.mixer.Sound("sound\\A Loop.wav")
    assets["trackB"] = pygame.mixer.Sound("sound\\B Loop.wav")
    assets["backMusic"] = pygame.mixer.Sound("sound\\backgroundmusic.wav")

    #SFX
    assets["place"] = pygame.mixer.Sound("sound\\place.wav")
    assets["place"].set_volume(0.15)
    assets["notificationsound"] = pygame.mixer.Sound("sound\\notificationsound.wav")
    assets["notificationsound"].set_volume(0.15)
    assets["loss"] = pygame.mixer.Sound("sound\\loss.wav")
    assets["loss"].set_volume(0.15)


    print("[Assets] Loading Assets Completed")

def LoadMainMenuWorld():
    global world, items, generators
    world = pickle.load(open("data/mainmenuworld.dat", "rb"))
    items = pickle.load(open("data/mainmenuitems.dat", "rb"))
    generators = pickle.load(open("data/mainmenugenerators.dat", "rb"))

def CreateNewNotification(text):
    newTextRender = assets["infoFont"].render(text, False, (250, 250, 250))
    newTextRender.convert_alpha()
    notifications.append((newTextRender,time.time()))
    assets["notificationsound"].play()

def TriggerLoss(reason):
    global isInMenu, menuType, items, generators, lossReason, delayedItems
    isInMenu = True
    menuType = MENU_LOST
    for gen in generators:
        gen.infinite = False
        gen.amount = -1
    items = []
    lossReason = reason
    delayedItems = []
    assets["loss"].play()

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
            musicChannel.set_volume(0.05)
            musicChannel.play(random.choice([assets["trackA"],assets["trackB"]]))


        #Handle Delayed Items
        for itemDelay in delayedItems: #timeStarted, delay, item
            if(time.time() - itemDelay[0] >= itemDelay[1]):
                items.append(itemDelay[2])
                delayedItems.remove(itemDelay)

        time.sleep(0.1)

def PlaceNewObjective():
    global levelCount
    global underExitButton, underEntranceButton
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
    if(levelCount > 1):
        CreateNewNotification("Level "+str(levelCount-1)+ " Completed!")

    if(levelCount == 3):
        underEntranceButton.originalIconSprite = assets["world"][[2, 0]]
        underExitButton.originalIconSprite = assets["world"][[3, 0]]
        underEntranceButton.ChangeScale(underEntranceButton.scale)
        underExitButton.ChangeScale(underExitButton.scale)
        CreateNewNotification("Underground Belts Unlocked!")
    elif(levelCount < 3):
        underEntranceButton.originalIconSprite = assets["world"][[0, 0]]
        underExitButton.originalIconSprite = assets["world"][[0, 0]]
        underEntranceButton.ChangeScale(underEntranceButton.scale)
        underExitButton.ChangeScale(underExitButton.scale)

    return generators[len(generators)-1]

def HandleObjectives():
    global lastObjectivePlaced
    if(time.time() - lastObjectivePlaced >= 15 and isInMenu == False):
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
    global assets, world, placementIdent, money, items, running, generators, isInMenu
    global lastCriticalOvertimeNotification, lastWarningOvertimeNotification, lastGeneratorBackedUpNotification
    global menuType, lossReason

    #Input Processing
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
                SetPlacementIdent((2,0),3)
            elif (event.key == pygame.K_3):
                SetPlacementIdent((3,0),3)
            elif(DEBUGGAME and event.key == pygame.K_F7):
                print("[Debug] Saving New Main Menu")
                if(path.exists("data") == False):
                    mkdir("data")
                pickle.dump(world,open("data/mainmenuworld.dat","wb"))
                pickle.dump(items,open("data/mainmenuitems.dat","wb"))
                pickle.dump(generators,open("data/mainmenugenerators.dat","wb"))
            elif(DEBUGGAME and event.key == pygame.K_F8):
                world = pickle.load(open("data/mainmenuworld.dat","rb"))
                items = pickle.load(open("data/mainmenuitems.dat","rb"))
                generators = pickle.load(open("data/mainmenugenerators.dat","rb"))
            elif(isInMenu and event.key == pygame.K_SPACE):
                if(menuType == MENU_MAIN):
                    isInMenu = False
                    ResetLevel()
                elif(menuType == MENU_LOST):
                    menuType = MENU_MAIN
            elif(DEBUGGAME and event.key == pygame.K_F5):
                CreateNewNotification("Test Notification: "+str(random.randint(1000,9999)))
            elif(DEBUGGAME and event.key == pygame.K_F2):
                TriggerLoss("DEBUG LOSS MESSAGE.")

    mouseWorldPosition = pygame.mouse.get_pos()
    mouseTilePosition = [int(mouseWorldPosition[0] // (32*displayScaleFactor)),int(mouseWorldPosition[1] // (32*displayScaleFactor))]
    if(mouseTilePosition[0] < 0):
        mouseTilePosition[0] = 0
    elif(mouseTilePosition[0] >= len(world)):
        mouseTilePosition[0] = len(world)-1
    if(mouseTilePosition[1] < 0):
        mouseTilePosition[1] = 0
    elif(mouseTilePosition[1] >= len(world[0])):
        mouseTilePosition[1] = len(world[0])-1

    mousedOverBlock = world[mouseTilePosition[0]][mouseTilePosition[1]]

    HandleObjectives()

    #Simulate Generators
    for gen in generators:
        result = gen.AttemptNewItem()
        if(result != False):
            items.append(result)
        #Check if generator is backed up
        if(isInMenu == False and levelCount >= 2 and time.time() - gen.lastCreationTime >= 10 and time.time() - lastGeneratorBackedUpNotification >= 5):
            if(time.time() - gen.lastCreationTime <= 15):
                CreateNewNotification("Warning: Generator Backed Up")
            elif(time.time() - gen.lastCreationTime < 20):
                CreateNewNotification("Critical: Generator Backed Up")
            elif(time.time() - gen.lastCreationTime >= 20):
                TriggerLoss("Backed up generator.")
            lastGeneratorBackedUpNotification = time.time()


    overtimeItems = 0.0
    #Simulate Items
    for item in items[:]:
        if(item.active == False):
            continue
        itemTilePosition = item.GetTilePosition()
        onBlockType = item.GetOnBlockType(world)

        if(isInMenu == False and time.time() - item.startTime >= 15):
            overtimeItems += 1

        #Handle input
        if(onBlockType[0] == 0 and onBlockType[1] == 3):
            items.remove(item)
            item.active = False
            if(onBlockType[2] == item.spriteIdent):
                money += 1
            else:
                money -= 2
                CreateNewNotification("Warning: Item entering wrong generator")

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

    #Handle overtime warnings/losing
    if(isInMenu == False and len(items) > 0):
        overtimeItemPercentage = overtimeItems / len(items)
        if(levelCount >= 3 and len(items) >= 15): #if above level 3, start doing overtiming. (and a min of 5 items)
            if(overtimeItemPercentage >= 0.30):
                TriggerLoss("items in overtime.")
            elif(overtimeItemPercentage >= 0.25 and time.time() - lastCriticalOvertimeNotification >= 5):
                CreateNewNotification("CRITICAL: 35% of items are overtiming!")
                lastCriticalOvertimeNotification = time.time()
            elif(overtimeItemPercentage >= 0.2 and overtimeItemPercentage < 0.35 and time.time() - lastWarningOvertimeNotification >= 5):
                CreateNewNotification("WARNING: 20% of items are overtiming!")
                lastWarningOvertimeNotification = time.time()


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

            if(isInMenu == False and world[x][y] != (0,1,0) and (world[x][y][0] != 0 or world[x][y][1] != 3) and mouseTilePosition[0] == x and mouseTilePosition[1] == y):
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
                            assets["place"].play()

                    elif(world[x][y] != (0,0,0)):
                        world[x][y] = (0,0,0)
                        money += 5
                        assets["place"].play()
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

    #If placing conveyors have helpful directional arrow appear
    if (isInMenu == False and placementIdent[0] == 1 and placementIdent[1] == 0 and (mousedOverBlock[0] != 0 or mousedOverBlock[1] != 1)):
        rot = placementRotation
        lookDirection = [0, 0]
        if (rot == 0):  # Move right
            lookDirection = [1, 0]
        elif (rot == 180):  # Move left
            lookDirection = [-1, 0]
        elif (rot == 270):  # Move down
            lookDirection = [0, 1]
        elif (rot == 90):  # Move up
            lookDirection = [0, -1]
        curPos = [mouseTilePosition[0],mouseTilePosition[1]]  # Convert from tuple
        curPos[0] += lookDirection[0] * 0.5
        curPos[1] += lookDirection[1] * 0.5

        rotatedPreview = pygame.transform.rotate(assets["world"][[2, 3]],rot)
        screen.blit(rotatedPreview, (curPos[0] * tileSize, curPos[1] * tileSize))

    #Render Generators
    for gen in generators:
        screen.blit(assets["world"][0,2], gen.position)

    #Render Items
    for item in items:
        screen.blit(assets["ritems"][item.spriteIdent], (item.position[0] + 3,item.position[1] + 3))


    #ENGINE RENDERING FINISH

    screenUIPass.blit(pygame.transform.scale(screen,(512 * displayScaleFactor,544 * displayScaleFactor)),(0,0))
    #pygame.draw.arc(window,(255,0,0),pygame.Rect(450,10,20,20),0,math.pi)

    #FPS Counter
    #if(trueDelta != 0):
    #    fpsText = assets["fpsFont"].render("FPS: "+str(int(1.0 / trueDelta)),False,(250,250,250))
    #    window.blit(fpsText,(100,3))

    if(isInMenu == False):
        moneyText = assets["moneyFont"].render("$" + str(money), False, (250, 250, 250))
        screenUIPass.blit(moneyText,(40*displayScaleFactor,5*displayScaleFactor))
        currentLevelText = assets["moneyFont"].render("Level: " + str(levelCount), False, (250, 250, 250))
        untilNextObjectiveText = assets["moneyFont"].render("Next Level: " + str(int(15 - (time.time() - lastObjectivePlaced))) + "s", False, (250, 250, 250))
        screenUIPass.blit(currentLevelText,(130*displayScaleFactor,5*displayScaleFactor))
        screenUIPass.blit(untilNextObjectiveText,(280*displayScaleFactor,5*displayScaleFactor))
        #Select Buttons
        for button in buttons:
            clickResult = button.Tick()
            if(clickResult == True):
                button.ChangeScale([45*displayScaleFactor,45*displayScaleFactor])
            else:
                button.ChangeScale([40*displayScaleFactor,40*displayScaleFactor])
            button.Render(screenUIPass)
        #Current Placmeent Ident Preview
        currentPreview = pygame.transform.scale(assets["world"][placementIdent],[32*displayScaleFactor,32*displayScaleFactor])
        currentPreview = pygame.transform.rotate(currentPreview, placementRotation)
        screenUIPass.blit(currentPreview,(448*displayScaleFactor,490*displayScaleFactor))

        #Notification Render
        notIndex = 0
        for notification in notifications[::-1]:
            render, startTime = notification
            if(time.time() - startTime <= 4):
                render.set_alpha(300 - 255 * ((time.time() - startTime) / 3.0))
                screenUIPass.blit(render,(35*displayScaleFactor,(460 - 30 * notIndex)*displayScaleFactor))
                notIndex += 1
            else:
                notifications.remove(notification)
    elif(menuType == MENU_MAIN): #Main Menu
        titleTextShadow = assets["titleFont"].render("Tiny Factory", False, (0, 0, 0))
        screenUIPass.blit(titleTextShadow,(103*displayScaleFactor,103*displayScaleFactor))
        titleText = assets["titleFont"].render("Tiny Factory", False, (255, 255, 255))
        screenUIPass.blit(titleText,(100*displayScaleFactor,100*displayScaleFactor))
        startTextShadow = assets["descFont"].render("Press Space to Start", False, (0, 0, 0))
        screenUIPass.blit(startTextShadow,(69*displayScaleFactor,203*displayScaleFactor))
        startText = assets["descFont"].render("Press Space to Start", False, (255, 255, 255))
        screenUIPass.blit(startText,(65*displayScaleFactor,200*displayScaleFactor))

        infoText = assets["infoFont"].render("A game by Ryan (AncientEntity) for Ludum Dare 54!", False, (255, 255, 255))
        screenUIPass.blit(infoText,(15*displayScaleFactor,500*displayScaleFactor))
    elif(menuType == MENU_LOST):
        titleTextShadow = assets["titleFont"].render("You Lost!", False, (0, 0, 0))
        screenUIPass.blit(titleTextShadow,(136*displayScaleFactor,103*displayScaleFactor))
        titleText = assets["titleFont"].render("You Lost!", False, (255, 255, 255))
        screenUIPass.blit(titleText,(133*displayScaleFactor,100*displayScaleFactor))
        startTextShadow = assets["descFont"].render("Press Space to Restart", False, (0, 0, 0))
        screenUIPass.blit(startTextShadow,(51*displayScaleFactor,203*displayScaleFactor))
        startText = assets["descFont"].render("Press Space to Restart", False, (255, 255, 255))
        screenUIPass.blit(startText,(48*displayScaleFactor,200*displayScaleFactor))
        currentLevelTextShadow = assets["moneyFont"].render("Level: " + str(levelCount), False, (0, 0, 0))
        screenUIPass.blit(currentLevelTextShadow,(93*displayScaleFactor,253*displayScaleFactor))
        currentLevelText = assets["moneyFont"].render("Level: " + str(levelCount), False, (250, 250, 250))
        screenUIPass.blit(currentLevelText,(90*displayScaleFactor,250*displayScaleFactor))
        finalMoneyTextShadow = assets["moneyFont"].render("Money: " + str(money), False, (0, 0, 0))
        screenUIPass.blit(finalMoneyTextShadow,(93*displayScaleFactor,283*displayScaleFactor))
        finalMoneyText = assets["moneyFont"].render("Money: " + str(money), False, (250, 250, 250))
        screenUIPass.blit(finalMoneyText,(90*displayScaleFactor,280*displayScaleFactor))

        lossReasonTextShadow = assets["moneyFont"].render("Reason: "+lossReason, False, (0,0,0))
        screenUIPass.blit(lossReasonTextShadow,(93*displayScaleFactor,313*displayScaleFactor))
        lossReasonText = assets["moneyFont"].render("Reason: "+lossReason, False, (250,250,250))
        screenUIPass.blit(lossReasonText,(90*displayScaleFactor,310*displayScaleFactor))


        infoText = assets["infoFont"].render("A game by Ryan (AncientEntity) for Ludum Dare 54!", False, (255, 255, 255))
        screenUIPass.blit(infoText,(15*displayScaleFactor,500*displayScaleFactor))

    window.blit(screenUIPass,(0,0))
    pygame.display.update(pygame.Rect(0,0,640 * displayScaleFactor,640 * displayScaleFactor))

#Engine Setup

OSPlatform = platform #From sys.platform
monitorSize = [1920,1080]
if(OSPlatform == "win32" or OSPlatform == "win64"):
    import ctypes
    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    monitorSize = [width,height]
displayScaleFactor = float(monitorSize[1]) / 1080.0
displayScaleFactor *= 1.25
print("[Engine] Monitor Scaling: "+str(displayScaleFactor)+"x dimensions: ",monitorSize)


pygame.init()

tileSize = 16
assets = {}
LoadAssets()

#Game Setup

placementRotation = 0
placementIdent = (1,0)

window = pygame.display.set_mode((512 * displayScaleFactor,544 * displayScaleFactor))
pygame.display.set_caption("Tiny Factory - LD54 - AncientEntity")
pygame.display.set_icon(assets["world"][(1,0)])
screen = pygame.Surface((256,272))
screenUIPass = pygame.Surface((512 * displayScaleFactor,544 * displayScaleFactor))
world = []
items = []
delayedItems = []
generators = []

#Initialize buttons
buttons = []

conveyorButton = Button(assets["world"][[1,3]],assets["world"][[1,0]],[32*displayScaleFactor,490*displayScaleFactor])
conveyorButton.onClick.append(lambda : SetPlacementIdent((1,0),0))
buttons.append(conveyorButton)
underEntranceButton = Button(assets["world"][[1,3]],assets["world"][[0,0]],[77*displayScaleFactor,490*displayScaleFactor])
underEntranceButton.onClick.append(lambda : SetPlacementIdent((2,0),3))
buttons.append(underEntranceButton)
underExitButton = Button(assets["world"][[1,3]],assets["world"][[0,0]],[122*displayScaleFactor,490*displayScaleFactor])
underExitButton.onClick.append(lambda : SetPlacementIdent((3,0),3))
buttons.append(underExitButton)

money = 160
def ResetLevel(mainMenu=False):
    global money,world, generators, delayedItems, items, levelCount, lastObjectivePlaced, lossReason
    money = 160
    generators = []
    delayedItems = []
    items = []
    levelCount = 0
    lastObjectivePlaced = 0
    world = []
    lossReason = ""
    for x in range(16):
        r = []
        for y in range(18):
            if(x == 0 or x == 15 or y == 0 or y >= 15):
                r.append((0,1,0))
            else:
                r.append((0,0,0))
        world.append(r)


MENU_MAIN = 0
MENU_LOST = 1

lossReason = ""
menuType = MENU_MAIN
isInMenu = True
LoadMainMenuWorld()
running = True
lastFrameTime = time.time()
trueDelta = 0

lastObjectivePlaced = 0
levelCount = 0

musicChannel = pygame.mixer.Channel(1)

lastWarningOvertimeNotification = 0
lastCriticalOvertimeNotification = 0
lastGeneratorBackedUpNotification = 0
notifications = []

subsystemThread = threading.Thread(target=ThreadSubsystemHandler)
subsystemThread.start()


def EngineLoop():
    while running:
        global lastFrameTime
        delta = time.time() - lastFrameTime
        lastFrameTime = time.time()

        trueDelta = delta
        if(delta >= 1.0 / 30.0): #We clamp delta time to prevent issues with things going too far. Not the best solution but for this project it'll do the trick!
            delta = 1.0 / 30.0

        Tick(delta)


if __name__ == "__main__":
    EngineLoop()
    print("[Engine] Loop has ended. Engine/Game shutting down.")
    pygame.mixer.quit()