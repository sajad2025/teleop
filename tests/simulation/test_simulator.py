"""
Tests for the simulation module.
"""

import time
import unittest
from unittest.mock import MagicMock, patch

from src.common.interfaces import Command, Pose, Vector3, Quaternion
from src.simulation.simulator import Simulator


class TestSimulator(unittest.TestCase):
    """Tests for the Simulator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simulator = Simulator()
        
        # Create a test robot
        self.robot_id = "test_robot"
        self.robot_type = "arm_6dof"
        self.robot_pose = Pose(
            position=Vector3(x=1.0, y=2.0, z=3.0),
            orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
        )
        
        # Add the robot to the simulator
        self.simulator.add_robot(self.robot_id, self.robot_type, self.robot_pose)
    
    def test_add_robot(self):
        """Test adding a robot to the simulator."""
        # Check that the robot was added correctly
        self.assertIn(self.robot_id, self.simulator.robots)
        self.assertEqual(self.simulator.robots[self.robot_id]["type"], self.robot_type)
        self.assertEqual(self.simulator.robots[self.robot_id]["pose"], self.robot_pose)
    
    def test_get_robot_state(self):
        """Test getting robot state."""
        # Get the robot state
        state = self.simulator.get_robot_state(self.robot_id)
        
        # Check that the state matches the expected values
        self.assertEqual(state.pose, self.robot_pose)
        self.assertEqual(len(state.joint_states), 0)  # No joints initialized in our test
    
    def test_step(self):
        """Test stepping the simulation."""
        # Record the initial time
        initial_time = self.simulator.time
        
        # Step the simulation
        dt = 0.1
        self.simulator.step(dt)
        
        # Check that the time advanced correctly
        self.assertAlmostEqual(self.simulator.time, initial_time + dt)
    
    def test_apply_command(self):
        """Test applying a command to a robot."""
        # Create a test command
        command = Command(
            type="test_command",
            data={"test_key": "test_value"},
            timestamp=time.time()
        )
        
        # Apply the command
        self.simulator.apply_command(self.robot_id, command)
        
        # Since apply_command is mostly a placeholder in our implementation,
        # we just check that it doesn't raise an exception
        
    def test_add_environment_object(self):
        """Test adding an environment object."""
        # Create a test object
        object_type = "test_object"
        object_pose = Pose(
            position=Vector3(x=4.0, y=5.0, z=6.0),
            orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
        )
        
        # Add the object to the environment
        object_id = self.simulator.add_environment_object(object_type, object_pose)
        
        # Check that the object was added correctly
        self.assertEqual(len(self.simulator.environment_objects), 1)
        self.assertEqual(self.simulator.environment_objects[0]["type"], object_type)
        self.assertEqual(self.simulator.environment_objects[0]["pose"], object_pose)
        self.assertEqual(self.simulator.environment_objects[0]["id"], object_id)
    
    def test_nonexistent_robot(self):
        """Test handling of a nonexistent robot."""
        # Try to get state of a nonexistent robot
        with self.assertRaises(KeyError):
            self.simulator.get_robot_state("nonexistent_robot")
        
        # Try to apply command to a nonexistent robot
        command = Command(
            type="test_command",
            data={"test_key": "test_value"},
            timestamp=time.time()
        )
        with self.assertRaises(KeyError):
            self.simulator.apply_command("nonexistent_robot", command)


if __name__ == "__main__":
    unittest.main() 