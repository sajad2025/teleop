"""
Visualization utilities for the simulation engine.

This module provides tools for visualizing the simulation state,
including rendering camera views and saving images/videos.
"""

import os
import time
from typing import List, Optional, Tuple, Dict, Any

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from PIL import Image, ImageDraw, ImageFont

from src.common.interfaces import Pose, Vector3, Quaternion
from src.common.utils import get_logger
from src.simulation.simulator import Simulator


class SimulationVisualizer:
    """
    Visualization helper for the simulation engine.
    
    This class provides methods to visualize the simulation state,
    capture images and videos, and display debug information.
    """
    
    def __init__(self, simulator: Simulator, output_dir: str = "output"):
        """
        Initialize the visualizer.
        
        Args:
            simulator: The simulator instance to visualize.
            output_dir: Directory to save output files.
        """
        self.logger = get_logger(__name__)
        self.simulator = simulator
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize plotting
        self.fig = None
        self.ax = None
        self.animation = None
        
        self.logger.info("Visualizer initialized")
    
    def capture_image(self, filename: str, width: int = 640, height: int = 480,
                     camera_pos: List[float] = [2, -2, 1.5],
                     target_pos: List[float] = [0, 0, 0]) -> np.ndarray:
        """
        Capture a single image from the simulation.
        
        Args:
            filename: Output filename (will be saved in output_dir).
            width: Image width in pixels.
            height: Image height in pixels.
            camera_pos: Camera position [x, y, z].
            target_pos: Camera target position [x, y, z].
            
        Returns:
            The captured image as a numpy array.
        """
        # Get image from simulator
        img = self.simulator.get_camera_image(
            width=width,
            height=height,
            position=camera_pos,
            target=target_pos
        )
        
        # Save the image
        output_path = os.path.join(self.output_dir, filename)
        Image.fromarray(img).save(output_path)
        
        self.logger.info(f"Saved image to {output_path}")
        return img
    
    def add_text_to_image(self, img: np.ndarray, text: str, 
                         position: Tuple[int, int] = (10, 10),
                         color: Tuple[int, int, int] = (255, 255, 255),
                         font_size: int = 20) -> np.ndarray:
        """
        Add text overlay to an image.
        
        Args:
            img: Input image as numpy array.
            text: Text to add.
            position: (x, y) position for text.
            color: RGB color for text.
            font_size: Font size for text.
            
        Returns:
            Image with text overlay.
        """
        # Convert to PIL Image
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        
        # Add text
        draw.text(position, text, color)
        
        # Convert back to numpy
        return np.array(pil_img)
    
    def create_video(self, filename: str, duration: float = 5.0, fps: int = 30,
                   width: int = 640, height: int = 480,
                   camera_pos: List[float] = [2, -2, 1.5],
                   orbital: bool = True) -> None:
        """
        Create a video of the simulation.
        
        Args:
            filename: Output filename (will be saved in output_dir).
            duration: Duration of video in seconds.
            fps: Frames per second.
            width: Frame width in pixels.
            height: Frame height in pixels.
            camera_pos: Initial camera position [x, y, z].
            orbital: Whether to orbit around the scene.
        """
        # Set up matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        self.ax.axis('off')
        
        # Number of frames
        n_frames = int(duration * fps)
        
        # Function to update the plot for each frame
        def update(frame):
            # Step the simulation
            self.simulator.step(1.0 / fps)
            
            # Update camera position if orbital
            if orbital:
                angle = frame * 2 * np.pi / n_frames
                radius = np.sqrt(camera_pos[0]**2 + camera_pos[1]**2)
                cam_x = radius * np.cos(angle)
                cam_y = radius * np.sin(angle)
                cur_camera_pos = [cam_x, cam_y, camera_pos[2]]
            else:
                cur_camera_pos = camera_pos
            
            # Get the image
            img = self.simulator.get_camera_image(
                width=width,
                height=height,
                position=cur_camera_pos,
                target=[0, 0, 0]
            )
            
            # Add timestamp
            timestamp = f"Time: {self.simulator.time:.2f}s"
            img = self.add_text_to_image(img, timestamp)
            
            # Update the plot
            self.ax.clear()
            self.ax.imshow(img)
            self.ax.axis('off')
            
            return self.ax,
        
        # Create the animation
        self.animation = FuncAnimation(
            self.fig, update, frames=n_frames, 
            blit=True, interval=1000/fps
        )
        
        # Save the animation
        output_path = os.path.join(self.output_dir, filename)
        writer = FFMpegWriter(fps=fps)
        self.animation.save(output_path, writer=writer)
        
        self.logger.info(f"Saved video to {output_path}")
    
    def plot_robot_trajectory(self, robot_id: str, duration: float = 10.0, 
                            dt: float = 0.1, filename: Optional[str] = None) -> None:
        """
        Plot the trajectory of a robot over time.
        
        Args:
            robot_id: ID of the robot to track.
            duration: Duration to track in seconds.
            dt: Time step between measurements.
            filename: Output filename (will be saved in output_dir if provided).
        """
        if robot_id not in self.simulator.robots:
            self.logger.warning(f"Robot {robot_id} does not exist in simulation")
            return
        
        # Record trajectory
        positions = []
        times = []
        initial_time = self.simulator.time
        
        while self.simulator.time - initial_time < duration:
            # Step simulation
            self.simulator.step(dt)
            
            # Get robot state
            state = self.simulator.get_robot_state(robot_id)
            positions.append([
                state.pose.position.x,
                state.pose.position.y,
                state.pose.position.z
            ])
            times.append(self.simulator.time - initial_time)
        
        # Convert to numpy arrays
        positions = np.array(positions)
        times = np.array(times)
        
        # Plot
        fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
        coords = ['X', 'Y', 'Z']
        
        for i in range(3):
            axs[i].plot(times, positions[:, i])
            axs[i].set_ylabel(f"{coords[i]} Position (m)")
            axs[i].grid(True)
        
        axs[-1].set_xlabel("Time (s)")
        fig.suptitle(f"Robot {robot_id} Trajectory")
        plt.tight_layout()
        
        # Save if filename provided
        if filename:
            output_path = os.path.join(self.output_dir, filename)
            plt.savefig(output_path)
            self.logger.info(f"Saved trajectory plot to {output_path}")
        
        plt.show()
    
    def display_robot_info(self, robot_id: str) -> None:
        """
        Display information about a robot.
        
        Args:
            robot_id: ID of the robot to display info for.
        """
        if robot_id not in self.simulator.robots:
            self.logger.warning(f"Robot {robot_id} does not exist in simulation")
            return
        
        robot_data = self.simulator.robots[robot_id]
        print(f"=== Robot {robot_id} Info ===")
        print(f"Type: {robot_data['type']}")
        print(f"Body ID: {robot_data['body_id']}")
        print(f"Active Joints: {len(robot_data['joint_indices'])}")
        
        for i, joint_idx in enumerate(robot_data['joint_indices']):
            joint_name = robot_data['joint_names'].get(joint_idx, f"joint_{joint_idx}")
            joint_state = robot_data['state'].joint_states[i]
            print(f"  - {joint_name}: position={joint_state.position:.2f}, velocity={joint_state.velocity:.2f}")
        
        pose = robot_data['state'].pose
        print(f"Position: [{pose.position.x:.2f}, {pose.position.y:.2f}, {pose.position.z:.2f}]")
        print(f"Orientation: [{pose.orientation.w:.2f}, {pose.orientation.x:.2f}, {pose.orientation.y:.2f}, {pose.orientation.z:.2f}]")
    
    def close(self) -> None:
        """Clean up resources."""
        if self.fig:
            plt.close(self.fig)
        self.logger.info("Visualizer closed") 