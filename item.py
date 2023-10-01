from time import time


class Item:
    def __init__(self,spriteIdent : tuple, position : list):
        self.position = position
        self.spriteIdent = spriteIdent
        self.active = True
        self.startTime = time()
    def GetTilePosition(self):
        return (round(self.position[0] / 16), round(self.position[1] / 16))

    def GetOnBlockType(self,worldRef):
        itemTilePosition = self.GetTilePosition()
        return worldRef[int(itemTilePosition[0])][int(itemTilePosition[1])]