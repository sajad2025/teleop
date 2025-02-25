"""
Utility functions shared across modules.

This module provides common functionality used by multiple components
of the teleoperation system.
"""

import time
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, Union

import numpy as np

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

T = TypeVar('T')

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance for a module."""
    return logging.getLogger(name)

def time_function(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure and log the execution time of a function."""
    def wrapper(*args: Any, **kwargs: Any) -> T:
        logger = get_logger(func.__module__)
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.debug(f"Function {func.__name__} took {elapsed_time:.4f} seconds to run")
        return result
    return wrapper

def throttle(period: float) -> Callable[[Callable[..., T]], Callable[..., Optional[T]]]:
    """
    Decorator to throttle a function to run at most once per period (in seconds).
    Returns None when throttled.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        last_execution = 0.0
        
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            nonlocal last_execution
            current_time = time.time()
            
            if current_time - last_execution >= period:
                last_execution = current_time
                return func(*args, **kwargs)
            return None
            
        return wrapper
    return decorator

def transform_pose(pose: Dict[str, Any], 
                   translation: np.ndarray, 
                   rotation_matrix: np.ndarray) -> Dict[str, Any]:
    """Transform a pose by a translation and rotation."""
    position = np.array([pose['position']['x'], 
                         pose['position']['y'], 
                         pose['position']['z']])
    
    # Apply transformation
    new_position = np.dot(rotation_matrix, position) + translation
    
    # Update pose
    new_pose = pose.copy()
    new_pose['position']['x'] = float(new_position[0])
    new_pose['position']['y'] = float(new_position[1])
    new_pose['position']['z'] = float(new_position[2])
    
    # TODO: Implement quaternion rotation
    
    return new_pose

def format_float(value: float, precision: int = 3) -> str:
    """Format a float with specified precision for display."""
    return f"{value:.{precision}f}" 