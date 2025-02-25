"""
Interface definitions for the teleoperation simulation.

This module defines abstract classes and protocols that establish
the contracts between different modules in the system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Tuple, Union
import numpy as np


# Data structures for inter-module communication

@dataclass
class Vector3:
    """3D vector representation."""
    x: float
    y: float
    z: float
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.x, self.y, self.z])
    
    @classmethod
    def from_array(cls, array: np.ndarray) -> 'Vector3':
        """Create from numpy array."""
        return cls(x=float(array[0]), y=float(array[1]), z=float(array[2]))


@dataclass
class Quaternion:
    """Quaternion for 3D rotation representation."""
    w: float
    x: float
    y: float
    z: float
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.w, self.x, self.y, self.z])
    
    @classmethod
    def from_array(cls, array: np.ndarray) -> 'Quaternion':
        """Create from numpy array."""
        return cls(w=float(array[0]), x=float(array[1]), 
                   y=float(array[2]), z=float(array[3]))


@dataclass
class Pose:
    """Representation of position and orientation."""
    position: Vector3
    orientation: Quaternion


@dataclass
class JointState:
    """State of a robot joint."""
    position: float
    velocity: float
    effort: float
    name: str


@dataclass
class RobotState:
    """Complete state of a robot."""
    joint_states: List[JointState]
    pose: Optional[Pose] = None
    timestamp: float = 0.0


@dataclass
class Command:
    """Command sent from operator to robot."""
    type: str
    data: Dict[str, Any]
    timestamp: float


# Simulation Module Interface

class SimulationInterface(ABC):
    """Interface for the simulation module."""
    
    @abstractmethod
    def step(self, dt: float) -> None:
        """Advance simulation by time step dt."""
        pass
    
    @abstractmethod
    def add_robot(self, robot_id: str, robot_type: str, pose: Pose) -> None:
        """Add a robot to the simulation."""
        pass
    
    @abstractmethod
    def get_robot_state(self, robot_id: str) -> RobotState:
        """Get the current state of a robot."""
        pass
    
    @abstractmethod
    def apply_command(self, robot_id: str, command: Command) -> None:
        """Apply a command to a robot."""
        pass


# Robot Module Interface

class RobotInterface(ABC):
    """Interface for robot implementation."""
    
    @abstractmethod
    def initialize(self, robot_type: str) -> None:
        """Initialize the robot with a specific type."""
        pass
    
    @abstractmethod
    def get_state(self) -> RobotState:
        """Get the current state of the robot."""
        pass
    
    @abstractmethod
    def apply_command(self, command: Command) -> None:
        """Apply a command to the robot."""
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the robot's internal state."""
        pass


# Operator Interface

class OperatorInterface(ABC):
    """Interface for the operator module."""
    
    @abstractmethod
    def process_input(self, input_data: Dict[str, Any]) -> Optional[Command]:
        """Process operator input and generate command."""
        pass
    
    @abstractmethod
    def update_display(self, robot_state: RobotState) -> None:
        """Update the operator display with robot state."""
        pass
    
    @abstractmethod
    def get_feedback(self) -> Dict[str, Any]:
        """Get feedback to be sent to the operator."""
        pass


# Communication Interface

class CommunicationInterface(ABC):
    """Interface for the communication module."""
    
    @abstractmethod
    def send_command(self, command: Command) -> None:
        """Send a command from operator to robot."""
        pass
    
    @abstractmethod
    def receive_command(self) -> Optional[Command]:
        """Receive a command sent to the robot."""
        pass
    
    @abstractmethod
    def send_state(self, state: RobotState) -> None:
        """Send robot state to the operator."""
        pass
    
    @abstractmethod
    def receive_state(self) -> Optional[RobotState]:
        """Receive robot state at the operator side."""
        pass
    
    @abstractmethod
    def set_network_conditions(self, latency: float, 
                               packet_loss: float, 
                               bandwidth: float) -> None:
        """Set network condition parameters for simulation."""
        pass 