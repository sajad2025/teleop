# Simulation Engine for Teleoperation

This module provides a physics-based simulation environment for telerobotic systems, built on PyBullet.

## Overview

The simulation engine is responsible for:
- Physics simulation (using PyBullet)
- Robot and environment modeling
- Sensor simulation
- Visualization and data collection

## Key Components

### `simulator.py`

The core simulator that integrates with PyBullet to provide physics simulation. Features include:
- Loading and simulating various robot models (KUKA LBR, Husky mobile platform, etc.)
- Adding environment objects (tables, cubes, etc.)
- Applying commands to robots
- Stepping the simulation
- Camera simulation

### `environment.py`

Helper class for creating and managing simulation environments:
- Pre-configured environments (tabletop, obstacle course, etc.)
- Object manipulation utilities
- Scene setup helpers

### `visualization.py`

Utilities for visualizing the simulation:
- Capturing images from the simulation
- Creating videos
- Plotting robot trajectories
- Displaying robot information

## Using the Simulation Engine

The simulation engine can be used in two ways:

1. **As part of the full teleoperation system**:
   When used with the other modules, the simulation engine receives commands from the operator through the communication layer and provides robot state updates.

2. **Standalone mode**:
   The simulation engine can be used independently for development and testing, as demonstrated in `examples/simulation_demo.py`.

## Integration Points

The simulation engine integrates with the rest of the system through these interfaces:

- `SimulationInterface`: Defines how other components interact with the simulator
- `Command`: Data structure for sending commands to robots
- `RobotState`: Data structure for retrieving the state of robots

## Running the Demo

To run the simulation demo:

```bash
# Run all demos
./examples/simulation_demo.py

# Run a specific demo
./examples/simulation_demo.py --demo physics

# Run in headless mode (no GUI)
./examples/simulation_demo.py --headless
```

## Extending the Simulation Engine

To add new robot types:
1. Add the URDF file to the PyBullet data directory
2. Add an entry to `ROBOT_URDF_MAP` in `simulator.py`

To add new object types:
1. Add the URDF file to the PyBullet data directory
2. Add an entry to `OBJECT_URDF_MAP` in `simulator.py`

To add new environment types:
1. Create a new method in the `Environment` class in `environment.py`

## Dependencies

- PyBullet: Physics engine
- NumPy: Numerical operations
- Matplotlib: Plotting
- PIL: Image processing 