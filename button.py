import pygame

class Button:
    def __init__(self, backSprite : pygame.Surface, iconSprite: pygame.Surface, position : list):
        self.position = position
        self.scale = [40,40]
        self.iconSizeOffset = 10

        self.originalBackSprite = backSprite
        self.originalIconSprite = iconSprite
        self.ChangeScale(self.scale)


        self.onClick = []

    def ChangeScale(self,newScale):
        self.scale = newScale
        self.backSprite = pygame.transform.scale(self.originalBackSprite,self.scale)
        self.iconSprite = pygame.transform.scale(self.originalIconSprite,[self.scale[0]-self.iconSizeOffset,self.scale[1]-self.iconSizeOffset])


    def Render(self,renderTarget : pygame.Surface):
        renderTarget.blit(self.backSprite, self.position)
        renderTarget.blit(self.iconSprite, [self.position[0]+(self.iconSizeOffset//2),self.position[1]+(self.iconSizeOffset//2)])

    def Tick(self):
        #On Click
        if(pygame.mouse.get_pressed()[0]):
            #Check if within bounds
            mousePos = pygame.mouse.get_pos()
            if(mousePos[0] >= self.position[0] and mousePos[0] <= self.position[0]+self.backSprite.get_width()):
                if (mousePos[1] >= self.position[1] and mousePos[1] <= self.position[1] + self.backSprite.get_height()):
                    for onClickEvent in self.onClick:
                        onClickEvent()
                    return True