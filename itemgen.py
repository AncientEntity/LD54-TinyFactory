from item import *
import time

class ItemGen:
    def __init__(self,itemIdent,position, delay=1):
        self.itemIdent = itemIdent
        self.recentItem : Item = None
        self.position = position
        self.delay = delay
        self.lastMade = 0
        self.infinite = True
        self.amount = 0
        self.lastCreationTime = time.time()
        self.startTime = time.time()
    def GetTilePosition(self):
        return (round(self.position[0] / 16), round(self.position[1] / 16))

    def AttemptNewItem(self):

        if(self.infinite == False and self.amount <= 0):
            return False

        if(time.time() - self.lastMade < self.delay):
            return False

        if(self.recentItem != None and self.recentItem.active):
            if(self.GetTilePosition() == self.recentItem.GetTilePosition()):
                return False

        self.recentItem = Item(self.itemIdent,self.position[:])
        self.lastMade = time.time()
        self.amount -= 1
        if(hasattr(self,"lastCreationTime")): #Main menu pickle doesn't have this variable.
            self.lastCreationTime = time.time()

        return self.recentItem
