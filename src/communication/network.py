"""
Network communication module for teleoperation.

This module handles simulated communication between the operator
and robot, including network effects like latency and packet loss.
"""

import queue
import random
import threading
import time
from typing import Dict, List, Optional, Tuple, Union, Any

from src.common.interfaces import (
    Command, CommunicationInterface, RobotState
)
from src.common.utils import get_logger


class NetworkChannel:
    """
    Simulated network channel for communication.
    
    This class simulates a communication channel with configurable
    latency, packet loss, and bandwidth restrictions.
    """
    
    def __init__(self, name: str):
        """
        Initialize a network channel.
        
        Args:
            name: Name of the channel.
        """
        self.logger = get_logger(__name__)
        self.name = name
        self.queue = queue.PriorityQueue()
        self.latency = 0.0  # seconds
        self.jitter = 0.0  # seconds
        self.packet_loss = 0.0  # probability (0.0-1.0)
        self.bandwidth = float('inf')  # bytes per second
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.running = False
        self.logger.info(f"Created network channel '{name}'")
    
    def start(self) -> None:
        """Start the channel processing thread."""
        self.running = True
        self.thread.start()
        self.logger.info(f"Started network channel '{self.name}'")
    
    def stop(self) -> None:
        """Stop the channel processing thread."""
        self.running = False
        self.thread.join()
        self.logger.info(f"Stopped network channel '{self.name}'")
    
    def send(self, data: Any, callback: Any) -> None:
        """
        Send data through the channel.
        
        Args:
            data: Data to send.
            callback: Callback to call when data arrives.
        """
        # Simulate packet loss
        if random.random() < self.packet_loss:
            self.logger.debug(f"Packet dropped in channel '{self.name}'")
            return
        
        # Calculate delivery time based on latency and jitter
        delivery_time = time.time() + self.latency
        if self.jitter > 0:
            delivery_time += random.uniform(-self.jitter/2, self.jitter/2)
        
        # Add to queue
        self.queue.put((delivery_time, (data, callback)))
        self.logger.debug(f"Data queued in channel '{self.name}', delivery at {delivery_time}")
    
    def _process_queue(self) -> None:
        """Process the queue of outgoing messages."""
        while self.running:
            try:
                if self.queue.empty():
                    time.sleep(0.01)  # Sleep to avoid busy waiting
                    continue
                
                # Peek at the next item
                delivery_time, _ = self.queue.queue[0]
                
                # If it's time to deliver, remove from queue and deliver
                if time.time() >= delivery_time:
                    _, (data, callback) = self.queue.get()
                    callback(data)
                    self.logger.debug(f"Data delivered in channel '{self.name}'")
                else:
                    # Not time yet, sleep a bit
                    time.sleep(0.01)
            except Exception as e:
                self.logger.error(f"Error in channel '{self.name}': {e}")
    
    def set_conditions(self, latency: float, jitter: float,
                      packet_loss: float, bandwidth: float) -> None:
        """
        Set network channel conditions.
        
        Args:
            latency: Base latency in seconds.
            jitter: Jitter in seconds.
            packet_loss: Packet loss probability (0.0-1.0).
            bandwidth: Bandwidth limit in bytes per second.
        """
        self.latency = max(0.0, latency)
        self.jitter = max(0.0, jitter)
        self.packet_loss = max(0.0, min(1.0, packet_loss))
        self.bandwidth = max(0.0, bandwidth)
        self.logger.info(
            f"Updated channel '{self.name}' conditions: "
            f"latency={self.latency:.3f}s, jitter={self.jitter:.3f}s, "
            f"packet_loss={self.packet_loss:.1%}, bandwidth={self.bandwidth} B/s"
        )


class NetworkSimulator(CommunicationInterface):
    """
    Network simulator for teleoperation.
    
    This class simulates a bidirectional communication network between
    the operator and robot, with configurable network conditions.
    """
    
    def __init__(self):
        """Initialize the network simulator."""
        self.logger = get_logger(__name__)
        
        # Communication channels
        self.operator_to_robot = NetworkChannel("operator_to_robot")
        self.robot_to_operator = NetworkChannel("robot_to_operator")
        
        # Command queues
        self.command_queue = queue.Queue()
        self.state_queue = queue.Queue()
        
        # Start channels
        self.operator_to_robot.start()
        self.robot_to_operator.start()
        
        self.logger.info("Network simulator initialized")
    
    def set_network_conditions(self, latency: float, 
                               packet_loss: float, 
                               bandwidth: float) -> None:
        """
        Set network condition parameters for simulation.
        
        Args:
            latency: Latency in seconds.
            packet_loss: Packet loss probability (0.0-1.0).
            bandwidth: Bandwidth limit in bytes per second.
        """
        # Set jitter to 10% of latency as a reasonable default
        jitter = latency * 0.1
        
        # Set conditions for both channels
        self.operator_to_robot.set_conditions(
            latency, jitter, packet_loss, bandwidth
        )
        self.robot_to_operator.set_conditions(
            latency, jitter, packet_loss, bandwidth
        )
    
    def send_command(self, command: Command) -> None:
        """
        Send a command from operator to robot.
        
        Args:
            command: Command to send.
        """
        self.logger.debug(f"Sending command: {command.type}")
        
        def command_callback(data: Command) -> None:
            self.command_queue.put(data)
            self.logger.debug("Command received at robot")
        
        self.operator_to_robot.send(command, command_callback)
    
    def receive_command(self) -> Optional[Command]:
        """
        Receive a command sent to the robot.
        
        Returns:
            Next command in the queue, or None if queue is empty.
        """
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None
    
    def send_state(self, state: RobotState) -> None:
        """
        Send robot state to the operator.
        
        Args:
            state: Robot state to send.
        """
        self.logger.debug("Sending robot state")
        
        def state_callback(data: RobotState) -> None:
            self.state_queue.put(data)
            self.logger.debug("State received at operator")
        
        self.robot_to_operator.send(state, state_callback)
    
    def receive_state(self) -> Optional[RobotState]:
        """
        Receive robot state at the operator side.
        
        Returns:
            Next state in the queue, or None if queue is empty.
        """
        try:
            return self.state_queue.get_nowait()
        except queue.Empty:
            return None
    
    def shutdown(self) -> None:
        """Stop the network simulator."""
        self.operator_to_robot.stop()
        self.robot_to_operator.stop()
        self.logger.info("Network simulator stopped") 