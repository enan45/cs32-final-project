# initialize pygame window
# load the circuit (build_555_timer)
# pick source and target from pads dict
#from youtube video on pygame....
# create the stepped generator ----> currently reading on generator protocols...
# for each (visited, frontier, came_from) yielded by the generator:
#     handle window events (close button etc.)
#     clear window and redraw all cells with current colors
#     display current iteration count
#     pygame.display.flip()
#     small delay for animation speed
# when generator returns the final path:
#     draw the path in purple on top
#     keep window open until user closes it

"""Simple Pygame viewer for one routed PCB net.

This file does not animate the search.
It only shows the board and the final path.
"""

import pygame

from grid import Cell
from lee import find_path


# Window and cell sizes
CELL_SIZE = 32
TOP_BAR_HEIGHT = 50
MARGIN = 20

# Colors
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
GRID_LINE_COLOR = (90, 90, 90)

FREE_COLOR = (240, 240, 240)
BLOCKED_COLOR = (70, 70, 70)
PAD_COLOR = (255, 210, 80)
PATH_COLOR = (80, 140, 255)

SOURCE_COLOR = (60, 200, 120)
TARGET_COLOR = (220, 90, 90)


def visualize_route(grid, source, target, net_name="NET"):
    """Show the grid and the final route in a Pygame window."""

    pygame.init()
    pygame.display.set_caption("PCB Router Demo")

    board_width = grid.cols * CELL_SIZE
    board_height = grid.rows * CELL_SIZE

    window_width = board_width + 2 * MARGIN
    window_height = board_height + 2 * MARGIN + TOP_BAR_HEIGHT

    screen = pygame.display.set_mode((window_width, window_height))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)

    # Find the path once
    path = find_path(grid, source, target)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Fill background
        screen.fill(BACKGROUND_COLOR)

        # Draw title text
        if path is None:
            message = f"{net_name}: no path found"
        else:
            message = f"{net_name}: path found with {len(path)} cells"

        text_surface = font.render(message, True, TEXT_COLOR)
        screen.blit(text_surface, (MARGIN, 12))

        # Draw the board cells
        for row in range(grid.rows):
            for col in range(grid.cols):
                cell = grid.get(col, row)
                rect = cell_rect(grid, col, row)

                if cell.state == Cell.FREE:
                    color = FREE_COLOR
                elif cell.state == Cell.BLOCKED:
                    color = BLOCKED_COLOR
                elif cell.state == Cell.PAD:
                    color = PAD_COLOR
                elif cell.state == Cell.TRACE:
                    color = PATH_COLOR
                else:
                    color = FREE_COLOR

                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)

        # Draw the final path on top
        if path is not None:
            for col, row in path:
                rect = cell_rect(grid, col, row)
                pygame.draw.rect(screen, PATH_COLOR, rect)
                pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)

        # Draw source and target last so they stand out
        draw_special_cell(screen, grid, source, SOURCE_COLOR)
        draw_special_cell(screen, grid, target, TARGET_COLOR)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


def cell_rect(grid, col, row):
    """Return the pygame.Rect for one grid cell."""

    x = MARGIN + col * CELL_SIZE

    # Row 0 is the bottom row, so flip the y direction for drawing
    y = MARGIN + TOP_BAR_HEIGHT + (grid.rows - 1 - row) * CELL_SIZE

    return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)


def draw_special_cell(screen, grid, position, color):
    """Draw one important cell, like source or target."""

    col, row = position
    rect = cell_rect(grid, col, row)

    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)
