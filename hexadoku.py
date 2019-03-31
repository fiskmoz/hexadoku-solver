import timeit

def Main():
    try: 
        hexafile = open("examplegrid.txt", "r")
    except Exception as e:
        return print("Error: "+ str(e))
    grid=[[0 for x in range(16)]for y in range(16)] 
    gridLines = [line for line in hexafile.readlines() if line.strip()]
    for row, line in enumerate(gridLines):
        values = line.split()
        for column, value in enumerate(values):
            try:
                grid[row][column] = int(value, 16)
            except:
                grid[row][column] = ord(value)
    PrintGrid(grid)
    computedGrid =[[[] for y in range(16)]for z in range(16)]
    computedGrid = PrecomputeHexa(grid, computedGrid)
    print("Now solving...")
    if not (SolveHexadoku(grid, computedGrid)):
        print("No more solutions!")
    
def PrecomputeHexa(grid, computedGrid):
    redo = False
    computedGrid = AssessPossibilities(grid, computedGrid)
    if(InsertSingles(grid, computedGrid)):
        computedGrid = AssessPossibilities(grid, computedGrid)
        redo = True
    if(CrossCheckRows(grid, computedGrid)):
        computedGrid = AssessPossibilities(grid, computedGrid)
        redo = True
    if(CrossCheckCollumns(grid, computedGrid)):
        computedGrid = AssessPossibilities(grid, computedGrid)
        redo = True
    if(CrossCheckSubGrid(grid, computedGrid)):
        computedGrid = AssessPossibilities(grid, computedGrid)
        redo = True
    if(redo):
        return PrecomputeHexa(grid, computedGrid)
    return computedGrid[:]

def AssessPossibilities(grid, computedGrid):
    computedGrid =[[[] for y in range(16)]for z in range(16)]
    for row in range(16):
        for column in range(16):
            if(grid[row][column] is 42):
                for i in range(16):
                    if(ValidationCheck(grid, row,column, i)):
                        computedGrid[row][column].append(i)
    computedGrid = RestrictPossibilites(grid, computedGrid)
    return computedGrid

def RestrictPossibilites(grid, computedGrid):
    for gridRow in range(4):
        for gridColumn in range(4):
            possibles = [[[] for x in range(4)]for y in range(4)]
            for row in range(4):
                for column in range(4):
                    if(grid[(gridRow*4) + row][(gridColumn*4) + column] is 42):
                        possibles[row][column] = computedGrid[(gridRow*4) + row][(gridColumn*4) + column]
            for x in range(4): 
                for y in range(4):
                    if(not possibles[x][y]):
                        continue
                    for guess in possibles[x][y]:
                        correct = True
                        for z in range(4):
                            for q in range(4):
                                if(x==z):
                                    continue
                                if(guess in possibles[z][q]):
                                    correct = False
                                    break
                        if(correct):
                            for col in range(16):
                                if(col == (gridColumn*4)+ col%4):
                                    continue
                                try:
                                    computedGrid[(gridRow*4) + x][col].remove(guess)
                                except:
                                    pass
            for x in range(4): 
                for y in range(4):
                    if(not possibles[x][y]):
                        continue
                    for guess in possibles[x][y]:
                        correct = True
                        for z in range(4):
                            for q in range(4):
                                if(q==y):
                                    continue
                                if(guess in possibles[z][q]):
                                    correct = False
                                    break
                        if(correct):
                            for row in range(16):
                                if(row == (gridRow*4)+ row%4):
                                    continue
                                try:
                                    computedGrid[row][(gridColumn*4) + y].remove(guess)
                                except:
                                    pass
    return computedGrid
                    
def InsertSingles(grid, computedGrid):
    gridChanged = False
    for row in range(16):
        for column in range(16):
            if(grid[row][column] is 42):
                if(len(computedGrid[row][column]) == 1):
                    grid[row][column] = computedGrid[row][column][0]
                    # print("Inserted single character!")
                    gridChanged = True
                    return True
    if(gridChanged):
        return True
    return False

def CrossCheckRows(grid, computeGrid):
    gridChanged = False
    for row in range(16):
        possibles = [[] for x in range(16)]
        for column in range(16):
            if(grid[row][column] is 42):
                possibles[column] = computeGrid[row][column]
        for x in range(16): 
            if(not possibles[x]):
                continue
            for guess in possibles[x]:
                correct = True
                for y in range(16):
                    if(guess in possibles[y] and x!=y):
                        correct = False
                        break
                if(correct):
                    grid[row][x] = guess
                    # print("Optimized a row!")
                    gridChanged = True
                    return True
    if(gridChanged):
        return True
    return False
                    
def CrossCheckCollumns(grid, computedGrid):
    gridChanged = False
    for row in range(16):
        possibles = [[] for x in range(16)]
        for column in range(16):
            if(grid[column][row] is 42):
                possibles[column] = computedGrid[column][row]
        for x in range(16): 
            if(not possibles[x]):
                continue
            for guess in possibles[x]:
                correct = True
                for y in range(16):
                    if(guess in possibles[y] and x!=y):
                        correct = False
                        break
                if(correct):
                    grid[x][row] = guess
                    # print("Optimized a column!")
                    gridChanged = True
                    return True
    if(gridChanged):
        return True        
    return False        

def CrossCheckSubGrid(grid, computedGrid):
    gridChanged = False
    for gridRow in range(4):
        for gridColumn in range(4):
            possibles = [[[] for x in range(4)]for y in range(4)]
            for row in range(4):
                for column in range(4):
                    if(grid[(gridRow*4) + row][(gridColumn*4) + column] is 42):
                        possibles[row][column] = computedGrid[(gridRow*4) + row][(gridColumn*4) + column]
            for x in range(4): 
                for y in range(4):
                    if(not possibles[x][y]):
                        continue
                    for guess in possibles[x][y]:
                        correct = True
                        for z in range(4):
                            for q in range(4):
                                if(x==z and y==q):
                                    continue
                                if(guess in possibles[z][q]):
                                    correct = False
                                    break
                        if(correct):
                            grid[(gridRow*4) + x][(gridColumn*4) + y] = guess
                            # print("Optimized a subgrid!")
                            gridChanged = True
                            return True
    if(gridChanged):
        return True
    return False     
                    

def SolveHexadoku(grid, computedGrid):
    currentLocation = [0,0]
    if(not FindEmptyLocation(grid,computedGrid, currentLocation)):
        print("Solution found!")
        PrintGrid(grid)
        stop = timeit.default_timer()
        print('Time: ', stop - start)  
        return False
    
    row = currentLocation[0]
    column = currentLocation[1]

    for number in computedGrid[row][column]:
        if (number is 42):
            continue
        if(ValidationCheck(grid, row, column, number)):
            grid[row][column] = number
            if(SolveHexadoku(grid, computedGrid)):
                return True
            grid[row][column] = 42
    return False

# Validate that the number provided as input is valid for that specific spot on the grid.
def ValidationCheck(grid, row, column, number):
    for i in range(4): 
        for j in range(4): 
            if(grid[i+row - row%4][j+column - column%4] == number): 
                return False
    for i in range(16): 
        if(grid[row][i] == number or grid[i][column] == number): 
            return False
    return True

# Find a empty location in the grid. 
# Choose the location with the least amount of options in increase performance of 
# DFS.
def FindEmptyLocation(grid, computedGrid, currentLocation):
    guesses = 16
    found = False
    for row in range(16): 
        for column in range(16): 
            if(grid[row][column] == 42): 
                if(len(computedGrid[row][column]) < guesses):
                    currentLocation[0]=row 
                    currentLocation[1]=column 
                    guesses = len(computedGrid[row][column])
                    found = True
    if(found):
        return True
    return False

#  Print a 16x16 grid and convert the output to hexadecimal
def PrintGrid(grid):
    print("This is the grid!")
    for i in range(16): 
        for j in range(16): 
            if(j%4 == 0):
                print("" , end= " ")
            if(grid[i][j] == 42):
                print("*", end=" ")
            else:
                print (hex(grid[i][j])[2:], end=" "),
        print(" ")
        if((1+i)%4 == 0):
            print(" ")
    return print(" ")
    
start = timeit.default_timer()
Main()