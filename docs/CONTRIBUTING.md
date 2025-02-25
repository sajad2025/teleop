# Contributing to Teleop Simulation

Thank you for your interest in contributing to the Teleop Simulation project! This document provides guidelines and best practices for contributing to the codebase.

## Code Organization

The project is organized into four main modules:

1. **Simulation Engine** (`src/simulation/`)
2. **Robot Models** (`src/robots/`)
3. **Operator Interface** (`src/operator/`)
4. **Communication Layer** (`src/communication/`)

Each module has its own team lead and responsibility area. When making changes, focus on your assigned module to minimize conflicts with other teams.

## Development Workflow

1. **Create a Branch**
   
   Always create a new branch for your work based on the current `main`:
   
   ```bash
   git checkout main
   git pull
   git checkout -b feature/your-feature-name
   ```
   
   Use prefixes like `feature/`, `bugfix/`, `enhancement/`, etc., to indicate the type of change.

2. **Make Focused Changes**
   
   Keep your changes focused on a single task. This makes reviewing and merging easier.

3. **Follow Coding Standards**
   
   - Follow PEP 8 guidelines for Python code
   - Use type hints consistently
   - Document your code with docstrings (Google style)
   - Add relevant unit tests for new functionality

4. **Run Tests Locally**
   
   Before submitting, run tests to ensure your changes don't break existing functionality:
   
   ```bash
   python -m pytest tests/
   ```

5. **Create a Pull Request**
   
   Push your branch and create a pull request (PR) to merge into `main`:
   
   ```bash
   git push -u origin feature/your-feature-name
   ```
   
   Then create a PR via GitHub/GitLab/etc.

## Interface Stability

The interfaces defined in `src/common/interfaces.py` are the contract between modules. Changing these interfaces requires coordination across teams:

1. **Discuss First**: Propose interface changes in team meetings or issues.
2. **Deprecation**: For breaking changes, add deprecation warnings first.
3. **Version Bumping**: Update the module version when changing interfaces.

## Code Review Guidelines

When reviewing PRs, focus on:

1. **Correctness**: Does the code do what it's supposed to?
2. **Testing**: Are there appropriate tests?
3. **Interface Compliance**: Does it adhere to the defined interfaces?
4. **Documentation**: Is the code well-documented?
5. **Performance**: Are there any obvious performance issues?

## Module-Specific Guidelines

### Simulation Engine
- Use vectorized operations for performance when possible
- Maintain deterministic behavior for reproducibility
- Document physics assumptions and limitations

### Robot Models
- Separate kinematics/dynamics from control logic
- Document coordinate frames clearly
- Include visualization helpers for debugging

### Operator Interface
- Prioritize usability and responsiveness
- Use consistent UI patterns
- Handle errors gracefully with user feedback

### Communication Layer
- Test with various network conditions
- Document protocol changes thoroughly
- Include timeout handling and recovery mechanisms

## Getting Help

If you're stuck or have questions:

1. Check existing documentation in the `docs/` directory
2. Reach out to your module's team lead
3. Create an issue for architectural questions

Thank you for following these guidelines and contributing to the project! 