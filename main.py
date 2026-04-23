### FP/main.py
"""Demo the PCB auto-router on realistic test circuits."""

from board     import Board
from nets      import Net
from dump_Astar     import route_all
from dump_visualize import show_ascii, show_matplotlib


# Net name constants — makes the code more readable than raw ints
VCC  = 0
GND  = 1
TRIG = 2
OUT  = 3


def build_simple_board():
    """A basic two-component, two-net board for initial testing.

    Used for verifying the router works at all before running the
    more complex 555 circuit.
    """
    board = Board(cols=20, rows=12)

    # Component A: left block
    for c in range(5, 8):
        for r in range(4, 8):
            board.block_cell(c, r)

    # Component B: right block
    for c in range(13, 16):
        for r in range(4, 8):
            board.block_cell(c, r)

    # Net 0 runs along the top between the two components
    board.place_pad(4, 7, net_id=0)
    board.place_pad(16, 7, net_id=0)

    # Net 1 runs along the bottom
    board.place_pad(4, 4, net_id=1)
    board.place_pad(16, 4, net_id=1)

    nets = [
        Net(net_id=0, start=(4, 7),  goal=(16, 7)),
        Net(net_id=1, start=(4, 4),  goal=(16, 4)),
    ]

    return board, nets


def build_555_timer_board():
    """A board representing a 555 timer astable oscillator circuit.

    This is a recognizable real-world circuit. The 555 is one of the
    most common ICs in electronics, used for timers and oscillators.

    Pinout (standard DIP-8):
        Pin 1 (GND)     <-- power ground
        Pin 2 (TRIG)    --> connects to pin 6 (feedback loop)
        Pin 3 (OUT)     --> drives the LED
        Pin 4 (RESET)   <-- tied to VCC (always on)
        Pin 6 (THRES)   --> connects to pin 2
        Pin 8 (VCC)     <-- power rail

    Four nets must be routed simultaneously without crossing.
    """
    board = Board(cols=30, rows=20)

    # 555 chip body - DIP-8 footprint in the middle of the board
    chip_left,  chip_right = 10, 18
    chip_bot,   chip_top   = 7,  13
    for c in range(chip_left, chip_right + 1):
        for r in range(chip_bot, chip_top + 1):
            board.block_cell(c, r)

    # External LED body (bottom right)
    for c in range(24, 27):
        for r in range(2, 5):
            board.block_cell(c, r)

    # Pads on the LEFT side of the chip (pins 1-4, bottom to top)
    pin1 = (chip_left - 1, chip_bot + 1)   # GND
    pin2 = (chip_left - 1, chip_bot + 3)   # TRIG
    pin3 = (chip_left - 1, chip_bot + 5)   # OUT
    pin4 = (chip_left - 1, chip_top)       # RESET (tied to VCC)

    # Pads on the RIGHT side of the chip (pins 5-8, top to bottom)
    pin6 = (chip_right + 1, chip_top)       # THRESHOLD
    pin8 = (chip_right + 1, chip_bot + 1)   # VCC

    # External pads
    gnd_external = (5, 3)               # ground rail
    led_anode    = (23, 3)              # LED input, driven by OUT

    # Mark every pad on the board with its owning net
    board.place_pad(pin1[0],        pin1[1],        GND)
    board.place_pad(pin2[0],        pin2[1],        TRIG)
    board.place_pad(pin3[0],        pin3[1],        OUT)
    board.place_pad(pin4[0],        pin4[1],        VCC)
    board.place_pad(pin6[0],        pin6[1],        TRIG)
    board.place_pad(pin8[0],        pin8[1],        VCC)
    board.place_pad(gnd_external[0], gnd_external[1], GND)
    board.place_pad(led_anode[0],    led_anode[1],    OUT)

    # The nets to route
    # NOTE: Ordering matters for sequential routing — VCC and GND first
    # because they're the "power rails" and should get the shortest paths
    nets = [
        Net(VCC,  start=pin8, goal=pin4),          # Pin 8 to Pin 4
        Net(GND,  start=pin1, goal=gnd_external),  # Pin 1 to external ground
        Net(TRIG, start=pin2, goal=pin6),          # Pin 2 to Pin 6 (loop)
        Net(OUT,  start=pin3, goal=led_anode),     # Pin 3 to LED
    ]

    return board, nets


def run_demo(name, build_fn):
    """Runs one demo: prints header, builds board, routes, shows result."""
    print("\n" + "=" * 60)
    print(f"  {name}")
    print("=" * 60)

    board, nets = build_fn()

    print(f"\nBoard: {board.cols} x {board.rows} cells")
    print(f"Nets to route: {len(nets)}")

    print("\nInitial board layout:")
    show_ascii(board)

    print("\nRouting...")
    routed, failed = route_all(board, nets)

    print(f"\nResult: {routed}/{len(nets)} nets routed successfully")
    if failed > 0:
        print(f"WARNING: {failed} net(s) could not be routed")

    print("\nFinal board layout:")
    show_ascii(board)

    # Save a matplotlib image of the result
    filename = name.lower().replace(" ", "_") + ".png"
    show_matplotlib(board, nets, save_to=filename)


def main():
    print("PCB Trace Auto-Router")
    print("Grid-based A* search with clearance-aware cost function")

    # Demo 1: Simple two-net board — sanity check
    run_demo("Simple two-net demo", build_simple_board)

    # Demo 2: 555 timer circuit — realistic example
    run_demo("555 timer astable circuit", build_555_timer_board)

    print("\nDone. Images saved as PNG files in current directory.")


if __name__ == "__main__":
    main()
