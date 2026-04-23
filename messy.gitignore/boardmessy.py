### FP/board.py

"""Board and Cell classes for PCB router."""

class Cell:
    """One cell in the PCB grid.
    Each cell has a state (what's in it) and a net_id (which net owns it).
    
    States:
      FREE      - empty, anything can pass through
      BLOCKED   - a component body, nothing can pass through
      PAD       - a connection point, only the owning net can use it
      TRACE     - a routed copper path, only the owning net can use it
    """

    FREE    = 'FREE'
    BLOCKED = 'BLOCKED'
    PAD     = 'PAD'
    TRACE   = 'TRACE'

    def __init__(self, col, row):
        self.col    = col
        self.row    = row
        self.state  = Cell.FREE
        self.net_id = None

    def is_passable(self, net_id):
        """Can a trace for this net pass through this cell?"""
        if self.state == Cell.FREE:
            return True
        # Pad or trace can be entered only if it belongs to same net
        if self.state in (Cell.PAD, Cell.TRACE) and self.net_id == net_id:
            return True
        return False


class Board:
    """The PCB board — a 2D grid of Cell objects.

    Indexed as grid[row][col]. Uses standard coordinate system where
    (0,0) is bottom-left.
    """

    # All four neighbor directions — no diagonals
    DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        # Build a 2D list of Cell objects
        self.grid = [[Cell(c, r) for c in range(cols)] for r in range(rows)]

    def in_bounds(self, col, row):
        """Is this location inside the board?"""
        return 0 <= col < self.cols and 0 <= row < self.rows

    def get_cell(self, col, row):
        return self.grid[row][col]

    def block_cell(self, col, row):
        """Mark a cell as BLOCKED (used for component bodies)."""
        cell = self.get_cell(col, row)
        cell.state = Cell.BLOCKED

    def place_pad(self, col, row, net_id):
        """Mark a cell as a PAD belonging to a specific net."""
        cell = self.get_cell(col, row)
        cell.state  = Cell.PAD
        cell.net_id = net_id

    def mark_trace(self, path, net_id):
        """Mark all FREE cells in a path as TRACE cells for this net.

        Note: doesn't overwrite pads — the endpoints stay as PADs.
        """
        for col, row in path:
            cell = self.get_cell(col, row)
            if cell.state == Cell.FREE:
                cell.state  = Cell.TRACE
                cell.net_id = net_id

    def neighbors(self, col, row, net_id):
        """Find all passable neighboring cells for this net."""
        result = []
        for dc, dr in Board.DIRECTIONS:
            nc, nr = col + dc, row + dr
            if self.in_bounds(nc, nr):
                if self.get_cell(nc, nr).is_passable(net_id):
                    result.append((nc, nr))
        return result

    def print_ascii(self):
        """Print the board as ASCII — good for debugging."""
        # Print top row first (flip the y-axis for printing)
        for r in range(self.rows - 1, -1, -1):
            line = ''
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell.state == Cell.FREE:
                    line += '.'
                elif cell.state == Cell.BLOCKED:
                    line += '#'
                elif cell.state == Cell.PAD:
                    line += str(cell.net_id)
                elif cell.state == Cell.TRACE:
                    line += '*'
            print(line)
