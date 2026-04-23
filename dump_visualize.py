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
    if not HAS_MPL:
        show_ascii(board)
        return

    fig, ax = plt.subplots(figsize=(12, 8))

    # Dark green PCB substrate background
    ax.set_facecolor('#0a3d2e')
    fig.patch.set_facecolor('#0a3d2e')

    # Copper-like colors for different nets
    net_colors = ['#d4a017', '#ff6b35', '#4ecdc4',
                  '#c77dff', '#06d6a0', '#ef476f']

    # Draw component bodies as dark silkscreen outlines
    for r in range(board.rows):
        for c in range(board.cols):
            cell = board.get_cell(c, r)
            if cell.state == 'BLOCKED':
                rect = patches.Rectangle(
                    (c, r), 1, 1,
                    facecolor='#1a1a1a',
                    edgecolor='white',
                    linewidth=0.5
                )
                ax.add_patch(rect)

    # Draw traces as thick copper-colored lines
    for net in nets:
        if net.routed:
            color = net_colors[net.net_id % len(net_colors)]
            xs = [p[0] + 0.5 for p in net.path]
            ys = [p[1] + 0.5 for p in net.path]
            # Outer glow (wider, darker)
            ax.plot(xs, ys, color=color, linewidth=8,
                    alpha=0.3, solid_capstyle='round')
            # Main trace
            ax.plot(xs, ys, color=color, linewidth=4,
                    solid_capstyle='round',
                    label=f"Net {net.net_id}")

    # Draw pads as donuts (outer ring + inner hole)
    for net in nets:
        color = net_colors[net.net_id % len(net_colors)]
        for pad in (net.start, net.goal):
            # Outer copper ring
            ax.plot(pad[0] + 0.5, pad[1] + 0.5, 'o',
                    color=color, markersize=16,
                    markeredgecolor='white', markeredgewidth=1)
            # Inner drill hole
            ax.plot(pad[0] + 0.5, pad[1] + 0.5, 'o',
                    color='#0a3d2e', markersize=6)

    # Subtle grid dots instead of lines
    for c in range(board.cols + 1):
        for r in range(board.rows + 1):
            ax.plot(c, r, '.', color='white', alpha=0.1, markersize=2)

    ax.set_xlim(-0.5, board.cols + 0.5)
    ax.set_ylim(-0.5, board.rows + 0.5)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("PCB Auto-Router — A* Grid Search",
                 color='white', fontsize=14, pad=15)

    legend = ax.legend(loc='upper right', framealpha=0.8,
                       facecolor='#1a1a1a', edgecolor='white',
                       labelcolor='white')

    if save_to:
        plt.savefig(save_to, facecolor='#0a3d2e', dpi=150)
    plt.show()
