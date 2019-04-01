import timeit

def Main():
    try: 
        hexafile = open("examplegrid.txt", "r")
    except Exception as e:
        return print("Error: "+ str(e))
    grid = [[0 for x in range(16)]for y in range(16)] 
    gridLines = [line for line in hexafile.readlines() if line.strip()]
    for row, line in enumerate(gridLines):
        values = line.split()
        for column, value in enumerate(values):
            try:
                grid[row][column] = int(value, 16)
            except:
                grid[row][column] = ord(value)
    PrintGrid(grid)
    possibilities = [[[] for y in range(16)]for z in range(16)]
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
    for row in range(16):
        for column in range(16):
            if(grid[row][column] is 42):
                possibilities[row][column].clear()
                for i in range(16):
                    if(ValidationCheck(grid, row,column, i)):
                        possibilities[row][column].append(i)
    RestrictPossibilites(grid, possibilities)

    # This reduces the amount of posibillites for each entry in the grid by 
    # checking if, for a subgrid, a number can only occur in a specific row or column.
    # If thats the case, then eliminate that number as a possible candidate on that row 
    # or column for other subgrids.
def RestrictPossibilites(grid, possibilities):
    for gridRow in range(4):
        for gridColumn in range(4):
            possibles = [[[] for x in range(4)]for y in range(4)]
            for row in range(4):
                for column in range(4):
                    if(grid[(gridRow*4) + row][(gridColumn*4) + column] is 42):
                        possibles[row][column] = possibilities[(gridRow*4) + row][(gridColumn*4) + column]
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
                            if(not correct):
                                break
                        if(correct):
                            for col in range(16):
                                if(col == (gridColumn*4)+ col%4):
                                    continue
                                try:
                                    possibilities[(gridRow*4) + x][col].remove(guess)
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
                            if(not correct):
                                break
                        if(correct):
                            for row in range(16):
                                if(row == (gridRow*4)+ row%4):
                                    continue
                                try:
                                    possibilities[row][(gridColumn*4) + y].remove(guess)
                                except:
                                    pass

    # If there is a single posibility for a specific entry we can just insert it since it has to be that one.
def InsertSingles(grid, possibilities):
    for row in range(16):
        for column in range(16):
            if(grid[row][column] is 42):
                if(len(possibilities[row][column]) == 1):
                    grid[row][column] = possibilities[row][column][0]
                    # print("Inserted single character!")
                    AssessPossibilities(grid, possibilities)
                    return True

    # Compare the possible values for a row, if a specific entry in a row has a unique value that 
    # the other entries do not share we know that the unique value has to fill that entry. 
    # Then repeat for all rows.
def CrossCheckRows(grid, possibilities):
    for row in range(16):
        possibles = [[] for x in range(16)]
        for column in range(16):
            if(grid[row][column] is 42):
                possibles[column] = possibilities[row][column]
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
                    possibilities[row][x].clear()
                    AssessPossibilities(grid, possibilities)
                    InsertSingles(grid, possibilities)
                    # print("Optimized a row!")
                    return True

    # Compare the possible values for a column, if a specific entry in a column has a unique value 
    # that the other entries in the column do not share we know that the unique value has to fill that entry. 
    # Then repeat for all columns.      
def CrossCheckCollumns(grid, possibilities):
    for row in range(16):
        possibles = [[] for x in range(16)]
        for column in range(16):
            if(grid[column][row] is 42):
                possibles[column] = possibilities[column][row]
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
                    possibilities[x][row].clear()
                    AssessPossibilities(grid, possibilities)
                    # print("Optimized a column!")
                    return True

    # Compare the possible values for a subgrid, if a specific entry has a unique value that the others
    # do not share we know that the unique value has to fill that entry. Then repeat for all subgrids.     
def CrossCheckSubGrid(grid, possibilities):
    for gridRow in range(4):
        for gridColumn in range(4):
            possibles = [[[] for x in range(4)]for y in range(4)]
            for row in range(4):
                for column in range(4):
                    if(grid[(gridRow*4) + row][(gridColumn*4) + column] is 42):
                        possibles[row][column] = possibilities[(gridRow*4) + row][(gridColumn*4) + column]
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
                            if(not correct):
                                break
                        if(correct):
                            grid[(gridRow*4) + x][(gridColumn*4) + y] = guess
                            possibilities[(gridRow*4) + x][(gridColumn*4) + y].clear()
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
        if (number is 42):
            continue
        if(ValidationCheck(grid, row, column, number)):
            grid[row][column] = number
            if(SolveHexadoku(grid, possibilities)):
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

# Find the next empty location in the grid. 
def FindEmptyLocation(grid, possibilities, currentLocation):
    for row in range(16): 
        for column in range(16): 
            if(grid[row][column] == 42): 
                currentLocation[0]=row 
                currentLocation[1]=column 
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