### grid.py

class Cell:
    """One cell on the PCB grid."""

    FREE    = 'FREE'
    BLOCKED = 'BLOCKED'
    PAD     = 'PAD'
    TRACE   = 'TRACE'

    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.state = Cell.FREE

    def is_passable(self):
        """for now free cells and pads can be entered."""
        return self.state in (Cell.FREE, Cell.PAD)

class Grid:
    """2D grid of Cell objects routing."""

    # Manhattan routing: right, left, down, up
    DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    def __init__(self, cols, rows): # three attributes
        self.cols = cols
        self.rows = rows
        self.cells = []

        # 2D list indexed as grid[row][col]
        for r in range(rows):
            row = []
            for c in range(cols):
                row.append(Cell(c, r))
            self.cells.append(row)

    def in_bounds(self, col, row):
        """Check if individual cell (col, row) is within the grid boundaries."""
        # Check if column is between 0 and the last column
        if col < 0 or col >= self.cols:
            return False
         # Check if row is between 0 and the last row
        if row < 0 or row >= self.rows:
            return False
        # If both checks passed, the position is inside the grid
        return True

    def get(self, col, row): # think of this as x then y cordinates
        """Return the Cell at (col, row)."""
        return self.cells[row][col]

    def block(self, col, row):
        """Mark a cell as blocked (component body)."""
        if self.in_bounds(col, row): #check if the position is within the grid boundaries before blocking
            cell = self.get(col, row)
            cell.state = Cell.BLOCKED

    def place_pad(self, col, row):
        """Mark a cell as a pad (connection point)."""
        if self.in_bounds(col, row): #check if the position is within the grid boundaries before placing a pad
            cell = self.get(col, row)
            cell.state = Cell.PAD

    def mark_trace(self, path):
        """After routing, mark the path cells as trace.
        Pads stay as pads without being overwritten.
        """
        for col, row in path:
            cell = self.get(col, row)
            if cell.state == Cell.FREE:
                cell.state = Cell.TRACE

    def neighbors(self, col, row):
        """Return list of passable neighboring (col, row) tuples."""
        result = []
        for dc, dr in Grid.DIRECTIONS:
            nc, nr = col + dc, row + dr
            if self.in_bounds(nc, nr) and self.get(nc, nr).is_passable():
                result.append((nc, nr))
        return result

    def print_ascii(self):
        """ASCII print for debugging. Top row prints first."""
        # Row 0 is at the bottom in our coordinate system,
        # so we iterate from the top down
        for r in range(self.rows - 1, -1, -1):
            line = ''
            for c in range(self.cols):
                cell = self.get(c, r)
                if cell.state == Cell.FREE:
                    line += '.'
                elif cell.state == Cell.BLOCKED:
                    line += '#'
                elif cell.state == Cell.PAD:
                    line += 'P'
                elif cell.state == Cell.TRACE:
                    line += '*'
            print(line)
