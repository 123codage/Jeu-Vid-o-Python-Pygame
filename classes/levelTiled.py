import pygame
from .common import *
import time

class Level_2D:

    def __init__(self,name,
                        nbrTilesWidth,nbrTilesHeight,
                        tileWidth,tileHeight,
                        tilesGroup,
                        collidersFloor,
                        collidersGroup):
        self.name=name
        self.new = True
        self.nbrTilesWidth=nbrTilesWidth
        self.nbrTilesHeight=nbrTilesHeight
        self.tileWidth=tileWidth
        self.tileHeight=tileHeight
        self.tilesGroup=tilesGroup
        self.collidersFloor=collidersFloor
        self.collidersGroup=collidersGroup

    def draw(self,screen,camera_x=0,camera_y=0):
        index = 0
        for sprite in self.tilesGroup:
            screen.blit(sprite.image, (sprite.rect.x,sprite.rect.y))

        if DEBUG.active :
            for sprite in self.collidersGroup:
                screen.blit(sprite.image, (sprite.rect.x,sprite.rect.y))
            for sprite in self.collidersFloor:
                screen.blit(sprite.image, (sprite.rect.x,sprite.rect.y))

    def getSize(self):
        return (self.nbrTilesWidth*self.tileWidth,self.nbrTilesHeight*self.tileHeight)

    def collide(self,player,direction):
        player.moveCollider(direction)
        collides = pygame.sprite.spritecollide(player, self.collidersGroup, False) if self.collidersGroup else None
        return collides if collides and len(collides) > 0 else None

    def isChanged(self):
        new = self.new
        self.new = False
        return new
