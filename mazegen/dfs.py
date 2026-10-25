#!/usr/bin/env python3

import random
from typing import Any
from utils.cell import Cell
from mazegen.mazegen_utils import get_42_pattern_cells, add_frontier_dfs, remove_walls, open_corners, braid_pass


def dfs_maze_generate(config: Any) -> list[list[Cell]]:
    """Depth-first search algorithm - iterative implementation (with stack)
    With a stack to track visited cells, and it will reach every cell. When all
    cells are visited, it trackback to the entry point.
    """
    #if config.seed is not None and config.seed >= 0:
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

    # 4. main dfs' generation loop
    while dfs_stack:
        # Pop a cell from the stack and make it a current cell
        current_cell = dfs_stack[-1]
        candidates = add_frontier_dfs(current_cell, width, height, grid)

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
        open_corners(grid, width, height)
        braid_pass(grid, width, height)

    # ========================================================
    return grid
