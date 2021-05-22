import random as rd
import pygame
from pygame.locals import *
import sys
import math

MAX_X = 640
MAX_Y = 480

def distance(p1, p2):
    return math.sqrt( ((int(p1[0])-int(p2[0]))**2)+((int(p1[1])-int(p2[1]))**2) )


class Blob:
    def __init__(self):
        self.color = "#"+''.join([rd.choice('0123456789ABCDEF') for j in range(6)])
        self.radius = rd.randint(5,20)
        self.energy = 10
        self.sight = 100


        self.coord = (rd.randint(0,MAX_X),  rd.randint(0,MAX_Y))
        self.goal = (rd.randint(0,MAX_X),  rd.randint(0,MAX_Y))
        self.wait = 1000

    def draw(self, DISPLAYSURF, simulation: 'Simulation'):
        self.energy -= 1/500

        dx, dy = (self.goal[0] - self.coord[0], self.goal[1] - self.coord[1])
        stepx, stepy = (dx / 500., dy / 500.)

        new_x = self.coord[0] + stepx
        new_y = self.coord[1] + stepy

        if stepy < 1 and stepx < 1:
            self.wait -= 1

        if self.wait <= 0:
            nearest_food = simulation.get_nearest_food(self.coord) 
            if distance(nearest_food.coord, self.coord) <= self.sight:
                self.goal = nearest_food.coord
            else:
                self.goal = (rd.uniform(self.coord[0] - 100, self.coord[0] + 100),  rd.uniform(self.coord[1] - 100, self.coord[1] + 100))
            self.wait = 500

        if new_x > MAX_X:
            new_x = MAX_X
        
        if new_x < 0:
            new_x = 0

        if new_y > MAX_Y:
            new_y = MAX_Y
        
        if new_y < 0:
            new_y = 0

        new_coord = (new_x, new_y)
        self.coord = new_coord
        pygame.draw.circle(DISPLAYSURF, self.color, self.coord, self.radius)

    

class Food:
    def __init__(self):
        self.coord = (rd.randint(0,MAX_X),  rd.randint(0,MAX_Y))

    def draw(self, DISPLAYSURF):
        pygame.draw.circle(DISPLAYSURF, (0, 255, 0), self.coord, 4)


class Simulation:
    def __init__(self, food_time):
        pygame.init()
        self.DISPLAYSURF = pygame.display.set_mode((MAX_X, MAX_Y))
        # self.DISPLAYSURF.fill((255, 255, 255))
        fps = pygame.time.Clock()
        fps.tick(25)
        self.food_time = food_time
        self.blobs = [Blob() for i in range(5)]
        self.food = [Food() for i in range(50)]
    
    def get_nearest_food(self, p1):

        return min(self.food, key=lambda f: distance(f.coord, p1))
            

    def run(self):
        
        wait = 0

        while True:
            self.DISPLAYSURF.fill((0, 0, 0))
            
            for b in self.blobs:
                for f in self.food:
                    if distance(b.coord, f.coord) <= b.radius:
                        b.energy += 10
                        self.food.remove(f)
                b.draw(self.DISPLAYSURF, self)
                
                if b.energy <= 0:
                    self.blobs.remove(b)

            for f in self.food:
                f.draw(self.DISPLAYSURF)

            if wait >= self.food_time:
                self.food.append(Food())
                wait = 0

            else:
                wait += 1

            if len(self.blobs) < 5:
                self.blobs.append(Blob())


            pygame.display.update()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()


def main():
   d = Simulation(1000)
   d.run()


if __name__ == "__main__":
    main()