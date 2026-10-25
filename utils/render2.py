import sys
from typing import Any, Callable

from utils.cell import Cell
from mlx import Mlx


# Number of pixels per cell
CELL = 20
PANEL_HEIGHT = 100

# Colors
COLOR_BG = 0x1E1E1E
COLOR_WALL = 0xFFFFFF
COLOR_ENTRY = 0x00FF00
COLOR_EXIT = 0xFF0000
COLOR_SPECIAL = 0x808080
COLOR_PANEL = 0x111111
COLOR_PATH = 0x00FFFF
COLOR_ANIMATION = 0xFF00FF


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
        self.solution = list(solution)
        self.on_regenerate = on_regenerate

        # Interactive menu states
        self.show_path_flag = False
        self.color_index = 0
        self.wall_colors = [
            COLOR_WALL,
            0x00FFFF,
            0xFFD700,
            0xFF69B4,
        ]

        # Animation states
        self.animating_path = False
        self.anim_index = 0

        # Precompute the solution cells for faster rendering
        self.solution_set = set(self.solution)

        # Window dimensions
        self.maze_width = config.width * CELL
        self.maze_height = config.height * CELL
        self.win_width = self.maze_width
        self.win_height = self.maze_height + PANEL_HEIGHT

        # Initialize MiniLibX
        self.m = Mlx()
        self.ptr = self.m.mlx_init()

        if not self.ptr:
            raise RuntimeError("Failed to initialize MiniLibX")

        # Create the window
        self.win = self.m.mlx_new_window(
            self.ptr,
            self.win_width,
            self.win_height,
            "A-Maze-ing",
        )

        if not self.win:
            raise RuntimeError("Failed to create the window")

        # Create the image buffer
        self.img = self.m.mlx_new_image(
            self.ptr,
            self.win_width,
            self.win_height,
        )

        if not self.img:
            raise RuntimeError("Failed to create the image")

        # Access the image pixel buffer
        (
            self.data,
            self.bpp,
            self.size_line,
            self.fmt,
        ) = self.m.mlx_get_data_addr(self.img)

        # Register keyboard and window events
        self.m.mlx_key_hook(self.win, self.on_key, None)
        self.m.mlx_hook(self.win, 17, 0, self.close, None)

    def put_pixel(self, x: int, y: int, color: int) -> None:
        """Write a pixel into the image buffer."""
        if not (0 <= x < self.win_width):
            return
        if not (0 <= y < self.win_height):
            return

        bytes_per_pixel = self.bpp // 8
        if bytes_per_pixel < 3:
            return

        offset = y * self.size_line + x * bytes_per_pixel

        if offset + bytes_per_pixel > len(self.data):
            return

        # Write the color in little-endian byte order
        self.data[offset] = color & 0xFF
        self.data[offset + 1] = (color >> 8) & 0xFF
        self.data[offset + 2] = (color >> 16) & 0xFF

        if bytes_per_pixel >= 4:
            self.data[offset + 3] = 0

    def draw_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: int,
    ) -> None:
        """Draw a filled rectangle."""
        for dy in range(height):
            for dx in range(width):
                self.put_pixel(x + dx, y + dy, color)

    def draw_horizontal(self, x: int, y: int, color: int) -> None:
        """Draw a horizontal wall."""
        for i in range(CELL):
            self.put_pixel(x + i, y, color)

    def draw_vertical(self, x: int, y: int, color: int) -> None:
        """Draw a vertical wall."""
        for i in range(CELL):
            self.put_pixel(x, y + i, color)

    def render_maze(self, *args: Any) -> int:
        """Render the complete maze into the image buffer."""

        # Draw the main background
        self.draw_rect(
            0, 0, self.win_width, self.win_height, COLOR_BG
        )

        # Draw the bottom menu panel
        self.draw_rect(
            0,
            self.maze_height,
            self.win_width,
            PANEL_HEIGHT,
            COLOR_PANEL,
        )

        current_wall_color = self.wall_colors[self.color_index]

        # Get the cells already revealed by the animation
        animated_cells = set(self.solution[:self.anim_index])

        # Draw the maze
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                px = x * CELL
                py = y * CELL

                # Draw special cells
                if getattr(cell, "is_special", False):
                    self.draw_rect(
                        px, py, CELL, CELL, COLOR_SPECIAL
                    )

                # Draw the walls
                if cell.north:
                    self.draw_horizontal(px, py, current_wall_color)

                if cell.west:
                    self.draw_vertical(px, py, current_wall_color)

                if cell.south:
                    self.draw_horizontal(
                        px, py + CELL - 1, current_wall_color
                    )

                if cell.east:
                    self.draw_vertical(
                        px + CELL - 1, py, current_wall_color
                    )

                # Draw the complete solution path
                if (
                    self.show_path_flag
                    and (x, y) in self.solution_set
                ):
                    self.draw_rect(
                        px + 6,
                        py + 6,
                        CELL - 12,
                        CELL - 12,
                        COLOR_PATH,
                    )

                # Draw the animated path
                elif (
                    self.animating_path
                    and (x, y) in animated_cells
                ):
                    self.draw_rect(
                        px + 6,
                        py + 6,
                        CELL - 12,
                        CELL - 12,
                        COLOR_ANIMATION,
                    )

                # Draw the entry point
                if (x, y) == self.config.entry:
                    self.draw_rect(
                        px + 4,
                        py + 4,
                        CELL - 8,
                        CELL - 8,
                        COLOR_ENTRY,
                    )

                # Draw the exit point
                if (x, y) == self.config.exit:
                    self.draw_rect(
                        px + 4,
                        py + 4,
                        CELL - 8,
                        CELL - 8,
                        COLOR_EXIT,
                    )

        # Display the image before drawing the menu text
        self.m.mlx_put_image_to_window(
            self.ptr, self.win, self.img, 0, 0
        )

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
            0x00FFFF, "2. Show/Hide path | 5. Animate"
        )

        self.m.mlx_string_put(
            self.ptr, self.win, 5, base_y + 50,
            0xFFD700, "3. Rotate wall colours"
        )

        self.m.mlx_string_put(
            self.ptr, self.win, 5, base_y + 65,
            0xFF0000, "4. Quit (ESC)"
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
        if keycode in (113, 81, 65307):
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


# menu2
base_y = (self.config.height * CELL) - 25
        self.m.mlx_string_put(
            self.ptr,
            self.win,
            0,
            base_y,
            0xFFFFFF,
            "=== A-Maze-ing ===")
        self.m.mlx_string_put(
            self.ptr,
            self.win,
            0,
            base_y + 20,
            0x00FF00,
            "1. Re-generate maze")
        self.m.mlx_string_put(
            self.ptr,
            self.win,
            0,
            base_y + 35,
            0x00FFFF,
            "2. Show/Hide path | 5. Animate")
        self.m.mlx_string_put(
            self.ptr,
            self.win,
            0,
            base_y + 50,
            0xFFD700,
            "3. Rotate wall colours")
        self.m.mlx_string_put(
            self.ptr,
            self.win,
            0,
            base_y + 65,
            0xFF0000,
            "4. Quit (ESC)")
    
        # 3. Put image to window
        self.m.mlx_put_image_to_window(
            self.ptr, self.win, self.img, 0, 0
        )
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
        if keycode in (113, 81, 21, 52):  # ESC, Q, or Key 4 65434 65307
            self.close()
        elif keycode in (18, 49):    # Key '1': Re-generate 65431
            print("Option 1: Re-generating maze...")
            self.animating_path = False
            if self.on_regenerate:
                try:
                    new_maze, new_solution = self.on_regenerate()
                    self.maze = new_maze
                    self.solution = list(new_solution) if isinstance(
                        new_solution, set) else new_solution
                except Exception as e:
                    print(f"-> Error inside on_regenerate: {e}")
            self.render_maze()
        elif keycode in (19, 50):     # Key '2': Show/Hide path 65432
            self.show_path_flag = not self.show_path_flag
            print(f"Option 2: Show path = {self.show_path_flag}")
            self.render_maze()
        elif keycode in (20, 51):     # Key '3': Rotate colors 65433
            self.color_index = (self.color_index + 1) % len(self.wall_colors)
            print("Option 3: Rotating wall colors")
            self.render_maze()
        elif keycode in (22, 53):    # Key '5': Start path animation 65435
            print("Option 5: Animating solution path...")
            self.show_path_flag = False
            self.animating_path = True
            self.anim_index = 0
            #return 0
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
