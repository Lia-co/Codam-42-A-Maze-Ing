#!/usr/bin/env python3
import random
from utils.cell import Cell


def check_walls(cell: Cell, neighbor: Cell) -> bool:
    """find the walls between two cells"""
    # check north wall
    if cell.y - neighbor.y == 1 and cell.north is True and neighbor.south is True:
        return True
    # check east wall
    if cell.x - neighbor.x == -1 and cell.east is True and neighbor.west is True:
        return True
    # check south wall
    if cell.y - neighbor.y == -1 and cell.south is True and neighbor.north is True:
        return True
    # check west wall
    if cell.x - neighbor.x == 1 and cell.west is True and neighbor.east is True:
        return True
    return False


def add_neighbors(cell: Cell, width: int, height: int, grid: list[list[Cell]]) -> list[Cell]:
    """Adds neighbors of a cell to the frontier list."""
    neighbors: list[Cell] = []
    directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]
    for dx, dy in directions:
        nx, ny = cell.x + dx, cell.y + dy
        # if neighbor cell is within the maze
        if 0 <= nx < width and 0 <= ny < height:
            neighbor = grid[ny][nx]
            # only add neighbor with wall in between and not in 42 pattern
            if not neighbor.is_special and check_walls(cell, neighbor) is True:
                neighbors.append(neighbor)
    return neighbors


def open_corners(grid: list[list[Cell]], width: int, height: int) -> None:
    corners = [
        (0, 0),
        (width - 1, 0),
        (width - 1, height - 1),
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
        if cell.is_special is False and num_exits(cell) == 1:
            # find neighbors and sort them according to num of exits
            cell_neighbors = add_neighbors(cell, width, height, grid)
            if cell_neighbors:
                random.shuffle(cell_neighbors)
                cell_neighbors.sort(key=num_exits)
                # remove walls between them
                remove_walls(cell, cell_neighbors[0])


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


def add_frontier(cell: Cell, width: int, height: int, grid: list[list[Cell]]) -> list[tuple[Cell, Cell]]:
    """Adds unvisited neighbors of a cell to the frontier list."""
    frontier: list[tuple[Cell, Cell]] = []

    directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]  # North, South, East, West
    for dx, dy in directions:
        nx, ny = cell.x + dx, cell.y + dy
        if 0 <= nx < width and 0 <= ny < height:
            neighbor = grid[ny][nx]
            if not neighbor.visited and not neighbor.is_special:
                frontier.append((cell, neighbor))
    return frontier


def add_frontier_dfs(cell: Cell, width: int, height: int, grid: list[list[Cell]]) -> list[Cell]:
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
