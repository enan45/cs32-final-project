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

### visualize.py
"""Live Pygame visualization of PCB routing with A* / Lee's algorithm."""

import sys
import math
import visualize

from grid     import Cell
from lee      import find_path_stepped


# ─── Visual theme ──────────────────────────────────────────────────────────
# Colors chosen to evoke a real PCB: dark green substrate, copper traces,
# warm amber pads. Everything on a dark palette so the routing colors pop.

C_BG          = (10,  20,  18)     # near-black background outside board
C_BOARD       = (10,  60,  45)     # dark green PCB substrate
C_GRID_DOT    = (60, 110,  90)     # faint grid dots on the board
C_FREE        = (10,  60,  45)     # same as board — free cells invisible
C_BLOCKED     = (35,  35,  38)     # component body, near-black
C_BLOCKED_EDGE= (180, 180, 180)    # white silkscreen outline
C_PAD         = (220, 170,  55)    # copper pad — warm amber
C_PAD_HOLE    = (15,  25,  20)     # drill hole in center of pad

C_VISITED     = (180,  60,  80)    # red-ish, cells already processed
C_FRONTIER    = (120, 220, 120)    # green, cells in the open set
C_CURRENT     = (255, 255, 120)    # bright yellow, the cell being expanded

C_PATH        = (240, 100, 220)    # magenta/purple, the final trace
C_PATH_GLOW   = (180,  40, 160)    # darker halo around the path

C_SOURCE      = (255, 140,  40)    # orange, source pad
C_TARGET      = (60,  220, 220)    # cyan, target pad

C_TEXT        = (230, 240, 235)
C_TEXT_DIM    = (150, 170, 160)
C_PANEL_BG    = (20,  30,  28)
C_PANEL_EDGE  = (80, 120, 100)


# ─── Layout ────────────────────────────────────────────────────────────────

CELL_SIZE       = 30       # pixels per grid cell
MARGIN          = 40       # board padding from window edge
PANEL_WIDTH     = 280      # info panel on the right
STEPS_PER_FRAME = 1        # how many BFS iterations per animation frame
FRAME_DELAY_MS  = 30       # milliseconds between frames
PATH_DRAW_MS    = 80       # ms per cell when drawing the final path


# ─── Main entry point ──────────────────────────────────────────────────────

def visualize_route(grid, source, target, net_name="NET",
                    title="PCB Auto-Router — Lee's Algorithm"):
    """Open a Pygame window and animate a single-net route live."""
    visualize.init()
    visualize.display.set_caption(title)

    board_w = grid.cols * CELL_SIZE
    board_h = grid.rows * CELL_SIZE
    win_w   = board_w + 2 * MARGIN + PANEL_WIDTH
    win_h   = board_h + 2 * MARGIN

    screen = visualize.display.set_mode((win_w, win_h))
    clock  = visualize.time.Clock()

    # Font setup — try nice fonts, fall back gracefully
    font_big    = _load_font(24, bold=True)
    font_med    = _load_font(18)
    font_small  = _load_font(14)
    font_mono   = _load_font(13, mono=True)

    fonts = {'big': font_big, 'med': font_med,
             'small': font_small, 'mono': font_mono}

    board_rect = visualize.Rect(MARGIN, MARGIN, board_w, board_h)
    panel_rect = visualize.Rect(board_w + 2*MARGIN, MARGIN, PANEL_WIDTH, board_h)

    # Run the generator through the search
    stepper = find_path_stepped(grid, source, target)
    state   = None
    path    = None
    paused  = False

    # Phase 1 — live search animation
    running = True
    search_done = False
    step_accumulator = 0.0

    while running and not search_done:
        dt = clock.tick(60)

        for event in visualize.event.get():
            if event.type == visualize.QUIT:
                visualize.quit()
                return
            if event.type == visualize.KEYDOWN:
                if event.key == visualize.K_SPACE:
                    paused = not paused
                if event.key == visualize.K_ESCAPE:
                    visualize.quit()
                    return

        # Advance the BFS by some steps per frame
        if not paused:
            step_accumulator += dt
            if step_accumulator >= FRAME_DELAY_MS:
                step_accumulator = 0.0
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

        # Draw everything
        _draw_background(screen, board_rect, panel_rect)
        if state is not None:
            _draw_grid(screen, grid, board_rect, state, source, target, path=None)
        else:
            _draw_grid(screen, grid, board_rect, None, source, target, path=None)
        _draw_panel(screen, panel_rect, state, source, target, net_name,
                    fonts, searching=True, paused=paused)
        visualize.display.flip()

    # Phase 2 — dramatic reveal of final path
    if path is not None:
        _animate_path_reveal(screen, grid, board_rect, panel_rect,
                             state, source, target, net_name, path, fonts, clock)
    else:
        _show_failure(screen, grid, board_rect, panel_rect,
                      state, source, target, net_name, fonts, clock)

    # Phase 3 — hold until user closes window
    _hold_window(screen, clock)


# ─── Drawing helpers ───────────────────────────────────────────────────────

def _load_font(size, bold=False, mono=False):
    """Try a few nice fonts, fall back to the default."""
    candidates = []
    if mono:
        candidates = ['JetBrains Mono', 'Fira Code', 'Menlo', 'Consolas',
                      'DejaVu Sans Mono', 'Courier New']
    else:
        candidates = ['SF Pro Display', 'Inter', 'Segoe UI', 'Helvetica Neue',
                      'DejaVu Sans', 'Arial']
    for name in candidates:
        try:
            return visualize.font.SysFont(name, size, bold=bold)
        except Exception:
            continue
    return visualize.font.Font(None, size)


def _cell_to_pixel(col, row, grid, board_rect):
    """Grid coordinate → top-left pixel of that cell.
    Row 0 is at the bottom so we flip y."""
    px = board_rect.x + col * CELL_SIZE
    py = board_rect.y + (grid.rows - 1 - row) * CELL_SIZE
    return px, py


def _cell_center(col, row, grid, board_rect):
    px, py = _cell_to_pixel(col, row, grid, board_rect)
    return px + CELL_SIZE // 2, py + CELL_SIZE // 2


def _draw_background(screen, board_rect, panel_rect):
    screen.fill(C_BG)
    # Board substrate with a subtle inner glow
    visualize.draw.rect(screen, C_BOARD, board_rect)
    visualize.draw.rect(screen, C_PANEL_EDGE, board_rect, width=2)
    # Panel
    visualize.draw.rect(screen, C_PANEL_BG, panel_rect)
    visualize.draw.rect(screen, C_PANEL_EDGE, panel_rect, width=2)


def _draw_grid(screen, grid, board_rect, state, source, target, path=None):
    """Draw all cells with colors reflecting their role in the search."""
    visited  = state['visited']  if state else set()
    frontier = set(state['frontier']) if state else set()
    current  = state['current']  if state else None

    # Pass 1 — dim background: visited and frontier
    for row in range(grid.rows):
        for col in range(grid.cols):
            cell = grid.get(col, row)
            px, py = _cell_to_pixel(col, row, grid, board_rect)
            rect = visualize.Rect(px, py, CELL_SIZE, CELL_SIZE)

            if cell.state == Cell.BLOCKED:
                _draw_component(screen, rect)
            elif (col, row) in visited and (col, row) != source and (col, row) != target:
                _draw_visited(screen, rect)
            elif (col, row) in frontier:
                _draw_frontier(screen, rect)
            # else: free / pad — background stays green, we'll overlay pads next

    # Pass 2 — grid dots on free cells
    for row in range(grid.rows):
        for col in range(grid.cols):
            if (col, row) in visited or (col, row) in frontier:
                continue
            cell = grid.get(col, row)
            if cell.state in (Cell.FREE, Cell.PAD):
                cx, cy = _cell_center(col, row, grid, board_rect)
                visualize.draw.circle(screen, C_GRID_DOT, (cx, cy), 1)

    # Pass 3 — the final path (if we have one)
    if path is not None:
        _draw_path(screen, grid, board_rect, path)

    # Pass 4 — pads on top of everything so they stay visible
    for row in range(grid.rows):
        for col in range(grid.cols):
            cell = grid.get(col, row)
            if cell.state == Cell.PAD:
                px, py = _cell_to_pixel(col, row, grid, board_rect)
                rect = visualize.Rect(px, py, CELL_SIZE, CELL_SIZE)
                if (col, row) == source:
                    _draw_pad(screen, rect, C_SOURCE, label='S')
                elif (col, row) == target:
                    _draw_pad(screen, rect, C_TARGET, label='T')
                else:
                    _draw_pad(screen, rect, C_PAD)

    # Pass 5 — the currently-expanding cell gets a bright highlight
    if current is not None and current not in (source, target):
        px, py = _cell_to_pixel(*current, grid, board_rect)
        rect = visualize.Rect(px, py, CELL_SIZE, CELL_SIZE)
        visualize.draw.rect(screen, C_CURRENT, rect.inflate(-6, -6), border_radius=4)


def _draw_component(screen, rect):
    """Draw a blocked cell as dark silicon with a silkscreen outline."""
    inner = rect.inflate(-2, -2)
    visualize.draw.rect(screen, C_BLOCKED, inner, border_radius=2)
    visualize.draw.rect(screen, C_BLOCKED_EDGE, inner, width=1, border_radius=2)


def _draw_visited(screen, rect):
    """Draw a cell that has been expanded — translucent red."""
    surf = visualize.Surface((CELL_SIZE, CELL_SIZE), visualize.SRCALPHA)
    inner = visualize.Rect(3, 3, CELL_SIZE - 6, CELL_SIZE - 6)
    visualize.draw.rect(surf, (*C_VISITED, 140), inner, border_radius=3)
    screen.blit(surf, rect.topleft)


def _draw_frontier(screen, rect):
    """Draw a cell in the open set — brighter green."""
    surf = visualize.Surface((CELL_SIZE, CELL_SIZE), visualize.SRCALPHA)
    inner = visualize.Rect(2, 2, CELL_SIZE - 4, CELL_SIZE - 4)
    visualize.draw.rect(surf, (*C_FRONTIER, 200), inner, border_radius=3)
    screen.blit(surf, rect.topleft)


def _draw_pad(screen, rect, color, label=None):
    """Draw a pad as a donut — copper ring with a drill hole."""
    cx, cy = rect.center
    radius_outer = CELL_SIZE // 2 - 3
    radius_inner = max(3, CELL_SIZE // 6)
    # Outer copper ring
    visualize.draw.circle(screen, color, (cx, cy), radius_outer)
    visualize.draw.circle(screen, (255, 255, 255), (cx, cy), radius_outer, width=1)
    # Drill hole
    visualize.draw.circle(screen, C_PAD_HOLE, (cx, cy), radius_inner)
    # Optional label
    if label:
        font = _load_font(12, bold=True)
        text = font.render(label, True, (255, 255, 255))
        trect = text.get_rect(center=(cx, cy - radius_outer - 8))
        screen.blit(text, trect)


def _draw_path(screen, grid, board_rect, path, progress=1.0):
    """Draw the final routed trace.

    progress: 0.0-1.0 fraction of the path to draw — used for animated reveal.
    """
    if len(path) < 2:
        return

    # How many full segments to draw
    total_segs = len(path) - 1
    full_segs  = int(total_segs * progress)
    partial    = (total_segs * progress) - full_segs

    # Build the list of points (cell centers)
    points = [_cell_center(c, r, grid, board_rect) for c, r in path]

    # Draw glow layer first
    if full_segs >= 1:
        visualize.draw.lines(screen, C_PATH_GLOW, False,
                          points[:full_segs + 1], width=14)
    if full_segs < total_segs and partial > 0:
        p0 = points[full_segs]
        p1 = points[full_segs + 1]
        px = p0[0] + (p1[0] - p0[0]) * partial
        py = p0[1] + (p1[1] - p0[1]) * partial
        visualize.draw.line(screen, C_PATH_GLOW, p0, (px, py), width=14)

    # Then the main trace on top
    if full_segs >= 1:
        visualize.draw.lines(screen, C_PATH, False,
                          points[:full_segs + 1], width=7)
    if full_segs < total_segs and partial > 0:
        p0 = points[full_segs]
        p1 = points[full_segs + 1]
        px = p0[0] + (p1[0] - p0[0]) * partial
        py = p0[1] + (p1[1] - p0[1]) * partial
        visualize.draw.line(screen, C_PATH, p0, (px, py), width=7)


def _draw_panel(screen, panel_rect, state, source, target, net_name, fonts,
                searching=True, paused=False, final_path=None):
    """Draw the info panel on the right."""
    x = panel_rect.x + 16
    y = panel_rect.y + 16

    # Title
    title = fonts['big'].render("PCB AUTO-ROUTER", True, C_TEXT)
    screen.blit(title, (x, y))
    y += 32
    subtitle = fonts['small'].render("Lee's algorithm · h=0 A*", True, C_TEXT_DIM)
    screen.blit(subtitle, (x, y))
    y += 30

    # Divider
    visualize.draw.line(screen, C_PANEL_EDGE,
                     (x, y), (panel_rect.right - 16, y))
    y += 16

    # Net info
    _panel_label(screen, fonts, x, y, "NET")
    y += 18
    net_text = fonts['med'].render(net_name, True, C_SOURCE)
    screen.blit(net_text, (x, y))
    y += 28

    _panel_kv(screen, fonts, x, y, "Source", f"{source}")
    y += 20
    _panel_kv(screen, fonts, x, y, "Target", f"{target}")
    y += 28

    # Stats
    visualize.draw.line(screen, C_PANEL_EDGE,
                     (x, y), (panel_rect.right - 16, y))
    y += 16
    _panel_label(screen, fonts, x, y, "SEARCH")
    y += 18

    iter_count = state['iteration'] if state else 0
    visited_n  = len(state['visited']) if state else 0
    frontier_n = len(state['frontier']) if state else 0

    _panel_kv(screen, fonts, x, y, "Iterations", f"{iter_count}")
    y += 20
    _panel_kv(screen, fonts, x, y, "Visited",    f"{visited_n}")
    y += 20
    _panel_kv(screen, fonts, x, y, "Frontier",   f"{frontier_n}")
    y += 28

    # Status
    visualize.draw.line(screen, C_PANEL_EDGE,
                     (x, y), (panel_rect.right - 16, y))
    y += 16
    _panel_label(screen, fonts, x, y, "STATUS")
    y += 18
    if paused:
        status = ("PAUSED", (255, 220, 80))
    elif searching:
        status = ("SEARCHING...", C_FRONTIER)
    elif final_path is not None:
        status = ("ROUTED ✓", C_PATH)
    else:
        status = ("NO PATH", (240, 80, 80))
    st_surf = fonts['med'].render(status[0], True, status[1])
    screen.blit(st_surf, (x, y))
    y += 28

    if final_path is not None:
        _panel_kv(screen, fonts, x, y, "Path length", f"{len(final_path)} cells")
        y += 24

    # Legend at the bottom
    ly = panel_rect.bottom - 16 - 8 * 22
    _panel_label(screen, fonts, x, ly, "LEGEND")
    ly += 22
    _legend_row(screen, fonts, x, ly, C_SOURCE,   "Source pad");   ly += 22
    _legend_row(screen, fonts, x, ly, C_TARGET,   "Target pad");   ly += 22
    _legend_row(screen, fonts, x, ly, C_PAD,      "Other pad");    ly += 22
    _legend_row(screen, fonts, x, ly, C_FRONTIER, "Frontier");     ly += 22
    _legend_row(screen, fonts, x, ly, C_VISITED,  "Visited");      ly += 22
    _legend_row(screen, fonts, x, ly, C_CURRENT,  "Expanding");    ly += 22
    _legend_row(screen, fonts, x, ly, C_PATH,     "Routed trace"); ly += 22

    # Hint
    hint = fonts['small'].render("SPACE: pause   ESC: quit", True, C_TEXT_DIM)
    screen.blit(hint, (x, panel_rect.bottom - 22))


def _panel_label(screen, fonts, x, y, text):
    surf = fonts['small'].render(text, True, C_TEXT_DIM)
    screen.blit(surf, (x, y))


def _panel_kv(screen, fonts, x, y, key, value):
    k = fonts['small'].render(key, True, C_TEXT_DIM)
    v = fonts['mono'].render(value, True, C_TEXT)
    screen.blit(k, (x, y))
    screen.blit(v, (x + 90, y))


def _legend_row(screen, fonts, x, y, color, label):
    visualize.draw.rect(screen, color, (x, y + 3, 14, 14), border_radius=2)
    surf = fonts['small'].render(label, True, C_TEXT)
    screen.blit(surf, (x + 24, y))


# ─── End-of-search animations ──────────────────────────────────────────────

def _animate_path_reveal(screen, grid, board_rect, panel_rect,
                         state, source, target, net_name, path, fonts, clock):
    """Dramatic reveal: the path draws itself from source to target."""
    total_ms = PATH_DRAW_MS * max(1, len(path) - 1)
    elapsed  = 0

    while elapsed < total_ms:
        dt = clock.tick(60)
        elapsed += dt

        for event in visualize.event.get():
            if event.type == visualize.QUIT:
                visualize.quit(); sys.exit()
            if event.type == visualize.KEYDOWN and event.key == visualize.K_ESCAPE:
                visualize.quit(); sys.exit()

        progress = min(1.0, elapsed / total_ms)

        _draw_background(screen, board_rect, panel_rect)
        _draw_grid(screen, grid, board_rect, state, source, target, path=None)

        # Partial path
        if len(path) >= 2:
            # Hack: clip the path for progress
            n_full = int((len(path) - 1) * progress)
            partial = ((len(path) - 1) * progress) - n_full
            segs = path[:n_full + 1]
            if segs:
                points = [_cell_center(c, r, grid, board_rect) for c, r in segs]
                if len(points) >= 2:
                    visualize.draw.lines(screen, C_PATH_GLOW, False, points, width=14)
                    visualize.draw.lines(screen, C_PATH,      False, points, width=7)
            if n_full < len(path) - 1 and partial > 0:
                p0 = _cell_center(*path[n_full],     grid, board_rect)
                p1 = _cell_center(*path[n_full + 1], grid, board_rect)
                px = p0[0] + (p1[0] - p0[0]) * partial
                py = p0[1] + (p1[1] - p0[1]) * partial
                visualize.draw.line(screen, C_PATH_GLOW, p0, (px, py), width=14)
                visualize.draw.line(screen, C_PATH,      p0, (px, py), width=7)

        _draw_panel(screen, panel_rect, state, source, target, net_name,
                    fonts, searching=False, final_path=path)
        visualize.display.flip()


def _show_failure(screen, grid, board_rect, panel_rect,
                  state, source, target, net_name, fonts, clock):
    """If no path was found, show the exhausted search briefly."""
    for _ in range(60):
        clock.tick(60)
        for event in visualize.event.get():
            if event.type == visualize.QUIT:
                visualize.quit(); sys.exit()
        _draw_background(screen, board_rect, panel_rect)
        _draw_grid(screen, grid, board_rect, state, source, target, path=None)
        _draw_panel(screen, panel_rect, state, source, target, net_name,
                    fonts, searching=False, final_path=None)
        visualize.display.flip()


def _hold_window(screen, clock):
    """Keep the window open until user closes or hits ESC."""
    while True:
        clock.tick(30)
        for event in visualize.event.get():
            if event.type == visualize.QUIT:
                visualize.quit()
                return
            if event.type == visualize.KEYDOWN and event.key == visualize.K_ESCAPE:
                visualize.quit()
                return
