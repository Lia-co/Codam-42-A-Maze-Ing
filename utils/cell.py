#!/usr/bin/env python3

class Cell:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

        self.visited = False
        self.is_special = False  # <-- to delimit the 42 cells
        self.north = True
        self.east = True
        self.south = True
        self.west = True
