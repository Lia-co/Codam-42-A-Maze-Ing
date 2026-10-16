import random
import sys

from typing import Any, List, Tuple
from mazegen.dfs import dfs_maze_generate
from mazegen.prim import generate_prim_maze
from utils.cell import Cell
from utils import output
from utils.bfs_solver import bfs_maze_solver
from utils.config_parse import parse_config
from utils.render import MazeVisualizer

is_first_run = True


def generate_and_solve(
        config: Any) -> Tuple[List[List[Cell]], List[Tuple[int, int]]]:
    """Generate a new maze and solve it based on the configured algorithm."""
    global is_first_run
    #print("-> Calling maze generator (DFS/PRIM)...")

    if is_first_run:
        # First execution: respect the seed from config.txt if valid
        if hasattr(
                config, 'seed'
                ) and config.seed is not None and config.seed >= 0:
            current_seed = config.seed
        else:
            current_seed = random.randint(1, 999999)
        is_first_run = False
    else:
        # Subsequent executions (interactive regeneration): generate a new
        # random seed and print it
        current_seed = random.randint(1, 999999)
        print(f"New random maze generated! SEED = {current_seed}")

    # Apply the seed for random generation
    random.seed(current_seed)

    if config.algorithm.upper() == "DFS":
        maze = dfs_maze_generate(config)
    elif config.algorithm.upper() == "PRIM":
        maze = generate_prim_maze(config)
    else:
        maze = dfs_maze_generate(config)  # Fallback safety

    #print("-> Solving maze with BFS...")
    solution = bfs_maze_solver(config, maze)
    #print("-> Done generating and solving!")
    return maze, solution


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python a_maze_ing.py <config_file>")
        return

    config_file = sys.argv[1]
    config = parse_config(config_file)

    # Generate and solve the initial maze
    maze, solution = generate_and_solve(config)

    # write output file
    output.write_output(maze, solution, config)

    # Pass the lambda callback so Option 1 can re-generate the maze
    renderer = MazeVisualizer(
        maze=maze,
        config=config,
        solution=solution,
        on_regenerate=lambda: generate_and_solve(config)
    )
    renderer.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
