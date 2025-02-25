"""
Environment creation utilities for the simulation engine.

This module provides tools for creating and managing simulation environments,
including predefined scenes and objects.
"""

import time
import math
import random
from typing import Dict, List, Optional, Tuple, Any

import numpy as np

from src.common.interfaces import Pose, Vector3, Quaternion
from src.common.utils import get_logger
from src.simulation.simulator import Simulator


class Environment:
    """
    Environment helper for the simulation engine.
    
    This class provides methods to create and manage simulation environments,
    including adding predefined scenes and objects.
    """
    
    def __init__(self, simulator: Simulator):
        """
        Initialize the environment helper.
        
        Args:
            simulator: The simulator instance to work with.
        """
        self.logger = get_logger(__name__)
        self.simulator = simulator
        self.object_ids = {}  # Dictionary to keep track of objects by name
        self.logger.info("Environment helper initialized")
    
    def create_tabletop_scene(self) -> Dict[str, int]:
        """
        Create a tabletop scene with a table and some objects.
        
        Returns:
            Dictionary mapping object names to object IDs.
        """
        self.logger.info("Creating tabletop scene")
        
        # Add a table
        table_pose = Pose(
            position=Vector3(x=0.0, y=0.0, z=0.0),
            orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
        )
        table_id = self.simulator.add_environment_object("table", table_pose)
        self.object_ids["table"] = table_id
        
        # Add some objects on the table
        objects = ["cube", "sphere", "duck"]
        for i, obj_type in enumerate(objects):
            obj_pose = Pose(
                position=Vector3(x=0.0 + 0.2 * i, y=0.0, z=0.65),
                orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
            )
            obj_id = self.simulator.add_environment_object(obj_type, obj_pose)
            self.object_ids[f"{obj_type}_{i}"] = obj_id
        
        self.logger.info(f"Created tabletop scene with {len(self.object_ids)} objects")
        return self.object_ids
    
    def create_obstacle_course(self, num_obstacles: int = 5) -> Dict[str, int]:
        """
        Create an obstacle course with random obstacles.
        
        Args:
            num_obstacles: Number of obstacles to create.
            
        Returns:
            Dictionary mapping object names to object IDs.
        """
        self.logger.info(f"Creating obstacle course with {num_obstacles} obstacles")
        
        # Add random obstacles
        obstacle_types = ["cube", "sphere"]
        
        for i in range(num_obstacles):
            # Random position within a 2x2 area
            x = random.uniform(-1.0, 1.0)
            y = random.uniform(-1.0, 1.0)
            
            # Random orientation
            angle = random.uniform(0, 2 * math.pi)
            axis = [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)]
            axis_norm = np.linalg.norm(axis)
            if axis_norm > 0:
                axis = [x / axis_norm for x in axis]
            
            # Convert to quaternion
            s = math.sin(angle / 2)
            w = math.cos(angle / 2)
            x_q = axis[0] * s
            y_q = axis[1] * s
            z_q = axis[2] * s
            
            # Create pose
            obstacle_pose = Pose(
                position=Vector3(x=x, y=y, z=0.1),
                orientation=Quaternion(w=w, x=x_q, y=y_q, z=z_q)
            )
            
            # Randomly select obstacle type
            obstacle_type = random.choice(obstacle_types)
            
            # Add to simulator
            obstacle_id = self.simulator.add_environment_object(
                obstacle_type, obstacle_pose
            )
            
            self.object_ids[f"obstacle_{i}"] = obstacle_id
        
        self.logger.info(f"Created obstacle course with {len(self.object_ids)} objects")
        return self.object_ids
    
    def create_stacking_scene(self, num_cubes: int = 4) -> Dict[str, int]:
        """
        Create a scene with stacked cubes.
        
        Args:
            num_cubes: Number of cubes to stack.
            
        Returns:
            Dictionary mapping object names to object IDs.
        """
        self.logger.info(f"Creating stacking scene with {num_cubes} cubes")
        
        # Add a table
        table_pose = Pose(
            position=Vector3(x=0.0, y=0.0, z=0.0),
            orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
        )
        table_id = self.simulator.add_environment_object("table", table_pose)
        self.object_ids["table"] = table_id
        
        # Stack cubes
        cube_size = 0.05  # Approximate cube size in meters
        for i in range(num_cubes):
            # Position each cube above the previous one
            z_offset = 0.65 + i * cube_size * 2
            
            cube_pose = Pose(
                position=Vector3(x=0.0, y=0.0, z=z_offset),
                orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
            )
            
            cube_id = self.simulator.add_environment_object("cube", cube_pose)
            self.object_ids[f"cube_{i}"] = cube_id
            
            # Let physics settle between adding cubes
            for _ in range(10):
                self.simulator.step(0.01)
        
        self.logger.info(f"Created stacking scene with {len(self.object_ids)} objects")
        return self.object_ids
    
    def create_sorting_scene(self) -> Dict[str, int]:
        """
        Create a sorting scene with a tray and objects to sort.
        
        Returns:
            Dictionary mapping object names to object IDs.
        """
        self.logger.info("Creating sorting scene")
        
        # Add a table
        table_pose = Pose(
            position=Vector3(x=0.0, y=0.0, z=0.0),
            orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
        )
        table_id = self.simulator.add_environment_object("table", table_pose)
        self.object_ids["table"] = table_id
        
        # Add a tray
        tray_pose = Pose(
            position=Vector3(x=0.0, y=0.0, z=0.65),
            orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
        )
        tray_id = self.simulator.add_environment_object("tray", tray_pose)
        self.object_ids["tray"] = tray_id
        
        # Add objects to sort
        object_types = ["cube", "sphere", "duck"]
        for i, obj_type in enumerate(object_types):
            # Add 2 of each type
            for j in range(2):
                x_offset = 0.05 + 0.1 * (i * 2 + j)
                y_offset = 0.05 * (j % 2)
                
                obj_pose = Pose(
                    position=Vector3(x=x_offset - 0.3, y=y_offset, z=0.72),
                    orientation=Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
                )
                
                obj_id = self.simulator.add_environment_object(obj_type, obj_pose)
                self.object_ids[f"{obj_type}_{i}_{j}"] = obj_id
        
        self.logger.info(f"Created sorting scene with {len(self.object_ids)} objects")
        return self.object_ids
    
    def create_custom_scene(self, objects: List[Tuple[str, Pose]]) -> Dict[str, int]:
        """
        Create a custom scene with specified objects and poses.
        
        Args:
            objects: List of (object_type, pose) tuples.
            
        Returns:
            Dictionary mapping object names to object IDs.
        """
        self.logger.info(f"Creating custom scene with {len(objects)} objects")
        
        for i, (obj_type, pose) in enumerate(objects):
            obj_id = self.simulator.add_environment_object(obj_type, pose)
            self.object_ids[f"{obj_type}_{i}"] = obj_id
        
        self.logger.info(f"Created custom scene with {len(self.object_ids)} objects")
        return self.object_ids
    
    def remove_all_objects(self) -> None:
        """Remove all objects from the environment."""
        for name, obj_id in self.object_ids.items():
            try:
                self.simulator.remove_environment_object(obj_id)
                self.logger.debug(f"Removed object {name} (ID: {obj_id})")
            except Exception as e:
                self.logger.warning(f"Failed to remove object {name}: {e}")
        
        self.object_ids = {}
        self.logger.info("Removed all objects from the environment")
    
    def get_object_id(self, name: str) -> Optional[int]:
        """
        Get the ID of an object by name.
        
        Args:
            name: Object name.
            
        Returns:
            Object ID, or None if not found.
        """
        return self.object_ids.get(name) 