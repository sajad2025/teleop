# Teleoperation System Architecture

This document provides a detailed overview of the teleoperation system architecture.

## System Overview

The teleoperation system is designed to simulate remote control of robotic systems with realistic network conditions. The architecture is divided into four main modules, each with clear interfaces and responsibilities:

![Architecture Diagram](https://i.ibb.co/VqJ6tNN/teleop-architecture.png)

## Module Descriptions

### 1. Simulation Engine

**Purpose**: Provides the core physics simulation, environment modeling, and time management.

**Key Components**:
- **Simulator**: Main simulation engine that maintains world state
- **Physics Engine**: Handles physical interactions (integrated with PyBullet, etc.)
- **Environment**: Manages objects, terrain, and obstacles
- **Sensors**: Simulates sensor data (cameras, LiDAR, etc.)

**Interfaces**:
- `SimulationInterface`: Defines how other components interact with the simulator
- The simulation engine provides robot state updates and accepts commands

**Responsibilities**:
- Advancing the simulation time
- Managing all physical entities in the simulation
- Computing collisions and physical interactions
- Providing sensor data from the simulated environment

### 2. Robot Models

**Purpose**: Defines robot kinematics, dynamics, and control interfaces.

**Key Components**:
- **RobotModel**: Base class for robot implementations
- **Specific Robot Types**: Implementations for different robot architectures
- **Kinematics**: Forward and inverse kinematics solvers
- **Controllers**: Low-level robot controllers

**Interfaces**:
- `RobotInterface`: Defines how robots are controlled and queried
- Robots provide their state and accept control commands

**Responsibilities**:
- Defining the kinematic and dynamic models of robots
- Implementing robot-specific behaviors and constraints
- Providing robot state information
- Translating high-level commands to actuator-level controls

### 3. Operator Interface

**Purpose**: Handles user input, visualization, and operator feedback.

**Key Components**:
- **UI**: User interface components
- **Input Handlers**: Process keyboard, mouse, joystick inputs
- **Visualizations**: 3D views, status displays, etc.
- **Feedback Systems**: Haptic feedback, alerts, etc.

**Interfaces**:
- `OperatorInterface`: Defines how operator inputs are processed and displayed
- Processes user inputs and displays robot state

**Responsibilities**:
- Capturing and processing operator inputs
- Displaying robot state and environment information
- Providing feedback to the operator
- Managing UI modes and configurations

### 4. Communication Layer

**Purpose**: Simulates the network connection between operator and robot.

**Key Components**:
- **NetworkSimulator**: Simulates network conditions
- **Channels**: Separate channels for commands and state updates
- **Protocol Handlers**: Serialize/deserialize messages

**Interfaces**:
- `CommunicationInterface`: Defines how commands and states are transmitted
- Provides methods to send/receive commands and states

**Responsibilities**:
- Simulating realistic network conditions (latency, packet loss, bandwidth limits)
- Handling message serialization and transmission
- Managing communication queues and scheduling
- Implementing reliability mechanisms

## Data Flow

1. **Operator → Robot**:
   - Operator input → Command generation → Network transmission → Robot command reception → Command execution

2. **Robot → Operator**:
   - Robot state capture → Network transmission → Operator state reception → UI update

## Interface Stability

The interfaces between modules (`src/common/interfaces.py`) serve as the contract between components. These interfaces should remain stable to allow independent development:

- **Public interfaces** should change rarely and with careful coordination
- **Internal implementations** can change freely within each module
- **Version numbering** should reflect interface changes

## Extension Points

Each module provides extension points for future development:

1. **Simulation Engine**:
   - Adding new environment types
   - Integrating alternative physics engines
   - Adding new sensor types

2. **Robot Models**:
   - Adding new robot architectures
   - Implementing specialized controllers
   - Supporting additional robot capabilities

3. **Operator Interface**:
   - Adding new input devices
   - Creating specialized visualizations
   - Implementing alternative UI paradigms

4. **Communication Layer**:
   - Implementing alternative network protocols
   - Adding security features
   - Supporting distributed simulation

## Deployment Considerations

The system is designed to run in different configurations:

1. **Local Simulation**: All components run on a single machine
2. **Split Simulation**: Operator and robot run on separate machines
3. **Distributed Simulation**: Multiple robots and operators in a shared environment

## Development Guidelines

To maintain the modularity of the system:

1. **Respect module boundaries**: Don't bypass interfaces
2. **Focus on your module**: Each team member should focus on their assigned module
3. **Test independently**: Each module should have comprehensive tests
4. **Document interfaces**: All public interfaces must be well-documented
5. **Consider performance**: Be mindful of performance implications in your module 