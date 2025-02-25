"""
Core simulation engine implementation.

This module provides the main simulation engine that handles physics,
time management, and object interactions using PyBullet.
"""

import os
import time
from typing import Dict, List, Optional, Tuple, Any, Union

import numpy as np
import pybullet as p
import pybullet_data

from src.common.interfaces import (
    Command, JointState, Pose, RobotState, SimulationInterface, Vector3, Quaternion
)
from src.common.utils import get_logger


class Simulator(SimulationInterface):
    """
    Main simulation engine implementation.
    
    This class handles the physics simulation and maintains the state
    of all objects in the virtual environment using PyBullet.
    """
    
    # Available robot URDFs
    ROBOT_URDF_MAP = {
        "arm_6dof": "kuka_iiwa/model.urdf",
        "mobile_platform": "husky/husky.urdf",
        "simple_gripper": "gripper/wsg50_one_motor_gripper.urdf",
    }
    
    # Available environment objects
    OBJECT_URDF_MAP = {
        "table": "table/table.urdf",
        "cube": "cube_small.urdf",
        "sphere": "sphere_small.urdf",
        "duck": "duck_vhacd.urdf",
        "tray": "tray/traybox.urdf",
    }
    
    def __init__(self, use_gui: bool = True, physics_engine: str = "pybullet"):
        """
        Initialize the simulator.
        
        Args:
            use_gui: Whether to use GUI visualization.
            physics_engine: Name of the physics engine to use.
        """
        self.logger = get_logger(__name__)
        self.physics_engine = physics_engine
        self.use_gui = use_gui
        self.robots: Dict[str, Dict] = {}
        self.environment_objects: List[Dict] = []
        self.time = 0.0
        
        # Connect to PyBullet
        self.physics_client = p.connect(p.GUI if use_gui else p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        
        # Load ground plane
        self.plane_id = p.loadURDF("plane.urdf")
        
        self.logger.info(f"Simulator initialized with {physics_engine} engine (GUI: {use_gui})")
    
    def step(self, dt: float) -> None:
        """
        Advance simulation by time step dt.
        
        Args:
            dt: Time step in seconds.
        """
        p.stepSimulation()
        self.time += dt
        
        # Update robot states
        for robot_id, robot_data in self.robots.items():
            body_id = robot_data["body_id"]
            joint_indices = robot_data["joint_indices"]
            
            # Get position and orientation
            pos, orn = p.getBasePositionAndOrientation(body_id)
            
            # Create pose
            pose = Pose(
                position=Vector3(x=float(pos[0]), y=float(pos[1]), z=float(pos[2])),
                orientation=Quaternion(w=float(orn[3]), x=float(orn[0]), y=float(orn[1]), z=float(orn[2]))
            )
            
            # Get joint states
            joint_states = []
            for i in joint_indices:
                joint_info = p.getJointState(body_id, i)
                joint_name = robot_data["joint_names"].get(i, f"joint_{i}")
                joint_states.append(JointState(
                    position=float(joint_info[0]),
                    velocity=float(joint_info[1]),
                    effort=float(joint_info[3]),
                    name=joint_name
                ))
            
            # Update robot state
            robot_data["state"] = RobotState(
                joint_states=joint_states,
                pose=pose,
                timestamp=self.time
            )
    
    def add_robot(self, robot_id: str, robot_type: str, pose: Pose) -> None:
        """
        Add a robot to the simulation.
        
        Args:
            robot_id: Unique identifier for the robot.
            robot_type: Type/model of the robot.
            pose: Initial pose of the robot.
        """
        if robot_id in self.robots:
            self.logger.warning(f"Robot {robot_id} already exists, removing old one")
            self._remove_robot(robot_id)
        
        # Get the URDF file for this robot type
        urdf_file = self.ROBOT_URDF_MAP.get(robot_type)
        if not urdf_file:
            self.logger.warning(f"Unknown robot type: {robot_type}, using default")
            urdf_file = "kuka_iiwa/model.urdf"  # Default robot
        
        # Load the robot URDF
        start_pos = [pose.position.x, pose.position.y, pose.position.z]
        start_orn = [pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w]
        
        body_id = p.loadURDF(urdf_file, start_pos, start_orn)
        
        # Get all joints and their names
        joint_indices = []
        joint_names = {}
        
        for i in range(p.getNumJoints(body_id)):
            joint_info = p.getJointInfo(body_id, i)
            if joint_info[2] != p.JOINT_FIXED:  # Skip fixed joints
                joint_indices.append(i)
                joint_names[i] = joint_info[1].decode('utf-8')
        
        # Store robot data
        self.robots[robot_id] = {
            "type": robot_type,
            "pose": pose,
            "body_id": body_id,
            "joint_indices": joint_indices,
            "joint_names": joint_names,
            "state": RobotState(joint_states=[], pose=pose, timestamp=self.time)
        }
        
        self.logger.info(f"Added robot {robot_id} of type {robot_type} with {len(joint_indices)} active joints")
        
        # Step once to update the state
        self.step(0.01)
    
    def _remove_robot(self, robot_id: str) -> None:
        """
        Remove a robot from the simulation.
        
        Args:
            robot_id: Unique identifier for the robot to remove.
        """
        if robot_id in self.robots:
            p.removeBody(self.robots[robot_id]["body_id"])
            del self.robots[robot_id]
            self.logger.info(f"Removed robot {robot_id}")
    
    def get_robot_state(self, robot_id: str) -> RobotState:
        """
        Get the current state of a robot.
        
        Args:
            robot_id: Unique identifier for the robot.
            
        Returns:
            Current state of the robot.
            
        Raises:
            KeyError: If robot_id does not exist.
        """
        if robot_id not in self.robots:
            raise KeyError(f"Robot {robot_id} does not exist in simulation")
        
        return self.robots[robot_id]["state"]
    
    def apply_command(self, robot_id: str, command: Command) -> None:
        """
        Apply a command to a robot.
        
        Args:
            robot_id: Unique identifier for the robot.
            command: Command to apply.
            
        Raises:
            KeyError: If robot_id does not exist.
        """
        if robot_id not in self.robots:
            raise KeyError(f"Robot {robot_id} does not exist in simulation")
        
        robot_data = self.robots[robot_id]
        body_id = robot_data["body_id"]
        
        if command.type == "joint_position":
            # Apply joint position command
            if "positions" in command.data:
                positions = command.data["positions"]
                for i, joint_idx in enumerate(robot_data["joint_indices"]):
                    if i < len(positions):
                        p.setJointMotorControl2(
                            bodyUniqueId=body_id,
                            jointIndex=joint_idx,
                            controlMode=p.POSITION_CONTROL,
                            targetPosition=positions[i]
                        )
        
        elif command.type == "velocity":
            # Apply velocity command
            if "linear" in command.data and "angular" in command.data:
                linear = command.data["linear"]
                angular = command.data["angular"]
                
                # This is a simplified model - in a real implementation,
                # you would convert these to joint velocities based on
                # the specific robot's kinematics
                for joint_idx in robot_data["joint_indices"]:
                    # Apply some velocity to the joints
                    p.setJointMotorControl2(
                        bodyUniqueId=body_id,
                        jointIndex=joint_idx,
                        controlMode=p.VELOCITY_CONTROL,
                        targetVelocity=linear * 0.5  # Scale down for demo
                    )
        
        elif command.type == "gripper":
            # Apply gripper command
            if "position" in command.data:
                # This assumes the last two joints control the gripper
                gripper_joints = robot_data["joint_indices"][-2:]
                position = command.data["position"]
                
                for joint_idx in gripper_joints:
                    p.setJointMotorControl2(
                        bodyUniqueId=body_id,
                        jointIndex=joint_idx,
                        controlMode=p.POSITION_CONTROL,
                        targetPosition=position
                    )
        
        else:
            self.logger.warning(f"Unknown command type: {command.type}")
        
        self.logger.info(f"Applied command {command.type} to robot {robot_id}")
    
    def add_environment_object(self, object_type: str, pose: Pose) -> int:
        """
        Add an object to the environment.
        
        Args:
            object_type: Type of object (e.g., "table", "cube").
            pose: Initial pose of the object.
            
        Returns:
            Index of the added object.
        """
        # Get the URDF file for this object type
        urdf_file = self.OBJECT_URDF_MAP.get(object_type)
        if not urdf_file:
            self.logger.warning(f"Unknown object type: {object_type}, using cube")
            urdf_file = "cube_small.urdf"  # Default object
        
        # Load the object URDF
        start_pos = [pose.position.x, pose.position.y, pose.position.z]
        start_orn = [pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w]
        
        body_id = p.loadURDF(urdf_file, start_pos, start_orn)
        
        # Store object data
        object_id = len(self.environment_objects)
        self.environment_objects.append({
            "type": object_type,
            "pose": pose,
            "id": object_id,
            "body_id": body_id
        })
        
        self.logger.info(f"Added {object_type} object with ID {object_id}")
        return object_id
    
    def remove_environment_object(self, object_id: int) -> None:
        """
        Remove an object from the environment.
        
        Args:
            object_id: ID of the object to remove.
            
        Raises:
            IndexError: If object_id is invalid.
        """
        if object_id < 0 or object_id >= len(self.environment_objects):
            raise IndexError(f"Invalid object ID: {object_id}")
        
        p.removeBody(self.environment_objects[object_id]["body_id"])
        # Note: We don't actually remove from the list to keep IDs stable
        self.environment_objects[object_id]["removed"] = True
        self.logger.info(f"Removed object with ID {object_id}")
    
    def get_camera_image(self, width: int = 320, height: int = 240, 
                        position: List[float] = [1, 0, 1],
                        target: List[float] = [0, 0, 0]) -> np.ndarray:
        """
        Get a camera image from the simulation.
        
        Args:
            width: Image width in pixels.
            height: Image height in pixels.
            position: Camera position [x, y, z].
            target: Camera target point [x, y, z].
            
        Returns:
            RGB image as numpy array.
        """
        # Set up the camera
        view_matrix = p.computeViewMatrix(
            cameraEyePosition=position,
            cameraTargetPosition=target,
            cameraUpVector=[0, 0, 1]
        )
        
        proj_matrix = p.computeProjectionMatrixFOV(
            fov=60.0,
            aspect=float(width) / height,
            nearVal=0.1,
            farVal=100.0
        )
        
        # Get the image
        _, _, rgb_img, _, _ = p.getCameraImage(
            width=width,
            height=height,
            viewMatrix=view_matrix,
            projectionMatrix=proj_matrix,
            renderer=p.ER_BULLET_HARDWARE_OPENGL
        )
        
        # Convert to numpy array
        rgb_array = np.array(rgb_img, dtype=np.uint8)
        rgb_array = rgb_array[:, :, :3]  # Remove alpha channel
        
        return rgb_array
    
    def reset(self) -> None:
        """Reset the simulation to initial state."""
        # Remove all objects
        for robot_id in list(self.robots.keys()):
            self._remove_robot(robot_id)
        
        for obj in self.environment_objects:
            if "body_id" in obj and not obj.get("removed", False):
                p.removeBody(obj["body_id"])
        
        self.robots = {}
        self.environment_objects = []
        
        # Reset simulation
        p.resetSimulation()
        p.setGravity(0, 0, -9.81)
        
        # Reload ground plane
        self.plane_id = p.loadURDF("plane.urdf")
        
        self.time = 0.0
        self.logger.info("Simulation reset")
    
    def close(self) -> None:
        """Close the simulator and clean up resources."""
        p.disconnect(self.physics_client)
        self.logger.info("Simulator closed") 