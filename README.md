# Teleoperation Simulation Project

A modular simulation platform for teleoperation of general robotic systems.

## Architecture Overview

This project is structured into four independent modules to facilitate parallel development:

1. **Simulation Engine** - Core physics simulation and virtual environment modeling (now with PyBullet integration!)
2. **Robot Models** - Robot definitions, kinematics, dynamics, and control interfaces
3. **Operator Interface** - Human input handling, visualization, and teleoperation UI
4. **Communication Layer** - Data transfer protocols, latency simulation, and network effects

## Enhanced Simulation Engine

The simulation engine has been significantly enhanced with:

- **PyBullet Integration**: Realistic physics simulation
- **Visual Rendering**: Camera views and video creation
- **Multiple Robot Types**: Support for various robot models (KUKA arm, Husky mobile platform, etc.)
- **Environment Creator**: Tools for building different simulation scenarios
- **Visualization Tools**: Plotting and data visualization utilities

To try the enhanced simulation engine demo:

```bash
# Run the full demo
./examples/simulation_demo.py

# Run a specific demo
./examples/simulation_demo.py --demo physics
./examples/simulation_demo.py --demo control
./examples/simulation_demo.py --demo trajectory
./examples/simulation_demo.py --demo multi
```

## Module Responsibilities

### Simulation Engine
- Physics engine integration
- Environment modeling
- Collision detection
- Sensor simulation
- Time management

### Robot Models
- Robot kinematic/dynamic models
- Robot state representation
- Low-level controllers
- Robot-specific sensors
- Actuation models

### Operator Interface
- User input processing
- Visualization components
- Command mapping
- Operator feedback systems
- Teleoperation UI

### Communication Layer
- Command/data serialization
- Network protocol simulation
- Latency and packet loss models
- Bandwidth limitation simulation
- Data buffering and synchronization

## Development Guidelines

To ensure smooth collaboration:

1. **Interface Stability**: Module interfaces should remain stable. Breaking changes require team discussion.
2. **Dependency Management**: Modules should only depend on published interfaces of other modules.
3. **Testing**: Each module should have comprehensive tests that can run independently.
4. **Documentation**: All module interfaces must be well-documented.
5. **Git Workflow**: 
   - Develop features in feature branches
   - Create pull requests for review
   - Merge to main only after tests pass
   - Rebase feature branches regularly against main

## Getting Started

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the simulation:
   ```
   python src/main.py
   ```

3. Try the enhanced simulation demo:
   ```
   ./examples/simulation_demo.py
   ```

## Directory Structure

```
teleop/
├── docs/                 # Documentation
├── src/                  # Source code
│   ├── simulation/       # Simulation engine module (enhanced!)
│   │   ├── simulator.py  # PyBullet-based physics simulation
│   │   ├── environment.py # Environment creation tools
│   │   └── visualization.py # Visualization utilities
│   ├── robots/           # Robot models module
│   ├── operator/         # Operator interface module
│   ├── communication/    # Communication layer module
│   ├── common/           # Shared utilities and interfaces
│   └── main.py           # Application entry point
├── tests/                # Test suite
│   ├── simulation/
│   ├── robots/
│   ├── operator/
│   ├── communication/
│   └── integration/
├── examples/             # Example usage scripts
│   ├── simple_teleop.py  # Simple teleoperation example
│   └── simulation_demo.py # Enhanced simulation engine demo
├── requirements.txt      # Project dependencies
└── README.md             # Project overview
``` 