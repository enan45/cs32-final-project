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

from grid import Grid, Cell


def build_555_timer():
    """
    A 555 timer astable oscillator circuit on a 20x20 grid.

    The 555 DIP-8 chip sits in the middle with Pins 1-4 are on the left,
    pins 5-8 on the right and External components (R1, C1) arround it.

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


        
    #  Pin 1 (V+ output)
    #  Pin 2 (-) input — virtual ground node
    #  Pin 3 (+) input — tied to ground/VREF
    #  Pin 4 V-
    #  Pin 8 V+
    
    # Nets (6):
    #  VCC      — pin 8, VCC header pad
    #  VEE      — pin 4, VEE header pad  
    #  GND      — pin 3, ground header
    #  VIN      — Rin input lead, VIN header
    #  VIRTUAL  — pin 2, Rin output, Rfb left lead
    #  VOUT     — pin 1, Rfb right lead, VOUT header

def build_inverting_opamp():
    """
    Inverting op-amp circuit: TL072 with input resistor and feedback resistor.

    """
    grid = Grid(cols=20, rows=15)
    
    # TL072 chip body — same DIP-8 layout as the 555
    chip_left,  chip_right = 8, 10
    chip_bot,   chip_top   = 5, 8
    for c in range(chip_left, chip_right + 1):
        for r in range(chip_bot, chip_top + 1):
            grid.block(c, r)
    
    # Chip pins (same DIP-8 pinout as 555)
    pin1 = (chip_left - 1, chip_bot)      # VOUT
    pin2 = (chip_left - 1, chip_bot + 1)  # (-) input — virtual ground
    pin3 = (chip_left - 1, chip_bot + 2)  # (+) input
    pin4 = (chip_left - 1, chip_top)      # V-
    pin8 = (chip_right + 1, chip_bot)     # V+
    
    # Rin — input resistor, vertical, to the left of the chip
    grid.block(4, 7)
    rin_top    = (4, 8)
    rin_bottom = (4, 6)
    
    # Rfb — feedback resistor, horizontal, above the chip
    grid.block(9, 11)
    rfb_left  = (8, 11)
    rfb_right = (10, 11)
    
    # I/O header pads on the right edge
    vin_header  = (15, 8)
    vout_header = (15, 6)
    vcc_header  = (15, 12)
    vee_header  = (15, 4)
    gnd_header  = (15, 2)
    
    # Place all pads
    all_pads = [pin1, pin2, pin3, pin4, pin8,
                rin_top, rin_bottom, rfb_left, rfb_right,
                vin_header, vout_header, vcc_header, vee_header, gnd_header]
    for col, row in all_pads:
        grid.place_pad(col, row)
    
    netlist = {
        'VCC':     [pin8, vcc_header],
        'VEE':     [pin4, vee_header],
        'GND':     [pin3, gnd_header],
        'VIN':     [vin_header, rin_top],
        'VIRTUAL': [pin2, rin_bottom, rfb_left],
        'VOUT':    [pin1, rfb_right, vout_header],
    }
    
    return grid, netlist

def build_l293d_motor_driver():
    """L293D dual H-bridge motor driver, generously spaced.
    
    DIP-16 with 8 pins per side. This version places components with
    enough breathing room that nets have multiple legal escape routes
    around the chip.
    """
    grid = Grid(cols=40, rows=26)
    
    # L293D chip body in the middle: 6 cols wide, 12 rows tall
    chip_left,  chip_right = 17, 22
    chip_bot,   chip_top   = 7,  18
    for c in range(chip_left, chip_right + 1):
        for r in range(chip_bot, chip_top + 1):
            grid.block(c, r)
    
    # Left side pins (1-8, top to bottom)
    pin1  = (chip_left - 1, chip_top)         # EN1,2
    pin2  = (chip_left - 1, chip_top - 1)     # 1A
    pin3  = (chip_left - 1, chip_top - 3)     # 1Y motor output
    pin4  = (chip_left - 1, chip_top - 5)     # GND heatsink
    pin5  = (chip_left - 1, chip_top - 7)     # GND heatsink
    pin6  = (chip_left - 1, chip_top - 9)     # 2Y motor output
    pin7  = (chip_left - 1, chip_top - 10)    # 2A
    pin8  = (chip_left - 1, chip_bot)         # VCC2 motor power
    
    # Right side pins (9-16, bottom to top)
    pin9  = (chip_right + 1, chip_bot)        # EN3,4
    pin10 = (chip_right + 1, chip_bot + 1)    # 3A
    pin11 = (chip_right + 1, chip_bot + 3)    # 3Y motor output
    pin12 = (chip_right + 1, chip_bot + 5)    # GND heatsink
    pin13 = (chip_right + 1, chip_bot + 7)    # GND heatsink
    pin14 = (chip_right + 1, chip_bot + 9)    # 4Y motor output
    pin15 = (chip_right + 1, chip_bot + 10)   # 4A
    pin16 = (chip_right + 1, chip_top)        # VCC1 logic power
    
    # Decoupling caps, well above and below the chip
    grid.block(10, 23)
    c1_top    = (10, 24)
    c1_bottom = (10, 22)
    
    grid.block(10, 3)
    c2_top    = (10, 4)
    c2_bottom = (10, 2)
    
    # Power and signal headers on the far right edge
    vcc1_pad = (37, 24)
    vcc2_pad = (37, 2)
    gnd_pad  = (37, 13)
    
    # Motor output headers (also right side, well above/below the chip)
    motor1_a_pad = (37, 19)
    motor1_b_pad = (37, 16)
    motor2_a_pad = (37, 10)
    motor2_b_pad = (37, 7)
    
    # Signal input headers on the far left
    en1_pad = (2, 24)
    en2_pad = (2, 2)
    in1_pad = (2, 22)
    in2_pad = (2, 18)
    in3_pad = (2, 8)
    in4_pad = (2, 5)
    
    all_pads = [
        pin1, pin2, pin3, pin4, pin5, pin6, pin7, pin8,
        pin9, pin10, pin11, pin12, pin13, pin14, pin15, pin16,
        c1_top, c1_bottom, c2_top, c2_bottom,
        vcc1_pad, vcc2_pad, gnd_pad,
        motor1_a_pad, motor1_b_pad, motor2_a_pad, motor2_b_pad,
        en1_pad, en2_pad, in1_pad, in2_pad, in3_pad, in4_pad,
    ]
    for col, row in all_pads:
        grid.place_pad(col, row)
    
    netlist = {
        'VCC1':     [pin16, c1_top, vcc1_pad],
        'VCC2':     [pin8,  c2_top, vcc2_pad],
        'GND':      [pin4, pin5, pin12, pin13, c1_bottom, c2_bottom, gnd_pad],
        'EN1':      [pin1, en1_pad],
        'EN2':      [pin9, en2_pad],
        'IN1':      [pin2, in1_pad],
        'IN2':      [pin7, in2_pad],
        'IN3':      [pin10, in3_pad],
        'IN4':      [pin15, in4_pad],
        'MOTOR1_A': [pin3, motor1_a_pad],
        'MOTOR1_B': [pin6, motor1_b_pad],
        'MOTOR2_A': [pin11, motor2_a_pad],
        'MOTOR2_B': [pin14, motor2_b_pad],
    }
    
    return grid, netlist