import sys
from utils.config_parse import parse_config
from mazegen.dfs import dfs_maze_generate
from mazegen.prim import generate_prim_maze
from utils.bfs_solver import bfs_maze_solver
from utils import output
from utils.render import MazeVisualizer

def generate_and_solve(config):
    """Generate a new maze and solve it based on the configured algorithm."""
    print("-> Calling maze generator (DFS/PRIM)...")
    if config.algorithm.upper() == "DFS":
        maze = dfs_maze_generate(config)
    elif config.algorithm.upper() == "PRIM":
        maze = generate_prim_maze(config)
    else:
        maze = dfs_maze_generate(config) # Fallback safety
    
    print("-> Solving maze with BFS...")
    solution = bfs_maze_solver(config, maze)
    print("-> Done generating and solving!")
    return maze, solution

def main():
    if len(sys.argv) < 2:
        print("Usage: python a_maze_ing.py <config_file>")
        return

    config_file = sys.argv[1]
    config = parse_config(config_file)
    
    # Generate and solve the initial maze
    maze, solution = generate_and_solve(config)

    # write output file
    output.write_output(maze, solution, config)

    # print maze for testing
    print(f"Laberinth generated: {len(maze[0])}x{len(maze)} ({len(maze) * len(maze[0])} total cells).")
    # --- print maze on terminal for testing ---
    print(f"\n--- DISPLAY MAZE FOR TESTING ({config.width}x{config.height}) ---")
    for y, row in enumerate(maze):
        line = ""
        for cell in row:
            top = "---" if cell.north else "   "
            left = "|" if cell.west else " "
            line += left + top
        print(line)
    print("-" * 40)

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