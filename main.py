### FP/main.py
"""Demo the PCB router on a small test board."""

from board     import Board
from nets      import Net
from dump_Astar     import route_all
from dump_visualize import show_ascii, show_matplotlib


def build_test_board():
    """Build a simple test board with two components and two nets."""
    board = Board(cols=20, rows=12)

    # Place two component bodies as obstacles
    # Component A: cols 5-7, rows 4-7
    for c in range(5, 8):
        for r in range(4, 8):
            board.block_cell(c, r)

    # Component B: cols 13-15, rows 4-7
    for c in range(13, 16):
        for r in range(4, 8):
            board.block_cell(c, r)

    # Place pads for Net 0 (top connection)
    board.place_pad(4, 7, net_id=0)
    board.place_pad(16, 7, net_id=0)

    # Place pads for Net 1 (bottom connection)
    board.place_pad(4, 4, net_id=1)
    board.place_pad(16, 4, net_id=1)

    # Build the net list
    nets = [
        Net(net_id=0, start=(4, 7), goal=(16, 7)),
        Net(net_id=1, start=(4, 4), goal=(16, 4)),
    ]

    return board, nets


def main():
    print("=" * 50)
    print("  PCB Trace Auto-Router Demo")
    print("=" * 50)

    board, nets = build_test_board()

    print("\nInitial board:")
    show_ascii(board)

    print("\nRouting nets...")
    routed, failed = route_all(board, nets)

    print(f"\nResult: {routed} routed, {failed} failed")

    print("\nFinal board:")
    show_ascii(board)

    # Try matplotlib if available
    show_matplotlib(board, nets, save_to="result.png")


if __name__ == "__main__":
    main()
