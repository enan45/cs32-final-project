###555 Oscillator Circuit
# 1 - GND
# 2 — TRIG (trigger)
# 3 — OUT (output)
# 4 — RESET (tied to VCC for always-on)
# 5 — CTL (control voltage)
# 6 — THR (threshold)
# 7 — DISCHG (discharge)
# 8 — VCC
# VCC connects pins 8 and 4 (and external stuff)
# GND connects pin 1 (and external stuff)
# DISCHG connects pin 7, R1, R2
# THR/TRIG connects pins 2 and 6
# CTL connects pin 5 and a cap
# OUT connects pin 3 and a header


### circuits.py
"""
Each function returns a Grid object with blocked cells as the component bodies
and pad cells
"""

from grid import Grid, Cell


def build_555_timer():
    """A 555 timer astable oscillator circuit on a 20x20 grid.

    The 555 DIP-8 chip sits in the middle with Pins 1-4 are on the left,
    pins 5-8 on the right and External components (R1, C1) arround it.

    Returns:
        grid: the Grid with obstacles and pads placed
        pads: a dict mapping net names to lists of (col, row) pad locations
    """
    grid = Grid(cols=20, rows=20)

    ## 555 chip body---> 3 columns wide, 4 rows tall, centered in the grid

    chip_left,  chip_right = 7, 9
    chip_bot,   chip_top   = 9, 12
    for c in range(chip_left, chip_right + 1):
        for r in range(chip_bot, chip_top + 1):
            grid.block(c, r)

    ## Chip pads
    # Left side: pin 1 (bottom) to pin 4 (top)
    pin1 = (chip_left - 1, chip_bot)      # GND
    pin2 = (chip_left - 1, chip_bot + 1)  # TRIG
    pin3 = (chip_left - 1, chip_bot + 2)  # OUT
    pin4 = (chip_left - 1, chip_top)      # RESET (tied to VCC)

    # Right side: pin 8 (bottom) to pin 5 (top)
    pin8 = (chip_right + 1, chip_bot)      # VCC
    pin7 = (chip_right + 1, chip_bot + 1)  # DISCHG
    pin6 = (chip_right + 1, chip_bot + 2)  # THR
    pin5 = (chip_right + 1, chip_top)      # CTL

    ## External component bodies
    for c in range(6, 9):
        grid.block(c, 16)

    # R1 above the chip
    r1_bottom = (7, 15)  # R1's bottom lead
    r1_top    = (7, 17)  # R1's top lead, goes to VCC rail

    # C1 below the chip
    for c in range(6, 9):
        grid.block(c, 5)
    c1_top    = (7, 6)   # C1's top lead, connects to TRIG
    c1_bottom = (7, 4)   # C1's bottom lead, goes to GND

    # Place all pads on the grid
    all_pads = [pin1, pin2, pin3, pin4, pin5, pin6, pin7, pin8,
                r1_bottom, r1_top, c1_top, c1_bottom]

    for col, row in all_pads:
        grid.place_pad(col, row)

    # generate Net list
    # Each net lists the pads that must be electrically connected
    pads = {
        'VCC':  [pin8, pin4, r1_top],
        'GND':  [pin1, c1_bottom],
        'TRIG': [pin2, pin6, c1_top],
        'OUT':  [pin3],
        'DISCHG': [pin7, r1_bottom],
        'CTL':  [pin5],                 
    }

    return grid, pads
