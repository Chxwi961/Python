import pygame as pyg 
pyg.init()
from sys import exit 
from random import randint as r
import math
import random

# Screen 
WIDTH = 800
HEIGHT = 400
screen = pyg.display.set_mode((WIDTH,HEIGHT))
pyg.display.set_caption('SOLARIUS')
# Frames
clock = pyg.time.Clock()
FPS = 60

# Classes 
class buttons(pyg.sprite.Sprite):
    def __init__(self, colour, w, L, x, y):
        super().__init__()
        if self not in buttonsGroup:
            buttonsGroup.add(self)
        self.colour = colour
        self.x = x 
        self.y = y
        self.w = w
        self.L = L
        self.rect = pyg.Rect(x, y, w, L)
    def draw(self, place):
        pyg.draw.rect(place, self.colour, self.rect)  

class ChoiceButton:
    def __init__(self, width, height, x, y, number_of, spacing):
        self.colour = (192,192,192)
        self.hover_colour = (128,128,128)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.number_of = number_of
        self.spacing = spacing
        self.rects = []  
        for i in range(self.number_of):
            rect = pyg.Rect(self.x, self.y + i * self.spacing, self.width, self.height)
            self.rects.append(rect)

    def draw(self, surface, mouse_pos):
        for rect in self.rects:
            if rect.collidepoint(mouse_pos):
                pyg.draw.rect(surface, self.hover_colour, rect)
            else:
                pyg.draw.rect(surface, self.colour, rect)


class backgroundStars(pyg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.counter = 0
        pos = r(0,WIDTH) , r(0,HEIGHT)
        side = r(4,8)
        self.image = pyg.Surface((side, side))
        pyg.draw.circle(self.image, 'white', (0,0), 1)
        self.rect = self.image.get_rect(center = pos)

    def count(self):
        self.counter += 1 

class stars(pyg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        pos = (r(WIDTH, 900) , r(1, HEIGHT))
        self.image = pyg.Surface((20,20), pyg.SRCALPHA)
        pyg.draw.circle(self.image, 'White', (10,10), r(2,7))
        self.rect = self.image.get_rect(center = pos)      
        self.velocity = r(1,8)
    def move(self):
        self.rect.x -= self.velocity
        if self.rect.x < -10:
            self.kill()

class Planet:
    AstroUnit = 150e6 * 1000 #in meters
    G = 6.67428e-11 #Grav constant
    SCALE = 125/AstroUnit #Default = 125 pixels = 1Au
    TIMESTEP = 3600 #1 hour
    def __init__(self, x, y, radius, color, mass):
        self.orbitvalue = 200 
        self.counter = 0 
        self.x = x 
        self.y = y 
        self.radius = radius
        self.color = color
        self.mass = mass 
        self.orbit = []
        self.Sun = False 
        self.dist_toSun = 0 
        self.originalx = x 
        self.orinialy = y
        self.is_comet = False
        self.x_vel = 0
        self.y_vel = 0
    def draw(self, win):
        global EarthyearBool
        global EarthYearCounter
        x = self.x * self.SCALE + 800/2 #Offsetting our planet positions from the center
        y = self.y * self.SCALE + 400/2
        updatedpoints = []
        if len(self.orbit) > 2:
            for point in self.orbit: 
                x , y = point 
                x = x* self.SCALE + 400
                y = y* self.SCALE + 200
                updatedpoints.append((x, y))
                # Script becomes so slow when listing such high amounts of points. So i guess im stuck with trails
            if self.is_comet:
                pyg.draw.lines(win, (255, 255, 255), False, updatedpoints, 2)
            else:
                pyg.draw.lines(win, self.color, False, updatedpoints, 2)
            if len(updatedpoints) > self.orbitvalue :
                updatedpoints.pop(0)
                self.orbit.pop(0)
            pyg.draw.lines(win, self.color, False, updatedpoints, 2)
        if self == Earth:
            EarthRect = pyg.Rect(x-self.radius, y-self.radius, self.radius*2, self.radius*2)
            if EarthRect.colliderect(EarthyearCheckRect):
                if EarthyearBool:
                    EarthYearCounter += 1 
                    # print(f'Your earth has been rotating for: {EarthYearCounter} years')
                    EarthyearBool = False
                    EarthyearCheckRect.center = (600,200)
                else:
                    EarthyearCheckRect.center = (200,200)
                    EarthyearBool = True

        pyg.draw.circle(win, self.color, (x, y), self.radius)
    def attraction(self, o):
        oX = o.x
        oY = o.y 
        dx = oX - self.x
        dy = oY - self.y
        d = math.sqrt(dx**2 + dy**2)

        if o.Sun:
            self.dist_toSun = d 
        force = 0
        if not self.Sun:
            force = self.G * self.mass * o.mass / (d**2 + 10)
        else:
            force = 0
        theta = math.atan2(dy , dx)
        Fx = force * math.cos(theta)
        Fy = force * math.sin(theta)
        return Fx, Fy
    def updatePos(self, planets):
        tfx = 0 
        tfy = 0 
        for planet in planets:
            if self == planet:
                continue
            fx, fy = self.attraction(planet)
            tfx += fx
            tfy += fy
        #Using the formula Vf = Vi + a(t), where a = tF/m 
        self.x_vel += tfx/self.mass * self.TIMESTEP
        self.y_vel += tfy/self.mass * self.TIMESTEP
        if self.Sun == True:
            self.y_vel = self.x_vel = 0 
        #Using the formula Xf = xi + vi(t) 
        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))
 
    def reset(self):
        self.x = self.originalx
        self.y = self.orinialy
        self.x_vel = 0
        if self == Earth:
            self.y_vel = 29.783 * 1000
        elif self == Mars:
            self.y_vel = 24.077 * 1000
        elif self == Mercury:
            self.y_vel = -47.4 * 1000
        elif self == Venus:
            self.y_vel = -35.02 * 1000
        elif self == Jupiter:
            self.y_vel = -13.05 * 1000
        elif self == Neptune:
            self.y_vel = -5.43 * 1000
        elif self == Uranus:
            self.y_vel = -6.67 * 1000
        elif self == Saturn:
            self.y_vel = -9.6725 * 1000
        elif self == Trappist1b:
            Trappist1b.y_vel = 80.1 * 1000
        elif self == Trappist1c:
            Trappist1c.y_vel = 69.5 * 1000
        elif self == Trappist1d:
            Trappist1d.y_vel = 54.6 * 1000
        elif self == Trappist1e:
            Trappist1e.y_vel = 44.6 * 1000
        elif self == Trappist1f:
            Trappist1f.y_vel = 42.1 * 1000
        elif self == Trappist1g:
            Trappist1g.y_vel = 35.1 * 1000
        elif self == Trappist1h:
            Trappist1h.y_vel = 33.7 * 1000
        elif self == Gaia:
            Gaia.y_vel = 15 * 1000
        elif self == Astraeus:
            Astraeus.y_vel = 18 * 1000
        elif self == Typhon:
            Typhon.y_vel = -23 * 1000
        elif self == Vesta:
            Vesta.y_vel = -13 * 1000
        elif self == Zephyra:
            Zephyra.y_vel = 14 * 1000
    

# Sprite groups 
buttonsGroup = pyg.sprite.Group()
starGroup = pyg.sprite.Group()
backgroundStarsGroup = pyg.sprite.Group()

# Fonts
smallFont = pyg.font.Font('Font/Pixel.ttf' , 25)
font = pyg.font.Font('Font/Pixel.ttf' , 45)
bigFont = pyg.font.Font('Font/Pixel.ttf' , 65)

# Game states
starterState = True
infoState = False
optionState = False 
galaxyState = False 
subgalaxy1 = False
subgalaxy2 = False 
subgalaxy3 = False
gameState = False
sunChoice = False
planetChoice = False  
peacefulState = False 
mediumState = False 
hardcoreState = False 
simulationPeaceful = False 

# Surfaces

    # Back Button
backButton = buttons((255,0,0), 150, 55, 10, 10)
backText = font.render('Back', False, 'White')
back = backText.get_rect(center = (85, .5*55+10))


    # StarterState
startButton = buttons((255,255,0), 200, 75, 575, 300)
startText = bigFont.render('Start' , False, 'Black') #didnt want to find my calculator
starterText = startText.get_rect(center = ((575+0.5*200),(300+0.5*75)))

infoButton = buttons((255,255,0), 150, 65, 50, 50)
infoText = font.render('Info', False, 'Black')
info = infoText.get_rect(center = (125, (0.5*65+50)))


galaxiesButton = buttons((225,225,0), 150, 65, 50, 175)
galaxiesText = font.render('Solars', False, 'Black')
galaxies = galaxiesText.get_rect(center = (125, (0.5*65+175)))

optionButton = buttons((225, 225, 0), 150, 65, 50, 300)
optionText = font.render('Options', False, 'Black')
options = optionText.get_rect(center = (125, (0.5*65+300)))

starterButtonslst = [startButton, infoButton, galaxiesButton, optionButton]

    # Info state
infoButtonlst = [backButton]

infoTitle = bigFont.render('INFORMATION' , False, 'White')
infoTitleRect = infoTitle.get_rect(center = (400,50))

infoBody = smallFont.render("You have the power to form SOLAR SYSTEMS." , False, 'White')
infoBodyRect = infoBody.get_rect(topleft = (30,100))
infoBody1 = smallFont.render("Add Planets, Stars, Black Holes, let your imagination run free!" , False, 'White')
infoBodyRect1 = infoBody1.get_rect(topleft = (30,130))
infoBody2 = smallFont.render("No inspiration? Don't know where to begin? Go take a quick look at our 'Solars' section.", False, 'White')
infoBodyRect2 = infoBody2.get_rect(topleft = (30,160))
infoBody3 = smallFont.render("Be as creative as you can be. You are now the most powerful being in the universe!", False, 'White')
infoBodyRect3 = infoBody3.get_rect(topleft = (30,190))
infoBody4 = smallFont.render(" -C and J 2024 ", False, 'White')
infoBodyRect4 = infoBody4.get_rect(topleft = (40,240))

tobeBlitted = [infoBody, infoBody1, infoBody2, infoBody3, infoBody4]
infoRects = [infoBodyRect, infoBodyRect1, infoBodyRect2, infoBodyRect3, infoBodyRect4]

moonImage = pyg.image.load('Images/Moon.png')
moonImage.set_alpha(125)
moonImageRect = moonImage.get_rect(center = (650,400))

    # Galaxy state
milkyWayButton = buttons((255,255,0), 450, 75, 175 ,75)
milkyWayText = bigFont.render('SOLAR   SYSTEM', False, (0,0,0))
milkyWayTextRect = milkyWayText.get_rect(center = (175 + 450/2 , 75 + 75/2))

myGalaxyButton = buttons((255,255,0), 450, 75, 175 , 175)
myGalaxyText = bigFont.render('TRAPPIST-1', False, (0,0,0))
myGalaxyTextRect = myGalaxyText.get_rect(center = (175 + 450/2 , 175 + 75/2))

AndromedaGalaxyButton = buttons((255,255,0), 450, 75, 175, 275)
AndromedaGalaxyText = bigFont.render('CHUDE', False, (0,0,0))
AndromedaGalaxyTextRect = AndromedaGalaxyText.get_rect(center = (175 + 450/2 , 275 + 75/2))

galaxyButtonlst = [backButton, milkyWayButton, myGalaxyButton, AndromedaGalaxyButton]

    # Sub galaxy state 1

# Buttons and stuff
speedUpButton = buttons((175,255,175), 45, 45, 675, 10)
speedUpButtonTextVariable = 'SPD'
slowDownButton = buttons((210,43,43), 45, 45, 725, 10)
slowDownButtonTextVariable = 'SLW'

Sun = Planet(0, 0, 25, (255,255,0), 1.989*10**30)
Sun.Sun = True 
Earth = Planet(-1*Planet.AstroUnit, 0, 14, (30,144,255), 5.9722e24)
Earth.y_vel = 29.783 * 1000
Mars = Planet(-1.5*Planet.AstroUnit, 0, 8, (136,8,8), 6.39e23)
Mars.y_vel = 24.077 * 1000
Mercury = Planet(0.387*Planet.AstroUnit, 0, 4, (105,105,105), 3.285e23)
Mercury.y_vel = -47.4 * 1000
Venus = Planet(0.723*Planet.AstroUnit, 0, 10, (204, 85, 0), 4.8685e24)
Venus.y_vel = -35.02 * 1000
Jupiter = Planet(5.2*Planet.AstroUnit, 0, 22, (255, 140, 100), 1.898e27)
Jupiter.y_vel = -13.05 * 1000
Saturn = Planet(9.538*Planet.AstroUnit, 0, 20, (225, 193, 110), 5.683e26)
Saturn.y_vel = -9.6725 * 1000
Uranus = Planet(19*Planet.AstroUnit, 0, 18, (8, 143, 143), 8.681e25)
Uranus.y_vel = -6.67 * 1000
Neptune = Planet(30*Planet.AstroUnit, 0, 16, (111, 143, 175), 1.024e26)
Neptune.y_vel = -5.43 * 1000

planets = [Sun, Earth, Mars, Mercury, Venus, Jupiter, Saturn, Uranus, Neptune]

EarthyearCheck = pyg.Surface((800/2, 1))

def resetGameStates():
    global starterState, infoState, optionState, galaxyState
    global subgalaxy1, subgalaxy2, subgalaxy3, gameState
    global sunChoice, planetChoice, peacefulState, mediumState
    global hardcoreState, simulationPeaceful

    starterState = True
    infoState = False
    optionState = False 
    galaxyState = False 
    subgalaxy1 = False
    subgalaxy2 = False 
    subgalaxy3 = False
    gameState = False
    sunChoice = False
    planetChoice = False
    peacefulState = False 
    mediumState = False 
    hardcoreState = False 
    simulationPeaceful = False
    if infoState:
        for button in infoButtonlst:
            if button.rect.collidepoint(mousePos):
                if button == backButton:
                    resetGameStates()

# EarthyearCheck.fill('red')
EarthyearBool = True
EarthyearCheckRect = EarthyearCheck.get_rect(center = (200,200))
EarthYearCounter = -1   
collideCheck = True
MilkyWayZoomFactor = 125 

#Information on planets clicky thingies 
EarthInformationBox = buttons((192,192,192), 55, 55, 722, 62.5)
MarsInformationBox = buttons((192,192,192), 55, 55, 722, 122.5)
VenusInformationBox = buttons((192,192,192), 55, 55, 722, 182.5)
MercuryInformationBox = buttons((192,192,192), 55, 55, 722, 242.5)
JupiterInformationBox = buttons((192,192,192), 55, 55, 722, 302.5)
SunInformationBox = buttons((192,192,192), 55, 55, 662, 62.5)
SaturnInformationBox = buttons((192,192,192), 55, 55, 662, 122.5)
UranusInformationBox = buttons((192,192,192), 55, 55, 662, 182.5)
NeptuneInformationBox = buttons((192,192,192), 55, 55, 662, 242.5)
HideInformationBox = buttons((169, 92, 104), 55, 55, 662, 302.5)

# text part of the information
initialInfoMilkyWayY = 100
MilkyWayInformationTextTitle = font.render('Information:', False, 'White')

# Earth
EarthInfo = smallFont.render('Name : Earth', False, 'White')
EarthInfo1 = smallFont.render('Mass : 5.972e24 kg', False, 'White')
EarthInfo2 = smallFont.render("Radius : 6'371 km ", False, 'White')
EarthInfo3 = smallFont.render('Distance fron the Sun: 1 AU', False, 'White')
EarthInfo4 = smallFont.render('Full Orbit time : ~365 Days', False, 'White')
EarthInfo5 = smallFont.render('Number of moons : 1', False, 'White')
EarthInfo6 = smallFont.render('Other info : You are living on it!', False, 'White')
EarthInfolst = [EarthInfo, EarthInfo1, EarthInfo2, EarthInfo3, EarthInfo4, EarthInfo5, EarthInfo6]

# Sun
SunInfo = smallFont.render('Name : Sun', False, 'White')
SunInfo1 = smallFont.render('Mass : 1.989e30 kg', False, 'White')
SunInfo2 = smallFont.render("Radius : 696'303 km", False, 'White')
SunInfo3 = smallFont.render("Average Surface temp : 5'600 Celsius", False, 'White')
SunInfo4 = smallFont.render("Average Center temp: 15'000'000 Celsius", False, 'White')
SunInfo5 = smallFont.render('Number of orbit Planets: 8', False, 'White')
SunInfo6 = smallFont.render('Other info : 4.5 billion years old!', False, 'White')
SunInfolst = [SunInfo,SunInfo1,SunInfo2,SunInfo3,SunInfo4,SunInfo5,SunInfo6]

# Mercury
MercInfo = smallFont.render("Name : Mercury", False, 'White')
MercInfo1 = smallFont.render("Mass : 3.285e23 kg ", False, 'White')
MercInfo2 = smallFont.render("Radius : 2'439 km", False, 'White')
MercInfo3 = smallFont.render("Distance from the Sun : 0.4 AU", False, 'White')
MercInfo4 = smallFont.render("Full Orbit time : ~88 Days ", False, 'White')
MercInfo5 = smallFont.render("Number of moons : None", False, 'White')
MercInfo6 = smallFont.render("Other info : Shrinks in size every year!", False, 'White')
MercInfolst = [MercInfo,MercInfo1,MercInfo2,MercInfo3,MercInfo4,MercInfo5,MercInfo6]

# Mars
MarsInfo = smallFont.render("Name : Mars", False, 'White')
MarsInfo1 = smallFont.render("Mass : 6.42e23 kg", False, 'White')
MarsInfo2 = smallFont.render("Radius : 3'389 km", False, 'White')
MarsInfo3 = smallFont.render("Distance from the Sun : 1.5 AU", False, 'White')
MarsInfo4 = smallFont.render("Full Orbit time : ~687 Days", False, 'White')
MarsInfo5 = smallFont.render("Number of moons : 2", False, 'White')
MarsInfo6 = smallFont.render("Other info : Surface temp is ~-80 Celcius!", False, 'White')
MarsInfolst = [MarsInfo,MarsInfo1,MarsInfo2,MarsInfo3,MarsInfo4,MarsInfo5,MarsInfo6]

# Venus
VenusInfo = smallFont.render("Name : Venus", False, 'White')
VenusInfo1 = smallFont.render("Mass : 4.867e24 kg", False, 'White')
VenusInfo2 = smallFont.render("Radius : 6'051 km", False, 'White')
VenusInfo3 = smallFont.render("Distance from the Sun : 0.72 AU", False, 'White')
VenusInfo4 = smallFont.render("Full Orbit time : ~255 Days", False, 'White')
VenusInfo5 = smallFont.render("Number of moons : None", False, 'White')
VenusInfo6 = smallFont.render("Other info : Only planet that orbits clockwise!", False, 'White')
VenusInfolst = [VenusInfo,VenusInfo1,VenusInfo2,VenusInfo3,VenusInfo4,VenusInfo5,VenusInfo6]


# Jupiter 
JupiterInfo = smallFont.render("Name : Jupiter", False, 'White')
JupiterInfo1 = smallFont.render("Mass : 1.898e27 kg", False, 'White')
JupiterInfo2 = smallFont.render("Radius : 69'911 km", False, 'White')
JupiterInfo3 = smallFont.render("Distance from the Sun: 5.2 AU", False, 'White')
JupiterInfo4 = smallFont.render("Full Orbit time: ~4'333 Days (11.8 years)", False, 'White')
JupiterInfo5 = smallFont.render("Number of moons : 95", False, 'White')
JupiterInfo6 = smallFont.render("Other info : Oldest planet in the solar system!", False, 'White')
ExtraJupiterInfo = smallFont.render("Note: Zoom out with your mouse to see it!", False, 'White')
JupiterInfolst = [JupiterInfo,JupiterInfo1,JupiterInfo2,JupiterInfo3,JupiterInfo4,JupiterInfo5,JupiterInfo6, ExtraJupiterInfo]


# Saturn
SaturnInfo = smallFont.render("Name : Saturn", False, 'White')
SaturnInfo1 = smallFont.render("Mass : 5.683e26 kg", False, 'White')
SaturnInfo2 = smallFont.render("Radius : 60'268 km", False, 'White')
SaturnInfo3 = smallFont.render("Distance from the Sun : 9.572 AU", False, 'White')
SaturnInfo4 = smallFont.render("Full Orbit time : ~10'756 Days (29.4 years)", False, 'White')
SaturnInfo5 = smallFont.render("Number of moons : 146", False, 'White')
SaturnInfo6 = smallFont.render("Other info: Has a moon bigger than Mercury!", False, 'White')
ExtraSaturnInfo = smallFont.render("Note: Zoom out with your mouse to see it!", False, 'White')
SaturnInfolst = [SaturnInfo,SaturnInfo1,SaturnInfo2,SaturnInfo3, SaturnInfo4, SaturnInfo5, SaturnInfo6, ExtraSaturnInfo]


# Uranus
UranusInfo = smallFont.render("Name : Uranus", False, 'White')
UranusInfo1 = smallFont.render("Mass : 8.681e25 kg", False, 'White')
UranusInfo2 = smallFont.render("Radius : 25'362 km", False, 'White')
UranusInfo3 = smallFont.render("Distance from the Sun : 19 AU", False, 'White')
UranusInfo4 = smallFont.render("Full Orbit time : ~30'687 Days (84 years)", False, 'White')
UranusInfo5 = smallFont.render("Number of moons : 28", False, 'White')
UranusInfo6 = smallFont.render("Other info : 63 Earths fit inside Uranus!", False, 'White')
ExtraUranusInfo = smallFont.render("Note : Too far away to display :(", False, 'White')
UranusInfolst = [UranusInfo,UranusInfo1,UranusInfo2,UranusInfo3,UranusInfo4,UranusInfo5,UranusInfo6, ExtraUranusInfo]


# Neptune
NeptuneInfo = smallFont.render("Name : Neptune", False, 'White')
NeptuneInfo1 = smallFont.render("Mass : 1.024e26 kg", False, 'White')
NeptuneInfo2 = smallFont.render("Radius : 24'622 km", False, 'White')
NeptuneInfo3 = smallFont.render("Distance from the Sun: 30.06 AU", False, 'White')
NeptuneInfo4 = smallFont.render("Full Orbit time : 60'190 Days (165 years)", False, 'White')
NeptuneInfo5 = smallFont.render("Number of moons : 16", False, 'White')
NeptuneInfo6 = smallFont.render("Other info : It's gravity is the closest to that of Earth!", False, 'White')
ExtraNeptuneInfo = smallFont.render("Note : Too far away to display :(", False, 'White')
NeptuneInfolst = [NeptuneInfo,NeptuneInfo1,NeptuneInfo2,NeptuneInfo3,NeptuneInfo4,NeptuneInfo5,NeptuneInfo6, ExtraNeptuneInfo]

#NeptuneInfo = smallFont.render("", False, 'White')
informationBoxeslst= [HideInformationBox, SaturnInformationBox, UranusInformationBox, NeptuneInformationBox, SunInformationBox, EarthInformationBox, MarsInformationBox, VenusInformationBox, MercuryInformationBox, JupiterInformationBox]
subgalaxy1buttonlst = [HideInformationBox, backButton, speedUpButton, slowDownButton, SaturnInformationBox, UranusInformationBox, NeptuneInformationBox, SunInformationBox, EarthInformationBox, MarsInformationBox, VenusInformationBox, MercuryInformationBox, JupiterInformationBox]

milkyWayDisplayDict = {
    'EarthInfoDisplay' : False, 
    'SunInfoDisplay' : False,
    'MercInfoDisplay' : False, 
    'MarsInfoDisplay' : False,
    'VenusInfoDisplay' : False, 
    'JupiterInfoDisplay' : False, 
    'SaturnInfoDisplay' : False,
    'UranusInfoDisplay' : False,
    'NeptuneInfoDisplay' : False,
    'Nothing' : False
}

def milkywayonlyonetrue(name):
    for key in milkyWayDisplayDict:
        milkyWayDisplayDict[key] = False 
    milkyWayDisplayDict[name] = True 

def traponlyonetrue(name):
    for key in t1DisplayDict:
        t1DisplayDict[key] = False 
    t1DisplayDict[name] = True 

def blitInfot1(current):
    screen.blit(MilkyWayInformationTextTitle, (50,100))
    for i in range(len(current)):
        screen.blit(current[i], (25, 150+i*25))

def blitInfoPeaceSun(current):
    screen.blit(MilkyWayInformationTextTitle, (250,125))
    for i in range(len(current)):
        screen.blit(current[i], (250, 175+i*25))

def blitInfoMilkyWay(current):
    screen.blit(MilkyWayInformationTextTitle, (50,100))
    for i in range(len(current)):
        screen.blit(current[i], (25, 150 + i*25))

def blitInfoPeacePlanet(current):
    screen.blit(MilkyWayInformationTextTitle, (375,225))
    for i in range(len(current)):
        screen.blit(current[i], (375, 275 + i*25))

    # sub galaxy 2 
#sub galaxy 2 plants
Trappist_1 = Planet(0, 0, 25, (255, 69, 0), 1.784e30)
Trappist_1.Sun = True 
Trappist1b = Planet(-0.1 * Planet.AstroUnit, 0, 8, (210, 105, 30), 8.18e24)
Trappist1b.y_vel = 80.1 * 1000
Trappist1c = Planet(-0.15 * Planet.AstroUnit, 0, 9, (178, 116, 93), 8.7e24)
Trappist1c.y_vel = 69.5 * 1000
Trappist1d = Planet(-0.22 * Planet.AstroUnit, 0, 7, (255, 182, 193), 3.94e24)
Trappist1d.y_vel = 54.6 * 1000
Trappist1e = Planet(-0.29 * Planet.AstroUnit, 0, 8, (135, 206, 250), 5.65e24)
Trappist1e.y_vel = 44.6 * 1000
Trappist1f = Planet(-0.37 * Planet.AstroUnit, 0, 8, (173, 216, 230), 6.56e24)
Trappist1f.y_vel = 42.1 * 1000
Trappist1g = Planet(-0.49 * Planet.AstroUnit, 0, 10, (176, 196, 222), 10.80e24)
Trappist1g.y_vel = 35.1 * 1000
Trappist1h = Planet(-0.68 * Planet.AstroUnit, 0, 6, (169, 169, 169), 2.64e24)
Trappist1h.y_vel = 33.7 * 1000

TRAPPISTplanets = [Trappist_1, Trappist1b, Trappist1c, Trappist1d, Trappist1e, Trappist1f, Trappist1g, Trappist1h]

Trappist_1InformationBox = buttons((192,192,192), 55, 55, 722, 62.5)
Trappist1bInformationBox = buttons((192,192,192), 55, 55, 722, 122.5)
Trappist1cInformationBox = buttons((192,192,192), 55, 55, 722, 182.5)
Trappist1dInformationBox = buttons((192,192,192), 55, 55, 722, 242.5)
Trappist1eInformationBox = buttons((192,192,192), 55, 55, 662, 62.5)
Trappist1fInformationBox = buttons((192,192,192), 55, 55, 662, 122.5)
Trappist1gInformationBox = buttons((192,192,192), 55, 55, 662, 182.5)
Trappist1hInformationBox = buttons((192,192,192), 55, 55, 662, 242.5)
HideTrappistInformationBox = buttons((169, 92, 104), 55, 55, 692, 302.5)


T_1Info = smallFont.render('Name : TRAPPIST_1', False, 'White')
T_1Info1 = smallFont.render('Mass : 1.784e30 kg', False, 'White')
T_1Info2 = smallFont.render("Radius : 84'371 km ", False, 'White')
T_1Info3 = smallFont.render('Dwarf star of this Solar System', False, 'White')
T_1Infolst = [T_1Info, T_1Info1, T_1Info2, T_1Info3]

T1b = smallFont.render('Name : TRAPPIST-1b', False, 'White')
T1b1 = smallFont.render('Mass :  8.18e24 kg', False, 'White')
T1b2 = smallFont.render("Radius :  7'141 km ", False, 'White')
T1b3 = smallFont.render('Distance from star: 0.11 AU', False, 'White')
T1bInfolst = [T1b, T1b1, T1b2, T1b3]

T1c = smallFont.render('Name : TRAPPIST-1c', False, 'White')
T1c1 = smallFont.render('Mass :  8.7e24 kg', False, 'White')
T1c2 = smallFont.render("Radius :  7'493 km ", False, 'White')
T1c3 = smallFont.render('Distance from star: 0.15 AU', False, 'White')
T1cInfolst = [T1c, T1c1, T1c2, T1c3]

T1d = smallFont.render('Name : TRAPPIST-1d', False, 'White')
T1d1 = smallFont.render('Mass : 3.94e24 kg', False, 'White')
T1d2 = smallFont.render("Radius :  2'243 km ", False, 'White')
T1d3 = smallFont.render('Distance from star: 0.22 AU', False, 'White')
T1dInfolst = [T1d, T1d1, T1d2, T1d3]

T1e = smallFont.render('Name : TRAPPIST-1e', False, 'White')
T1e1 = smallFont.render('Mass :  5.65e24 kg', False, 'White')
T1e2 = smallFont.render("Radius :  4'457 km ", False, 'White')
T1e3 = smallFont.render('Distance from star: 0.29 AU', False, 'White')
T1eInfolst = [T1e, T1e1, T1e2, T1e3]

T1f = smallFont.render('Name : TRAPPIST-1f', False, 'White')
T1f1 = smallFont.render('Mass :  6.56e24 kg', False, 'White')
T1f2 = smallFont.render("Radius :  5'023 km ", False, 'White')
T1f3 = smallFont.render('Distance from star: 0.37 AU', False, 'White')
T1fInfolst = [T1f, T1f1, T1f2, T1f3]

T1g = smallFont.render('Name : TRAPPIST-1g', False, 'White')
T1g1 = smallFont.render('Mass :  10.8e24 kg', False, 'White')
T1g2 = smallFont.render("Radius : 9'331 km ", False, 'White')
T1g3 = smallFont.render('Distance from star: 0.49 AU', False, 'White')
T1gInfolst = [T1g, T1g1, T1g2, T1g3]

T1h = smallFont.render('Name : TRAPPIST-1h', False, 'White')
T1h1 = smallFont.render('Mass :  2.64e24 kg', False, 'White')
T1h2 = smallFont.render("Radius :  2'047 km ", False, 'White')
T1h3 = smallFont.render('Distance from star: 0.68 AU', False, 'White')
T1hInfolst = [T1h, T1h1, T1h2, T1h3]

t1DisplayDict = {
    'T_1InfoDisplay' : False, 
    'T1bInfoDisplay' : False,
    'T1cInfoDisplay' : False, 
    'T1dInfoDisplay' : False,
    'T1eInfoDisplay' : False, 
    'T1fInfoDisplay' : False, 
    'T1gInfoDisplay' : False,
    'T1hInfoDisplay' : False,
    'Nothing' : False
}

trappInformationBoxlst = [Trappist1hInformationBox, Trappist_1InformationBox,Trappist1bInformationBox,Trappist1cInformationBox,Trappist1dInformationBox,Trappist1eInformationBox,Trappist1fInformationBox,Trappist1gInformationBox, Trappist1hInformationBox, HideTrappistInformationBox]
trapDescriptionTitle = bigFont.render('DESCRIPTION: ', False, 'White')
trapDescriptionTitleRect = trapDescriptionTitle.get_rect(center = (750, 75))

subgalaxy2buttonlst = [backButton, speedUpButton, slowDownButton, Trappist1hInformationBox, Trappist_1InformationBox,Trappist1bInformationBox,Trappist1cInformationBox,Trappist1dInformationBox,Trappist1eInformationBox,Trappist1fInformationBox,Trappist1gInformationBox,HideTrappistInformationBox]

    # sub galaxy 3

Solara = Planet(0, 0, 27, (255,255,0), 1e30)
Solara.Sun = True 
Gaia = Planet(-1.8*Planet.AstroUnit, 0, 12, (255,0,0), 5.97e24)
Gaia.y_vel = 15 * 1000
Astraeus = Planet(-1.3 * Planet.AstroUnit, 0, 10, (255,127,0), 4.87e24)
Astraeus.y_vel = 18 * 1000
Typhon = Planet(1 * Planet.AstroUnit, 0, 10 , (0,255,0), 1.6e26)
Typhon.y_vel = -23 * 1000
Vesta = Planet(2.8 * Planet.AstroUnit, 0, 13, (75,0,130), 1.9e27)
Vesta.y_vel = -13 * 1000
Zephyra = Planet(2.4 * Planet.AstroUnit, 0, 14, (0,0,255), 7.3e22)
Zephyra.y_vel = 14 * 1000
chudePlanets = [Solara, Gaia, Astraeus, Typhon, Vesta, Zephyra]

chudeDescTitle = font.render('DESCRIPTION : ', False, 'white')
chudeDescTitleRect = chudeDescTitle.get_rect(center = (50,100))

chudeDesc1 = smallFont.render('This is a system we played around with!', False, 'white')
chudeDesc2 = smallFont.render('We used random masses and velocities', False, 'white')
chudeDesc3 = smallFont.render(' to study how planets would revolve.', False, 'white')
chudeDesc4 = smallFont.render('With this, we got a better understanding', False, 'white')
chudeDesc5 = smallFont.render(' of how celestial bodies interact with', False, 'white')
chudeDesc6 = smallFont.render('one another in space.', False, 'white')
chudeDesc7 = smallFont.render('Try to create a better system!', False, 'white')
chudeDesc8 = smallFont.render('Good Luck! :)', False, 'white')

chudeDesc1Rect = chudeDesc1.get_rect(center = (175,125))
chudeDesc2Rect = chudeDesc2.get_rect(center = (175,150))
chudeDesc3Rect = chudeDesc3.get_rect(center = (175,175))
chudeDesc4Rect = chudeDesc4.get_rect(center = (175,200))
chudeDesc5Rect = chudeDesc5.get_rect(center = (175,225))
chudeDesc6Rect = chudeDesc6.get_rect(center = (175,250))
chudeDesc7Rect = chudeDesc7.get_rect(center = (175,275))
chudeDesc8Rect = chudeDesc8.get_rect(center = (175,300))

subgalaxy3buttonlst = [backButton, speedUpButton, slowDownButton]

    # Option state
optionTitleText = bigFont.render('OPTIONS', False, 'White')
optionTextRect = optionTitleText.get_rect(center = (400,50))

#On
ONtext = smallFont.render('ON', False, 'Black')
#Off
OFFtext = smallFont.render('OFF', False, 'Black')

visualizeStarBool = True
visualizeStar = buttons((175,255,175), 75, 25, 275 , 110)
visualizeStarText = smallFont.render('Visualize background stars: ', False, 'White')
visualizeStarTextRect = visualizeStarText.get_rect(center = (150,125))
visualizeStarONRect = ONtext.get_rect(center = (75/2 + 275, 25/2 + 110))
visualizeStarOFFRect = OFFtext.get_rect(center = (75/2 + 275, 25/2 + 110))

observeOrbitsBool = True 
observeOrbitButton = buttons((175,225,175), 75, 25, 275, 155)
observeOrbitText = smallFont.render('Observe planet orbits : ', False, 'White')
observeOrbitTextRect = observeOrbitText.get_rect(center = (150, 170))
observeOrbitONRect = ONtext.get_rect(center = (75/2 + 275, 25/2 + 155))
observeOrbitOFFRect = OFFtext.get_rect(center = (75/2 + 275, 25/2 + 155))

orbitChangeText = smallFont.render('Orbit pixel length: ', False, 'white')
orbitChangeTextRect = orbitChangeText.get_rect(center = (50 + 145, 235))
orbit200Button = buttons((169,169,169), 100, 50, 35, 250)
text200 = smallFont.render("200 px", False, "Black")
text200Rect = text200.get_rect(center = (50 + 35, 275))


orbit600Button = buttons((169,169,169), 100, 50, 145, 250)
text600 = smallFont.render('600 px', False, 'black')
text600Rect = text600.get_rect(center = (50 + 145 , 275))

orbit1000Button = buttons((169,169,169), 100, 50, 255, 250)
text1000 = smallFont.render('1000 px', False, 'black')
text1000Rect = text1000.get_rect(center = (50 + 255, 275))


pixelLengthOrbit = [orbit200Button, orbit600Button, orbit1000Button]

optionButtonlst = [backButton, visualizeStar, observeOrbitButton, orbit200Button, orbit600Button, orbit1000Button]

    # Game state

peacefulButton = buttons((192,192,192), 500, 75, 150, 75)
peacefulButtonText = bigFont.render('Peaceful Mode', False, 'black')
peacefulButtonTextRect = peacefulButtonText.get_rect(center = (500/2+150, 75/2+75))

mediumButton = buttons((192,192,192), 450, 75, 175, 175)
mediumButtonText = bigFont.render('Medium Mode', False, 'black')
mediumButtonTextRect = mediumButtonText.get_rect(center = (450/2+175, 75/2+175))

hardcoreButton = buttons((192,192,192), 400 , 75, 200 , 275)
hardcoreButtonText = bigFont.render('Hardcore Mode', False, 'black')
hardcoreButtonTextRect = hardcoreButtonText.get_rect(center = (400/2+200, 75/2+275))

gameButtonlst = [backButton, peacefulButton, mediumButton, hardcoreButton]


#LISTS OF STUFF
Sun1 = Planet(0, 0, 22, (255, 255, 0), 1.2e29)
Sun1.Sun = True

Sun2 = Planet(0, 0, 25, (0, 255, 255), 1.43e30)
Sun2.Sun = True

Sun3 = Planet(0, 0, 27, (255, 99, 71), 1.1e31)
Sun3.Sun = True

Sun4 = Planet(0, 0, 22, (255, 255, 255), 4e29)
Sun4.Sun = True

Sun5 = Planet(0, 0, 25, (175, 238, 238), 1.83e30)
Sun5.Sun = True

Sun6 = Planet(0, 0, 27, (65, 105, 225), 1.6e31)
Sun6.Sun = True

Sun7 = Planet(0, 0, 20, (95, 158, 160), 3.96e27)
Sun7.Sun = True

Sun8 = Planet(0, 0, 22, (178, 34, 34), 6.41e28)
Sun8.Sun = True

Sun9 = Planet(0, 0, 24, (255, 20, 147), 2.53e29)
Sun9.Sun = True

Sun10 = Planet(0, 0, 31, (255, 192, 203), 3.3e35)
Sun10.Sun = True

Sun11 = Planet(0, 0, 32, (139, 0, 0), 1e36)
Sun11.Sun = True 

Sun1Text = smallFont.render('Name: Sun1', False, 'White')
Sun1Text2 = smallFont.render('Mass: 1.2e29 kg', False, 'White')
Sun1Text3 = smallFont.render('Radius: ~25,000 km', False, 'White')
Sun1Textlst = [Sun1Text, Sun1Text2, Sun1Text3]

Sun2Text = smallFont.render('Name: Sun2', False, 'White')
Sun2Text2 = smallFont.render('Mass: 1.43e30 kg', False, 'White')
Sun2Text3 = smallFont.render('Radius: ~26,000 km', False, 'White')
Sun2Textlst = [Sun2Text, Sun2Text2, Sun2Text3]

Sun3Text = smallFont.render('Name: Sun3', False, 'White')
Sun3Text2 = smallFont.render('Mass: 1.1e31 kg', False, 'White')
Sun3Text3 = smallFont.render('Radius: ~27,000 km', False, 'White')
Sun3Textlst = [Sun3Text, Sun3Text2, Sun3Text3]

Sun4Text = smallFont.render('Name: Sun4', False, 'White')
Sun4Text2 = smallFont.render('Mass: 4e29 kg', False, 'White')
Sun4Text3 = smallFont.render('Radius: ~33,000 km', False, 'White')
Sun4Textlst = [Sun4Text, Sun4Text2, Sun4Text3]

Sun5Text = smallFont.render('Name: Sun5', False, 'White')
Sun5Text2 = smallFont.render('Mass: 1.83e30 kg', False, 'White')
Sun5Text3 = smallFont.render('Radius: ~23,000 km', False, 'White')
Sun5Textlst = [Sun5Text, Sun5Text2, Sun5Text3]

Sun6Text = smallFont.render('Name: Sun6', False, 'White')
Sun6Text2 = smallFont.render('Mass: 1.6e31 kg', False, 'White')
Sun6Text3 = smallFont.render('Radius: ~24,000 km', False, 'White')
Sun6Textlst = [Sun6Text, Sun6Text2, Sun6Text3]

Sun7Text = smallFont.render('Name: Sun7', False, 'White')
Sun7Text2 = smallFont.render('Mass: 3.96e27 kg', False, 'White')
Sun7Text3 = smallFont.render('Radius: ~28,000 km', False, 'White')
Sun7Textlst = [Sun7Text, Sun7Text2, Sun7Text3]

Sun8Text = smallFont.render('Name: Sun8', False, 'White')
Sun8Text2 = smallFont.render('Mass: 6.41e28 kg', False, 'White')
Sun8Text3 = smallFont.render('Radius: ~29,000 km', False, 'White')
Sun8Textlst = [Sun8Text, Sun8Text2, Sun8Text3]

Sun9Text = smallFont.render('Name: Sun9', False, 'White')
Sun9Text2 = smallFont.render('Mass: 2.53e29 kg', False, 'White')
Sun9Text3 = smallFont.render('Radius: ~30,000 km', False, 'White')
Sun9Textlst = [Sun9Text, Sun9Text2, Sun9Text3]

planetCounterPeaceful = 0 


Sun10Text = smallFont.render('Name: Sun10', False, 'White')
Sun10Text2 = smallFont.render('Mass: 3.3e35 kg', False, 'White')
Sun10Text3 = smallFont.render('Radius: ~31,000 km', False, 'White')
Sun10Textlst = [Sun10Text, Sun10Text2, Sun10Text3]

Sun11Text = smallFont.render('Name: Sun11', False, 'White')
Sun11Text2 = smallFont.render('Mass: 1e36 kg', False, 'White')
Sun11Text3 = smallFont.render('Radius: ~32,000 km', False, 'White')
Sun11Textlst = [Sun11Text, Sun11Text2, Sun11Text3]

Planet1 = Planet(-0.7 * Planet.AstroUnit, 0, 6, (178, 34, 34), 6e24)
Planet1.y_vel = 10 * 1000
Planet2 = Planet(-1 * Planet.AstroUnit, 0, 7, (255, 69, 0), 7.3e24)
Planet2.y_vel = -8 * 1000
Planet3 = Planet(1.1 * Planet.AstroUnit, 0, 12, (255, 215, 0), 5.9e26)
Planet3.y_vel = -6 * 1000
Planet4 = Planet(-2 * Planet.AstroUnit, 0, 16, (238, 232, 170), 2.1e27)
Planet4.y_vel = -16 * 1000
Planet5 = Planet(-1.25 * Planet.AstroUnit, 0, 14, (255, 0, 255), 8.9e26)
Planet5.y_vel = 22 * 1000
Planet6 = Planet(-3 * Planet.AstroUnit, 0, 25, (106, 90, 205), 3.2e28)
Planet6.y_vel = -17 * 1000
Planet7 = Planet(-1.2 * Planet.AstroUnit, 0, 15, (173, 255, 47), 9.1e26)
Planet7.y_vel = 24 * 1000
Planet8 = Planet(0.3 * Planet.AstroUnit, 0, 10, (255, 192, 203), 4.4e25)
Planet8.y_vel = 19 * 1000
Planet9 = Planet(1.2 * Planet.AstroUnit, 0, 22, (255, 160, 122), 7.2e28)
Planet9.y_vel = -6.2 * 1000
Planet10 = Planet(1.1 * Planet.AstroUnit, 0, 12, (255, 165, 0), 5.1e26)
Planet10.y_vel = 18 * 1000
Planet11 = Planet(1.4 * Planet.AstroUnit, 0, 9, (216, 191, 216), 1.5e25)
Planet11.y_vel = -18 * 1000
Planet12 = Planet(2 * Planet.AstroUnit, 0, 20, (153, 50, 204), 6e28)
Planet12.y_vel = 22 * 1000
Planet13 = Planet(1.4 * Planet.AstroUnit, 0, 15, (123, 104, 238), 8.4e26)
Planet13.y_vel = -19 * 1000
Planet14 = Planet(1.8 * Planet.AstroUnit, 0, 16, (152, 251, 152), 1.2e27)
Planet14.y_vel = 14.8 * 1000
Planet15 = Planet(4 * Planet.AstroUnit, 0, 11, (0, 255, 127), 1.6e26)
Planet15.y_vel = -10.5 * 1000
Planet16 = Planet(-2.3 * Planet.AstroUnit, 0, 14, (0, 100, 0), 7.8e28)
Planet16.y_vel = 19.8 * 1000
Planet17 = Planet(1.25 * Planet.AstroUnit, 0, 16, (143, 188, 139), 9.9e26)
Planet17.y_vel = -14.5 * 1000
Planet18 = Planet(1.75 * Planet.AstroUnit, 0, 14, (0, 128, 128), 5.7e26)
Planet18.y_vel = 21 * 1000
Planet19 = Planet(-1.25 * Planet.AstroUnit, 0, 21, (0, 255, 255), 2.3e28)
Planet19.y_vel = 18.5 * 1000
Planet20 = Planet(-1.75 * Planet.AstroUnit, 0, 11, (176, 196, 222), 1.7e26)
Planet20.y_vel = -18 * 1000
PlanetX = Planet(2.75 * Planet.AstroUnit, 0, 21, (0, 0, 205), 9e28)
PlanetX.y_vel = -8 * 1000
PlanetY = Planet(-2.75 * Planet.AstroUnit, 0, 15, (255, 235, 205), 1.2e27)
PlanetY.y_vel = -50 * 1000


Planet1Text = smallFont.render('Name: Planet1', False, 'White')
Planet1Text2 = smallFont.render('Mass: 6e24 kg', False, 'White')
Planet1Text3 = smallFont.render('Distance to Sun: ~0.7 AU', False, 'White')
Planet1Text4 = smallFont.render('Velocity: ~10 km/s', False, 'White')
Planet1Textlst = [Planet1Text, Planet1Text2, Planet1Text3, Planet1Text4]

Planet2Text = smallFont.render('Name: Planet2', False, 'White')
Planet2Text2 = smallFont.render('Mass: 7.3e24 kg', False, 'White')
Planet2Text3 = smallFont.render('Distance to Sun: ~1.0 AU', False, 'White')
Planet2Text4 = smallFont.render('Velocity: ~8 km/s', False, 'White')
Planet2Textlst = [Planet2Text, Planet2Text2, Planet2Text3, Planet2Text4]

Planet3Text = smallFont.render('Name: Planet3', False, 'White')
Planet3Text2 = smallFont.render('Mass: 5.9e26 kg', False, 'White')
Planet3Text3 = smallFont.render('Distance to Sun: ~1.1 AU', False, 'White')
Planet3Text4 = smallFont.render('Velocity: ~6 km/s', False, 'White')
Planet3Textlst = [Planet3Text, Planet3Text2, Planet3Text3, Planet3Text4]

Planet4Text = smallFont.render('Name: Planet4', False, 'White')
Planet4Text2 = smallFont.render('Mass: 2.1e27 kg', False, 'White')
Planet4Text3 = smallFont.render('Distance to Sun: ~2.0 AU', False, 'White')
Planet4Text4 = smallFont.render('Velocity: ~16 km/s', False, 'White')
Planet4Textlst = [Planet4Text, Planet4Text2, Planet4Text3, Planet4Text4]

Planet5Text = smallFont.render('Name: Planet5', False, 'White')
Planet5Text2 = smallFont.render('Mass: 8.9e26 kg', False, 'White')
Planet5Text3 = smallFont.render('Distance to Sun: ~1.25 AU', False, 'White')
Planet5Text4 = smallFont.render('Velocity: ~22 km/s', False, 'White')
Planet5Textlst = [Planet5Text, Planet5Text2, Planet5Text3, Planet5Text4]

Planet6Text = smallFont.render('Name: Planet6', False, 'White')
Planet6Text2 = smallFont.render('Mass: 3.2e28 kg', False, 'White')
Planet6Text3 = smallFont.render('Distance to Sun: ~3.0 AU', False, 'White')
Planet6Text4 = smallFont.render('Velocity: ~17 km/s', False, 'White')
Planet6Textlst = [Planet6Text, Planet6Text2, Planet6Text3, Planet6Text4]

Planet7Text = smallFont.render('Name: Planet7', False, 'White')
Planet7Text2 = smallFont.render('Mass: 9.1e26 kg', False, 'White')
Planet7Text3 = smallFont.render('Distance to Sun: ~1.2 AU', False, 'White')
Planet7Text4 = smallFont.render('Velocity: ~24 km/s', False, 'White')
Planet7Textlst = [Planet7Text, Planet7Text2, Planet7Text3, Planet7Text4]

Planet8Text = smallFont.render('Name: Planet8', False, 'White')
Planet8Text2 = smallFont.render('Mass: 4.4e25 kg', False, 'White')
Planet8Text3 = smallFont.render('Distance to Sun: ~0.3 AU', False, 'White')
Planet8Text4 = smallFont.render('Velocity: ~19 km/s', False, 'White')
Planet8Textlst = [Planet8Text, Planet8Text2, Planet8Text3, Planet8Text4]

Planet9Text = smallFont.render('Name: Planet9', False, 'White')
Planet9Text2 = smallFont.render('Mass: 7.2e28 kg', False, 'White')
Planet9Text3 = smallFont.render('Distance to Sun: ~1.2 AU', False, 'White')
Planet9Text4 = smallFont.render('Velocity: ~6.2 km/s', False, 'White')
Planet9Textlst = [Planet9Text, Planet9Text2, Planet9Text3, Planet9Text4]

Planet10Text = smallFont.render('Name: Planet10', False, 'White')
Planet10Text2 = smallFont.render('Mass: 5.1e26 kg', False, 'White')
Planet10Text3 = smallFont.render('Distance to Sun: ~1.1 AU', False, 'White')
Planet10Text4 = smallFont.render('Velocity: ~18 km/s', False, 'White')
Planet10Textlst = [Planet10Text, Planet10Text2, Planet10Text3, Planet10Text4]

Planet11Text = smallFont.render('Name: Planet11', False, 'White')
Planet11Text2 = smallFont.render('Mass: 1.5e25 kg', False, 'White')
Planet11Text3 = smallFont.render('Distance to Sun: ~1.4 AU', False, 'White')
Planet11Text4 = smallFont.render('Velocity: ~18 km/s', False, 'White')
Planet11Textlst = [Planet11Text, Planet11Text2, Planet11Text3, Planet11Text4]

Planet12Text = smallFont.render('Name: Planet12', False, 'White')
Planet12Text2 = smallFont.render('Mass: 6e28 kg', False, 'White')
Planet12Text3 = smallFont.render('Distance to Sun: ~2.0 AU', False, 'White')
Planet12Text4 = smallFont.render('Velocity: ~22 km/s', False, 'White')
Planet12Textlst = [Planet12Text, Planet12Text2, Planet12Text3, Planet12Text4]

Planet13Text = smallFont.render('Name: Planet13', False, 'White')
Planet13Text2 = smallFont.render('Mass: 8.4e26 kg', False, 'White')
Planet13Text3 = smallFont.render('Distance to Sun: ~1.4 AU', False, 'White')
Planet13Text4 = smallFont.render('Velocity: ~19 km/s', False, 'White')
Planet13Textlst = [Planet13Text, Planet13Text2, Planet13Text3, Planet13Text4]

Planet14Text = smallFont.render('Name: Planet14', False, 'White')
Planet14Text2 = smallFont.render('Mass: 1.2e27 kg', False, 'White')
Planet14Text3 = smallFont.render('Distance to Sun: ~1.8 AU', False, 'White')
Planet14Text4 = smallFont.render('Velocity: ~14.8 km/s', False, 'White')
Planet14Textlst = [Planet14Text, Planet14Text2, Planet14Text3, Planet14Text4]

Planet15Text = smallFont.render('Name: Planet15', False, 'White')
Planet15Text2 = smallFont.render('Mass: 1.6e26 kg', False, 'White')
Planet15Text3 = smallFont.render('Distance to Sun: ~4.0 AU', False, 'White')
Planet15Text4 = smallFont.render('Velocity: ~10.5 km/s', False, 'White')
Planet15Textlst = [Planet15Text, Planet15Text2, Planet15Text3, Planet15Text4]

Planet16Text = smallFont.render('Name: Planet16', False, 'White')
Planet16Text2 = smallFont.render('Mass: 7.8e28 kg', False, 'White')
Planet16Text3 = smallFont.render('Distance to Sun: ~2.3 AU', False, 'White')
Planet16Text4 = smallFont.render('Velocity: ~19.8 km/s', False, 'White')
Planet16Textlst = [Planet16Text, Planet16Text2, Planet16Text3, Planet16Text4]

Planet17Text = smallFont.render('Name: Planet17', False, 'White')
Planet17Text2 = smallFont.render('Mass: 9.9e26 kg', False, 'White')
Planet17Text3 = smallFont.render('Distance to Sun: ~1.25 AU', False, 'White')
Planet17Text4 = smallFont.render('Velocity: ~14.5 km/s', False, 'White')
Planet17Textlst = [Planet17Text, Planet17Text2, Planet17Text3, Planet17Text4]

Planet18Text = smallFont.render('Name: Planet18', False, 'White')
Planet18Text2 = smallFont.render('Mass: 5.7e26 kg', False, 'White')
Planet18Text3 = smallFont.render('Distance to Sun: ~1.75 AU', False, 'White')
Planet18Text4 = smallFont.render('Velocity: ~21 km/s', False, 'White')
Planet18Textlst = [Planet18Text, Planet18Text2, Planet18Text3, Planet18Text4]

Planet19Text = smallFont.render('Name: Planet19', False, 'White')
Planet19Text2 = smallFont.render('Mass: 2.3e28 kg', False, 'White')
Planet19Text3 = smallFont.render('Distance to Sun: ~1.25 AU', False, 'White')
Planet19Text4 = smallFont.render('Velocity: ~12 km/s', False, 'White')
Planet19Textlst = [Planet19Text, Planet19Text2, Planet19Text3, Planet19Text4]

Planet20Text = smallFont.render('Name: Planet20', False, 'White')
Planet20Text2 = smallFont.render('Mass: 1.7e26 kg', False, 'White')
Planet20Text3 = smallFont.render('Distance to Sun: ~1.75 AU', False, 'White')
Planet20Text4 = smallFont.render('Velocity: ~14.5 km/s', False, 'White')
Planet20Textlst = [Planet20Text, Planet20Text2, Planet20Text3, Planet20Text4]

PlanetXText = smallFont.render('Name: PlanetX', False, 'White')
PlanetXText2 = smallFont.render('Mass: 9e28 kg', False, 'White')
PlanetXText3 = smallFont.render('Distance to Sun: ~2.75 AU', False, 'White')
PlanetXText4 = smallFont.render('Velocity: ~18 km/s', False, 'White')
PlanetXTextlst = [PlanetXText, PlanetXText2, PlanetXText3, PlanetXText4]

PlanetYText = smallFont.render('Name: PlanetY', False, 'White')
PlanetYText2 = smallFont.render('Mass: 1.2e27 kg', False, 'White')
PlanetYText3 = smallFont.render('Distance to Sun: ~2.75 AU', False, 'White')
PlanetYText4 = smallFont.render('Velocity: ~15 km/s', False, 'White')
PlanetYTextlst = [PlanetYText, PlanetYText2, PlanetYText3, PlanetYText4]


chooseButton = buttons((152, 251, 152), 150, 75, 550, 250)
chooseText = bigFont.render('CHOOSE', False, "black")
chooseTextRect = chooseText.get_rect(center = (150/2 + 550, 75/2 + 250))

peacefulModeSun = {
    "Sun1Display": False,
    "Sun2Display": False,
    "Sun3Display": False,
    "Sun4Display": False,
    "Sun5Display": False,
    "Sun6Display": False,
    "Sun7Display": False,
    "Sun8Display": False,
    "Sun9Display": False,
    "Sun10Display": False,
    "Sun11Display": False,
    "Nothing": True
}

peacefulModePlanet = {
    "Planet1Display": False,
    "Planet2Display": False,
    "Planet3Display": False,
    "Planet4Display": False,
    "Planet5Display": False,
    "Planet6Display": False,
    "Planet7Display": False,
    "Planet8Display": False,
    "Planet9Display": False,
    "Planet10Display": False,
    "Planet11Display": False,
    "Planet12Display": False,
    "Planet13Display": False,
    "Planet14Display": False,
    "Planet15Display": False,
    "Planet16Display": False,
    "Planet17Display": False,
    "Planet18Display": False,
    "Planet19Display": False,
    "Planet20Display": False,
    "PlanetXDisplay": False,
    "PlanetYDisplay": False,
    "Nothing": True
}


peacefulButtonlst = [chooseButton, backButton]
# Free Code
comet_last_reset = pyg.time.get_ticks()


def generate_random_comet():
    # Génère une position aléatoire à la périphérie du système solaire
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(3 * Planet.AstroUnit, 5 * Planet.AstroUnit)
    x = distance * math.cos(angle)
    y = distance * math.sin(angle)

    # Vitesse initiale aléatoire
    speed = random.uniform(30e3, 50e3)  # Entre 30 km/s et 50 km/s
    direction = random.uniform(0, 2 * math.pi)
    x_vel = speed * math.cos(direction)
    y_vel = speed * math.sin(direction)

    comet = Planet(x, y, 6, (200, 200, 200), 1e14)
    comet.x_vel = x_vel
    comet.y_vel = y_vel
    comet.is_comet = True
    return comet

comet = generate_random_comet()

def displayOnlyOne(selected, dict):
    for elem in dict:
        dict[elem] = False
    dict[selected] = True

peacefulPlanetlst = [comet]

quitButton = buttons((255,0,0), 150, 55, 10, 75)
quitButtonText = smallFont.render('QUIT', False, 'black')
quitButtonTextRect = quitButtonText.get_rect(center = (150/2 + 10 , 55/2 + 75))

simulationPeacefulButtonlst = [backButton, quitButton]

# use button.rects[index (0 to x)] to find which is clicked
choiceBox = ChoiceButton(75, 75, 25, 25, 4, 90)
choiceBox2 = ChoiceButton(75, 75, 115, 25, 4, 90)
choiceBox3 = ChoiceButton(75, 75, 205, 25, 4, 90)
choiceBox4 = ChoiceButton(75, 75, 295, 25, 4, 90)

choiceboxlst = [choiceBox, choiceBox2]
planetChoiceBoxlst = [choiceBox, choiceBox2, choiceBox3, choiceBox4]



pixelLength = 200

# Loop 
while True:
    for planet in TRAPPISTplanets:
        if pixelLength == 200:
            planet.orbitvalue = 40
        elif pixelLength == 600:
            planet.orbitvalue = 140
        elif pixelLength == 1000:
            planet.orbitvalue = 240


    mousePos = pyg.mouse.get_pos()
    
    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            pyg.quit()
            exit()
        if event.type == pyg.MOUSEBUTTONDOWN:
            # Zooming section
            if event.button == 5:
                if subgalaxy1:
                    if MilkyWayZoomFactor > 25:
                        MilkyWayZoomFactor -= 12.5
                    for planet in planets:
                        planet.orbit.clear()
                        planet.reset()
                        EarthyearBool = False 
                        EarthYearCounter = 0
                        EarthyearCheckRect.center = (600,200)
                        planet.TIMESTEP = 3600                         
                        planet.SCALE = MilkyWayZoomFactor /planet.AstroUnit   
            if event.button == 4:
                if subgalaxy1:
                    if MilkyWayZoomFactor < 187.5:
                        MilkyWayZoomFactor += 12.5    
                    for planet in planets:
                        planet.orbit.clear()
                        planet.reset()
                        EarthyearBool = False 
                        EarthYearCounter = 0
                        EarthyearCheckRect.center = (600,200)
                        planet.TIMESTEP = 3600                         
                        planet.SCALE = MilkyWayZoomFactor /planet.AstroUnit
            # Clicky thing state
            if starterState: 
                for button in starterButtonslst:
                    if button.rect.collidepoint(mousePos):
                        if button == startButton:
                            gameState = True
                        elif button == infoButton:
                            infoState = True 
                        elif button == optionButton:
                            optionState = True
                        elif button == galaxiesButton:
                            galaxyState = True
                        starterState = False 
                        starGroup.empty()
                continue
                # the continue is cuz a weird glitch is happening if i click the background randomly
            if infoState:
                for button in infoButtonlst:
                    if button.rect.collidepoint(mousePos):
                        if button == backButton:
                            starterState = True 
                        infoState = False
            if galaxyState:
                for button in galaxyButtonlst:
                    if button.rect.collidepoint(mousePos):
                        if button == backButton:
                            starterState = True
                        if button == milkyWayButton:
                            subgalaxy1 = True
                        galaxyState = False 
                        if button == myGalaxyButton:
                            subgalaxy2 = True 
                        if button == AndromedaGalaxyButton:
                            subgalaxy3 = True
                        galaxyState = False 
            if subgalaxy1:
                for button in subgalaxy1buttonlst:
                    if button.rect.collidepoint(mousePos):
                        if button == backButton:
                            milkywayonlyonetrue('Nothing')
                            for backgroundStar in backgroundStarsGroup:
                                backgroundStar.kill()
                            for planet in planets:
                                planet.orbit.clear()
                                planet.reset()
                                EarthyearBool = False 
                                EarthYearCounter = 0
                                EarthyearCheckRect.center = (600,200)
                                planet.SCALE = 125 / planet.AstroUnit
                                planet.TIMESTEP = 3600 
                            subgalaxy1 = False 
                            galaxyState = True                          
                        if button in informationBoxeslst:
                            if button ==  EarthInformationBox:
                                milkywayonlyonetrue('EarthInfoDisplay')
                            if button == SunInformationBox:
                                milkywayonlyonetrue('SunInfoDisplay')
                            if button == MarsInformationBox:
                                milkywayonlyonetrue('MarsInfoDisplay')
                            if button == MercuryInformationBox:
                                milkywayonlyonetrue('MercInfoDisplay')
                            if button == JupiterInformationBox:
                                milkywayonlyonetrue('JupiterInfoDisplay')
                            if button == VenusInformationBox:
                                milkywayonlyonetrue('VenusInfoDisplay')
                            if button == SaturnInformationBox:
                                milkywayonlyonetrue('SaturnInfoDisplay')
                            if button == UranusInformationBox:
                                milkywayonlyonetrue('UranusInfoDisplay')
                            if button == NeptuneInformationBox:
                                milkywayonlyonetrue('NeptuneInfoDisplay')
                            if button == HideInformationBox:
                                milkywayonlyonetrue('Nothing')
                        for planet in planets:
                            if button == speedUpButton and planet.TIMESTEP <= 23400:
                                    planet.TIMESTEP += 1800
                            if button == slowDownButton and planet.TIMESTEP >= 1800:
                                    planet.TIMESTEP -= 1800 
            if subgalaxy2: 
                for button in subgalaxy2buttonlst:
                    if button.rect.collidepoint(mousePos):
                        if button == backButton: 
                            traponlyonetrue('Nothing')
                            for backgroundStar in backgroundStarsGroup:
                                backgroundStar.kill()
                            for planet in TRAPPISTplanets:
                                planet.orbit.clear()
                                planet.reset()
                                planet.TIMESTEP = 3600
                            galaxyState = True 
                            subgalaxy2 = False 
                        if button == speedUpButton:
                            for planet in TRAPPISTplanets:
                                if planet.TIMESTEP <= 23400:
                                        planet.TIMESTEP += 1800
                        if button == slowDownButton:
                            for planet in TRAPPISTplanets:
                                if planet.TIMESTEP >= 1800:
                                        planet.TIMESTEP -= 1800
                        if button in trappInformationBoxlst:
                            if button ==  Trappist_1InformationBox:
                                traponlyonetrue('T_1InfoDisplay')
                            if button == Trappist1bInformationBox:
                                traponlyonetrue('T1bInfoDisplay')
                            if button == Trappist1cInformationBox:
                                traponlyonetrue('T1cInfoDisplay')
                            if button == Trappist1dInformationBox:
                                traponlyonetrue('T1dInfoDisplay')
                            if button == Trappist1eInformationBox:
                                traponlyonetrue('T1eInfoDisplay')
                            if button == Trappist1fInformationBox:
                                traponlyonetrue('T1fInfoDisplay')
                            if button == Trappist1gInformationBox:
                                traponlyonetrue('T1gInfoDisplay')
                            if button == Trappist1hInformationBox:
                                traponlyonetrue('T1hInfoDisplay')
                            if button == HideTrappistInformationBox:
                                traponlyonetrue('Nothing')
                continue

            if subgalaxy3: 
                for button in subgalaxy3buttonlst:
                    if button.rect.collidepoint(mousePos):
                        if button == backButton:
                            for backgroundStar in backgroundStarsGroup:
                                backgroundStar.kill()
                            for planet in chudePlanets:
                                planet.reset()
                                planet.TIMESTEP = 3600
                                planet.orbit.clear()
                            subgalaxy3 = False 
                            galaxyState = True
                        if button == speedUpButton:
                            for planet in chudePlanets:
                                if planet.TIMESTEP <= 23400:
                                        planet.TIMESTEP += 1800
                        if button == slowDownButton:
                            for planet in chudePlanets:
                                if planet.TIMESTEP >= 1800:
                                        planet.TIMESTEP -= 1800
                continue

            if optionState:
                for button in optionButtonlst:
                    if button.rect.collidepoint(mousePos):
                        if button == backButton:
                            starterState = True
                            optionState = False 
                        if button == visualizeStar:
                            visualizeStarBool = not visualizeStarBool 
                        if button == observeOrbitButton:
                            observeOrbitsBool = not observeOrbitsBool
                for button in pixelLengthOrbit:
                    if button.rect.collidepoint(mousePos):
                        for planet in TRAPPISTplanets:
                            if button == orbit200Button:
                                pixelLength = 200
                            elif button == orbit600Button:
                                pixelLength = 600
                            elif button == orbit1000Button:
                                pixelLength = 1000
                        for planet in planets:
                            if button == orbit200Button:
                                planet.orbitvalue = 200 
                                pixelLength = 200
                            elif button == orbit600Button:
                                planet.orbitvalue = 600
                                pixelLength = 600
                            elif button == orbit1000Button:
                                planet.orbitvalue = 1000
                                pixelLength = 1000
            if gameState:
                for button in gameButtonlst:
                    if button.rect.collidepoint(mousePos):
                        if button == backButton:
                            gameState = False
                            sunChoice = True
                            starterState = True
                        if button == peacefulButton:
                            peacefulState = True
                            sunChoice = True
                            gameState = False
                        if button == mediumButton:
                            mediumState = True 
                            sunChoice = True
                            gameState = False
                        if button == hardcoreButton:
                            hardcoreState = True
                            sunChoice = True
                            gameState = False
            if peacefulState: 
                for button in peacefulButtonlst: 
                    if button.rect.collidepoint(mousePos):
                        if button == backButton and simulationPeaceful:
                            peacefulPlanetlst.clear()
                            peacefulPlanetlst = [comet]
                            resetGameStates() 
                            
                            
                            
                            # peacefulPlanetlst.clear()
                            


                        if button == chooseButton:
                            if peacefulModeSun['Sun1Display']:
                                peacefulPlanetlst.append(Sun1)
                            elif peacefulModeSun['Sun2Display']:
                                peacefulPlanetlst.append(Sun2)
                            elif peacefulModeSun['Sun3Display']:
                                peacefulPlanetlst.append(Sun3)
                            elif peacefulModeSun['Sun4Display']:
                                peacefulPlanetlst.append(Sun4)
                            elif peacefulModeSun['Sun5Display']:
                                peacefulPlanetlst.append(Sun5)
                            elif peacefulModeSun['Sun6Display']:
                                peacefulPlanetlst.append(Sun6)
                            elif peacefulModeSun['Sun7Display']:
                                peacefulPlanetlst.append(Sun7)
                            elif peacefulModeSun['Sun8Display']:
                                peacefulPlanetlst.append(Sun8)
                            elif peacefulModePlanet['Planet1Display']:
                                peacefulPlanetlst.append(Planet1)
                            elif peacefulModePlanet['Planet2Display']:
                                peacefulPlanetlst.append(Planet2)
                            elif peacefulModePlanet['Planet3Display']:
                                peacefulPlanetlst.append(Planet3)
                            elif peacefulModePlanet['Planet4Display']:
                                peacefulPlanetlst.append(Planet4)
                            elif peacefulModePlanet['Planet5Display']:
                                peacefulPlanetlst.append(Planet5)
                            elif peacefulModePlanet['Planet6Display']:
                                peacefulPlanetlst.append(Planet6)
                            elif peacefulModePlanet['Planet7Display']:
                                peacefulPlanetlst.append(Planet7)
                            elif peacefulModePlanet['Planet8Display']:
                                peacefulPlanetlst.append(Planet8)
                            elif peacefulModePlanet['Planet9Display']:
                                peacefulPlanetlst.append(Planet9)
                            elif peacefulModePlanet['Planet10Display']:
                                peacefulPlanetlst.append(Planet10)
                            elif peacefulModePlanet['Planet11Display']:
                                peacefulPlanetlst.append(Planet11)
                            elif peacefulModePlanet['Planet12Display']:
                                peacefulPlanetlst.append(Planet12)
                            elif peacefulModePlanet['Planet13Display']:
                                peacefulPlanetlst.append(Planet13)
                            elif peacefulModePlanet['Planet14Display']:
                                peacefulPlanetlst.append(Planet14)
                            elif peacefulModePlanet['Planet15Display']:
                                peacefulPlanetlst.append(Planet15)
                            elif peacefulModePlanet['Planet16Display']:
                                peacefulPlanetlst.append(Planet16)
                            elif peacefulModePlanet['Planet17Display']:
                                peacefulPlanetlst.append(Planet17)
                            elif peacefulModePlanet['Planet18Display']:
                                peacefulPlanetlst.append(Planet18)
                            elif peacefulModePlanet['Planet19Display']:
                                peacefulPlanetlst.append(Planet19)
                            elif peacefulModePlanet['Planet20Display']:
                                peacefulPlanetlst.append(Planet20)
                            elif peacefulModePlanet['PlanetXDisplay']:
                                peacefulPlanetlst.append(PlanetX)
                            elif peacefulModePlanet['PlanetYDisplay']:
                                peacefulPlanetlst.append(PlanetY)
                            if planetChoice:
                                planetCounterPeaceful += 1
                                displayOnlyOne("Nothing", peacefulModePlanet)
                                if planetCounterPeaceful > 2:
                                    simulationPeaceful = True 
                                    planetChoice = False 
                                    planetCounterPeaceful = 0 
                            if not planetChoice:
                                sunChoice = False
                                displayOnlyOne("Nothing", peacefulModeSun)
                                print('not')
                                planetChoice = True
                                

                for button in choiceBox.rects:
                    if sunChoice:
                        if button.collidepoint(mousePos):
                            if button == choiceBox.rects[0]: 
                                displayOnlyOne("Sun1Display", peacefulModeSun)
                            if button == choiceBox.rects[1]: 
                                displayOnlyOne("Sun2Display", peacefulModeSun)
                            if button == choiceBox.rects[2]: 
                                displayOnlyOne("Sun3Display", peacefulModeSun)
                            if button == choiceBox.rects[3]: 
                                displayOnlyOne("Sun4Display", peacefulModeSun)
                    if planetChoice:
                        if button.collidepoint(mousePos):
                            if button == choiceBox.rects[0]: 
                                displayOnlyOne("Planet1Display", peacefulModePlanet)
                            if button == choiceBox.rects[1]: 
                                displayOnlyOne("Planet2Display", peacefulModePlanet)
                            if button == choiceBox.rects[2]: 
                                displayOnlyOne("Planet3Display", peacefulModePlanet)
                            if button == choiceBox.rects[3]: 
                                displayOnlyOne("Planet4Display", peacefulModePlanet)
                for button in choiceBox2.rects:
                    if sunChoice:
                        if button.collidepoint(mousePos):
                            if button == choiceBox2.rects[0]: 
                                displayOnlyOne("Sun5Display", peacefulModeSun)
                            if button == choiceBox2.rects[1]: 
                                displayOnlyOne("Sun6Display", peacefulModeSun)
                            if button == choiceBox2.rects[2]: 
                                displayOnlyOne("Sun7Display", peacefulModeSun)
                            if button == choiceBox2.rects[3]: 
                                displayOnlyOne("Sun8Display", peacefulModeSun)
                    if planetChoice:
                        if button.collidepoint(mousePos):
                            if button == choiceBox2.rects[0]: 
                                displayOnlyOne("Planet5Display", peacefulModePlanet)
                            if button == choiceBox2.rects[1]: 
                                displayOnlyOne("Planet6Display", peacefulModePlanet)
                            if button == choiceBox2.rects[2]: 
                                displayOnlyOne("Planet7Display", peacefulModePlanet)
                            if button == choiceBox2.rects[3]: 
                                displayOnlyOne("Planet8Display", peacefulModePlanet)
                for button in choiceBox3.rects:
                    if planetChoice:
                        if button.collidepoint(mousePos):
                            if button == choiceBox3.rects[0]: 
                                displayOnlyOne("Planet9Display", peacefulModePlanet)
                            if button == choiceBox3.rects[1]: 
                                displayOnlyOne("Planet10Display", peacefulModePlanet)
                            if button == choiceBox3.rects[2]: 
                                displayOnlyOne("Planet11Display", peacefulModePlanet)
                            if button == choiceBox3.rects[3]: 
                                displayOnlyOne("Planet12Display", peacefulModePlanet)
                for button in choiceBox4.rects:
                    if planetChoice:
                        if button.collidepoint(mousePos):
                            if button == choiceBox4.rects[0]: 
                                displayOnlyOne("Planet13Display", peacefulModePlanet)
                            if button == choiceBox4.rects[1]: 
                                displayOnlyOne("Planet14Display", peacefulModePlanet)
                            if button == choiceBox4.rects[2]: 
                                displayOnlyOne("Planet15Display", peacefulModePlanet)
                            if button == choiceBox4.rects[3]: 
                                displayOnlyOne("Planet16Display", peacefulModePlanet)


            

            if mediumState:
                pass
            if hardcoreState:
                pass

            
    if starterState:
        screen.fill('Black')
        # Stars section
        starChance = r(1,4)

        if starChance == 2:
            star = stars()
            starGroup.add(star)

        for star in starGroup:
            star.move()
    
        starGroup.draw(screen)

        # Buttons with text section
        startButton.draw(screen)
        screen.blit(startText , starterText)

        infoButton.draw(screen)
        screen.blit(infoText, info)

        galaxiesButton.draw(screen)
        screen.blit(galaxiesText, galaxies)

        optionButton.draw(screen)
        screen.blit(optionText, options)

        #Hover thingy section
        darkerColour = (186, 142, 35)
        defaultColour = (255,255,0)
        
        for button in starterButtonslst:
            if button.rect.collidepoint(mousePos):
                button.colour = darkerColour
            else:
                button.colour = defaultColour
    if infoState:
        screen.fill('Black')
        screen.blit(moonImage, moonImageRect)

        # Buttons with text section
        backButton.draw(screen)
        screen.blit(backText, back)

        screen.blit(infoTitle, infoTitleRect)
        for i in range(len(tobeBlitted)):
            screen.blit(tobeBlitted[i], infoRects[i])

    if galaxyState:
        screen.fill('Black')

        # Buttons with text section
        darkerColour = (186, 142, 35)
        defaultColour = (255,255,0)
        
        for button in galaxyButtonlst:
            if button == backButton:
                continue
            if button.rect.collidepoint(mousePos):
                button.colour = darkerColour
            else:
                button.colour = defaultColour
        backButton.draw(screen)
        
        
        for button in galaxyButtonlst:
            button.draw(screen)

        screen.blit(backText, back)    
        screen.blit(milkyWayText, milkyWayTextRect)
        screen.blit(myGalaxyText, myGalaxyTextRect)
        screen.blit(AndromedaGalaxyText, AndromedaGalaxyTextRect)

    if subgalaxy1:
        screen.blit(EarthyearCheck, EarthyearCheckRect)
        screen.fill('black')
        normalgreen = (175,255,175)
        darkgreen = (79,121,66)
        if not observeOrbitsBool:
            for planet in planets:
                planet.orbit.clear()

        if visualizeStarBool: 
            if len(backgroundStarsGroup) < 150:
                star = backgroundStars()
                backgroundStarsGroup.add(star)
            
            backgroundStarsGroup.draw(screen)



        #Buttons Section
        backButton.draw(screen)    
        screen.blit(backText, back)
        
        for planet in planets:
            if planet.TIMESTEP == 25200:
                speedUpButtonTextVariable = 'MAX'
            else:
                speedUpButtonTextVariable = 'SPD'
            if planet.TIMESTEP == 0:
                slowDownButtonTextVariable = 'MIN'
            else:
                slowDownButtonTextVariable = 'SLW'
            currentTimeStepText = smallFont.render('Current Time Step: ', False, 'White')
            displayCurrentTimeStep = smallFont.render(f'{(planet.TIMESTEP/60/24):.1f} days per tick.', False, 'White')
            screen.blit(currentTimeStepText, (630, 363))
            screen.blit(displayCurrentTimeStep, (640, 380))

        speedUpButton.draw(screen)
        slowDownButton.draw(screen)
        speedUpButtonText = smallFont.render(speedUpButtonTextVariable , False, 'Black')
        speedUpButtonTextRect = speedUpButtonText.get_rect(center = (675+45/2, 10+45/2))

        slowDownButtonText = smallFont.render(slowDownButtonTextVariable, False, 'Black')
        slowDownButtonTextRect = slowDownButtonText.get_rect(center = (725+45/2, 10+45/2))

        screen.blit(speedUpButtonText, speedUpButtonTextRect)
        screen.blit(slowDownButtonText, slowDownButtonTextRect)

        if speedUpButton.rect.collidepoint(mousePos):
            speedUpButton.colour = darkgreen
        else:
            speedUpButton.colour = normalgreen


        if slowDownButton.rect.collidepoint(mousePos):
            slowDownButton.colour = (155,0,0)
        else:
            slowDownButton.colour = (210,43,43)


        if EarthYearCounter <= 1:
            EarthYeartext = smallFont.render(f'Earth has been rotating for: {EarthYearCounter} year', False, 'White')
        else:
            EarthYeartext = smallFont.render(f'Earth has been rotating for: {EarthYearCounter} years', False, 'White')
        
        screen.blit(EarthYeartext, (20,375))
        
        for planet in planets:
            planet.updatePos(planets)
            planet.draw(screen)

        normalgreen = (175,255,175)
        darkgreen = (79,121,66)

        

        #information section
        for button in informationBoxeslst:
            button.draw(screen)
            if button != HideInformationBox:
                if button.rect.collidepoint(mousePos):
                    button.colour = (128,128,128)
                else:
                    button.colour = (192,192,192)
            else:
                if button.rect.collidepoint(mousePos):
                    button.colour = (119, 7, 55)
                else:
                    button.colour = (169, 92, 104)

        pyg.draw.circle(screen, (30,144,255), (750, 90), 18) #Earth
        pyg.draw.circle(screen, (136,8,8), (750, 150), 12) #Mars
        pyg.draw.circle(screen, (204,85,0), (750, 210), 14) #Venus
        pyg.draw.circle(screen, (105,105,105), (750, 270), 8) #Mercury
        pyg.draw.circle(screen, (255, 140, 100), (750, 330), 24) #Jupiter
        pyg.draw.circle(screen, (255,255,0), ( 690 ,90), 27) #Sun
        pyg.draw.circle(screen, (255,193,110), (690 ,150), 22) # Saturn
        pyg.draw.circle(screen, (8,143,143), (690,210 ), 20) #Uranus
        pyg.draw.circle(screen, (111,143,175), (690, 270), 18) #Neptune
        screen.blit(bigFont.render('X', False, 'black'), (680, 315))

        #Bliting the info section
        #if EarthInfoDisplay:
        
        if milkyWayDisplayDict["EarthInfoDisplay"]:
            blitInfoMilkyWay(EarthInfolst)
        if milkyWayDisplayDict["SunInfoDisplay"]: 
            blitInfoMilkyWay(SunInfolst)
        if milkyWayDisplayDict['JupiterInfoDisplay']:
            blitInfoMilkyWay(JupiterInfolst)
        if milkyWayDisplayDict['MercInfoDisplay']:
            blitInfoMilkyWay(MercInfolst)
        if milkyWayDisplayDict['MarsInfoDisplay']:
            blitInfoMilkyWay(MarsInfolst)
        if milkyWayDisplayDict['NeptuneInfoDisplay']:
            blitInfoMilkyWay(NeptuneInfolst)
        if milkyWayDisplayDict['UranusInfoDisplay']:
            blitInfoMilkyWay(UranusInfolst)
        if milkyWayDisplayDict['VenusInfoDisplay']:
            blitInfoMilkyWay(VenusInfolst)
        if milkyWayDisplayDict['SaturnInfoDisplay']:
            blitInfoMilkyWay(SaturnInfolst)
            
    if subgalaxy2:

        screen.fill('black')
        if not observeOrbitsBool:
            for planet in TRAPPISTplanets:
                planet.orbit.clear()
        
        normalgreen = (175,255,175)
        darkgreen = (79,121,66)
        if visualizeStarBool: 
            if len(backgroundStarsGroup) < 150:
                star = backgroundStars()
                backgroundStarsGroup.add(star)
            
            backgroundStarsGroup.draw(screen)

        for planet in TRAPPISTplanets:
            planet.SCALE = 550 / planet.AstroUnit
            planet.draw(screen)
            planet.updatePos(planets)

        for button in trappInformationBoxlst:
            button.draw(screen)
            if button != HideTrappistInformationBox:
                if button.rect.collidepoint(mousePos):
                    button.colour = (192,192,192)
                else:
                    button.colour = (128,128,128)
            else:
                if button.rect.collidepoint(mousePos):
                    button.colour = (119, 7, 55)
                else:
                    button.colour = (169, 92, 104)
        pyg.draw.circle(screen, ((255,69,0)), (750, 90), 24) #Sun
        pyg.draw.circle(screen, (210,105,30), (750, 150), 11) #Trappist 1b
        pyg.draw.circle(screen, (178,116,93), (750, 210), 13) #Trappist 1c
        pyg.draw.circle(screen, (255,182,193), (750, 270), 7) #Trappist 1d
        pyg.draw.circle(screen, (135,206,250), (690, 90), 10) #Trappist 1e
        pyg.draw.circle(screen, (173,216,230), ( 690 ,150), 10) #Trappist 1f
        pyg.draw.circle(screen, (176,196,222), (690 ,210), 14) #Trappist 1g
        pyg.draw.circle(screen, (169,169,169), (690 , 270), 6) #Trappist 1h

        for planet in TRAPPISTplanets:
            if planet.TIMESTEP == 25200:
                speedUpButtonTextVariable = 'MAX'
            else:
                speedUpButtonTextVariable = 'SPD'
            if planet.TIMESTEP == 0:
                slowDownButtonTextVariable = 'MIN'
            else:
                slowDownButtonTextVariable = 'SLW'
            currentTimeStepText = smallFont.render('Current Time Step: ', False, 'White')
            displayCurrentTimeStep = smallFont.render(f'{(planet.TIMESTEP/60/24):.1f} days per tick.', False, 'White')
            screen.blit(currentTimeStepText, (630, 363))
            screen.blit(displayCurrentTimeStep, (640, 380))

        speedUpButton.draw(screen)
        slowDownButton.draw(screen)
        speedUpButtonText = smallFont.render(speedUpButtonTextVariable , False, 'Black')
        speedUpButtonTextRect = speedUpButtonText.get_rect(center = (675+45/2, 10+45/2))

        slowDownButtonText = smallFont.render(slowDownButtonTextVariable, False, 'Black')
        slowDownButtonTextRect = slowDownButtonText.get_rect(center = (725+45/2, 10+45/2))
        screen.blit(speedUpButtonText, speedUpButtonTextRect)
        screen.blit(slowDownButtonText, slowDownButtonTextRect)

        if speedUpButton.rect.collidepoint(mousePos):
            speedUpButton.colour = darkgreen
        else:
            speedUpButton.colour = normalgreen

        if slowDownButton.rect.collidepoint(mousePos):
            slowDownButton.colour = (155,0,0)
        else:
            slowDownButton.colour = (210,43,43)

        screen.blit(bigFont.render('X', False, 'black'), (710, 315))
        backButton.draw(screen)
        screen.blit(backText, back)

        if t1DisplayDict["T_1InfoDisplay"]:
            blitInfot1(T_1Infolst)
        if t1DisplayDict["T1bInfoDisplay"]: 
            blitInfot1(T1bInfolst)
        if t1DisplayDict['T1cInfoDisplay']:
            blitInfot1(T1cInfolst)
        if t1DisplayDict['T1dInfoDisplay']:
            blitInfot1(T1dInfolst)
        if t1DisplayDict['T1eInfoDisplay']:
            blitInfot1(T1eInfolst)
        if t1DisplayDict['T1fInfoDisplay']:
            blitInfot1(T1fInfolst)
        if t1DisplayDict['T1gInfoDisplay']:
            blitInfot1(T1gInfolst)
        if t1DisplayDict['T1hInfoDisplay']:
            blitInfot1(T1hInfolst)
 
    if subgalaxy3:
        screen.fill('black')
        if visualizeStarBool: 
            if len(backgroundStarsGroup) < 150:
                star = backgroundStars()
                backgroundStarsGroup.add(star)
            
            backgroundStarsGroup.draw(screen)

        for planet in chudePlanets:
            if planet.TIMESTEP == 25200:
                speedUpButtonTextVariable = 'MAX'
            else:
                speedUpButtonTextVariable = 'SPD'
            if planet.TIMESTEP == 0:
                slowDownButtonTextVariable = 'MIN'
            else:
                slowDownButtonTextVariable = 'SLW'
            currentTimeStepText = smallFont.render('Current Time Step: ', False, 'White')
            displayCurrentTimeStep = smallFont.render(f'{(planet.TIMESTEP/60/24):.1f} days per tick.', False, 'White')
            screen.blit(currentTimeStepText, (630, 363))
            screen.blit(displayCurrentTimeStep, (640, 380))

        speedUpButton.draw(screen)
        slowDownButton.draw(screen)
        speedUpButtonText = smallFont.render(speedUpButtonTextVariable , False, 'Black')
        speedUpButtonTextRect = speedUpButtonText.get_rect(center = (675+45/2, 10+45/2))

        slowDownButtonText = smallFont.render(slowDownButtonTextVariable, False, 'Black')
        slowDownButtonTextRect = slowDownButtonText.get_rect(center = (725+45/2, 10+45/2))

        screen.blit(speedUpButtonText, speedUpButtonTextRect)
        screen.blit(slowDownButtonText, slowDownButtonTextRect)
        normalgreen = (175,255,175)
        darkgreen = (79,121,66)
        
        if speedUpButton.rect.collidepoint(mousePos):
            speedUpButton.colour = darkgreen
        else:
            speedUpButton.colour = normalgreen

        if slowDownButton.rect.collidepoint(mousePos):
            slowDownButton.colour = (155,0,0)
        else:
            slowDownButton.colour = (210,43,43)

        backButton.draw(screen)
        screen.blit(backText, back)

        for planet in chudePlanets:
            planet.SCALE = 70/planet.AstroUnit
            planet.draw(screen)
            planet.updatePos(chudePlanets)

        screen.blit(chudeDesc1, chudeDesc1Rect)
        screen.blit(chudeDesc2, chudeDesc2Rect)
        screen.blit(chudeDesc3, chudeDesc3Rect)
        screen.blit(chudeDesc4, chudeDesc4Rect)
        screen.blit(chudeDesc5, chudeDesc5Rect)
        screen.blit(chudeDesc6, chudeDesc6Rect)
        screen.blit(chudeDesc7, chudeDesc7Rect)
        screen.blit(chudeDesc8, chudeDesc8Rect)

    if optionState:
        screen.fill('Black')

        # Buttons with text section
        backButton.draw(screen)
        screen.blit(backText, back)

        screen.blit(optionTitleText, optionTextRect)

        for button in optionButtonlst:
            if button != backButton:
                button.draw(screen)
            if button == visualizeStar:
                button.colour = (175,255,175) if visualizeStarBool else (210,4,45)
            if button == observeOrbitButton:
                button.colour = (175,255,175) if observeOrbitsBool else (210,4,45)

        screen.blit(visualizeStarText, visualizeStarTextRect)
        screen.blit(observeOrbitText, observeOrbitTextRect)
        screen.blit(orbitChangeText, orbitChangeTextRect)
        screen.blit(text200, text200Rect)
        screen.blit(text600, text600Rect)
        screen.blit(text1000, text1000Rect)
        currentPixelLength = smallFont.render(f'Current pixel length : {pixelLength} px', False, 'white')
        currentPixelLengthRect = currentPixelLength.get_rect(center = (195,325))

        screen.blit(currentPixelLength, currentPixelLengthRect)


        if observeOrbitsBool:
            screen.blit(ONtext, observeOrbitONRect)
        else:
            screen.blit(OFFtext, observeOrbitOFFRect)

        if visualizeStarBool:
            screen.blit(ONtext, visualizeStarONRect)
        else:
            screen.blit(OFFtext, visualizeStarOFFRect)

        for button in pixelLengthOrbit:
            if button.rect.collidepoint(mousePos):
                button.colour = (128, 128, 128)
            else:
                button.colour = (169,169,169)



    if gameState:
        screen.fill('black')
        backButton.draw(screen)
        screen.blit(backText, back)

        for button in gameButtonlst:
            if button != backButton:
                button.draw(screen)
        screen.blit(peacefulButtonText, peacefulButtonTextRect)
        screen.blit(mediumButtonText, mediumButtonTextRect)
        screen.blit(hardcoreButtonText, hardcoreButtonTextRect)

        for button in gameButtonlst:
            if button in {peacefulButton , mediumButton, hardcoreButton}:
                if button.rect.collidepoint(mousePos):
                    button.colour = (128,128,128)
                else:
                    button.colour = (192,192,192)

    if peacefulState:
        screen.fill('black')
        
        #first choice, the sun
        if sunChoice:
            for elem in choiceboxlst:
                elem.draw(screen, mousePos)
            pyg.draw.circle(screen, (255,255,0), (choiceBox.rects[0].center), 22)
            pyg.draw.circle(screen, (0,255,255), (choiceBox.rects[1].center), 25)
            pyg.draw.circle(screen, (255, 99, 71), (choiceBox.rects[2].center), 27) #Sun3
            pyg.draw.circle(screen, (255,255,255), (choiceBox.rects[3].center), 22)
            pyg.draw.circle(screen, (175, 238, 238), (choiceBox2.rects[0].center), 25) 
            pyg.draw.circle(screen, (65, 105, 225), (choiceBox2.rects[1].center), 27) #Sun6
            pyg.draw.circle(screen, (95, 158, 160), (choiceBox2.rects[2].center), 20) 
            pyg.draw.circle(screen, (178, 34, 34), (choiceBox2.rects[3].center), 22) #Sun8 

            GamemodeText = smallFont.render('GAMEMODE :    PEACEFUL', False, 'white')
            GamemodeTextRect = GamemodeText.get_rect(center = (625, 50))
            screen.blit(GamemodeText, GamemodeTextRect)

            TimeScoreText = smallFont.render('SCORE TO WIN :', False, 'white')
            TimeScoreText2 = smallFont.render('N/A', False, 'white')
            screen.blit(TimeScoreText, TimeScoreText.get_rect(center = (625, 90)))
            screen.blit(TimeScoreText2, TimeScoreText2.get_rect(center = (625, 115)))

            DescriptionText = smallFont.render('DESCRIPTION : ', False, 'white')
            DescText2 = smallFont.render("Let your imagination run wild!", False, 'white')
            DescText3 = smallFont.render("You can't lose in this gamemode.", False, 'white')
            screen.blit(DescriptionText, DescriptionText.get_rect(center = (625, 150)))
            screen.blit(DescText2, DescText2.get_rect(center = (625, 175)))
            screen.blit(DescText3, DescText3.get_rect(center = (625, 195)))

            chooseButton.draw(screen)
            screen.blit(chooseText, chooseTextRect)

            if peacefulModeSun['Sun1Display']:
                blitInfoPeaceSun(Sun1Textlst)
            if peacefulModeSun['Sun2Display']:
                blitInfoPeaceSun(Sun2Textlst)
            if peacefulModeSun['Sun3Display']:
                blitInfoPeaceSun(Sun3Textlst)
            if peacefulModeSun['Sun4Display']:
                blitInfoPeaceSun(Sun4Textlst)
            if peacefulModeSun['Sun5Display']:
                blitInfoPeaceSun(Sun5Textlst)
            if peacefulModeSun['Sun6Display']:
                blitInfoPeaceSun(Sun6Textlst)
            if peacefulModeSun['Sun7Display']:
                blitInfoPeaceSun(Sun7Textlst)
            if peacefulModeSun['Sun8Display']:
                blitInfoPeaceSun(Sun8Textlst)



            if chooseButton.rect.collidepoint(mousePos):
                chooseButton.colour = (46, 139, 87)
            else:
                chooseButton.colour = (152, 251, 152)
            # DescText2 = smallFont.render("", False, 'white')
 
        if planetChoice: 
            screen.fill('black')

            for elem in planetChoiceBoxlst:
                elem.draw(screen, mousePos)
                # pyg.draw.circle(screen, (255,255,0), (choiceBox.rects[0].center), 25)
            pyg.draw.circle(screen, (178, 34, 34), (choiceBox.rects[0].center), 6)  # Planet1
            pyg.draw.circle(screen, (255, 69, 0), (choiceBox.rects[1].center), 7)  # Planet2
            pyg.draw.circle(screen, (255, 215, 0), (choiceBox.rects[2].center), 8)  # Planet3
            pyg.draw.circle(screen, (238, 232, 170), (choiceBox.rects[3].center), 9)  # Planet4
            pyg.draw.circle(screen, (255, 0, 255), (choiceBox2.rects[0].center), 10)  # Planet5
            pyg.draw.circle(screen, (106, 90, 205), (choiceBox2.rects[1].center), 11)  # Planet6
            pyg.draw.circle(screen, (173, 255, 47), (choiceBox2.rects[2].center), 12)  # Planet7
            pyg.draw.circle(screen, (255, 192, 203), (choiceBox2.rects[3].center), 13)  # Planet8
            pyg.draw.circle(screen, (255, 160, 122), (choiceBox3.rects[0].center), 14)  # Planet9
            pyg.draw.circle(screen, (255, 165, 0), (choiceBox3.rects[1].center), 15)  # Planet10
            # pyg.draw.circle(screen, (216, 191, 216), (choiceBox3.rects[2].center), 16)  # Planet11
            pyg.draw.circle(screen, (153, 50, 204), (choiceBox3.rects[3].center), 17)  # Planet12
            pyg.draw.circle(screen, (123, 104, 238), (choiceBox4.rects[0].center), 18)  # Planet13
            pyg.draw.circle(screen, (152, 251, 152), (choiceBox4.rects[1].center), 19)  # Planet14
            pyg.draw.circle(screen, (0, 255, 127), (choiceBox4.rects[2].center), 20)  # Planet15
            pyg.draw.circle(screen, (0, 100, 0), (choiceBox4.rects[3].center), 21)  # Planet16
            
            pyg.draw.circle(screen, (143, 188, 139), (choiceBox3.rects[2].center), 22)  # Planet17 in 11th Place

            # pyg.draw.circle(screen, (0, 128, 128), (choiceBox5.rects[1].center), 20)  # Planet18
            # pyg.draw.circle(screen, (0, 255, 255), (choiceBox5.rects[2].center), 21)  # Planet19
            # pyg.draw.circle(screen, (176, 196, 222), (choiceBox5.rects[3].center), 9)  # Planet20
            # pyg.draw.circle(screen, (0, 0, 205), (choiceBox6.rects[0].center), 24)  # PlanetX
            # pyg.draw.circle(screen, (255, 235, 205), (choiceBox6.rects[1].center), 5)  # PlanetY  
            # 

            GamemodeText = smallFont.render('GAMEMODE :    PEACEFUL', False, 'white')
            GamemodeTextRect = GamemodeText.get_rect(center = (625, 50))
            screen.blit(GamemodeText, GamemodeTextRect)

            TimeScoreText = smallFont.render('SCORE TO WIN :', False, 'white')
            TimeScoreText2 = smallFont.render('N/A', False, 'white')
            screen.blit(TimeScoreText, TimeScoreText.get_rect(center = (625, 90)))
            screen.blit(TimeScoreText2, TimeScoreText2.get_rect(center = (625, 115)))

            DescriptionText = smallFont.render('DESCRIPTION : ', False, 'white')
            DescText2 = smallFont.render("Let your imagination run wild!", False, 'white')
            DescText3 = smallFont.render("You can't lose in this gamemode.", False, 'white')
            screen.blit(DescriptionText, DescriptionText.get_rect(center = (625, 150)))
            screen.blit(DescText2, DescText2.get_rect(center = (625, 175)))
            screen.blit(DescText3, DescText3.get_rect(center = (625, 195)))

            chooseButton.draw(screen)
            screen.blit(chooseText, chooseTextRect)

            if peacefulModeSun['Sun1Display']:
                blitInfoPeaceSun(Sun1Textlst)
            if peacefulModeSun['Sun2Display']:
                blitInfoPeaceSun(Sun2Textlst)
            if peacefulModeSun['Sun3Display']:
                blitInfoPeaceSun(Sun3Textlst)
            if peacefulModeSun['Sun4Display']:
                blitInfoPeaceSun(Sun4Textlst)
            if peacefulModeSun['Sun5Display']:
                blitInfoPeaceSun(Sun5Textlst)
            if peacefulModeSun['Sun6Display']:
                blitInfoPeaceSun(Sun6Textlst)
            if peacefulModeSun['Sun7Display']:
                blitInfoPeaceSun(Sun7Textlst)
            if peacefulModeSun['Sun8Display']:
                blitInfoPeaceSun(Sun8Textlst)

            if peacefulModePlanet['Planet1Display']:
                blitInfoPeacePlanet(Planet1Textlst)
            if peacefulModePlanet['Planet2Display']:
                blitInfoPeacePlanet(Planet2Textlst)
            if peacefulModePlanet['Planet3Display']:
                blitInfoPeacePlanet(Planet3Textlst)
            if peacefulModePlanet['Planet4Display']:
                blitInfoPeacePlanet(Planet4Textlst)
            if peacefulModePlanet['Planet5Display']:
                blitInfoPeacePlanet(Planet5Textlst)
            if peacefulModePlanet['Planet6Display']:
                blitInfoPeacePlanet(Planet6Textlst)
            if peacefulModePlanet['Planet7Display']:
                blitInfoPeacePlanet(Planet7Textlst)
            if peacefulModePlanet['Planet8Display']:
                blitInfoPeacePlanet(Planet8Textlst)
            if peacefulModePlanet['Planet9Display']:
                blitInfoPeacePlanet(Planet9Textlst)
            if peacefulModePlanet['Planet10Display']:
                blitInfoPeacePlanet(Planet10Textlst)
            if peacefulModePlanet['Planet11Display']:
                blitInfoPeacePlanet(Planet11Textlst)
            if peacefulModePlanet['Planet12Display']:
                blitInfoPeacePlanet(Planet12Textlst)
            if peacefulModePlanet['Planet13Display']:
                blitInfoPeacePlanet(Planet13Textlst)
            if peacefulModePlanet['Planet14Display']:
                blitInfoPeacePlanet(Planet14Textlst)
            if peacefulModePlanet['Planet15Display']:
                blitInfoPeacePlanet(Planet15Textlst)
            if peacefulModePlanet['Planet16Display']:
                blitInfoPeacePlanet(Planet16Textlst)
            if peacefulModePlanet['Planet17Display']:
                blitInfoPeacePlanet(Planet17Textlst)
            if peacefulModePlanet['Planet18Display']:
                blitInfoPeacePlanet(Planet18Textlst)
            if peacefulModePlanet['Planet19Display']:
                blitInfoPeacePlanet(Planet19Textlst)
            if peacefulModePlanet['Planet20Display']:
                blitInfoPeacePlanet(Planet20Textlst)
            if peacefulModePlanet['PlanetXDisplay']:
                blitInfoPeacePlanet(PlanetXTextlst)
            if peacefulModePlanet['PlanetYDisplay']:
                blitInfoPeacePlanet(PlanetYTextlst)



            if chooseButton.rect.collidepoint(mousePos):
                chooseButton.colour = (46, 139, 87)
            else:
                chooseButton.colour = (152, 251, 152)

        if simulationPeaceful:
            screen.fill('black') 

            current_time = pyg.time.get_ticks()
            if current_time - comet_last_reset >= 7000:  # 7000 millisecondes = 7 secondes
                peacefulPlanetlst.remove(comet)
                comet = generate_random_comet()
                peacefulPlanetlst.append(comet)
                comet_last_reset = current_time

            if visualizeStarBool: 
                if len(backgroundStarsGroup) < 150:
                    star = backgroundStars()
                    backgroundStarsGroup.add(star)
            
            backgroundStarsGroup.draw(screen)
            print(peacefulPlanetlst)
            for planet in peacefulPlanetlst:
                planet.draw(screen)
                planet.TIMESTEP = 3600*24
                planet.updatePos(peacefulPlanetlst)
            
            backButton.draw(screen)
            screen.blit(backText, back)


    if mediumState:
        screen.fill('black')
    
    if hardcoreState:
        screen.fill('black')



    # Back button hover thingy for all sections
    defaultBack = (255, 0, 0)
    darkerBack = (155, 0, 0)
    if backButton.rect.collidepoint(mousePos):
        backButton.colour = darkerBack
    else:
        backButton.colour = defaultBack

    pyg.display.flip()
    
    if subgalaxy2: 
        clock.tick(220)
    elif peacefulState:
        clock.tick(1000)
    elif subgalaxy3:
        clock.tick(820)
    elif not subgalaxy1:
        clock.tick(FPS)



