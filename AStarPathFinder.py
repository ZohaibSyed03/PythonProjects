import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption('A* Path Finding Algorithm')

RED = (255, 0, 0)
BLUE = (0, 0 ,255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREEN = (10, 100, 23)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
TURQUOISE = (64, 225, 208)

class Node:
    def __init__(self, row, col, width, totalRows) :
        self.row = row
        self.col = col
        self.x = row * width                                # This helps keep track of where on the display you are at
        self.y = col * width                                # WHatever row/col you're at times the width of the cubes = your position
        self.totalRows = totalRows
        self.color = WHITE
        self.borders = []
        self.width = width

    # Getter methods

    def getPosition(self):
        return self.row, self.col

    def isClosed(self):
        return self.color == RED
    
    def isOpen(self):
        return self.color == GREEN
    
    def isBarrier(self):
        return self.color == BLACK
    
    def isStartPos(self):
        return self.color == ORANGE
    
    def isEndGoal(self):
        return self.color == TURQUOISE
    
    # Setter methods
    
    def resetNode(self):
        self.color = WHITE
    
    def setOpen(self):
        self.color = GREEN
    
    def setClosed(self):
        self.color = RED

    def setBarrier(self):
        self.color = BLACK
    
    def setStartPos(self):
        self.color = ORANGE

    def setEndGoal(self):
        self.color = TURQUOISE

    def setAsPath(self):
        self.color = DARKGREEN

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

    def updateBorders(self, grid):
        self.borders = []
        if self.row < self.totalRows - 1 and not grid[self.row + 1][self.col].isBarrier(): # checking if you can add downward node to open list
            self.borders.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].isBarrier(): # checking if you can add upward node to open list
            self.borders.append(grid[self.row - 1][self.col])

        if self.col < self.totalRows - 1 and not grid[self.row][self.col + 1].isBarrier(): # checking if you can add rightward node to open list
            self.borders.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].isBarrier(): # checking if you can add leftward node to open list
            self.borders.append(grid[self.row][self.col - 1])


    def __lt__(self, otherNode):
        return False
        
# Finds the "L distance" between two points (H value for F = G + H)
def heuristicDist(point1, point2):
    # Following uses a python shortcut where variable made up of components
    # can have values of those components stored in two diff variables
    x1, y1 = point1
    x2, y2, = point2

    return abs(x1 - x2) + abs(y1 - y2)

def constructPath(previousNode, currentNode, draw):

    # goes through all nodes in previousNode set, and sets them as path until startPos is hit
    while currentNode in previousNode:
        currentNode = previousNode[currentNode]
        currentNode.setAsPath()
        draw()




'''
Remember that F + G + H where,
F = total cost node
G = distance between the current node and the starting node
H = the hueristic distance between the current node and the end node
'''
def pathAlgorithm(draw, grid, startPos, endPos):
    count = 0
    openSet = PriorityQueue()           # In PriorityQueue, push or append is called "put"
    openSet.put((0, count, startPos))           # First putting an F-score of 0 for starting position. Count is there to keep track
                                        # of when items were added to the open set in case of necessary tiebreak, the node added first will be chosen
    previousNode = {}

    #G and F values consist of key:value pairs in which it's node: G/F value
    G_val = {node: float("inf") for row in grid for node in row} # list comprehension to set all nodes' g scores to infinity
    G_val[startPos] = 0
    F_val = {node: float("inf") for row in grid for node in row} # list comprehension to set all nodes' f scores to infinity
    F_val[startPos] = heuristicDist(startPos.getPosition(), endPos.getPosition())

    openSetHash = {startPos} # PriorityQueue doesn't have a way of showing it's contents so this hash stores all the same items that the
                             #  PriorityQueue stores so we can see what's in the queue. It'll also be able to give us the "smallest" value

    while not openSet.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:           # Gives used option to quit and exit while loop if needed
                pygame.quit()

        currentNode = openSet.get()[2]              # PriorityQueue sorts it's contents so when we call for the first node, we are getting the node with the smallest F value
        openSetHash.remove(currentNode)             # It then removes that node from the open list and puts it in a "closed list"

        if currentNode == endPos:
            constructPath(previousNode, endPos, draw)
            endPos.setEndGoal()
            return True

        # consider all bordering nodes for the current node
        for borderNode in currentNode.borders:
            temp_G_val = G_val[currentNode] + 1  # if we were to travel to this next node from our current node, it would add 1 to the distance from the startPos
            
            # if a more efficient path is found with a lower g score, this updates the path
            if temp_G_val < G_val[borderNode]:
                previousNode[borderNode] = currentNode
                G_val[borderNode] = temp_G_val
                F_val[borderNode] = temp_G_val + heuristicDist(borderNode.getPosition(), endPos.getPosition())
                if borderNode not in openSetHash:       #puts borderNodes into the open list
                    count += 1
                    openSet.put((F_val[borderNode], count, borderNode))
                    openSetHash.add(borderNode)
                    borderNode.setOpen()

        draw()

        #if current node isn't the starting position, then we close it off as it has already been considered
        if currentNode != startPos:
            currentNode.setClosed()

    return False

# creates 2D list filled with lists which contain Node objects
def createGrid(rows, width):
    grid = []
    gap = width // rows # where '//' is integer division ensuring 
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows) # where i and j represent row and col respectively. gap is width of node
            grid[i].append(node)
    
    return grid

def createGridLines(window, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(window, GRAY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(window, GRAY, (j * gap, 0), (j * gap, width))

def draw(window, grid, rows, width):
    window.fill(WHITE)

    # draws out all the cubes (node objects)
    for row in grid:
        for node in row:
            node.draw(window)
    
    createGridLines(window, rows, width)
    pygame.display.update() # takes what we've drawn and updates display window accordingly


# This method takes the position of mouse, the number of rows and width of window as args
# and divides the mouse's x and y position by the gap between the rows to find which row 
# and column the mouse is located at
def getPositionClicked(mousePos, rows, width):
    gap = width // rows
    y, x = mousePos

    row = y // gap
    col = x // gap

    return row, col

def main(window, width):
    ROWS = 50
    grid = createGrid(ROWS, width)

    # keeps track of start and end goal's position
    startPos = None
    endPos = None

    running = True      # whether or not main loop has been ran yet

    while running:
        draw(window, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # if right-click button was pressed
            if pygame.mouse.get_pressed()[0]:
                mousePos = pygame.mouse.get_pos()
                row, col = getPositionClicked(mousePos, ROWS, width)
                node = grid[row][col] # sets "node" equal to square which is underneath the mouse's location when right click is pressed
                
                # if starting position hasn't been placed
                if not startPos and node != endPos:
                    startPos = node
                    startPos.setStartPos()

                # if ending position hasn't been placed
                elif not endPos and node != startPos:
                    endPos = node
                    endPos.setEndGoal()

                #if both start and end have been placed and random node is pressed
                elif node != endPos and node != startPos:
                    node.setBarrier()

            #if left-click button was pressed
            elif pygame.mouse.get_pressed()[2]:
                mousePos = pygame.mouse.get_pos()
                row, col = getPositionClicked(mousePos, ROWS, width)
                node = grid[row][col]
                node.resetNode()
                if node == startPos:
                    startPos = None
                elif node == endPos:
                    endPos = None

            # if enter key was pressed and program hasn't been run yet
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and startPos and endPos:
                    for row in grid:
                        for node in row:
                            node.updateBorders(grid)  # checks surrounding squares of current node

                    pathAlgorithm(lambda: draw(window, grid, ROWS, width), grid, startPos, endPos)

                if event.key == pygame.K_BACKSPACE:
                    startPos = None
                    endPos = None
                    grid = createGrid(ROWS, width)

                








    pygame.quit()

    
main(WINDOW, WIDTH)