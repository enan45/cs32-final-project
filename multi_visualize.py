### multi_visualize.py
"""Live Pygame visualization of multi-net PCB routing animate each one at a time."""

import pygame
from grid import Cell
from astar import find_path
from lee import find_path_stepped as lee_stepped
from astar import find_path_stepped as astar_stepped
from visualize import ( _draw_background, _draw_grid, _draw_panel, _load_font, _hold_window, _animate_path_reveal, 
                       CELL_SIZE, MARGIN, PANEL_WIDTH,C_PATH, C_PATH_GLOW, FRAME_DELAY_MS, STEPS_PER_FRAME,
)


# Distinct colors for each net's final trace
NET_COLORS = [
    (240, 100, 220),  # magenta
    (100, 200, 255),  # cyan
    (255, 180,  60),  # amber
    (140, 240, 140),  # green
    (255, 120, 120),  # coral
    (180, 140, 255),  # violet
]


def visualize_multinet(grid, netlist, order=None, title="PCB Auto-Router — Multi-Net", algorithm='astar'):
    """Open one Pygame window and animate every net in the netlist."""
    pygame.init()
    pygame.display.set_caption(title)
    
    board_w = grid.cols * CELL_SIZE
    board_h = grid.rows * CELL_SIZE
    win_w   = board_w + 2 * MARGIN + PANEL_WIDTH
    win_h   = board_h + 2 * MARGIN
    
    screen = pygame.display.set_mode((win_w, win_h))
    clock  = pygame.time.Clock()
    
    fonts = {
        'big':   _load_font(24, bold=True),
        'med':   _load_font(18),
        'small': _load_font(14),
        'mono':  _load_font(13, mono=True),
    }
    
    board_rect = pygame.Rect(MARGIN, MARGIN, board_w, board_h)
    panel_rect = pygame.Rect(board_w + 2*MARGIN, MARGIN, PANEL_WIDTH, board_h)
    
    completed_traces = []  # list of (path, color)
    
    if order is None:
        order = list(netlist.keys())
    
    for net_idx, net_name in enumerate(order):
        pads = netlist[net_name]
        if len(pads) < 2:
            continue
        
        net_color = NET_COLORS[net_idx % len(NET_COLORS)]
        net_failed = False
        
        for i in range(len(pads) - 1):
            if net_failed:
                break
            
            source = pads[i]
            target = pads[i + 1]
            
            if algorithm == 'astar': # generator object
                stepper = astar_stepped(grid, source, target)
            else:
                stepper = lee_stepped(grid, source, target) 
            state = None
            path = None
            search_done = False
            step_accum = 0.0
            
            while not search_done:
                dt = clock.tick(60)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); return
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit(); return
                
                step_accum += dt
                if step_accum >= FRAME_DELAY_MS:
                    step_accum = 0.0
                    for _ in range(STEPS_PER_FRAME):
                        try:
                            state = next(stepper)
                            if state['done']:
                                path = state['path']
                                search_done = True
                                break
                        except StopIteration:
                            search_done = True
                            break
                
                _draw_background(screen, board_rect, panel_rect)
                _draw_completed_traces(screen, grid, board_rect, completed_traces)
                _draw_grid(screen, grid, board_rect, state, source, target, path=None)
                _draw_panel(screen, panel_rect, state, source, target,
                           net_name, fonts, searching=True)
                pygame.display.flip()
            
            if path is None:
                print(f"FAIL: {net_name} segment {source} → {target} — abandoning net")
                net_failed = True
                continue
            
            grid.mark_trace(path)
            completed_traces.append((path, net_color))
            
            # Brief reveal pause so the new trace appears
            for _ in range(30):
                clock.tick(60)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); return
                _draw_background(screen, board_rect, panel_rect)
                _draw_completed_traces(screen, grid, board_rect, completed_traces)
                _draw_grid(screen, grid, board_rect, None, source, target, path=None)
                _draw_panel(screen, panel_rect, state, source, target,
                           net_name, fonts, searching=False, final_path=path)
                pygame.display.flip()
    
    print("\nAll nets attempted. Final board ready.")
    _hold_window(screen, clock)

def _draw_completed_traces(screen, grid, board_rect, traces):
    """Draw all previously-completed traces with their net colors."""
    for path, color in traces:
        if len(path) < 2:
            continue
        points = [_cell_center_external(c, r, grid, board_rect) for c, r in path]
        # Glow
        glow = tuple(c // 2 for c in color)
        pygame.draw.lines(screen, glow,  False, points, width=14)
        pygame.draw.lines(screen, color, False, points, width=7)


def _cell_center_external(col, row, grid, board_rect):
    """Re-import-safe cell center calculator."""
    px = board_rect.x + col * CELL_SIZE
    py = board_rect.y + (grid.rows - 1 - row) * CELL_SIZE
    return px + CELL_SIZE // 2, py + CELL_SIZE // 2