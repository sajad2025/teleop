#!/usr/bin/env python3
"""
Main application entry point for the teleoperation simulation.

This script initializes all components and runs the simulation.
"""

import argparse
import logging
import sys
import os
import time
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.common.interfaces import (
    Command, Pose, Vector3, Quaternion
)
from src.common.utils import get_logger

from src.simulation.simulator import Simulator
from src.robots.robot_model import Arm6DOF
from src.operator.ui import OperatorUI
from src.communication.network import NetworkSimulator


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Teleoperation Simulation")
    
    parser.add_argument(
        "--robot-type",
        type=str,
        default="arm_6dof",
        choices=["arm_6dof", "mobile_platform"],
        help="Type of robot to simulate"
    )
    
    parser.add_argument(
        "--ui-mode",
        type=str,
        default="simple",
        choices=["simple", "advanced", "vr"],
        help="UI mode for operator interface"
    )
    
    parser.add_argument(
        "--latency",
        type=float,
        default=0.1,
        help="Network latency in seconds"
    )
    
    parser.add_argument(
        "--packet-loss",
        type=float,
        default=0.0,
        help="Network packet loss probability (0.0-1.0)"
    )
    
    parser.add_argument(
        "--bandwidth",
        type=float,
        default=float('inf'),
        help="Network bandwidth in bytes per second"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    
    return parser.parse_args()


def main():
    """Run the teleoperation simulation."""
    # Parse command-line arguments
    args = parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = get_logger(__name__)
    
    logger.info("Starting teleoperation simulation")
    
    # Initialize components
    robot_id = "robot1"
    
    # Initialize simulator
    simulator = Simulator()
    logger.info("Simulator initialized")
    
    # Add robot to simulation
    robot_pose = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.5),
        orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
    )
    simulator.add_robot(robot_id, args.robot_type, robot_pose)
    
    # Initialize communication
    network = NetworkSimulator()
    network.set_network_conditions(
        args.latency,
        args.packet_loss,
        args.bandwidth
    )
    logger.info("Network simulator initialized")
    
    # Initialize operator UI
    operator = OperatorUI(robot_id, args.ui_mode)
    logger.info("Operator UI initialized")
    
    # Example input data
    example_input = {
        "type": "keyboard",
        "key": "w"
    }
    
    try:
        # Main simulation loop
        dt = 0.01  # 10ms timestep
        last_time = time.time()
        
        while True:
            current_time = time.time()
            elapsed = current_time - last_time
            
            if elapsed >= dt:
                # Step simulation
                simulator.step(elapsed)
                last_time = current_time
                
                # Process operator input
                command = operator.process_input(example_input)
                if command:
                    network.send_command(command)
                
                # Process commands at robot
                robot_command = network.receive_command()
                if robot_command:
                    simulator.apply_command(robot_id, robot_command)
                
                # Get robot state
                robot_state = simulator.get_robot_state(robot_id)
                
                # Send state to operator
                network.send_state(robot_state)
                
                # Update operator display
                operator_state = network.receive_state()
                if operator_state:
                    operator.update_display(operator_state)
            
            # Sleep to avoid busy waiting
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        logger.info("Simulation interrupted")
    finally:
        # Clean up
        network.shutdown()
        logger.info("Simulation ended")


if __name__ == "__main__":
    main() 