# Teleoperation Simulation Project

A modular simulation platform for teleoperation of general robotic systems.

## Architecture Overview

This project is structured into four independent modules to facilitate parallel development:

1. **Simulation Engine** - Core physics simulation and virtual environment modeling
2. **Robot Models** - Robot definitions, kinematics, dynamics, and control interfaces
3. **Operator Interface** - Human input handling, visualization, and teleoperation UI
4. **Communication Layer** - Data transfer protocols, latency simulation, and network effects

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

### Setting Up the Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/teleop.git
   cd teleop
   ```

2. Create a virtual environment:
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Simulation

1. Activate the virtual environment (if not already activated):
   ```bash
   # On macOS/Linux
   source venv/bin/activate

   # On Windows
   venv\Scripts\activate
   ```

2. Run the main simulation:
   ```bash
   python src/main.py
   ```

3. Or try one of the examples:
   ```bash
   python examples/simple_teleop.py
   ```

### Running Tests

With the virtual environment activated:
```bash
python -m pytest tests/
```

## Directory Structure

```
teleop/
├── docs/                 # Documentation
├── src/                  # Source code
│   ├── simulation/       # Simulation engine module
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
├── requirements.txt      # Project dependencies
├── venv/                 # Virtual environment (not tracked by git)
└── README.md             # Project overview
```

## Troubleshooting

### IDE Import Resolution Issues

If you're experiencing "Import could not be resolved" errors in your IDE (for modules like numpy, matplotlib, etc.) even though the code runs correctly, try the following:

1. **Install in Development Mode**:
   After activating your virtual environment, run:
   ```bash
   pip install -e .
   ```

2. **Configure VSCode**:
   - Make sure your Python interpreter is set to the virtual environment's Python
   - Reload your VSCode window after making configuration changes
   - The provided `.vscode/settings.json` should handle most import resolution issues

3. **Environment Variables**:
   If the above doesn't work, you can set the PYTHONPATH environment variable before starting your IDE:
   ```bash
   PYTHONPATH=$PYTHONPATH:$PWD code .
   ```

### Module Override Warnings

If you're seeing module override warnings, these are typically harmless but can be fixed by:
- Ensuring module names don't conflict with standard library or installed packages
- Using explicit relative imports

### Missing Module Source Issues

If you see errors like `Import "setuptools" could not be resolved from source`, try:

1. **Install Missing Packages**:
   ```bash
   pip install setuptools
   ```

2. **Disable Missing Module Source Warnings**:
   In VSCode, you can disable these warnings by adding to your settings.json:
   ```json
   "python.analysis.diagnosticSeverityOverrides": {
       "reportMissingModuleSource": "none"
   }
   ```

3. **Reload Your Editor**:
   After making changes, reload your editor window to apply them.