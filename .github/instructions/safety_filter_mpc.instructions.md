---
applyTo: '**'
---
# General Instructions for AI Code Generation

## Coding Style & Language
- Write modern, robust C++17 code.
- Follow ROS2 best practices.
- Use `Eigen3` for all linear algebra and vector/matrix operations.
- Private and protected class member variables MUST have a trailing underscore (e.g., `logger_`).
- Prefer `std::array` over raw C-style arrays for fixed-size data.
- Avoid raw pointers. Use `std::unique_ptr` and `std::shared_ptr` for memory management. Raw pointers are only acceptable when interfacing with C-APIs like Acados.

## Documentation
- All public classes and methods must have Doxygen-style comments explaining their purpose, parameters, and return values.
- Explain complex algorithms (like MPC formulation or data transformations) in a brief comment block.
- Use the google C++ style guide for all code contributions.

## Communication
- When answering questions about this codebase, please respond in German.
- Provide clear, concise code examples for any new implementation.