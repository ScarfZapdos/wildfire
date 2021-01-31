import sys, math, random
import pygame
import pygame.draw
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

__screenSize__ = (900,900)
#__screenSize__ = (1280,1280)
__cellSize__ = 10
__gridDim__ = tuple(map(lambda x: int(x/__cellSize__), __screenSize__))
__density__ = 3
__probability__ = 0.55
__fireprob__ = 0.80
__lightningprob__ = 0.00001
__regrowthprob__ = 0.005
__rivernbprob__ = [0.1,0.35,0.4,0.15]
#__riverwidthprob__ = [0,0,0,0.5,0]
__water__ = np.full(__gridDim__, 4, dtype='int8')
wind_c = (0,0)
__colors__ = [(255,255,255),(0,150,0),(150,0,0),(200,200,0),(50,50,210)]


glidergun=[
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
  [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
  [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

def getColorCell(n):
    return __colors__[n]

class Grid:
    _grid= None
    _gridbis = None
    #_indexVoisins = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    _indexVoisins = [(-1,0),(0,-1),(0,1),(1,0)]
    _indexProba = [0,0,0,0]
    _wind = (0,0)
    def __init__(self):
        print("Creating a grid of dimensions " + str(__gridDim__))
        self._grid = np.zeros(__gridDim__, dtype='int8')
        self._gridbis = np.zeros(__gridDim__, dtype='int8')
        nx, ny = __gridDim__
        if False: # True to init with one block at the center
            self._grid[nx//2,ny//2] = 1
            self._grid[nx//2+1,ny//2] = 1
            self._grid[nx//2,ny//2+1] = 1
            self._grid[nx//2+1,ny//2+1] = 1
        elif True: # True to init with random values at the center
            #mx, my = 20, 16
            ones = np.around(np.random.random(self._grid.shape)+__probability__ - 0.5).astype(int)
            ones[nx//2,ny//2] = 2
            ones[nx//2+1,ny//2] = 2
            ones[nx//2,ny//2+1] = 2
            ones[nx//2+1,ny//2+1] = 2
            #Spawn rivers
            for k in range(2):
                nbrivers = np.random.choice(4,p=__rivernbprob__)
                print(nbrivers)
                for i in range(nbrivers):
                    #widthriver = np.random.choice(5,p=__riverwidthprob__)
                    #print(widthriver)
                    randi = np.random.randint(1,__gridDim__[0]-1)#-widthriver)
                    f=1
                    for l in range(__gridDim__[0]):
                        randj = np.random.randint(6)
                        print("randj="+str(randj))
                        print("randi+f="+str(randi+f))
                        if k==0:
                            ones[randi+f,l] = __water__[randi+f,l]
                            ones[randi,l] = __water__[randi,l]
                        if k==1:
                            ones[l,randi+f] = __water__[l,randi+f]
                            ones[l,randi] = __water__[l,randi]
                        if randj==0:
                            f=-f
            #self._grid[nx//2-mx//2:nx//2+mx//2, ny//2-my//2:ny//2+my//2] = ones
            self._grid = ones

        else: # Else if init with glider gun
            a = np.fliplr(np.rot90(np.array(glidergun),3))
            mx, my = a.shape
            self._grid[nx//2-mx//2:nx//2+mx//2, ny//2-my//2:ny//2+my//2] = a

    def set_wind(self,x,y):
        self.wind = (x,y)

    def update_index_v(self):
        d = self.wind
        p = __fireprob__
        if d[1]==0: # West or East
            self._indexVoisins = [(d[0],0),(2*d[0],0),(3*d[0],0),(d[0],-1),(2*d[0],-1),(3*d[0],-1),(d[0],1),(2*d[0],1),(3*d[0],1)]
            self._indexProba = [p,p,p*0.9,p*0.5,p*0.8,p*0.35,p*0.5,p*0.8,p*0.35]
        elif d[0]==0: # North or South
            self._indexVoisins = [(0,d[1]),(0,2*d[1]),(0,3*d[1]),(-1,d[1]),(-1,2*d[1]),(-1,3*d[1]),(1,d[1]),(1,2*d[1]),(1,3*d[1])]
            self._indexProba = [p,p,p*0.9,p*0.5,p*0.8,p*0.35,p*0.5,p*0.8,p*0.35]
        else:
            self._indexVoisins = [(d[0],0),(2*d[0],0),(0,d[1]),(0,2*d[1]),(d[0],d[1]),(2*d[0],d[1]),(d[0],2*d[1]),(2*d[0],2*d[1])]
            #self._indexProba = [0,0,0,0,p,0,0,p*0.4]
            self._indexProba = [p*0.55,p*0.35,p*0.55,p*0.35,p,p*0.5,p*0.5,p*0.6]

        print(self._indexVoisins)
        print(self._indexProba)

    def indiceVoisins(self, x,y):
        return [(dx+x,dy+y) for (dx,dy) in self._indexVoisins if dx+x >=0 and dx+x < __gridDim__[0] and dy+y>=0 and dy+y < __gridDim__[1]]

    def voisins(self,x,y):
        return [self._grid[vx,vy] for (vx,vy) in self.indiceVoisins(x,y)]

    def sommeVoisins(self, x, y):
        return sum(self.voisins(x,y))

    def sumEnumerate(self):
        return [(c, self.sommeVoisins(c[0], c[1])) for c, _ in np.ndenumerate(self._grid)]

    def closeFire(self,x,y):
        bool = False
        max_prob = 0
        k = 0
        for x in self.voisins(x,y):
            bool = bool or (x==2)
            if self._indexProba[k]>max_prob and x==2:
                max_prob = self._indexProba[k]
            k+=1
        return bool,max_prob

    def drawMe(self):
        pass

class Scene:
    _mouseCoords = (0,0)
    _grid = None
    _font = None

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode(__screenSize__)
        self._font = pygame.font.SysFont('Arial',25)
        self._grid = Grid()

    def drawMe(self):
        if self._grid._grid is None:
            return
        self._screen.fill((120,120,120))
        for x in range(__gridDim__[0]):
            for y in range(__gridDim__[1]):
                pygame.draw.rect(self._screen,
                        getColorCell(self._grid._grid.item((x,y))),
                        (x*__cellSize__ + 1, y*__cellSize__ + 1, __cellSize__-2, __cellSize__-2))


    def drawText(self, text, position, color = (255,64,64)):
        self._screen.blit(self._font.render(text,1,color),position)

    def update(self):
        '''B234/S rule'''
        for c, s in self._grid.sumEnumerate():
            self._grid._gridbis[c[0], c[1]] = 1 if (2 <= s <= 4) and self._grid._grid[c[0],c[1]] == 0 else 0
        self._grid._grid = np.copy(self._grid._gridbis)

    def updatebis(self):
        for c, s in self._grid.sumEnumerate():
            if self._grid._grid[c[0],c[1]] == 1:
                ret = 2 <= s <= 3
            else:
                ret = s == 3
            self._grid._gridbis[c[0], c[1]] = 1 if ret else 0
        self._grid._grid = np.copy(self._grid._gridbis)

    def updateBrain(self):
        for c, s in self._grid.sumEnumerate():
            if self._grid._grid[c[0],c[1]] == 2:
                ret = 0
            elif self._grid._grid[c[0],c[1]] == 1:
                ret = 2
            else:
                ret = 1 if s == 2 else 0
            self._grid._gridbis[c[0], c[1]] = ret
        self._grid._grid = np.copy(self._grid._gridbis)

    def updateRule(self, B, S):
        # Maze is B3/S12345
        ''' Many rules in https://www.conwaylife.com/wiki/List_of_Life-like_cellular_automata '''
        for c, s in self._grid.sumEnumerate():
            if self._grid._grid[c[0],c[1]] == 1:
                ret = s in S
            else:
                ret = s in B
            self._grid._gridbis[c[0], c[1]] = 1 if ret else 0
        self._grid._grid = np.copy(self._grid._gridbis)

    def updateFire(self):
        for c, s in self._grid.sumEnumerate():
            if self._grid._grid[c[0],c[1]] == 2:
                ret = 0
            if self._grid._grid[c[0],c[1]] == 4:
                ret = 4
            elif self._grid._grid[c[0],c[1]] == 1:
                bool,p = self._grid.closeFire(c[0],c[1])
                if bool:
                    randy = np.random.random()
                    if randy < p:
                        ret = 2
                    else:
                        ret = 1
                else:
                    randy = np.random.random()
                    if randy < __lightningprob__:
                        ret = 3
                    else:
                        ret = 1
            elif self._grid._grid[c[0],c[1]] == 3:
                ret = 2
            else:
                randy = np.random.random()
                if randy < __regrowthprob__:
                    ret = 1
                else:
                    ret = 0
            self._grid._gridbis[c[0], c[1]] = ret
        self._grid._grid = np.copy(self._grid._gridbis)


    def eventClic(self, coord, b):
        pass

    def recordMouseMove(self, coord):
        pass

def main():
    print("What is the direction of the wind ? (n/s/w/e/nw/ne/se/sw)")
    valid_wind_dir = False
    while not valid_wind_dir:
        try:
            wind_dir = input()
            assert (wind_dir == "n" or wind_dir == "e" or wind_dir == "w" or wind_dir == "s" or wind_dir == "nw" or wind_dir == "ne" or wind_dir == "sw" or wind_dir == "se")
            valid_wind_dir  = True
        except AssertionError:
            print("Not a valid direction ! Try again.")

    scene = Scene()

    if (wind_dir == "n"):
        scene._grid.set_wind(0,1)
    elif (wind_dir == "s"):
        scene._grid.set_wind(0,-1)
    elif (wind_dir == "e"):
        scene._grid.set_wind(-1,0)
    elif (wind_dir == "w"):
        scene._grid.set_wind(1,0)
    elif (wind_dir == "nw"):
        scene._grid.set_wind(1,1)
    elif (wind_dir == "ne"):
        scene._grid.set_wind(-1,1)
    elif (wind_dir == "se"):
        scene._grid.set_wind(-1,-1)
    elif (wind_dir == "sw"):
        scene._grid.set_wind(1,-1)

    scene._grid.update_index_v()

    print("Initial tree spawn probability = " + str(__probability__))
    print("Fire propagation probability = " + str(__fireprob__))
    print("Lightning strike probability = " + str(__lightningprob__))
    print("Tree respawning probability = " + str(__regrowthprob__))
    done = False
    running = True
    pause_text = pygame.font.SysFont('Consolas', 32).render('Pause', True, pygame.color.Color('White'))
    clock = pygame.time.Clock()
    while done == False:
        if running == True:
            scene.drawMe()
            pygame.display.flip()
            pygame.display.set_mode(__screenSize__)
        #scene.updatebis()
        #scene.updateBrain()
        #scene.updateRule([3],[2,3]) # Glider Gun
        #scene.updateRule([2,3,4],[]) # Carpets
        #scene.updateRule([3],[1,2,3,4,5]) # Maze
            scene.updateFire()
            clock.tick(25)

        elif running == False:
            scene._screen.blit(pause_text, (100, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Exiting")
                done=True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mp = pygame.mouse.get_pos()
                print(mp)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    running = not running

    pygame.quit()

if not sys.flags.interactive: main()
