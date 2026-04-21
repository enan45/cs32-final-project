### FP/visualize.py
"""Board visualization — both ASCII and matplotlib versions."""

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def show_ascii(board):
    """Print the board as ASCII to the terminal."""
    board.print_ascii()


def show_matplotlib(board, nets, save_to=None):
    """Draw the board with matplotlib.

    Components are gray rectangles, pads are colored circles,
    traces are colored lines.
    """
    if not HAS_MPL:
        print("matplotlib not installed — falling back to ASCII")
        show_ascii(board)
        return

    fig, ax = plt.subplots(figsize=(10, 8))

    # A small palette of distinct colors for each net
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink']

    # Draw blocked cells as gray squares
    for r in range(board.rows):
        for c in range(board.cols):
            cell = board.get_cell(c, r)
            if cell.state == 'BLOCKED':
                rect = patches.Rectangle((c, r), 1, 1,
                                         facecolor='gray', edgecolor='black')
                ax.add_patch(rect)

    # Draw traces as colored lines
    for net in nets:
        if net.routed:
            color = colors[net.net_id % len(colors)]
            xs = [p[0] + 0.5 for p in net.path]
            ys = [p[1] + 0.5 for p in net.path]
            ax.plot(xs, ys, color=color, linewidth=3,
                    label=f"Net {net.net_id}")

    # Draw pads as colored circles on top
    for net in nets:
        color = colors[net.net_id % len(colors)]
        for pad in (net.start, net.goal):
            ax.plot(pad[0] + 0.5, pad[1] + 0.5, 'o',
                    color=color, markersize=12,
                    markeredgecolor='black')

    ax.set_xlim(0, board.cols)
    ax.set_ylim(0, board.rows)
    ax.set_aspect('equal')
    ax.set_xticks(range(board.cols + 1))
    ax.set_yticks(range(board.rows + 1))
    ax.grid(True, alpha=0.3)
    ax.set_title("PCB Router — A* Results")
    ax.legend()

    if save_to:
        plt.savefig(save_to)
        print(f"Saved visualization to {save_to}")
    plt.show()
