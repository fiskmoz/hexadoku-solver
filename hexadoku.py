import timeit
import math

def Main():
    try: 
        hexafile = open("hexa.txt", "r")
    except Exception as e:
        return print("Error: "+ str(e))
    grid = [[0 for x in range(size)]for y in range(size)] 
    gridLines = [line for line in hexafile.readlines() if line.strip()]
    for row, line in enumerate(gridLines):
        values = line.split()
        for column, value in enumerate(values):
            try:
                grid[row][column] = int(value, size)
            except:
                grid[row][column] = ord(value)
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
        redo = True
    if(CrossCheckRows(grid, possibilities)):
        redo = True
    if(CrossCheckCollumns(grid, possibilities)):
        redo = True
    if(CrossCheckSubGrid(grid, possibilities)):
        redo = True
    if(redo):
        return PrecomputeHexa(grid, possibilities)
    return possibilities[:]

    # Asses the possible values for each entry in the grid.
    # Further calls ValidationCheck() which checks if the value is valid.
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
    for gridRow in range(subgridsize):
        for gridColumn in range(subgridsize):
            possibles = [[[] for x in range(subgridsize)]for y in range(subgridsize)]
            for row in range(subgridsize):
                for column in range(subgridsize):
                    if(grid[(gridRow*subgridsize) + row][(gridColumn*subgridsize) + column] is unknown):
                        possibles[row][column] = possibilities[(gridRow*subgridsize) + row][(gridColumn*subgridsize) + column]
            for x in range(subgridsize): 
                for y in range(subgridsize):
                    if(not possibles[x][y]):
                        continue
                    for guess in possibles[x][y]:
                        correct = True
                        for z in range(subgridsize):
                            for q in range(subgridsize):
                                if(x==z):
                                    continue
                                if(guess in possibles[z][q]):
                                    correct = False
                                    break
                            if(not correct):
                                break
                        if(correct):
                            for col in range(size):
                                if(col == (gridColumn*subgridsize)+ col%subgridsize):
                                    continue
                                try:
                                    possibilities[(gridRow*subgridsize) + x][col].remove(guess)
                                except:
                                    pass
            for x in range(subgridsize): 
                for y in range(subgridsize):
                    if(not possibles[x][y]):
                        continue
                    for guess in possibles[x][y]:
                        correct = True
                        for z in range(subgridsize):
                            for q in range(subgridsize):
                                if(q==y):
                                    continue
                                if(guess in possibles[z][q]):
                                    correct = False
                                    break
                            if(not correct):
                                break
                        if(correct):
                            for row in range(size):
                                if(row == (gridRow*subgridsize)+ row%subgridsize):
                                    continue
                                try:
                                    possibilities[row][(gridColumn*subgridsize) + y].remove(guess)
                                except:
                                    pass

    # If there is a single posibility for a specific entry we can just insert it since it has to be that one.
def InsertSingles(grid, possibilities):
    for row in range(size):
        for column in range(size):
            if(grid[row][column] is unknown):
                if(len(possibilities[row][column]) == 1):
                    grid[row][column] = possibilities[row][column][0]
                    # print("Inserted single character!")
                    AssessPossibilities(grid, possibilities)
                    return True

    # Compare the possible values for a row, if a specific entry in a row has a unique value that 
    # the other entries do not share we know that the unique value has to fill that entry. 
    # Then repeat for all rows.
def CrossCheckRows(grid, possibilities):
    for row in range(size):
        possibles = [[] for x in range(size)]
        for column in range(size):
            if(grid[row][column] is unknown):
                possibles[column] = possibilities[row][column]
        for x in range(size): 
            if(not possibles[x]):
                continue
            for guess in possibles[x]:
                correct = True
                for y in range(size):
                    if(guess in possibles[y] and x!=y):
                        correct = False
                        break
                if(correct):
                    grid[row][x] = guess
                    possibilities[row][x].clear()
                    AssessPossibilities(grid, possibilities)
                    InsertSingles(grid, possibilities)
                    # print("Optimized a row!")
                    return True

    # Compare the possible values for a column, if a specific entry in a column has a unique value 
    # that the other entries in the column do not share we know that the unique value has to fill that entry. 
    # Then repeat for all columns.      
def CrossCheckCollumns(grid, possibilities):
    for row in range(size):
        possibles = [[] for x in range(size)]
        for column in range(size):
            if(grid[column][row] is unknown):
                possibles[column] = possibilities[column][row]
        for x in range(size): 
            if(not possibles[x]):
                continue
            for guess in possibles[x]:
                correct = True
                for y in range(size):
                    if(guess in possibles[y] and x!=y):
                        correct = False
                        break
                if(correct):
                    grid[x][row] = guess
                    possibilities[x][row].clear()
                    AssessPossibilities(grid, possibilities)
                    # print("Optimized a column!")
                    return True

    # Compare the possible values for a subgrid, if a specific entry has a unique value that the others
    # do not share we know that the unique value has to fill that entry. Then repeat for all subgrids.     
def CrossCheckSubGrid(grid, possibilities):
    for gridRow in range(subgridsize):
        for gridColumn in range(subgridsize):
            possibles = [[[] for x in range(subgridsize)]for y in range(subgridsize)]
            for row in range(subgridsize):
                for column in range(subgridsize):
                    if(grid[(gridRow*subgridsize) + row][(gridColumn*subgridsize) + column] is unknown):
                        possibles[row][column] = possibilities[(gridRow*subgridsize) + row][(gridColumn*subgridsize) + column]
            for x in range(subgridsize): 
                for y in range(subgridsize):
                    if(not possibles[x][y]):
                        continue
                    for guess in possibles[x][y]:
                        correct = True
                        for z in range(subgridsize):
                            for q in range(subgridsize):
                                if(x==z and y==q):
                                    continue
                                if(guess in possibles[z][q]):
                                    correct = False
                                    break
                            if(not correct):
                                break
                        if(correct):
                            grid[(gridRow*subgridsize) + x][(gridColumn*subgridsize) + y] = guess
                            possibilities[(gridRow*subgridsize) + x][(gridColumn*subgridsize) + y].clear()
                            AssessPossibilities(grid, possibilities)
                            # print("Optimized a subgrid!")
                            return True
    # A backtracking agorithm to ensure that all solutions are presented.
    # This is a really slow algorithm so some very difficult puzzles might take some time to complete.
    # Backtracking works by going through each entry in the grid and then testing a valid number. Then continue 
    # with the next entry, this repeats untill a entry cannot be filled, then it loops back to the first entry and tries 
    # another path. This can be represented as a tree (very large) and performing a brute force depth first search.
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
    for i in range(subgridsize): 
        for j in range(subgridsize): 
            if(grid[i+row - row%subgridsize][j+column - column%subgridsize] is number): 
                return False
    for i in range(size): 
        if(grid[row][i] == number or grid[i][column] is number): 
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
    for i in range(size): 
        for j in range(size): 
            if(j%subgridsize == 0):
                print("" , end= " ")
            if(grid[i][j] is unknown):
                print("*", end=" ")
            else:
                print (hex(grid[i][j])[2:], end=" "),
        print(" ")
        if((1+i)%subgridsize == 0):
            print(" ")
    return print(" ")
    
start = timeit.default_timer()
unknown = 42
size = 16
subgridsize = int(math.sqrt(size))
Main()