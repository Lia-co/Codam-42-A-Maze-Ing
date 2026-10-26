import sys
from typing import Any, Callable
from utils.cell import Cell

from mlx import Mlx

# Amount of pixels x cell
CELL = 20
PANEL_HEIGHT =120  # Extra height in pixels for the bottom menu
PANEL_WIDTH = 250  # Width of the menu panel
COLOR_BG = 0x1E1E1E      # Dark background for the cell
COLOR_WALL = 0xFFFFFF   # White
COLOR_ENTRY = 0x00FF00  # Green
COLOR_EXIT = 0xFF0000   # Red
COLOR_SPECIAL = 0x808080  # Grey for special cells (42 pattern)
COLOR_PANEL = 0x111111   # Background of the menu panel


class MazeVisualizer:
    def __init__(
        self,
        maze: list[list[Cell]],
        config: Any,
        solution: list[tuple[int, int]],
        on_regenerate: Callable[
            [],
            tuple[list[list[Cell]], list[tuple[int, int]]]
        ] | None = None,
    ) -> None:
        self.maze = maze
        self.config = config
        self.solution = solution
        self.on_regenerate = on_regenerate
        self.path_style = 0
        
        # Interactive menu states
        self.show_path_flag = False
        self.color_index = 0
        self.wall_colors = [
            COLOR_WALL,
            0x00FFFF,
            0xFFD700,
            0xFF69B4]  # White, Cyan, Gold, Pink

        # Animation states for the solution path
        self.animating_path = False
        self.anim_index = 0

        # Precompute the solution cells for faster rendering
        self.solution_set = set(self.solution)

        # Window dimensions
        self.maze_width = config.width * CELL
        self.maze_height = config.height * CELL
        self.win_width = self.maze_width if self.maze_width > PANEL_WIDTH else PANEL_WIDTH
        self.win_height = self.maze_height + PANEL_HEIGHT

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
        (self.data, self.bpp, self.size_line,
         self.fmt) = self.m.mlx_get_data_addr(self.img)

        # Monitoring events
        self.m.mlx_key_hook(self.win, self.on_key, None)

        # Call close method on pressing ESC or closing window
        self.m.mlx_hook(self.win, 17, 0, self.close, None)

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

    def draw_rect(self, x: int, y: int, width: int,
                  height: int, color: int) -> None:
        for dy in range(height):
            for dx in range(width):
                self.put_pixel(x + dx, y + dy, color)

    def draw_horizontal(self, x: int, y: int, color: int) -> None:
        for i in range(CELL):
            self.put_pixel(x + i, y, color)

    def draw_vertical(self, x: int, y: int, color: int) -> None:
        for i in range(CELL):
            self.put_pixel(x, y + i, color)

    # Change style of path
    def draw_path_marker(self, x: int, y: int, color: int) -> None:
        px = x * CELL
        py = y * CELL

        #square
        if self.path_style == 0:
            self.draw_rect(px + 6, py + 6, 8, 8, 0x00FFFF)

        elif self.path_style == 1:
        # Diamond
            self.draw_rect(px + 8, py + 5, 4, 10, 0xFF00FF)
            self.draw_rect(px + 6, py + 7, 8, 6, 0xFF00FF)

        elif self.path_style == 2:
        # Cross
            self.draw_rect(px + 8, py + 4, 4, 12, 0xFFD700)
            self.draw_rect(px + 4, py + 8, 12, 4, 0xFFD700)

        elif self.path_style == 3:
        # Small diamond
            self.draw_rect(px + 8, py + 7, 4, 6, 0x00FF00)
            self.draw_rect(px + 7, py + 8, 6, 4, 0x00FF00)

    def render_maze(self, *args: Any) -> int:
        # 1. Fill general background and menu panel
        self.draw_rect(0, 0, self.win_width, self.win_height, COLOR_BG)
        self.draw_rect(
            0,
            self.config.height *
            CELL,
            self.win_width,
            PANEL_HEIGHT,
            COLOR_PANEL)
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

                # Show shortest path if active (Option 2)
                #        x, y) in self.solution:
                #    self.draw_rect(
                #        px + 6, py + 6, CELL - 12, CELL - 12, 0x00FFFF)
                
                if self.show_path_flag and not self.animating_path and (
                        x, y) in self.solution_set:
                    self.draw_path_marker(x, y, 0x00FFFF)

                # Animate path step by step (Option 5)
                #if self.animating_path and (
                #        x, y) in self.solution[:self.anim_index]:
                #    self.draw_rect(
                #        px + 6,
                #        py + 6,
                #        CELL - 12,
                #        CELL - 12,
                #        0xFF00FF)  # Magenta for animation trail

                if self.animating_path and (x, y) in self.solution[:self.anim_index]:
                    self.draw_path_marker(x, y, 0xFF00FF)  # Magenta for animation trail

                # Entry point
                if (x, y) == self.config.entry:
                    self.draw_rect(
                        px + 4, py + 4, CELL - 8, CELL - 8, COLOR_ENTRY)

                # Exit point
                if (x, y) == self.config.exit:
                    self.draw_rect(
                        px + 4, py + 4, CELL - 8, CELL - 8, COLOR_EXIT)

        # 3. Put image to window
        self.m.mlx_put_image_to_window(
            self.ptr, self.win, self.img, 0, 0
        )

        # 4. Draw menu text with mlx_string_put on the bottom panel
        # Draw the menu text after the image
        # This prevents the image from covering the text
        base_y = self.maze_height + 5

        self.m.mlx_string_put(
            self.ptr, self.win, 5, base_y,
            0xFFFFFF, "=== A-Maze-ing ==="
        )

        self.m.mlx_string_put(
            self.ptr, self.win, 5, base_y + 20,
            0x00FF00, "1. Re-generate maze"
        )

        self.m.mlx_string_put(
            self.ptr, self.win, 5, base_y + 35,
            0x00FFFF, "2. Show/Hide path"
        )

        self.m.mlx_string_put(
            self.ptr, self.win, 5, base_y + 50,
            0xFFD700, "3. Rotate wall colours"
        )

        self.m.mlx_string_put(
            self.ptr, self.win, 5, base_y + 65,
            0xFF0000, "4. Quit (ESC)"
        )

        self.m.mlx_string_put(
            self.ptr, self.win, 5, base_y + 80,
            0xFF00FF, "5. Animate path"
        )

        return 0

    def loop_hook(self, *args: Any) -> int:
        """Update the animation one step at a time."""
        if not self.animating_path:
            return 0

        if self.anim_index < len(self.solution):
            self.anim_index += 1
            self.render_maze()
        else:
            self.animating_path = False
            self.render_maze()

        return 0

    def on_key(self, keycode: int, *args: Any) -> int:
        """Handle keyboard input."""

        # Quit using ESC or Q
        if keycode in (113, 81, 65307, 52):
            self.close()
            return 0

        # Option 1: Regenerate the maze
        if keycode in (18, 49):
            print("Option 1: Re-generating maze...")

            self.animating_path = False
            self.anim_index = 0
            self.show_path_flag = False

            if self.on_regenerate:
                try:
                    new_maze, new_solution = self.on_regenerate()

                    self.maze = new_maze
                    self.solution = list(new_solution)
                    self.solution_set = set(self.solution)

                except Exception as error:
                    print(f"Error regenerating maze: {error}")

            self.render_maze()

        # Option 2: Show or hide the solution
        elif keycode in (19, 50):
            self.animating_path = False
            self.show_path_flag = not self.show_path_flag
            self.render_maze()

        # Option 3: Change wall colours
        elif keycode in (20, 51):
            self.color_index = (
                self.color_index + 1
            ) % len(self.wall_colors)

            self.render_maze()

        # Option 5: Animate the solution
        elif keycode in (22, 53):
            print("Option 5: Animating solution path...")

            self.show_path_flag = False
            self.animating_path = True
            self.anim_index = 0
            self.path_style = (self.path_style + 1) % 4  # Toggle between styles
            self.render_maze()

        return 0

    def close(self, *args: Any) -> int:
        """Release MiniLibX resources and close the application."""
        try:
            if getattr(self, "img", None):
                self.m.mlx_destroy_image(self.ptr, self.img)
                self.img = None

            if getattr(self, "win", None):
                self.m.mlx_destroy_window(self.ptr, self.win)
                self.win = None

            if hasattr(self.m, "mlx_loop_exit"):
                self.m.mlx_loop_exit(self.ptr)

        except Exception as error:
            print(f"Error while closing: {error}")

        raise SystemExit(0)

    def start(self) -> None:
        """Render the maze and start the MiniLibX event loop."""
        try:
            self.render_maze()

            if hasattr(self.m, "mlx_loop_hook"):
                self.m.mlx_loop_hook(
                    self.ptr, self.loop_hook, None
                )

            self.m.mlx_loop(self.ptr)

        except Exception as error:
            print(f"Error detected: {error}")
            self.close()