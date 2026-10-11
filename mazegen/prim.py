#!/usr/bin/env python3
import random
from typing import Any, List, Tuple
from utils.cell import Cell

def get_42_pattern_cells(width: int, height: int) -> set:
    """
    Define the coordinates of the '42' adapted to the maze size.
    """
    special_cells = set()
    
    # If the maze is too small, avoid placing the '42' to prevent breaking it
    if width < 15 or height < 15:
        return special_cells

    center_x = width // 2 - 4
    center_y = height // 2 - 3
    
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


def remove_walls(current: Cell, neighbor: Cell) -> None:
    """Carves a passage between two adjacent cells."""
    dx = neighbor.x - current.x
    dy = neighbor.y - current.y

    if dx == 1:       # Neighbor is East
        current.east = False
        neighbor.west = False
    elif dx == -1:    # Neighbor is West
        current.west = False
        neighbor.east = False  # Fixed: was set to True, causing wall artifacts/squares
    elif dy == 1:     # Neighbor is South
        current.south = False
        neighbor.north = False
    elif dy == -1:    # Neighbor is North
        current.north = False
        neighbor.south = False


def generate_prim_maze(config: Any) -> List[List[Cell]]:
    # Set seed for random generation if specified and valid
    # if config.seed is not None and config.seed >= 0:
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
                grid[y][x].visited = True  # Prevents Prim from carving through them

    # 2. Pick a random starting cell (that doesn't belong to the "42" pattern)
    while True:
        start_x = random.randint(0, width - 1)
        start_y = random.randint(0, height - 1)
        if not grid[start_y][start_x].is_special:
            break

    start_cell = grid[start_y][start_x]
    start_cell.visited = True

    # 3. Frontier list storing wall connections: (visited_cell, neighbor_cell)
    frontier: List[Tuple[Cell, Cell]] = []

    def add_frontier(cell: Cell) -> None:
        """Adds unvisited neighbors of a cell to the frontier list."""
        directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]  # North, South, East, West
        for dx, dy in directions:
            nx, ny = cell.x + dx, cell.y + dy
            if 0 <= nx < width and 0 <= ny < height:
                neighbor = grid[ny][nx]
                if not neighbor.visited and not neighbor.is_special:
                    frontier.append((cell, neighbor))

    add_frontier(start_cell)

    # 4. Main Prim's generation loop (creates a perfect maze tree structure)
    while frontier:
        cell, neighbor = frontier.pop(random.randint(0, len(frontier) - 1))

        if not neighbor.visited and not neighbor.is_special:
            neighbor.visited = True
            remove_walls(cell, neighbor)
            add_frontier(neighbor)

    # 5. If PERFECT is False, create an imperfect maze by opening extra walls to introduce loops
    # config.perfect is a boolean (True = perfect maze, False = imperfect maze with loops)
    if not config.perfect:
        # Break a percentage of internal walls in a controlled way
        for y in range(height):
            for x in range(width):
                cell = grid[y][x]
                if cell.is_special:
                    continue
                # Choose random neighbors to open extra passages
                directions = []
                if x < width - 1 and cell.east:
                    directions.append(grid[y][x + 1])
                if y < height - 1 and cell.south:
                    directions.append(grid[y + 1][x])
                
                # With a low probability (e.g., 15%), remove an extra wall to create clean loops
                if directions and random.random() < 0.15:
                    neighbor = random.choice(directions)
                    if not neighbor.is_special:
                        remove_walls(cell, neighbor)

    return grid