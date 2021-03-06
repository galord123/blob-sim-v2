import random as rd
import pygame
from pygame.locals import *
import sys
import math
import threading
import graph
from concurrent.futures import ThreadPoolExecutor
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import time
import numpy as np

MAX_X = 640
MAX_Y = 480
MUTATION_RATE = 0.2

def distance(p1, p2):
    return math.sqrt(((int(p1[0])-int(p2[0]))**2)+((int(p1[1])-int(p2[1]))**2))


def mutation(genome):

    if rd.random() < MUTATION_RATE:
        return genome

    index = rd.randint(0, len(genome) - 1)
    if index == 0:
        temp = list(genome[index])
        temp[rd.randint(1, len(genome[index]) - 1)] = rd.choice('0123456789ABCDEF')
        genome[index] = "".join(temp)
    
    else:
        genome[index] += rd.randint(-1, 1)

    return genome


def crossover(a: 'Blob', b: 'Blob'):
    p = rd.randint(1, len(a.genome) - 1)

    a_genome = a.genome[0:p] + b.genome[p:]
    b_genome = b.genome[0:p] + a.genome[p:]

    return Blob(mutation(a_genome)), Blob(mutation(b_genome))


class Blob:
    def __init__(self, genome=[]):
        self.genome = genome

        if len(genome) == 0:
            self.color = "#"+''.join([rd.choice('0123456789ABCDEF') for j in range(6)])
            self.radius = rd.randint(5, 20)

            self.sight = rd.randint(50, 150)
            self.speed = rd.randint(30, 50)

            self.genome.append(self.color)
            self.genome.append(self.radius)
            self.genome.append(self.sight)
            self.genome.append(self.speed)

        else:
            self.color = genome[0]
            self.radius = genome[1]
            self.sight = genome[2]
            self.speed = genome[3]

        self.state = 1
        self.energy = 10
        self.coord = (rd.randint(0, MAX_X),  rd.randint(0, MAX_Y))
        self.goal = (rd.randint(0, MAX_X),  rd.randint(0, MAX_Y))
        self.wait = 50
        self.produce_timer = 10

    def draw(self, DISPLAYSURF, simulation: 'Simulation', delta_time):
        self.energy -= 1/500
        self.produce_timer -= 1/500

        dx, dy = (self.goal[0] - self.coord[0], self.goal[1] - self.coord[1])
        length = math.sqrt(dx*dx + dy*dy)
        if length == 0:
            length = 1
        dx /= length
        dy /= length
        stepx, stepy = (dx * self.speed * delta_time, dy * self.speed * delta_time)

        new_x = self.coord[0] + stepx
        new_y = self.coord[1] + stepy

        if self.energy <= 5:
            self.state = 1

        elif self.produce_timer <= 0:
            self.state = 2

        if stepy < 1 and stepx < 1:
            self.wait -= 1

        nearest_blob = simulation.get_nearest_blob(self.coord)

        if self.state == 2 and nearest_blob.state == 2 and distance(nearest_blob.coord, self.coord) <= self.radius:
            self.state = 1
            self.produce_timer = 10
            child_a, child_b = crossover(nearest_blob, self)
            simulation.blobs.append(child_a)
            simulation.blobs.append(child_b)

        if self.wait <= 0:
            nearest_food = simulation.get_nearest_food(self.coord)
            nearest_blob = simulation.get_nearest_blob(self.coord)

            if nearest_blob != self and distance(nearest_blob.coord, self.coord) <= self.sight and self.state == 2:
                self.goal = nearest_blob.coord

            elif distance(nearest_food.coord, self.coord) <= self.sight and self.state == 1:
                self.goal = nearest_food.coord

            else:
                self.goal = (rd.uniform(self.coord[0] - 100, self.coord[0] + 100),  rd.uniform(self.coord[1] - 100, self.coord[1] + 100))

            self.wait = 50

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
        pygame.draw.circle(DISPLAYSURF, self.color, self.coord, self.sight, width=1)

    
class Food:
    def __init__(self):
        self.coord = (rd.randint(0, MAX_X),  rd.randint(0, MAX_Y))

    def draw(self, DISPLAYSURF):
        pygame.draw.circle(DISPLAYSURF, (0, 255, 0), self.coord, 4)


class Simulation:
    def __init__(self, food_time, num_of_blobs):
        pygame.init()
        self.DISPLAYSURF = pygame.display.set_mode((MAX_X, MAX_Y))
        # self.DISPLAYSURF.fill((255, 255, 255))
        fps = pygame.time.Clock()
        fps.tick(25)
        self.food_time = food_time
        self.blobs = [Blob([]) for i in range(num_of_blobs)]
        self.blobs_num_over_time = [len(self.blobs),]
        
        self.food = [Food() for i in range(50)]
        self.lock = threading.Lock()
        self.terminate = False
        self.main_game_thread: threading.Thread
        # self.thread_executor: ThreadPoolExecutor = ThreadPoolExecutor()

    def get_nearest_food(self, p1):
        if len(self.food) == 0:
            return Food()

        return min(self.food, key=lambda f: distance(f.coord, p1))

    def get_nearest_blob(self, p1):
        return min(self.blobs, key=lambda f: distance(f.coord, p1) if p1 != f.coord else 20000)

    def handle_events(self):
        wait = 0
        update_wait = 0
        prev_time = time.time()
        now_time = time.time()
    
        while True:
            self.DISPLAYSURF.fill((255, 255, 255))
            
            now_time = time.time()
            delta_time = now_time - prev_time 
            prev_time = now_time
            
            for b in self.blobs:
                for f in self.food:
                    if distance(b.coord, f.coord) <= b.radius:
                        b.energy += 2
                        self.food.remove(f)
                b.draw(self.DISPLAYSURF, self, delta_time)
                # print(b.state)
                
                if b.energy <= 0:
                    self.blobs.remove(b)

            for f in self.food:
                f.draw(self.DISPLAYSURF)

            if wait >= self.food_time:
                for i in range(10):
                    self.food.append(Food())
                wait = 0

            else:
                wait += 1


            blobs_num = len(self.blobs)

            if wait >= 500 and not self.lock.locked():
                with self.lock:
                    
                    self.blobs_num_over_time.append(blobs_num)
                # self.lock.release()
                wait = 0            
            else:
                wait += 1    

            if blobs_num < 5:
                self.blobs.append(Blob([]))


            pygame.display.update()
            for event in pygame.event.get():
                if event.type == QUIT or self.terminate:
                    pygame.quit()
                    sys.exit()
            

    def run(self):
        # self.thread_executor. target=self.handle_events, args=(self,))
        self.main_game_thread = threading.Thread(target=self.handle_events)
        self.main_game_thread.start()
        try:
            choice = input("enter monitor mode:")
            if choice == "p":
                show_blob_population(self)
            else:
                self.terminate = True

        except KeyboardInterrupt:
            pygame.quit()
            

def show_blob_population(simulation: Simulation):
    x_vals = []
    

    time.sleep(1)
    if not simulation.lock.locked():
        
        ani = FuncAnimation(plt.gcf(), graph.animate, fargs=(simulation,), interval=1000)
        plt.tight_layout()
        plt.show()
            


def main():
    d = Simulation(500, 10)
    d.run()


if __name__ == "__main__":
    main()
