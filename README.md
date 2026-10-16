*This project has been created as part of the 42 curriculum by betferna and sliang.*

# 1. Description
## 1.1 Overview
*insert a gif to present the demo*</br>
A_Maze_Ing project is aimed at make a reusable maze generation program with UI design. The user can pass data into a config file to manage how the maze look like. The config file decides the size of the maze(WIDTH, HEIGHT), entry and exit location(ENTRY, EXIT), the name of output file including maze map in hexdecimal code, and if the maze is perfect(only one path) or not(multiple paths).

This project is perfect for beginers to understand module logic, algorithms, data parsing process and have fun for UI design.

## 1.2 Tasks distribution

The project is mainly distributed like following:

| Student           | Tasks                                                               |
| -----------       | ------------------------------------------------------------------- |
| sliang            | parse config file                                                   |
| sliang            | dfs maze generating algorithm                                       |
| betferna          | Prim's maze generating algorithm                                    |
| betferna          | Makefile, handle package for virtual environment                    |
| sliang            | bfs solution algorithm                                              |
| betferna          | make (im)perfect pattern                                            |
| betferna          | visualize maze with MLX and add animation                           |
| sliang            | export output file                                                  |
| betferna & sliang | align with mypy and flake8 format                                   |



### 1.2.1 The structure of files
present a tree screenshot and explain briefly

### 1.2.2 Decision reasons for distribution
We seperate tasks equally and both of us work with maze algorithms to make sure that we know the whole structure of generating maze, which is the core part of this projects. We organically cooperate with each other, if one of us finish a task, then another one picks up different tasks.

## 1.3 Data parsing, validation and return object
This project needs to parse the config.txt and return an immutable object with valid data
for later generating a maze.

Here is an example of a config file:
```
# config file
# mandatory part
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True

# conditional part
SEED=42
ALGORITHM=BFS
```

The parsing process is separated into 3 stages:
- read the file and find valid KEY=VALUE pair per line
- validate data and convert to valid data types
- store data into an immutable class and return it
and all empty line or line comment line (start with '#') will be skipped


## 1.4 Algorithms choices
For algorithms of generating maze, we choose Depth-first search algorithm, one of the most common choices, and Prim's algorithm. DFS is suitable for what? Why Prim is special?

For maze solution, we choose Breadth First Search algorithm. 
This algorithm is suitable to find the shortest path since it checks all neighbors by depth level. When it find the exit, it will break immediately.

### 1.4.1 Maze generating algorithm
Depth-first search algorithm - iterative implementatoin (with stack)
With a stack to track visited cells, and it will reach every cell. When all
cells are visited, it trackback to the entry point.

This algorithm follows below steps:
1. Choose the initial cell, mark it as visited and push it to the stack
2. While the stack is not empty
    2.1 Pop a cell from the stack and make it a current cell
    2.2 If the current cell has any neighbours which have not been visited
        2.2.1 Push the current cell to the stack
        2.2.2 Choose one of the unvisited neighbours
        2.2.3 Remove the wall between the current cell and the chosen cell
        2.2.4 Mark the chosen cell as visited and push it to the stack

Prim's algorithm
This algorithm follows below steps:
1. Pick a random cell, mark it as visited
2. Add the cell's all adjacent walls to a frontier list.
3. While the frontier list is not empty:
    3.1 Randomly pick a wall from frontier list.
    3.2 Check if the two cells divided by that wall.
        3.2.1 If only one of them has been visited:
        3.2.2 Carve the wall to connect both cells.
4. Mark the unvisited cell as "visited" and repeat from step 2.
5. If both cells are already visited, simply remove the wall from the list
without doing anything (to prevent creating loops/cycles).

While the frontier list is completely empty and the maze is generated.

### 1.4.2 Maze solution path algorithm
Since this algorithm explores the grid level by level, the first time when it reaches the exit, it is the shortest path. Close your eyes and imagine an image: you throw a stone in the water, there are ripples appear starting from the center point, the first time when the ripple reaches shore, it is the shortest way to find the path to shore.

It is perfect for unweighted maze when compared with other A* and Dijkstra's algorithm, which requires additional heuristic or weight-tracking. DFS can also be used as maze solution algorithm, however, it goes by depth first and it may find the solution quickly, but it is not guaranteed as the shortest one.

This algorithm follows below steps:
1. Start at the entry cell, push it to the queue and visited, and mark its parent cell(None at the start)
2. While the queue is not empty
    2.1 Left pop a cell from the queue and make it a current cell (first in first out)
    2.2 If current cell
        2.2.1 Is the exit, break the loop
        2.2.2 Else, add all accessible neighbors. If neigbors are not visited:
            2.2.2.1 Push the neighbor cell to visited
            2.2.2.2 Push the neighbor cell to queue
            2.2.2.3 Add current cell as neighbor cell's parent as key value pair in a dictionary

When finally it reaches the exit, extra path from parent dictionary and reverse the path. This is the shortest solution for the maze. 


## 1.5 UI design
We decide to use MiniLibX(MLX) as interface window. with MLX, we can have more space for UI design and make it more fun. 

# 2. Instruction
## 2.1 How to install
## 2.2 How to run the program

# 3. Resources
[Grokking Algorithms: An Illustrated Guide for Programmers and Other Curious People](https://www.manning.com/books/grokking-algorithms)</br>
I(sliang) will highly recommend this fun and interesting book. The appealing illustration makes the journey of understanding algorithms really fun. Big thanks for student *ekramer* providing this resource.

[Python Documentation: Dataclass in Python](https://docs.python.org/3/library/dataclasses.html)

[MiniLibX Documentation by 42 students hsmits and jvan-sni](https://harm-smits.github.io/42docs/libs/minilibx/introduction.html)

[GeeksfoGeeks: Differences and Applications of List, Tuple, Set and Dictionary in Python](https://www.geeksforgeeks.org/python/differences-and-applications-of-list-tuple-set-and-dictionary-in-python/)

[W3Schools: Python Random seed() Method](https://www.w3schools.com/PYTHON/ref_random_seed.asp)

[W3Schools: Python List pop() Method](https://www.w3schools.com/python/ref_list_pop.asp)

[W3Schools: Python list() Function](https://www.w3schools.com/python/ref_func_list.asp)

[GeeksforGeeks: Deque in Python](https://www.geeksforgeeks.org/python/deque-in-python/)

[Wikipedia: Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm)

[Breadth First Search or BFS for a Graph](https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/)

