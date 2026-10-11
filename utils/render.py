import sys
from typing import Any
from mlx import Mlx

# Amount of pixels x cell
CELL = 20
PANEL_HEIGHT = 100  # Extra height in pixels for the bottom menu

COLOR_BG = 0x1E1E1E      # Dark background for the cell
COLOR_WALL = 0xFFFFFF   # White
COLOR_ENTRY = 0x00FF00  # Green
COLOR_EXIT = 0xFF0000   # Red
COLOR_SPECIAL = 0x808080 # Grey for special cells (42 pattern)
COLOR_PANEL = 0x111111   # Background of the menu panel

class MazeVisualizer:

    def __init__(self, maze: list, config: Any, solution: list, on_regenerate=None) -> None:
        self.maze = maze
        self.config = config
        self.solution = list(solution) if isinstance(solution, set) else solution
        self.on_regenerate = on_regenerate # Callback for re-generating the maze

        # Interactive menu states
        self.show_path_flag = False
        self.color_index = 0
        self.wall_colors = [COLOR_WALL, 0x00FFFF, 0xFFD700, 0xFF69B4] # White, Cyan, Gold, Pink

        # Animation states
        self.animating_path = False
        self.anim_index = 0

        # Total window dimensions (Maze + Bottom panel)
        self.win_width = config.width * CELL
        self.win_height = (config.height * CELL) + PANEL_HEIGHT

        # Create and init object
        self.m = Mlx()
        self.ptr = self.m.mlx_init()

        # Create window with extended height
        self.win = self.m.mlx_new_window(
            self.ptr,
            self.win_width,
            self.win_height,
            "A-Maze-ing"
        )

        # Create image dimensions
        self.img = self.m.mlx_new_image(
            self.ptr,
            self.win_width,
            self.win_height
        )

        # Access image data
        (
            self.data,
            self.bpp,
            self.size_line,
            self.fmt
        ) = self.m.mlx_get_data_addr(self.img)

        # Monitoring events
        self.m.mlx_key_hook(
            self.win,
            self.on_key,
            None
        )

        # Call close method on pressing ESC or closing window
        self.m.mlx_hook(
            self.win,
            17,
            0,
            self.close,
            None
        )

    def put_pixel(self, x: int, y: int, color: int) -> None:
        if x < 0 or x >= self.win_width:
            return
        if y < 0 or y >= self.win_height:
            return

        offset = y * self.size_line + x * 4
        self.data[offset:offset + 4] = bytes([
            color & 0xFF,
            (color >> 8) & 0xFF,
            (color >> 16) & 0xFF,
            255
        ])

    def draw_rect(self, x: int, y: int, width: int, height: int, color: int) -> None:
        for dy in range(height):
            for dx in range(width):
                self.put_pixel(x + dx, y + dy, color)

    def draw_horizontal(self, x: int, y: int, color: int) -> None:
        for i in range(CELL):
            self.put_pixel(x + i, y, color)

    def draw_vertical(self, x: int, y: int, color: int) -> None:
        for i in range(CELL):
            self.put_pixel(x, y + i, color)

    def render_maze(self, *args: Any) -> int:
        # 1. Fill general background and menu panel
        self.draw_rect(0, 0, self.win_width, self.win_height, COLOR_BG)
        self.draw_rect(0, self.config.height * CELL, self.win_width, PANEL_HEIGHT, COLOR_PANEL)

        current_wall_color = self.wall_colors[self.color_index]

        # 2. Draw the maze
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                px = x * CELL
                py = y * CELL

                if hasattr(cell, 'is_special') and cell.is_special:
                    self.draw_rect(px, py, CELL, CELL, COLOR_SPECIAL)

                if cell.north:
                    self.draw_horizontal(px, py, current_wall_color)
                if cell.west:
                    self.draw_vertical(px, py, current_wall_color)
                if cell.south:
                    self.draw_horizontal(px, py + CELL - 1, current_wall_color)
                if cell.east:
                    self.draw_vertical(px + CELL - 1, py, current_wall_color)

                # Show shortest path if active (Option 2) or during animation
                if self.show_path_flag and (x, y) in self.solution:
                    self.draw_rect(px + 6, py + 6, CELL - 12, CELL - 12, 0x00FFFF)

                # Animate path step by step (Option 5)
                if self.animating_path and (x, y) in self.solution[:self.anim_index]:
                    self.draw_rect(px + 6, py + 6, CELL - 12, CELL - 12, 0xFF00FF) # Magenta for animation trail

                # Entry point
                if (x, y) == self.config.entry:
                    self.draw_rect(px + 4, py + 4, CELL - 8, CELL - 8, COLOR_ENTRY)

                # Exit point
                if (x, y) == self.config.exit:
                    self.draw_rect(px + 4, py + 4, CELL - 8, CELL - 8, COLOR_EXIT)

        # 3. Put image to window
        self.m.mlx_put_image_to_window(
            self.ptr,
            self.win,
            self.img,
            0,
            0
        )

        # 4. Draw menu text with mlx_string_put on the bottom panel
        base_y = (self.config.height * CELL) + 15
        self.m.mlx_string_put(self.ptr, self.win, 20, base_y, 0xFFFFFF, "=== A-Maze-ing ===")
        self.m.mlx_string_put(self.ptr, self.win, 20, base_y + 20, 0x00FF00, "1. Re-generate maze")
        self.m.mlx_string_put(self.ptr, self.win, 20, base_y + 35, 0x00FFFF, "2. Show/Hide path | 5. Animate")
        self.m.mlx_string_put(self.ptr, self.win, 20, base_y + 50, 0xFFD700, "3. Rotate wall colours")
        self.m.mlx_string_put(self.ptr, self.win, 20, base_y + 65, 0xFF0000, "4. Quit (ESC)")

        return 0

    def loop_hook(self, *args: Any) -> int:
        """Handles frame updates for path animation"""
        if self.animating_path:
            if self.anim_index < len(self.solution):
                self.anim_index += 1
                self.render_maze()
            else:
                self.animating_path = False
        return 0

    def on_key(self, keycode: int, *args: Any) -> int:
        """Detect keys to interact with the integrated menu"""
        if keycode in (53, 65307, 113, 81, 21, 52, 65434):  # ESC, Q, or Key 4
            self.close()

        elif keycode in (18, 49, 65431):    # Key '1': Re-generate
            print("Option 1: Re-generating maze...")
            if self.on_regenerate:
                try:
                    new_maze, new_solution = self.on_regenerate()
                    self.maze = new_maze
                    self.solution = list(new_solution) if isinstance(new_solution, set) else new_solution
                    print("-> Success: New maze loaded into visualizer.")
                except Exception as e:
                    print(f"-> Error inside on_regenerate: {e}")
            self.render_maze()

        elif keycode in (19, 50, 65432):     # Key '2': Show/Hide path
            self.show_path_flag = not self.show_path_flag
            print(f"Option 2: Show path = {self.show_path_flag}")
            self.render_maze()
        elif keycode in (20, 51, 65433):     # Key '3': Rotate colors
            self.color_index = (self.color_index + 1) % len(self.wall_colors)
            print("Option 3: Rotating wall colors")
            self.render_maze()
        elif keycode in (22, 53, 65435):     # Key '5': Start path animation
            print("Option 5: Animating solution path...")
            self.animating_path = True
            self.anim_index = 0
        return 0

    def close(self, *args: Any) -> int:
        try:
            if self.img:
                self.m.mlx_destroy_image(self.ptr, self.img)
            if self.win:
                self.m.mlx_destroy_window(self.ptr, self.win)
            if hasattr(self.m, "mlx_loop_exit"):
                self.m.mlx_loop_exit(self.ptr)
        except Exception:
            pass
        sys.exit(0)
        return 0

    def start(self) -> None:
        try:
            self.render_maze()
            # Register loop hook for animations if supported by mlx wrapper
            if hasattr(self.m, "mlx_loop_hook"):
                self.m.mlx_loop_hook(self.ptr, self.loop_hook, None)
            self.m.mlx_loop(self.ptr)
        except Exception as e:
            print(f"Error detected: {e}")
            self.close()