# cs32-final-project
# PCB Trace Auto-Router

A grid-based printed circuit board (PCB) trace auto-router built in Python.
Given a board with components and a list of electrical nets that must be
connected, the router finds an optimal path for each trace using Lee's
classical maze-routing algorithm.

The current version
implements single-net routing on a hardcoded representation of a 555 timer
oscillator circuit, with full ASCII visualization of the result.

## Background

PCB routing is the problem of physically connecting electrical nets
(groups of pins that must be electrically connected) on a printed circuit
board, given that traces cannot cross each other or pass through
component bodies.

The router operates on a 2D grid where each cell can be:
- `FREE` — empty space, traces may pass through
- `BLOCKED` — a component body, no traces allowed
- `PAD` — a connection point belonging to a specific net
- `TRACE` — a routed copper path

The core algorithm is **Lee's algorithm** (Lee, 1961), which performs
breadth-first search outward from the source pad. Every cell visited
exactly once. Guaranteed shortest path if one exists. Lee's algorithm is
mathematically equivalent to A* search with heuristic h=0, and serves as
the correctness baseline for more advanced routers.

## What works in this milestone

- Grid and Cell classes with proper state and neighbor logic
- Hardcoded 555 timer astable oscillator circuit with chip body,
  external resistor R1, capacitor C1, and 6 named electrical nets:
  VCC, GND, TRIG, OUT, DISCHG, CTL
- Lee's algorithm finds shortest paths between pads on the same net
- Other nets' pads are correctly treated as obstacles, preventing
  traces from electrically shorting unrelated signals
- ASCII visualization of the board before and after routing

## to do
- Multi-net routing: routing all 6 nets sequentially with each
  successful trace becoming an obstacle for later nets
- A* with Manhattan-distance heuristic for faster search
- Live Pygame visualization showing the wavefront expand in real time
- Larger and denser test circuits. I am thinking of(ATmega328P breakout, motor driver)
- Rip-up and reroute when a net c
- Two-layer routing with vias (maybe) :)
