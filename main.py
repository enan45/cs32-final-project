### main.py
"""
Lets the user choose a circuit and a routing mode. 
"""

from circuits import (build_555_timer, build_inverting_opamp, build_l293d_motor_driver)
from visualize import visualize_route
from multi_visualize import visualize_multinet

def main():

    print("PCB Auto-Router")
    print()
    print("Choose a circuit:")
    print("1 - 555 Timer")
    print("2 - Inverting Op-Amp")
    print("3 - L293D Motor Driver")

    circuit_choice = input("Which circuit would you like to route?: ").strip()

    if circuit_choice == "1":

        circuit_name = "555 Timer"
        builder = build_555_timer
        order = ["TRIG", "DISCHG", "GND", "VCC"] #order matters

    elif circuit_choice == "2":

        circuit_name = "Inverting Op-Amp"
        builder = build_inverting_opamp
        order = None

    elif circuit_choice == "3":

        circuit_name = "L293D Motor Driver"
        builder = build_l293d_motor_driver
        order = [ "IN1", "IN2", "IN3", "IN4", "EN1", "EN2",
                 "MOTOR1_A", "MOTOR1_B", "MOTOR2_A", "MOTOR2_B",
                 "GND", "VCC1", "VCC2" ]

    else:

        print("Invalid circuit choice.")
        return
    

 # Algorithm choice
 
    print()
    print("Choose an algorithm:")
    print("1 - Lee (BFS, h=0)")
    print("2 - A* (Manhattan heuristic)")

    algo_choice = input("Which algorithm? ").strip()

    if algo_choice == "1":
        algorithm = "lee"
    elif algo_choice == "2":
        algorithm = "astar"
    else:
        print("Invalid algorithm choice.")
        return
    print()
    print("Please Choose a mode:")
    print("1 - Simple")
    print("2 -hardcore")

##Mode choice

    mode_choice = input("would you like simple or hardcore: ").strip()

    if mode_choice == "1":

        grid, netlist = builder()
        print()
        print("Available nets:")

        for net_name in netlist:
            print("-", net_name)

        chosen_net = input("Which net do you want to route? ").strip()

        if chosen_net not in netlist:
            print("Invalid net name.")
            return

        pads = netlist[chosen_net]

        if len(pads) < 2:
            print("That net does not have enough pads to route.")
            return

        source = pads[0]
        target = pads[1]

        visualize_route(
            grid,
            source,
            target,
            net_name=chosen_net,
            title="PCB Auto-Router - " + circuit_name,
            algorithm=algorithm #This was the bug in my video, This parameter that is passed to visualize route got deleted
        )

    elif mode_choice == "2":
        grid, netlist = builder()
        visualize_multinet(
            grid,
            netlist,
            order=order,
            title="PCB Auto-Router - " + circuit_name,
            algorithm=algorithm
        )


    else:
        print("Invalid mode choice.")
        return

if __name__ == "__main__":
    main()