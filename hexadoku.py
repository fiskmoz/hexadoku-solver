import timeit
import math
from typing import List
from io import TextIOWrapper


def main():
    grid_file = get_grid_file()
    grid = initialize_grid(grid_file)
    print_grid(grid)
    possibilities = [[[] for y in range(size)] for z in range(size)]
    possibilities = precompute_grid(grid, possibilities)
    print("Now solving...")
    if not (solve_single_solution(grid, possibilities)):
        print("No more solutions!")


# Use some rules to reduce running time of brute force DFS
# Given easier puzzles this might just straight out solve them.


def precompute_grid(
    grid: List[List[int]], possibilities: List[List[list]]
) -> List[List[list]]:
    redo = False
    assess_possibilities(grid, possibilities)
    if insert_single_valid_number_in_line(grid, possibilities):
        assess_possibilities(grid, possibilities)
        redo = True
    if cross_check(grid, possibilities, "row"):
        assess_possibilities(grid, possibilities)
        redo = True
    if cross_check(grid, possibilities, "column"):
        assess_possibilities(grid, possibilities)
        redo = True
    if subgrid_match(grid, possibilities, "single"):
        assess_possibilities(grid, possibilities)
        redo = True
    if redo:
        return precompute_grid(grid, possibilities)
    return possibilities[:]


def assess_possibilities(grid: List[List[int]], possibilities: List[List[int]]):
    for row in range(size):
        for column in range(size):
            if grid[row][column] is unknown:
                possibilities[row][column].clear()
                for number in range(size):
                    if number_has_valid_position(grid, row, column, number):
                        possibilities[row][column].append(number)
    subgrid_match(grid, possibilities, "column")
    subgrid_match(grid, possibilities, "row")


# This reduces the amount of possibilities for each entry in the grid by
# checking if, for a subgrid, a number can only occur in a specific row or column.
# If thats the case, then eliminate that number as a possible candidate on that row
# or column for other subgrids.


def subgrid_match(
    grid: List[List[int]],
    possibilities: List[List[list]],
    target: str,
) -> bool:
    for gridRow in range(subgridsize):
        for gridColumn in range(subgridsize):
            possibles = init_subsgrid_possibilities(
                grid, possibilities, gridRow, gridColumn
            )
            for x in range(subgridsize):
                for y in range(subgridsize):
                    if not possibles[x][y]:
                        continue
                    match_found = make_and_match_guess(
                        grid,
                        possibilities,
                        possibles,
                        target,
                        gridRow,
                        gridColumn,
                        x,
                        y,
                    )
                    if match_found:
                        return True

    return False


# Initialize all possible values for a given subgrid based on given row and column (will always target first square in subgrid).


def make_and_match_guess(
    grid: List[List[int]],
    possibilities: List[List[list]],
    possibles: List[List[list]],
    target: str,
    gridRow: int,
    gridColumn: int,
    x: int,
    y: int,
) -> bool:
    for guess in possibles[x][y]:
        correct = True
        for z in range(subgridsize):
            for q in range(subgridsize):
                if q == y:
                    if x == z:
                        if target is "single":
                            continue
                    elif target is "row":
                        continue
                elif x == z and target is "column":
                    continue
                if guess in possibles[z][q]:
                    correct = False
                    break
            if not correct:
                break
        if correct:
            row_adjusted = gridRow * subgridsize
            col_adjusted = gridColumn * subgridsize
            if target is "single":
                grid[(row_adjusted) + x][(col_adjusted) + y] = guess
                possibilities[(row_adjusted) + x][(col_adjusted) + y].clear()
                return True
            elif target is "row":
                for row in range(size):
                    if row is (row_adjusted) + row % subgridsize:
                        continue
                    if guess not in possibilities[row][(col_adjusted) + y]:
                        continue
                    possibilities[row][(col_adjusted) + y].remove(guess)
            elif target is "column":
                for col in range(size):
                    if col is (col_adjusted) + col % subgridsize:
                        continue
                    if guess not in possibilities[(row_adjusted) + x][col]:
                        continue
                    possibilities[(row_adjusted) + x][col].remove(guess)
    return False


def init_subsgrid_possibilities(
    grid: List[List[int]],
    possibilities: List[List[list]],
    gridRow: int,
    gridColumn: int,
) -> List[List[list]]:
    return [
        [
            possibilities[(gridRow * subgridsize) + row][
                (gridColumn * subgridsize) + column
            ]
            if grid[(gridRow * subgridsize) + row][(gridColumn * subgridsize) + column]
            is unknown
            else []
            for column in range(subgridsize)
        ]
        for row in range(subgridsize)
    ]


def insert_single_valid_number_in_line(
    grid: List[List[int]], possibilities: List[List[list]]
) -> bool:
    for row in range(size):
        for column in range(size):
            if grid[row][column] is unknown and len(possibilities[row][column]) == 1:
                grid[row][column] = possibilities[row][column][0]
                return True
    return False


# Compare the possible values for a row or column, if a specific entry in a row has a unique value that
# the other entries do not share we know that the unique value has to fill that entry.
# Then repeat for all rows or column. Target can only be "row" or "column".


def cross_check(
    grid: List[List[int]], possibilities: List[List[list]], target: str
) -> bool:
    for row in range(size):
        possibles = [[] for x in range(size)]
        for column in range(size):
            if target is "row":
                if grid[row][column] is unknown:
                    possibles[column] = possibilities[row][column]
            elif target is "column":
                if grid[column][row] is unknown:
                    possibles[column] = possibilities[column][row]
        for column in range(size):
            if not possibles[column]:
                continue
            for guess in possibles[column]:
                correct = True
                for counter in range(size):
                    if guess in possibles[counter] and column != counter:
                        correct = False
                        break
                if correct:
                    if target is "row":
                        grid[row][column] = guess
                        possibilities[row][column].clear()
                    elif target is "column":
                        grid[column][row] = guess
                        possibilities[column][row].clear()
                    return True


# A backtracking algorithm to ensure that all solutions are presented.
# Backtracking works by going through each entry in the grid and then testing a valid number. Then continue
# with the next entry, this repeats until a entry cannot be filled, then it loops back to the first entry and tries
# another path. This can be represented as a tree and performing a brute force depth first search.


def solve_single_solution(
    grid: List[List[int]], possibilities: List[List[list]]
) -> bool:
    next_location = get_next_location(grid)
    if not next_location:
        print("Solution found!")
        print_grid(grid)
        stop = timeit.default_timer()
        print("Time: ", stop - start)
        return False

    row = next_location[0]
    column = next_location[1]

    for number in possibilities[row][column]:
        if number is unknown:
            continue
        if number_has_valid_position(grid, row, column, number):
            grid[row][column] = number
            if solve_single_solution(grid, possibilities):
                return True
            grid[row][column] = unknown
    return False


# Validate that the number provided as input is valid for that specific spot on the grid.


def number_has_valid_position(
    grid: List[List[int]], row: int, column: int, number: int
) -> bool:
    for x in range(subgridsize):
        for y in range(subgridsize):
            if (
                grid[x + row - row % subgridsize][y + column - column % subgridsize]
                is number
            ):
                return False
    for count in range(size):
        if grid[row][count] == number or grid[count][column] is number:
            return False
    return True


# Get the next empty location in the grid.


def get_next_location(grid: List[List[int]]) -> List[int]:
    for row in range(size):
        for column in range(size):
            if grid[row][column] is unknown:
                return [row, column]


#  Print a 16x16 grid and convert the output to hexadecimal


def print_grid(grid: List[List[int]]):
    print("This is the grid!")
    for row in range(size):
        for column in range(size):
            if column % subgridsize == 0:
                print("", end=" ")
            if grid[row][column] is unknown:
                print("*", end=" ")
            else:
                print(hex(grid[row][column])[2:], end=" "),
        print(" ")
        if (1 + row) % subgridsize == 0:
            print(" ")


# Init 2D array for the grid. Enter values given from file.


def initialize_grid(file: TextIOWrapper) -> List[List[int]]:
    grid = [[0 for x in range(size)] for y in range(size)]
    lines = [line for line in file.readlines() if line.strip()]
    for row, line in enumerate(lines):
        values = line.split()
        for column, value in enumerate(values):
            try:
                grid[row][column] = int(value, size)
            except:
                grid[row][column] = ord(value)
    return grid


# Loading the grid from a .txt file, see examplegrid file for formatting to use your own grid.


def get_grid_file() -> TextIOWrapper:
    try:
        grid_file = open("examplegrid.txt", "r")
    except Exception as e:
        return print("Error: " + str(e))
    return grid_file


start = timeit.default_timer()
unknown = 42
size = 16
subgridsize = int(math.sqrt(size))
main()
