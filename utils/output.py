#!/usr/bin/env python3

import itertools
from typing import Final

from utils.cell import Cell
from utils.config_parse import Config

"""
Bit masks wall's direction
"""
DIR_BIT: Final[dict[str, int]] = {
    "north": 1,     # 0001
    "east": 2,      # 0010
    "south": 4,     # 0100
    "west": 8       # 1000
}

DIR_MOVE: Final[dict[tuple[int, int], str]] = {
    (0, -1): "N",
    (1, 0): "E",
    (0, 1): "S",
    (-1, 0): "W"
}


def cell_to_hex(cell: Cell) -> str:
    val: int = 0
    for wall, wall_bitmask in DIR_BIT.items():
        if getattr(cell, wall):
            val = val | wall_bitmask
    return format(val, "X")


def maze_to_hex(maze: list[list[Cell]]) -> list[str]:
    width, height = len(maze[0]), len(maze)
    lines: list[str] = []
    for y in range(height):
        line = "".join(cell_to_hex(maze[y][x])for x in range(width))
        lines.append(line)
    return lines


def path_to_str(solution: list[tuple[int, int]]) -> str:
    dir_path: list[str] = []
    for (x1, y1), (x2, y2) in itertools.pairwise(solution):
        dx, dy = x2 - x1, y2 - y1
        dir_path.append(DIR_MOVE[(dx, dy)])
    path_str = "".join(dir_path)
    return path_str


def write_output(
        maze: list[list[Cell]],
        solution: list[tuple[int, int]],
        config: Config) -> None:
    lines_hex = maze_to_hex(maze)
    solution_str = path_to_str(solution)
    entry_pos_str = ','.join(str(val) for val in config.entry)
    exit_pos_str = ','.join(str(val) for val in config.exit)

    with open(config.output_file, "w") as f:
        f.writelines(line + "\n" for line in lines_hex)
        f.write("\n")
        f.write(entry_pos_str + "\n")
        f.write(exit_pos_str + "\n")
        f.write(solution_str + "\n")

    # write seed
        seed_val = getattr(config, 'seed', 'N/A')
        f.write(f"SEED={seed_val}\n")
