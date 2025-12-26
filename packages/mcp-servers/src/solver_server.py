"""
Solver MCP Server
=================

Exposes neuro-symbolic solvers as MCP tools:
- BFS state-space search
- CP-SAT constraint solver
- Plan validation
"""

import json
from typing import Any
from dataclasses import dataclass, field
from enum import Enum


class SearchStrategy(str, Enum):
    BFS = "bfs"
    DFS = "dfs"
    ASTAR = "astar"


@dataclass
class State:
    """Represents a state in the search space."""
    data: dict[str, Any]
    cost: float = 0.0
    parent_action: str | None = None

    def __hash__(self):
        return hash(json.dumps(self.data, sort_keys=True))

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.data == other.data


@dataclass
class Action:
    """An action that transforms state."""
    name: str
    preconditions: dict[str, Any]
    effects: dict[str, Any]
    cost: float = 1.0

    def is_applicable(self, state: State) -> bool:
        """Check if action can be applied to state."""
        for key, expected in self.preconditions.items():
            if key not in state.data:
                return False
            if state.data[key] != expected:
                return False
        return True

    def apply(self, state: State) -> State:
        """Apply action to state, return new state."""
        new_data = state.data.copy()
        for key, value in self.effects.items():
            if callable(value):
                new_data[key] = value(new_data.get(key))
            else:
                new_data[key] = value
        return State(
            data=new_data,
            cost=state.cost + self.cost,
            parent_action=self.name,
        )


@dataclass
class Problem:
    """A search problem definition."""
    initial_state: State
    goal_conditions: dict[str, Any]
    actions: list[Action]

    def is_goal(self, state: State) -> bool:
        """Check if state satisfies goal conditions."""
        for key, expected in self.goal_conditions.items():
            if key not in state.data:
                return False
            if callable(expected):
                if not expected(state.data[key]):
                    return False
            elif state.data[key] != expected:
                return False
        return True


@dataclass
class SearchResult:
    """Result of a search operation."""
    success: bool
    plan: list[str] = field(default_factory=list)
    plan_cost: float = 0.0
    states_explored: int = 0
    final_state: dict[str, Any] = field(default_factory=dict)
    failure_reason: str | None = None


def bfs_search(problem: Problem, max_expansions: int = 100000) -> SearchResult:
    """
    Breadth-first search for optimal plans.

    Args:
        problem: The search problem to solve
        max_expansions: Maximum states to explore

    Returns:
        SearchResult with plan if found
    """
    from collections import deque

    # Track visited states and their paths
    visited: set[int] = set()
    # Queue of (state, path)
    queue: deque[tuple[State, list[str]]] = deque()
    queue.append((problem.initial_state, []))

    expansions = 0

    while queue and expansions < max_expansions:
        state, path = queue.popleft()
        state_hash = hash(state)

        if state_hash in visited:
            continue
        visited.add(state_hash)
        expansions += 1

        # Check goal
        if problem.is_goal(state):
            return SearchResult(
                success=True,
                plan=path,
                plan_cost=state.cost,
                states_explored=expansions,
                final_state=state.data,
            )

        # Expand
        for action in problem.actions:
            if action.is_applicable(state):
                new_state = action.apply(state)
                if hash(new_state) not in visited:
                    queue.append((new_state, path + [action.name]))

    return SearchResult(
        success=False,
        states_explored=expansions,
        failure_reason="No solution found" if expansions < max_expansions else "Expansion limit reached",
    )


def validate_plan(problem: Problem, plan: list[str]) -> tuple[bool, str]:
    """
    Validate that a plan achieves the goal.

    Args:
        problem: The problem definition
        plan: List of action names to execute

    Returns:
        (success, message) tuple
    """
    state = problem.initial_state
    action_map = {a.name: a for a in problem.actions}

    for i, action_name in enumerate(plan):
        if action_name not in action_map:
            return False, f"Unknown action at step {i}: {action_name}"

        action = action_map[action_name]
        if not action.is_applicable(state):
            return False, f"Action '{action_name}' not applicable at step {i}"

        state = action.apply(state)

    if problem.is_goal(state):
        return True, "Plan achieves goal"
    else:
        return False, f"Plan does not achieve goal. Final state: {state.data}"


# MCP Tool definitions (to be exposed via MCP server)
SOLVER_TOOLS = [
    {
        "name": "solve_bfs",
        "description": "Solve a state-space search problem using breadth-first search",
        "inputSchema": {
            "type": "object",
            "properties": {
                "initial_state": {"type": "object", "description": "Initial state as key-value pairs"},
                "goal_conditions": {"type": "object", "description": "Goal conditions as key-value pairs"},
                "actions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "preconditions": {"type": "object"},
                            "effects": {"type": "object"},
                            "cost": {"type": "number", "default": 1.0},
                        },
                        "required": ["name", "preconditions", "effects"],
                    },
                },
                "max_expansions": {"type": "integer", "default": 100000},
            },
            "required": ["initial_state", "goal_conditions", "actions"],
        },
    },
    {
        "name": "validate_plan",
        "description": "Validate that a plan achieves the goal",
        "inputSchema": {
            "type": "object",
            "properties": {
                "initial_state": {"type": "object"},
                "goal_conditions": {"type": "object"},
                "actions": {"type": "array"},
                "plan": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["initial_state", "goal_conditions", "actions", "plan"],
        },
    },
]


def handle_solve_bfs(params: dict) -> dict:
    """Handle solve_bfs tool call."""
    actions = [
        Action(
            name=a["name"],
            preconditions=a["preconditions"],
            effects=a["effects"],
            cost=a.get("cost", 1.0),
        )
        for a in params["actions"]
    ]

    problem = Problem(
        initial_state=State(data=params["initial_state"]),
        goal_conditions=params["goal_conditions"],
        actions=actions,
    )

    result = bfs_search(problem, params.get("max_expansions", 100000))

    return {
        "success": result.success,
        "plan": result.plan,
        "plan_cost": result.plan_cost,
        "states_explored": result.states_explored,
        "final_state": result.final_state,
        "failure_reason": result.failure_reason,
    }


def handle_validate_plan(params: dict) -> dict:
    """Handle validate_plan tool call."""
    actions = [
        Action(
            name=a["name"],
            preconditions=a["preconditions"],
            effects=a["effects"],
            cost=a.get("cost", 1.0),
        )
        for a in params["actions"]
    ]

    problem = Problem(
        initial_state=State(data=params["initial_state"]),
        goal_conditions=params["goal_conditions"],
        actions=actions,
    )

    success, message = validate_plan(problem, params["plan"])

    return {
        "valid": success,
        "message": message,
    }
