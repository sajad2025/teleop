#!/usr/bin/env python3
"""
Simple teleoperation example.

This example demonstrates the basic usage of the teleoperation system
with a 6DOF robot arm and keyboard controls.
"""

import sys
import time
import threading
from typing import Dict, Any

# Add the parent directory to the path so we can import the src module
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.common.interfaces import (
    Command, Pose, Vector3, Quaternion
)
from src.simulation.simulator import Simulator
from src.robots.robot_model import Arm6DOF
from src.operator.ui import OperatorUI
from src.communication.network import NetworkSimulator


def keyboard_input_simulator(ui: OperatorUI, stop_event: threading.Event) -> None:
    """
    Simulate keyboard input for the operator UI.
    
    Args:
        ui: The operator UI instance.
        stop_event: Event to signal when to stop.
    """
    keys = ['w', 'a', 's', 'd', 'w', 'w', 's', 's', 'a', 'd']
    idx = 0
    
    while not stop_event.is_set():
        # Simulate keyboard input
        key = keys[idx % len(keys)]
        
        input_data = {
            "type": "keyboard",
            "key": key
        }
        
        # Process the input
        command = ui.process_input(input_data)
        if command:
            print(f"Generated command: {command.type}")
        
        # Move to the next key
        idx += 1
        
        # Wait for a bit
        time.sleep(0.5)


def main():
    """Run a simple teleoperation example."""
    print("Starting simple teleoperation example")
    
    # Create a robot and add it to the simulator
    robot_id = "robot1"
    robot_pose = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.5),
        orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
    )
    
    # Initialize simulator
    simulator = Simulator()
    print("Simulator initialized")
    
    simulator.add_robot(robot_id, "arm_6dof", robot_pose)
    
    # Initialize communication network
    network = NetworkSimulator()
    network.set_network_conditions(
        latency=0.1,  # 100ms latency
        packet_loss=0.05,  # 5% packet loss
        bandwidth=1000000  # 1 Mbps
    )
    print("Network simulator initialized")
    
    # Initialize operator UI
    operator = OperatorUI(robot_id, "simple")
    print("Operator UI initialized")
    
    # Create a thread to simulate keyboard input
    stop_event = threading.Event()
    input_thread = threading.Thread(
        target=keyboard_input_simulator,
        args=(operator, stop_event)
    )
    input_thread.start()
    
    try:
        # Main simulation loop
        dt = 0.02  # 20ms timestep
        last_time = time.time()
        simulation_time = 0.0
        end_time = 10.0  # Run for 10 seconds
        
        print(f"Running simulation for {end_time} seconds...")
        
        while simulation_time < end_time:
            current_time = time.time()
            elapsed = current_time - last_time
            
            if elapsed >= dt:
                # Step simulation
                simulator.step(elapsed)
                simulation_time += elapsed
                last_time = current_time
                
                # Process commands at robot
                robot_command = network.receive_command()
                if robot_command:
                    print(f"Robot received command: {robot_command.type}")
                    simulator.apply_command(robot_id, robot_command)
                
                # Get robot state
                robot_state = simulator.get_robot_state(robot_id)
                
                # Send state to operator
                network.send_state(robot_state)
                
                # Update operator display
                operator_state = network.receive_state()
                if operator_state:
                    operator.update_display(operator_state)
                
                # Print simulation progress
                if int(simulation_time) != int(simulation_time - elapsed):
                    print(f"Simulation time: {simulation_time:.1f}s")
            
            # Sleep to avoid busy waiting
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        print("Simulation interrupted")
    finally:
        # Clean up
        stop_event.set()
        input_thread.join()
        network.shutdown()
        print("Simulation ended")


if __name__ == "__main__":
    main() 