#!/usr/bin/env python3
"""
BLACKICE Quick Start Example

Demonstrates dispatching tasks to different backends.
"""

import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from integrations.dispatcher import Dispatcher, Task, Backend


def main():
    dispatcher = Dispatcher()

    print("=" * 60)
    print("BLACKICE Dispatcher Demo")
    print("=" * 60)

    # Example 1: Optimization problem → ai-factory
    print("\n[1] Optimization Problem")
    task1 = Task(
        description="Optimize warehouse layout to minimize travel time",
        task_type="optimization",
        inputs={"warehouse_id": "WH-001", "constraints": ["aisle_width >= 3m"]},
    )
    result1 = dispatcher.dispatch(task1)
    print(f"    Description: {task1.description}")
    print(f"    Dispatched to: {result1.backend.value}")
    print(f"    Output: {result1.output}")

    # Example 2: Feature specification → speckit
    print("\n[2] Feature Specification")
    task2 = Task(
        description="Specify a new payment processing feature with Stripe integration",
        task_type="feature",
        inputs={"priority": "P1"},
    )
    result2 = dispatcher.dispatch(task2)
    print(f"    Description: {task2.description}")
    print(f"    Dispatched to: {result2.backend.value}")
    print(f"    Output: {result2.output}")

    # Example 3: Code generation → LLM
    print("\n[3] Code Generation")
    task3 = Task(
        description="Generate a Python class for handling API rate limiting",
        task_type="generation",
        inputs={"language": "python", "framework": "fastapi"},
    )
    result3 = dispatcher.dispatch(task3)
    print(f"    Description: {task3.description}")
    print(f"    Dispatched to: {result3.backend.value}")
    print(f"    Output: {result3.output}")

    # Example 4: Explicit backend hint
    print("\n[4] Explicit Backend (forced to ai-factory)")
    task4 = Task(
        description="Generate test data",  # Would normally go to LLM
        task_type="generation",
        inputs={},
        backend_hint=Backend.AI_FACTORY,  # Force deterministic
    )
    result4 = dispatcher.dispatch(task4)
    print(f"    Description: {task4.description}")
    print(f"    Dispatched to: {result4.backend.value} (forced)")

    print("\n" + "=" * 60)
    print("The dispatcher routes tasks based on:")
    print("  - Keywords in description")
    print("  - Task type")
    print("  - Explicit backend hints")
    print("=" * 60)


if __name__ == "__main__":
    main()
