import pygame
import sys
import random
import time
import math
from queue import PriorityQueue

pygame.init()

WIDTH = 1200
HEIGHT = 800
GRID_WIDTH = 800
ROWS = 30

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Pathfinding")

FONT = pygame.font.SysFont("Segoe UI", 18)


# ===== CYBERPUNK NEON =====
BG = (12, 12, 20)
PANEL = (28, 18, 40)
TEXT = (255, 240, 255)

BUTTON = (255, 0, 140)
BUTTON_BORDER = (0, 255, 255)

START = (0, 255, 255)
GOAL = (57, 255, 20)
BARRIER = (50, 50, 70)
OPEN = (255, 255, 0)
CLOSED = (255, 60, 120)
PATH = (0, 255, 200)
GRID_LINE = (40, 40, 70)

class Node:
    def __init__(self,row,col,width,total):
        self.row=row
        self.col=col
        self.x=col*width
        self.y=row*width
        self.width=width
        self.total=total
        self.color=BG
        self.neighbors=[]

    def __lt__(self, other):
        return False

    def __hash__(self):
        return hash((self.row, self.col))

    def __eq__(self, other):
        return (self.row, self.col) == (other.row, other.col)

    def draw(self):
        pygame.draw.rect(WIN,self.color,(self.x,self.y,self.width,self.width),border_radius=4)

    def reset(self): self.color=BG
    def make_start(self): self.color=START
    def make_goal(self): self.color=GOAL
    def make_barrier(self): self.color=BARRIER
    def make_open(self): self.color=OPEN
    def make_closed(self): self.color=CLOSED
    def make_path(self): self.color=PATH
    def is_barrier(self): return self.color==BARRIER

    def update_neighbors(self,grid):
        self.neighbors=[]
        if self.row<self.total-1 and not grid[self.row+1][self.col].is_barrier():
            self.neighbors.append(grid[self.row+1][self.col])
        if self.row>0 and not grid[self.row-1][self.col].is_barrier():
            self.neighbors.append(grid[self.row-1][self.col])
        if self.col<self.total-1 and not grid[self.row][self.col+1].is_barrier():
            self.neighbors.append(grid[self.row][self.col+1])
        if self.col>0 and not grid[self.row][self.col-1].is_barrier():
            self.neighbors.append(grid[self.row][self.col-1])

# ================= BUTTON =================
class Button:
    def __init__(self,x,y,w,h,text):
        self.rect=pygame.Rect(x,y,w,h)
        self.text=text

    def draw(self):
        pygame.draw.rect(WIN,BUTTON,self.rect,border_radius=8)
        pygame.draw.rect(WIN,BUTTON_BORDER,self.rect,2,border_radius=8)
        label=FONT.render(self.text,True,TEXT)
        WIN.blit(label,(self.rect.x+15,self.rect.y+10))

    def clicked(self,pos):
        return self.rect.collidepoint(pos)

# ================= GRID =================
def make_grid(rows,width):
    grid=[]
    gap=width//rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            grid[i].append(Node(i,j,gap,rows))
    return grid

def draw_grid(grid):
    for row in grid:
        for node in row:
            node.draw()

    gap=GRID_WIDTH//ROWS
    for i in range(ROWS):
        pygame.draw.line(WIN,GRID_LINE,(0,i*gap),(GRID_WIDTH,i*gap))
        pygame.draw.line(WIN,GRID_LINE,(i*gap,0),(i*gap,GRID_WIDTH))

# ================= SEARCH =================
def manhattan(a,b):
    return abs(a[0]-b[0])+abs(a[1]-b[1])

def reconstruct(came,current):
    while current in came:
        current=came[current]
        current.make_path()

def run_search(grid,start,goal,algorithm):
    open_set=PriorityQueue()
    open_set.put((0,id(start),start))
    came={}
    g={node:float("inf") for row in grid for node in row}
    g[start]=0
    nodes=0
    start_time=time.time()

    while not open_set.empty():
        current=open_set.get()[2]
        nodes+=1

        if current==goal:
            reconstruct(came,goal)
            return nodes,g[goal],(time.time()-start_time)*1000

        for n in current.neighbors:
            temp=g[current]+1
            if temp<g[n]:
                came[n]=current
                g[n]=temp
                h=manhattan((n.row,n.col),(goal.row,goal.col))

                f = h if algorithm=="Greedy" else temp+h
                open_set.put((f,id(n),n))
                n.make_open()

        if current!=start:
            current.make_closed()

    return 0,0,0

# ================= MAIN =================
def main():
    grid=make_grid(ROWS,GRID_WIDTH)
    start=None
    goal=None
    nodes=0
    cost=0
    time_ms=0
    selected_algo="A*"

    run_btn=Button(GRID_WIDTH+50,200,300,50,"Run Search")
    reset_btn=Button(GRID_WIDTH+50,270,300,50,"Reset Grid")
    random_btn=Button(GRID_WIDTH+50,340,300,50,"Random Obstacles")
    algo_btn=Button(GRID_WIDTH+50,130,300,50,"Algorithm: A*")

    running=True
    while running:
        WIN.fill(BG)
        draw_grid(grid)
        pygame.draw.rect(WIN,PANEL,(GRID_WIDTH,0,400,HEIGHT))

        algo_btn.text=f"Algorithm: {selected_algo}"
        algo_btn.draw()
        run_btn.draw()
        reset_btn.draw()
        random_btn.draw()

        info=[
            f"Nodes Expanded: {nodes}",
            f"Path Cost: {cost}",
            f"Execution Time: {round(time_ms,2)} ms"
        ]

        y=450
        for line in info:
            text=FONT.render(line,True,TEXT)
            WIN.blit(text,(GRID_WIDTH+60,y))
            y+=35

        pygame.display.update()

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False

            if event.type==pygame.MOUSEBUTTONDOWN:
                pos=pygame.mouse.get_pos()

                if pos[0]>=GRID_WIDTH:
                    if algo_btn.clicked(pos):
                        selected_algo="Greedy" if selected_algo=="A*" else "A*"

                    if run_btn.clicked(pos) and start and goal:
                        for row in grid:
                            for node in row:
                                node.update_neighbors(grid)
                        nodes,cost,time_ms=run_search(grid,start,goal,selected_algo)

                    if reset_btn.clicked(pos):
                        grid=make_grid(ROWS,GRID_WIDTH)
                        start=None
                        goal=None
                        nodes=cost=time_ms=0

                    if random_btn.clicked(pos):
                        for row in grid:
                            for node in row:
                                if random.random()<0.25 and node!=start and node!=goal:
                                    node.make_barrier()

                else:
                    gap=GRID_WIDTH//ROWS
                    col=pos[0]//gap
                    row=pos[1]//gap

                    if 0<=row<ROWS and 0<=col<ROWS:
                        node=grid[row][col]

                        if not start:
                            start=node
                            start.make_start()
                        elif not goal and node!=start:
                            goal=node
                            goal.make_goal()
                        elif node!=start and node!=goal:
                            node.make_barrier()

    pygame.quit()
    sys.exit()

main()