#!/usr/bin/env python3
import random
from typing import Any
from utils.cell import Cell
from mazegen.mazegen_utils import get_42_pattern_cells, add_frontier, remove_walls, open_corners, braid_pass


def generate_prim_maze(config: Any) -> list[list[Cell]]:
    # Set seed for random generation if specified and valid
    #if config.seed is not None and config.seed >= 0:
    #    random.seed(config.seed)

    width, height = config.width, config.height

    # 1. Initialize grid using your existing Cell class
    grid = [[Cell(x, y) for x in range(width)] for y in range(height)]

    # Get coordinates of the "42" pattern
    special_coords = get_42_pattern_cells(width, height)

    # Mark "42" cells as special and visited so the maze surrounds them
    for y in range(height):
        for x in range(width):
            if (x, y) in special_coords:
                grid[y][x].is_special = True
                # Prevents Prim from carving through them
                grid[y][x].visited = True

    # 2. Pick a random starting cell (that doesn't belong to the "42" pattern)
    while True:
        start_x = random.randint(0, width - 1)
        start_y = random.randint(0, height - 1)
        if not grid[start_y][start_x].is_special:
            break

    start_cell = grid[start_y][start_x]
    start_cell.visited = True

    # 3. Frontier list storing wall connections: (visited_cell, neighbor_cell)
    frontier: list[tuple[Cell, Cell]] = []
    frontier = add_frontier(start_cell, width, height, grid)

    # 4. Main Prim's generation loop (creates a perfect maze tree structure)
    while frontier:
        cell, neighbor = frontier.pop(random.randint(0, len(frontier) - 1))

        if not neighbor.visited and not neighbor.is_special:
            neighbor.visited = True
            remove_walls(cell, neighbor)
            frontier.extend(add_frontier(neighbor, width, height, grid))

    # 5. If PERFECT is False, create pac-man pattern with multiple solutions
    # open 4 corners and try to minimize dead ends until 0
    if not config.perfect:
        open_corners(grid, width, height)
        braid_pass(grid, width, height)

    return grid
