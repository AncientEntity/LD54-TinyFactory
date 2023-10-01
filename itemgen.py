from item import *
import time

class ItemGen:
    def __init__(self,itemIdent,position, delay=1):
        self.itemIdent = itemIdent
        self.recentItem : Item = None
        self.position = position
        self.delay = delay
        self.lastMade = time.time()
    def GetTilePosition(self):
        return (round(self.position[0] / 16), round(self.position[1] / 16))

    def AttemptNewItem(self):
        if(time.time() - self.lastMade < self.delay):
            return False

        if(self.recentItem != None and self.recentItem.active):
            if(self.GetTilePosition() == self.recentItem.GetTilePosition()):
                return False
        self.recentItem = Item(self.itemIdent,self.position[:])
        self.lastMade = time.time()
        return self.recentItem
