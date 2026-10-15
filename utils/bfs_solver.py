#!/usr/bin/env python3

"""
Breadth-first Search (BFS) Solution

The algorithm starts at the entry point, and it push all surrounding
accessible neighbors in a queue waiting for visiting. The visited current
cell will be the parent cell for its neighbors.

Important variables for this algorithm:
- current cell: mark the current cell
- queue: the waiting line of cells will be visited
- visited: record all visited cell. If the cell is within the visited cell
- list, it won't be add to the queue again
- parent: record the cell's parent cell, and it will become the path
"""

from collections import deque

from utils.cell import Cell
from utils.config_parse import Config


def add_accessible_neighbors(
        current: Cell,
        maze: list[list[Cell]]) -> list[Cell]:
    """check available neighbor cells."""
    available_neighbor: list[Cell] = []
    directions = {
        "north": (0, -1, "north"),
        "east": (1, 0, "east"),
        "south": (0, 1, "south"),
        "west": (-1, 0, "west")}
    for dx, dy, wall in directions.values():
        # not that clear about how does getattr check if wall exits
        if getattr(current, wall):
            continue
        dx, dy = current.x + dx, current.y + dy
        if 0 <= dx < len(maze[0]) and 0 <= dy < len(maze):
            available_neighbor.append(maze[dy][dx])
    return available_neighbor


def bfs_maze_solver(
        config: Config,
        maze: list[list[Cell]]) -> list[tuple[int, int]]:
    # initialize start, goal, visited, queue and parent
    x1, y1 = config.entry
    start = maze[y1][x1]
    x2, y2 = config.exit
    goal = maze[y2][x2]

    visited: set[tuple[int, int]] = {(start.x, start.y)}
    queue: deque[tuple[int, int]] = deque([start])
    parent: dict[tuple[int, int], tuple[int, int] | None] = {
        (start.x, start.y): None}

    while len(queue) != 0:
        # howt to make current as a Cell?
        current = queue.popleft()

        # if it reaches the exit, break the loop
        if current == goal:
            break
        # else add accessible neighbors to the queue
        for neighbor in add_accessible_neighbors(current, maze):
            neighbor_pos: tuple[int, int] = (neighbor.x, neighbor.y)
            if neighbor_pos not in visited:
                visited.add(neighbor_pos)
                queue.append(neighbor)
                # how to add current cell as neighbor's parent cell in a dict?
                parent[neighbor_pos] = (current.x, current.y)

    # check if exit in path
    if config.exit not in parent:
        raise ValueError("EXIT is not visited.")
    # if exit in path, then reconstruct path from exit to entry
    else:
        last_spot: tuple[int, int] | None = config.exit
        path: list[tuple[int, int]] = []
        while last_spot is not None:
            path.append(last_spot)
            last_spot = parent[last_spot]
    path.reverse()
    return path
