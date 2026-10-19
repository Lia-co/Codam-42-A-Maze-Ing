#!/usr/bin/env python3

import random
from typing import Any

from utils.cell import Cell


def add_frontier(cell: Cell, width: int, height: int, grid: list[list[Cell]]) -> list[Cell]:
    """Adds unvisited neighbors of a cell to the frontier list."""
    frontier: list[Cell] = []
    directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]
    for dx, dy in directions:
        nx, ny = cell.x + dx, cell.y + dy
        # if neighbor cell is within the maze
        if 0 <= nx < width and 0 <= ny < height:
            neighbor = grid[ny][nx]
            if not neighbor.visited and not neighbor.is_special:
                frontier.append(neighbor)
    return frontier


def add_neighbors(cell: Cell, width: int, height: int, grid: list[list[Cell]]) -> list[Cell]:
    """Adds neighbors of a cell to the frontier list."""
    neighbors: list[Cell] = []
    directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]
    for dx, dy in directions:
        nx, ny = cell.x + dx, cell.y + dy
        # if neighbor cell is within the maze
        if 0 <= nx < width and 0 <= ny < height:
            neighbor = grid[ny][nx]
            if not neighbor.is_special:
                neighbors.append(neighbor)
    return neighbors


def remove_walls(current: Cell, neighbor: Cell) -> None:
    """Carves a passage between two adjacent cells."""
    dx = neighbor.x - current.x
    dy = neighbor.y - current.y

    if dx == 1:       # Neighbor is East
        current.east = False
        neighbor.west = False
    elif dx == -1:    # Neighbor is West
        current.west = False
        neighbor.east = False
    elif dy == 1:     # Neighbor is South
        current.south = False
        neighbor.north = False
    elif dy == -1:    # Neighbor is North
        current.north = False
        neighbor.south = False


# 42 pattern
def get_42_pattern_cells(width: int, height: int) -> set[tuple[int, int]]:
    """
    Define the coordinates of the '42' adapted to the maze size.
    """
    special_cells: set[tuple[int, int]] = set()

    # If the maze is too small, avoid placing the '42' to prevent breaking it
    if width < 15 or height < 15:
        return special_cells

    center_x = width // 2 - 3
    center_y = height // 2 - 2

    four = [
        (0, 0), (0, 1), (0, 2),
        (1, 2),
        (2, 2), (2, 3), (2, 4)
    ]
    two = [
        (4, 0), (5, 0), (6, 0),
        (6, 1),
        (4, 2), (5, 2), (6, 2),
        (4, 3),
        (4, 4), (5, 4), (6, 4)
    ]

    for dx, dy in four:
        if 0 <= center_x + dx < width and 0 <= center_y + dy < height:
            special_cells.add((center_x + dx, center_y + dy))

    for dx, dy in two:
        if 0 <= center_x + dx < width and 0 <= center_y + dy < height:
            special_cells.add((center_x + dx, center_y + dy))

    return special_cells


def open_corners(grid: list[list[Cell]], width: int, height: int) -> None:
    corners = [
        (0, 0),
        (width - 1, 0),
        (width - 1, 0),
        (0, height - 1)]
    for cx, cy in corners:
        corner_cell: Cell = grid[cy][cx]
        corner_cell_neighbors: list[Cell] = add_neighbors(corner_cell, width, height, grid)
        for neighbor in corner_cell_neighbors:
            remove_walls(corner_cell, neighbor)


def num_exits(cell: Cell) -> int:
    """number of exits for a cell"""
    return sum(not getattr(cell, s) for s in ("north", "east", "south", "west"))


def braid_pass(grid: list[list[Cell]], width: int, height: int) -> None:
    cells = [c for row in grid for c in row]
    random.shuffle(cells)
    for cell in cells:
        if num_exits(cell) == 1:
            # find neighbors and sort them according to num of exits
            cell_neighbors = add_neighbors(cell, width, height, grid)
            if cell_neighbors:
                # random.shuffle(cell_neighbors)
                cell_neighbors.sort(key=num_exits)
                # remove walls between them
                remove_walls(cell, cell_neighbors[0])


def dfs_maze_generate(config: Any) -> list[list[Cell]]:
    """Depth-first search algorithm - iterative implementation (with stack)
    With a stack to track visited cells, and it will reach every cell. When all
    cells are visited, it trackback to the entry point.
    """
    # if config.seed is not None and config.seed >= 0:
    #    random.seed(config.seed)

    width, height = config.width, config.height

    # 1. Initialize grid using existing Cell class and stack to track path
    grid = [[Cell(x, y) for x in range(width)] for y in range(height)]
    # Cambiado a lista de Cell para que coincida con el stack
    dfs_stack: list[Cell] = []

    # --- NEW adds 42 pattern ---
    special_coords = get_42_pattern_cells(width, height)
    for y_idx in range(height):
        for x_idx in range(width):
            if (x_idx, y_idx) in special_coords:
                grid[y_idx][x_idx].is_special = True
                grid[y_idx][x_idx].visited = True
    # -----------------------------------------------------

    # 2. Pick the start cell and mark it as visited
    init_pos: tuple[int, int] = config.entry
    x1, y1 = init_pos
    start_cell = grid[y1][x1]
    exit_pos: tuple[int, int] = config.exit
    x2, y2 = exit_pos
    exit_cell = grid[y2][x2]

    if start_cell.is_special or exit_cell.is_special:
        raise ValueError("Entry/EXIT can't be located inside the 42 pattern.")

    start_cell.visited = True
    dfs_stack.append(start_cell)

    # 3. look for unvisited neighbor cells in 4 directions

    # 4. main dfs' generation loop
    while dfs_stack:
        # Pop a cell from the stack and make it a current cell
        current_cell = dfs_stack[-1]
        candidates = add_frontier(current_cell, width, height, grid)

        # If the current cell has any neighbours which have not been visited
        if candidates:
            neighbor_cell = random.choice(candidates)
            # Remove the wall
            remove_walls(current_cell, neighbor_cell)
            # Mark the chosen cell as visited and push it to the stack
            neighbor_cell.visited = True
            dfs_stack.append(neighbor_cell)
        else:
            dfs_stack.pop()

    # ==== NEW === if perfect == false (Same as in Prim's)

    if not config.perfect:
        # Break a percentage of internal walls in a controlled way
        # for y in range(height):
        #     for x in range(width):
        #         cell = grid[y][x]
        #         if cell.is_special:
        #             continue
        #         # Choose random neighbors to open extra passages
        #         directions = []
        #         if x < width - 1 and cell.east:
        #             directions.append(grid[y][x + 1])
        #         if y < height - 1 and cell.south:
        #             directions.append(grid[y + 1][x])

        #         # With a low probability
        #         if directions and random.random() < 0.15:
        #             neighbor = random.choice(directions)
        #             if not neighbor.is_special:
        #                 remove_walls(cell, neighbor)

        open_corners(grid, width, height)
        braid_pass(grid, width, height)

    # ========================================================
    return grid
