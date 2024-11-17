import pygame as p 
p.init()
from random import randint as r 

screen = p.display.set_mode((800,400))

class backgroundStars(p.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.counter = 0
        pos = r(0,800) , r(0,400)
        side = r(4,8)
        self.image = p.Surface((side, side))
        p.draw.circle(self.image, 'white', (0,0), 2)
        self.rect = self.image.get_rect(center = pos)

    def count(self):
        self.counter += 1 


font = p.font.Font('Font/Pixel.ttf', 275)
title = font.render('SOLARIUS', False, (255,255,0))
titleRect = title.get_rect(center = (400,200))

backgroundStarsGroup = p.sprite.Group()

while True:
    for event in p.event.get():
        if event.type == p.QUIT:
            p.quit()
    screen.fill('black')   

    
    if len(backgroundStarsGroup) < 250:
        star = backgroundStars()
        backgroundStarsGroup.add(star) 
    backgroundStarsGroup.draw(screen)



    p.display.flip()
        
    