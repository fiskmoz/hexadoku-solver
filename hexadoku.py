"""Base application, run this to start the application."""

from enum import Enum
import timeit
import math
from typing import List
from io import TextIOWrapper

start = timeit.default_timer()

UNKNOWN = 42
SIZE = 16
SUBGRIDSIZE = int(math.sqrt(SIZE))


class Cell():
    """Cell class, contains posiblities and actual known value of a cell"""

    def __init__(self, posibilities: List[int], value: int):
        self.posibilties = posibilities
        self.value = value

    posibilties: List[int]
    value: int


class Grid():
    """Grid class, contains all cells"""

    def __init__(self, cells: List[List[Cell]]):
        self.cells = cells

    cells: List[List[Cell]]


class CellCheck(Enum):
    """Enumeration of cells or cellpaths to check"""
    SINGLE = 1
    ROW = 2
    COLUMN = 3


def main():
    """Base application, run this to start the application."""
    grid_file = get_grid_file()
    grid = initialize_grid(grid_file)
    print_grid(grid)
    print("Precomputing...")
    precompute_grid(grid)
    print("Precomputation done... could simply grid to this")
    print_grid(grid)
    if not get_next_location(grid):
        return
    print_grid_posibilities(grid)
    print("I am probably not stuck, sometimes this just takes a while")
    print("Now solving...")
    if not solve_single_solution(grid):
        print("No more solutions!")


def get_grid_file() -> TextIOWrapper:
    """
    Loading the grid from a .txt file, see examplegrid file for formatting to use your own grid.
    """
    try:
        grid_file = open("medium_difficulty_example.txt", "r", encoding="utf-8")
    except OSError as exception:
        return print("Error: " + str(exception))
    return grid_file


def print_grid(grid: Grid) -> None:
    """Print a 16x16 grid and convert the output to hexadecimal"""
    print("This is the grid!")
    for row in range(SIZE):
        for column in range(SIZE):
            if column % SUBGRIDSIZE == 0:
                print("", end=" ")
            if grid.cells[row][column].value is UNKNOWN:
                print("*", end=" ")
            else:
                _ = print(hex(grid.cells[row][column].value)[2:], end=" ")
        print(" ")
        if (1 + row) % SUBGRIDSIZE == 0:
            print(" ")


def initialize_grid(file: TextIOWrapper) -> Grid:
    """Init 2D array for the grid. Enter values given from file."""
    grid = [[Cell(list(range(SIZE)), 0) for _ in range(SIZE)] for _ in range(SIZE)]
    lines = [line for line in file.readlines() if line.strip()]
    for row, line in enumerate(lines):
        values = line.split()
        for column, value in enumerate(values):
            try:
                grid[row][column].value = int(value, SIZE)
                grid[row][column].posibilties = []
            except:  # pylint: disable=bare-except
                grid[row][column].value = ord(value)
    return Grid(grid)


def precompute_grid(grid: Grid) -> Grid:
    """
    Use some rules to reduce running time of brute force DFS
    Given easier puzzles this might just straight out solve them.
    """
    redo = False
    assess_possibilities(grid)
    if insert_single_valid_number(grid):
        assess_possibilities(grid)
        redo = True
    if cross_check(grid, CellCheck.ROW):
        assess_possibilities(grid)
        redo = True
    if cross_check(grid, CellCheck.COLUMN):
        assess_possibilities(grid)
        redo = True
    if subgrid_match(grid, CellCheck.SINGLE):
        assess_possibilities(grid)
        redo = True
    if redo:
        return precompute_grid(grid)
    return grid


def assess_possibilities(grid: Grid) -> None:
    """ Update the amount of posibilities for each cell in the grid """
    for row in range(SIZE):
        for column in range(SIZE):
            if grid.cells[row][column].value is UNKNOWN:
                grid.cells[row][column].posibilties.clear()
                for number in range(SIZE):
                    if number_has_valid_position(grid, row, column, number):
                        grid.cells[row][column].posibilties.append(number)
    subgrid_match(grid, CellCheck.COLUMN)
    subgrid_match(grid, CellCheck.ROW)


def subgrid_match(
        grid: Grid,
        target: CellCheck) -> bool:
    """
    This reduces the amount of possibilities for each entry in the grid by
    checking if, for a subgrid, a number can only occur in a specific row or column.
    If thats the case, then eliminate that number as a possible candidate on that row
    or column for other subgrids.
    """
    for grid_row in range(SUBGRIDSIZE):
        for grid_column in range(SUBGRIDSIZE):
            subgrid_possibilities = init_subgrid_possibilities(
                grid, grid_row, grid_column
            )
            for subgrid_x in range(SUBGRIDSIZE):
                for subgrid_y in range(SUBGRIDSIZE):
                    if not subgrid_possibilities[subgrid_x][subgrid_y]:
                        continue
                    for guess in subgrid_possibilities[subgrid_x][subgrid_y]:
                        guess_validity = is_guess_possible(
                            subgrid_possibilities,
                            target,
                            subgrid_x,
                            subgrid_y,
                            guess
                        )
                        if guess_validity:
                            match_found = match_guess(
                                grid,
                                target,
                                grid_row * SUBGRIDSIZE,
                                grid_column * SUBGRIDSIZE,
                                subgrid_x,
                                subgrid_y,
                                guess
                            )
                            if match_found:
                                return True

    return False


def match_guess(
    grid: Grid,
    target: str,
    row_adjusted: int,
    col_adjusted: int,
    subgrid_x: int,
    subgrid_y: int,
    guess: int
) -> bool:
    """
    Tries to update a grid with a guess, if it finds a clear match, add it
    Otherwise reduces posibilties
    """
    if target is CellCheck.SINGLE:
        grid.cells[(row_adjusted) + subgrid_x][(col_adjusted) + subgrid_y].value = guess
        grid.cells[(row_adjusted) + subgrid_x][(col_adjusted) + subgrid_y].posibilties.clear()
        return True
    elif target is CellCheck.ROW:
        for row in range(SIZE):
            if row is (row_adjusted) + row % SUBGRIDSIZE:
                continue
            if guess not in grid.cells[row][(col_adjusted) + subgrid_y].posibilties:
                continue
            grid.cells[row][(col_adjusted) + subgrid_y].posibilties.remove(guess)
    elif target is CellCheck.COLUMN:
        for col in range(SIZE):
            if col is (col_adjusted) + col % SUBGRIDSIZE:
                continue
            if guess not in grid.cells[(row_adjusted) + subgrid_x][col].posibilties:
                continue
            grid.cells[(row_adjusted) + subgrid_x][col].posibilties.remove(guess)
    return False


def is_guess_possible(
    possibles: List[List[int]],
    target: CellCheck,
    subgrid_x: int,
    subgrid_y: int,
    guess: int
) -> bool:
    """
    Tries to deduce if a guess (number) is valid at a specific position inside the grid
    if found update the grid depending on the target
    """
    correct = True
    for new_subgrid_x in range(SUBGRIDSIZE):
        for new_subgrid_y in range(SUBGRIDSIZE):
            if new_subgrid_y == subgrid_y:
                if subgrid_x == new_subgrid_x:
                    if target == CellCheck.SINGLE:
                        continue
                elif target == CellCheck.ROW:
                    continue
            elif subgrid_x == new_subgrid_x and target == CellCheck.COLUMN:
                continue
            if guess in possibles[new_subgrid_x][new_subgrid_y]:
                correct = False
                break
        if not correct:
            break
    return correct


def init_subgrid_possibilities(
    grid: Grid,
    grid_row: int,
    grid_column: int,
) -> List[List[list]]:
    """
    Initialize all possible values for a given subgrid based on given
    row and column (will always target first square in subgrid).
    """
    return [
        [
            grid.cells[(grid_row * SUBGRIDSIZE) + row][
                (grid_column * SUBGRIDSIZE) + column
            ].posibilties
            if grid.cells[(grid_row * SUBGRIDSIZE) + row][(grid_column * SUBGRIDSIZE) + column]
            .value is UNKNOWN
            else []
            for column in range(SUBGRIDSIZE)
        ]
        for row in range(SUBGRIDSIZE)
    ]


def insert_single_valid_number(grid: Grid) -> bool:
    """
    if a position in a line has only 1 possible insert it
    """
    for row in range(SIZE):
        for column in range(SIZE):
            cell = grid.cells[row][column]
            if cell.value is UNKNOWN and len(cell.posibilties) == 1:
                grid.cells[row][column].value = cell.posibilties[0]
                grid.cells[row][column].posibilties.clear()
                return True
    return False


def cross_check(grid: Grid, target: CellCheck) -> bool:
    """
    Compare the possible values for a row or column, if a specific entry in a row has a unique
    value that the other entries do not share we know that the unique value has to fill that entry.
    Then repeat for all rows or column. Target can only be "row" or "column".
    """
    for row in range(SIZE):
        possibles = [[] for _ in range(SIZE)]
        for column in range(SIZE):
            if target is CellCheck.ROW:
                if grid.cells[row][column].value is UNKNOWN:
                    possibles[column] = grid.cells[row][column].posibilties
            elif target is CellCheck.COLUMN:
                if grid.cells[column][row].value is UNKNOWN:
                    possibles[column] = grid.cells[column][row].posibilties
        for column in range(SIZE):
            if not possibles[column]:
                continue
            for guess in possibles[column]:
                correct = True
                for counter in range(SIZE):
                    if guess in possibles[counter] and column != counter:
                        correct = False
                        break
                if correct:
                    if target is CellCheck.ROW:
                        grid.cells[row][column].value = guess
                        grid.cells[row][column].posibilties.clear()
                    elif target is CellCheck.COLUMN:
                        grid.cells[column][row].value = guess
                        grid.cells[column][row].posibilties.clear()
                    return True
    return False


def solve_single_solution(grid: Grid) -> bool:
    """
    A backtracking algorithm to ensure that all solutions are presented.
    Backtracking works by going through each entry in the grid and then testing a valid number.
    Then continue with the next entry, this repeats until a entry cannot be filled,
    then it loops back to the first entry and tries another path.
    This can be represented as a tree and performing a brute force depth first search.
    """
    next_location = get_next_location(grid)
    if not next_location:
        print("Solution found!")
        print_grid(grid)
        stop = timeit.default_timer()
        print("Time: ", stop - start)
        return False
    row = next_location[0]
    column = next_location[1]
    for number in grid.cells[row][column].posibilties:
        if number is UNKNOWN:
            continue
        if number_has_valid_position(grid, row, column, number):
            grid.cells[row][column].value = number
            if solve_single_solution(grid):
                return True
            grid.cells[row][column].value = UNKNOWN
    return False


def number_has_valid_position(grid: Grid, row: int, column: int, number: int) -> bool:
    """
    Validate that the number provided as input is valid for that specific spot on the grid.
    """
    for subgrid_x in range(SUBGRIDSIZE):
        for subgrid_y in range(SUBGRIDSIZE):
            subgrid_position_x = subgrid_x + row - row % SUBGRIDSIZE
            subgrid_position_y = subgrid_y + column - column % SUBGRIDSIZE
            value_at_position = grid.cells[subgrid_position_x][subgrid_position_y].value
            if value_at_position is number:
                return False
    for count in range(SIZE):
        if grid.cells[row][count].value == number or grid.cells[count][column].value is number:
            return False
    return True


def get_next_location(grid: Grid) -> List[int] | None:
    """
    Get the next empty location in the grid.
    """
    for row in range(SIZE):
        for column in range(SIZE):
            if grid.cells[row][column].value is UNKNOWN:
                return [row, column]
    return None


def print_grid_posibilities(grid: Grid) -> None:
    """
    Prints the calculated posibilities for each cell
    """
    print("Possibilities for each cell in the grid")
    print(" ")
    for row in range(SIZE):
        for col in range(SIZE):
            if grid.cells[row][col].value is not UNKNOWN:
                continue
            print(f"[{row}, {col}] : {[hex(v)[2] for v in grid.cells[row][col].posibilties]}")
    print(" ")


main()
