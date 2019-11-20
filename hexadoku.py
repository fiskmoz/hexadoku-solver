import timeit
import math

def Main():
    hexafile = LoadGrid()
    grid = InitGrid(hexafile)
    PrintGrid(grid)
    possibilities = [[[] for y in range(size)]for z in range(size)]
    possibilities = PrecomputeHexa(grid, possibilities)
    print("Now solving...")
    if not (SolveHexadoku(grid, possibilities)):
        print("No more solutions!")
    
    # Use some rules to reduce running time of brute forece DFS
    # Given easier puzzles this might just straight out solve them. 
def PrecomputeHexa(grid, possibilities):
    redo = False
    AssessPossibilities(grid, possibilities)
    if(InsertSingles(grid, possibilities)):
        redo = MatchFound(grid, possibilities)
    if(CrossCheck(grid, possibilities, "row")):
        redo = MatchFound(grid, possibilities)
    if(CrossCheck(grid, possibilities, "column")):
        redo = MatchFound(grid, possibilities)
    if(SubgridMatching(grid, possibilities, "single")):
        redo = MatchFound(grid, possibilities)
    if(redo):
        return PrecomputeHexa(grid, possibilities)
    return possibilities[:]

    # If a match is found we must update the current possibilities with the new information
def MatchFound(grid, possibilities):
    AssessPossibilities(grid, possibilities)
    return True

    # Asses the possible values for each entry in the grid.
def AssessPossibilities(grid, possibilities):
    for row in range(size):
        for column in range(size):
            if(grid[row][column] is unknown):
                possibilities[row][column].clear()
                for i in range(size):
                    if(ValidationCheck(grid, row,column, i)):
                        possibilities[row][column].append(i)
    RestrictPossibilites(grid, possibilities)

    # This reduces the amount of posibillites for each entry in the grid by 
    # checking if, for a subgrid, a number can only occur in a specific row or column.
    # If thats the case, then eliminate that number as a possible candidate on that row 
    # or column for other subgrids.
def RestrictPossibilites(grid, possibilities):
    SubgridMatching(grid, possibilities, "column")
    SubgridMatching(grid, possibilities, "row")

    # column and row targets explained above.
    # single target checks if there is a unique number in possibilities for a specific subgrid.
def SubgridMatching(grid, possibilities, target):
    for gridRow in range(subgridsize):
        for gridColumn in range(subgridsize):
            possibles = initSubgridPossibles(grid, possibilities, gridRow, gridColumn)
            for x in range(subgridsize): 
                for y in range(subgridsize):
                    if(not possibles[x][y]):
                        continue
                    for guess in possibles[x][y]:
                        correct = True
                        for z in range(subgridsize):
                            for q in range(subgridsize):
                                if(q==y):
                                    if(x==z):
                                        if target is "single":
                                            continue
                                    elif target is "row":
                                        continue
                                elif(x==z):
                                    if target is "column":
                                        continue
                                if(guess in possibles[z][q]):
                                    correct = False
                                    break
                            if(not correct):
                                break
                        if(correct):
                            if target is "single":
                                grid[(gridRow*subgridsize) + x][(gridColumn*subgridsize) + y] = guess
                                possibilities[(gridRow*subgridsize) + x][(gridColumn*subgridsize) + y].clear()
                                return True
                            elif target is "row":
                                for row in range(size):
                                    if(row is (gridRow*subgridsize)+ row%subgridsize):
                                        continue
                                    if(guess not in possibilities[row][(gridColumn*subgridsize) + y]):
                                        continue
                                    possibilities[row][(gridColumn*subgridsize) + y].remove(guess)
                            elif target is "column":
                                for col in range(size):
                                    if(col is (gridColumn*subgridsize)+ col%subgridsize):
                                        continue
                                    if(guess not in possibilities[(gridRow*subgridsize) + x][col]):
                                        continue
                                    possibilities[(gridRow*subgridsize) + x][col].remove(guess)

    # Initialize all possible values for a given subgrid based on given row and column (will always target first square in subgrid). 
def initSubgridPossibles(grid, possibilities, gridRow, gridColumn):
    possibles = [[[] for x in range(subgridsize)]for y in range(subgridsize)]
    for row in range(subgridsize):
        for column in range(subgridsize):
            if(grid[(gridRow*subgridsize) + row][(gridColumn*subgridsize) + column] is unknown):
                possibles[row][column] = possibilities[(gridRow*subgridsize) + row][(gridColumn*subgridsize) + column]
    return possibles

    # If there is a single posibility for a specific entry we can just insert it since it has to be that one.
def InsertSingles(grid, possibilities):
    for row in range(size):
        for column in range(size):
            if(grid[row][column] is unknown):
                if(len(possibilities[row][column]) == 1):
                    grid[row][column] = possibilities[row][column][0]
                    return True

    # Compare the possible values for a row or column, if a specific entry in a row has a unique value that 
    # the other entries do not share we know that the unique value has to fill that entry. 
    # Then repeat for all rows or column. Target can only be "row" or "column".
def CrossCheck(grid, possibilities, target):
    for row in range(size):
        possibles = [[] for x in range(size)]
        for column in range(size):
            if target is "row":
                if(grid[row][column] is unknown):
                    possibles[column] = possibilities[row][column]
            elif target is "column":
                if(grid[column][row] is unknown):
                    possibles[column] = possibilities[column][row]
        for column in range(size): 
            if(not possibles[column]):
                continue
            for guess in possibles[column]:
                correct = True
                for counter in range(size):
                    if(guess in possibles[counter] and column!=counter):
                        correct = False
                        break
                if(correct):
                    if target is "row":
                        grid[row][column] = guess
                        possibilities[row][column].clear()
                    elif target is "column":
                        grid[column][row] = guess
                        possibilities[column][row].clear()
                    return True

    # A backtracking agorithm to ensure that all solutions are presented.
    # Backtracking works by going through each entry in the grid and then testing a valid number. Then continue 
    # with the next entry, this repeats untill a entry cannot be filled, then it loops back to the first entry and tries 
    # another path. This can be represented as a tree and performing a brute force depth first search.
def SolveHexadoku(grid, possibilities):
    currentLocation = [0,0]
    if(not FindEmptyLocation(grid,possibilities, currentLocation)):
        print("Solution found!")
        PrintGrid(grid)
        stop = timeit.default_timer()
        print('Time: ', stop - start)  
        return False
    
    row = currentLocation[0]
    column = currentLocation[1]

    for number in possibilities[row][column]:
        if (number is unknown):
            continue
        if(ValidationCheck(grid, row, column, number)):
            grid[row][column] = number
            if(SolveHexadoku(grid, possibilities)):
                return True
            grid[row][column] = unknown
    return False

# Validate that the number provided as input is valid for that specific spot on the grid.
def ValidationCheck(grid, row, column, number):
    for rowCount in range(subgridsize): 
        for colCount in range(subgridsize): 
            if(grid[rowCount+row - row%subgridsize][colCount+column - column%subgridsize] is number): 
                return False
    for count in range(size): 
        if(grid[row][count] == number or grid[count][column] is number): 
            return False
    return True

# Find the next empty location in the grid. 
def FindEmptyLocation(grid, possibilities, currentLocation):
    for row in range(size): 
        for column in range(size): 
            if(grid[row][column] is unknown): 
                currentLocation[0]=row 
                currentLocation[1]=column 
                return True
    return False

#  Print a 16x16 grid and convert the output to hexadecimal
def PrintGrid(grid):
    print("This is the grid!")
    for row in range(size): 
        for column in range(size): 
            if(column%subgridsize == 0):
                print("" , end= " ")
            if(grid[row][column] is unknown):
                print("*", end=" ")
            else:
                print (hex(grid[row][column])[2:], end=" "),
        print(" ")
        if((1+row)%subgridsize == 0):
            print(" ")

    # Init 2D array for the grid. Enter values given from hexafile.
def InitGrid(hexafile):
    grid = [[0 for x in range(size)]for y in range(size)] 
    gridLines = [line for line in hexafile.readlines() if line.strip()]
    for row, line in enumerate(gridLines):
        values = line.split()
        for column, value in enumerate(values):
            try:
                grid[row][column] = int(value, size)
            except:
                grid[row][column] = ord(value)
    return grid

# Loading the grid from a .txt file, see examplegrid file for formatting to use your own grid.
def LoadGrid():
    try: 
        hexafile = open("examplegrid.txt", "r")
    except Exception as e:
        return print("Error: "+ str(e))
    return hexafile
    
start = timeit.default_timer()
unknown = 42
size = 16
subgridsize = int(math.sqrt(size))
Main()