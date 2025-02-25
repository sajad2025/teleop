#!/usr/bin/env python3
"""
Simulation Engine Demo

This script demonstrates the enhanced simulation engine with various
scenes and robot interactions, without requiring the other components.
"""

import os
import sys
import time
import argparse
from typing import List, Dict, Any

# Add the parent directory to the path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np

from src.common.interfaces import Pose, Vector3, Quaternion, Command
from src.simulation.simulator import Simulator
from src.simulation.environment import Environment
from src.simulation.visualization import SimulationVisualizer


def demo_simple_physics(simulator: Simulator, visualizer: SimulationVisualizer) -> None:
    """
    Demonstrate simple physics interactions.
    
    Args:
        simulator: The simulator instance.
        visualizer: The visualizer instance.
    """
    print("\n=== Simple Physics Demo ===")
    
    # Reset the simulator
    simulator.reset()
    
    # Create an environment
    environment = Environment(simulator)
    
    # Create a stacking scene
    environment.create_stacking_scene(num_cubes=5)
    
    # Let physics run for a while
    print("Running physics simulation...")
    for i in range(100):
        simulator.step(0.01)
        if i % 20 == 0:
            print(f"Step {i}")
    
    # Capture and save a snapshot
    visualizer.capture_image("physics_demo.png")
    print("Snapshot saved to output/physics_demo.png")


def demo_robot_control(simulator: Simulator, visualizer: SimulationVisualizer) -> None:
    """
    Demonstrate robot control.
    
    Args:
        simulator: The simulator instance.
        visualizer: The visualizer instance.
    """
    print("\n=== Robot Control Demo ===")
    
    # Reset the simulator
    simulator.reset()
    
    # Create an environment
    environment = Environment(simulator)
    
    # Create a tabletop scene
    environment.create_tabletop_scene()
    
    # Add a robot
    robot_id = "demo_robot"
    robot_pose = Pose(
        position=Vector3(x=0.0, y=0.5, z=0.6),
        orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
    )
    simulator.add_robot(robot_id, "arm_6dof", robot_pose)
    
    # Display robot info
    visualizer.display_robot_info(robot_id)
    
    # Move the robot - first joint positions command
    print("\nMoving robot with joint position command...")
    joint_positions = [0.3, 0.4, 0.2, -0.5, 0.5, 0.0]
    command = Command(
        type="joint_position",
        data={"positions": joint_positions},
        timestamp=time.time()
    )
    simulator.apply_command(robot_id, command)
    
    # Let the robot move
    for i in range(50):
        simulator.step(0.01)
    
    # Capture and save a snapshot
    visualizer.capture_image("robot_joint_position.png")
    print("Snapshot saved to output/robot_joint_position.png")
    
    # Move the robot - velocity command
    print("\nMoving robot with velocity command...")
    command = Command(
        type="velocity",
        data={"linear": 0.5, "angular": 0.2},
        timestamp=time.time()
    )
    simulator.apply_command(robot_id, command)
    
    # Let the robot move
    for i in range(50):
        simulator.step(0.01)
    
    # Capture and save a snapshot
    visualizer.capture_image("robot_velocity.png")
    print("Snapshot saved to output/robot_velocity.png")


def demo_robot_trajectory(simulator: Simulator, visualizer: SimulationVisualizer) -> None:
    """
    Demonstrate robot trajectory tracking.
    
    Args:
        simulator: The simulator instance.
        visualizer: The visualizer instance.
    """
    print("\n=== Robot Trajectory Demo ===")
    
    # Reset the simulator
    simulator.reset()
    
    # Create an environment with obstacles
    environment = Environment(simulator)
    environment.create_obstacle_course(num_obstacles=7)
    
    # Add a mobile robot
    robot_id = "mobile_robot"
    robot_pose = Pose(
        position=Vector3(x=-1.0, y=-1.0, z=0.1),
        orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
    )
    simulator.add_robot(robot_id, "mobile_platform", robot_pose)
    
    # Create a sequence of commands to navigate
    commands = [
        {"linear": 0.3, "angular": 0.0},   # Forward
        {"linear": 0.1, "angular": 0.5},   # Slight right turn
        {"linear": 0.3, "angular": 0.0},   # Forward
        {"linear": 0.1, "angular": -0.5},  # Slight left turn
        {"linear": 0.4, "angular": 0.0},   # Forward
    ]
    
    # Execute the commands
    print("Executing navigation commands...")
    for i, cmd_data in enumerate(commands):
        command = Command(
            type="velocity",
            data=cmd_data,
            timestamp=time.time()
        )
        simulator.apply_command(robot_id, command)
        
        # Run each command for a short time
        for _ in range(25):
            simulator.step(0.01)
        
        print(f"Completed command {i+1}/{len(commands)}")
    
    # Plot the trajectory
    visualizer.plot_robot_trajectory(robot_id, duration=0.1, dt=0.01, filename="robot_trajectory.png")
    print("Trajectory plot saved to output/robot_trajectory.png")


def demo_multi_robot(simulator: Simulator, visualizer: SimulationVisualizer) -> None:
    """
    Demonstrate multiple robots interacting.
    
    Args:
        simulator: The simulator instance.
        visualizer: The visualizer instance.
    """
    print("\n=== Multiple Robot Demo ===")
    
    # Reset the simulator
    simulator.reset()
    
    # Create an environment
    environment = Environment(simulator)
    environment.create_sorting_scene()
    
    # Add robots
    robot_ids = []
    robot_types = ["arm_6dof", "simple_gripper"]
    positions = [
        Vector3(x=-0.5, y=0.0, z=0.6),
        Vector3(x=0.5, y=0.0, z=0.6)
    ]
    
    for i, (robot_type, position) in enumerate(zip(robot_types, positions)):
        robot_id = f"robot_{i}"
        robot_pose = Pose(
            position=position,
            orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
        )
        simulator.add_robot(robot_id, robot_type, robot_pose)
        robot_ids.append(robot_id)
        print(f"Added {robot_type} as {robot_id}")
    
    # Move the robots
    print("\nMoving robots...")
    
    # Robot 0 - Joint positions
    joint_positions = [0.2, 0.3, 0.1, -0.2, 0.3, 0.0]
    command = Command(
        type="joint_position",
        data={"positions": joint_positions},
        timestamp=time.time()
    )
    simulator.apply_command(robot_ids[0], command)
    
    # Robot 1 - Gripper
    command = Command(
        type="gripper",
        data={"position": 0.5},  # Open the gripper
        timestamp=time.time()
    )
    simulator.apply_command(robot_ids[1], command)
    
    # Let the robots move
    for i in range(30):
        simulator.step(0.01)
    
    # Create a video
    print("\nCreating video of the scene...")
    visualizer.create_video(
        "multi_robot_demo.mp4",
        duration=5.0,
        fps=30,
        camera_pos=[1.5, 1.5, 1.0],
        orbital=True
    )
    print("Video saved to output/multi_robot_demo.mp4")


def main():
    """Run the simulation engine demonstration."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Simulation Engine Demo")
    parser.add_argument(
        "--demo", 
        type=str, 
        default="all",
        choices=["physics", "control", "trajectory", "multi", "all"],
        help="Which demo to run"
    )
    parser.add_argument(
        "--headless", 
        action="store_true",
        help="Run in headless mode (no GUI)"
    )
    args = parser.parse_args()
    
    # Initialize the simulator
    simulator = Simulator(use_gui=not args.headless)
    
    # Initialize the visualizer
    visualizer = SimulationVisualizer(simulator)
    
    try:
        # Run the selected demo
        if args.demo == "physics" or args.demo == "all":
            demo_simple_physics(simulator, visualizer)
        
        if args.demo == "control" or args.demo == "all":
            demo_robot_control(simulator, visualizer)
        
        if args.demo == "trajectory" or args.demo == "all":
            demo_robot_trajectory(simulator, visualizer)
        
        if args.demo == "multi" or args.demo == "all":
            demo_multi_robot(simulator, visualizer)
        
        print("\nDemo completed. Press Ctrl+C to exit...")
        
        # Keep the visualization window open (if in GUI mode)
        if not args.headless:
            while True:
                simulator.step(0.01)
                time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("Demo interrupted by user")
    finally:
        # Clean up
        simulator.close()
        visualizer.close()


if __name__ == "__main__":
    main() 