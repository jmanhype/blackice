"""
Solvers
=======

State-space search and constraint solvers for validation.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from collections import deque


@dataclass
class State:
    """A state in the search space."""
    data: dict[str, Any]
    cost: float = 0.0

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
    preconditions: Callable[[State], bool]
    effects: Callable[[State], State]
    cost: float = 1.0


@dataclass
class SearchResult:
    """Result of a search."""
    success: bool
    plan: list[str] = field(default_factory=list)
    cost: float = 0.0
    states_explored: int = 0
    final_state: Optional[State] = None
    failure_reason: Optional[str] = None


class BFSSolver:
    """
    Breadth-first search solver.

    Guarantees optimal solutions for uniform-cost problems.
    """

    def __init__(self, max_expansions: int = 100000):
        self.max_expansions = max_expansions

    def solve(
        self,
        initial: State,
        goal: Callable[[State], bool],
        actions: list[Action],
    ) -> SearchResult:
        """
        Solve a search problem.

        Args:
            initial: Starting state
            goal: Function that returns True if state is a goal
            actions: Available actions

        Returns:
            SearchResult with plan if found
        """
        visited: set[int] = set()
        queue: deque[tuple[State, list[str], float]] = deque()
        queue.append((initial, [], 0.0))

        expansions = 0

        while queue and expansions < self.max_expansions:
            state, path, cost = queue.popleft()
            state_hash = hash(state)

            if state_hash in visited:
                continue
            visited.add(state_hash)
            expansions += 1

            if goal(state):
                return SearchResult(
                    success=True,
                    plan=path,
                    cost=cost,
                    states_explored=expansions,
                    final_state=state,
                )

            for action in actions:
                if action.preconditions(state):
                    new_state = action.effects(state)
                    new_cost = cost + action.cost
                    if hash(new_state) not in visited:
                        queue.append((new_state, path + [action.name], new_cost))

        return SearchResult(
            success=False,
            states_explored=expansions,
            failure_reason="No solution found" if expansions < self.max_expansions else "Expansion limit",
        )


class CPSATSolver:
    """
    Constraint programming solver using OR-Tools CP-SAT.

    For complex constraint satisfaction problems.
    """

    def __init__(self, time_limit_seconds: int = 60):
        self.time_limit = time_limit_seconds
        self._model = None
        self._solver = None

    def _init_solver(self):
        """Initialize the CP-SAT solver."""
        try:
            from ortools.sat.python import cp_model
            self._model = cp_model.CpModel()
            self._solver = cp_model.CpSolver()
            self._solver.parameters.max_time_in_seconds = self.time_limit
            return True
        except ImportError:
            return False

    def solve_scheduling(
        self,
        tasks: list[dict],
        constraints: list[dict],
    ) -> SearchResult:
        """
        Solve a scheduling problem.

        Args:
            tasks: List of {"name": str, "duration": int, "deadline": int}
            constraints: List of {"type": "before", "task1": str, "task2": str}

        Returns:
            SearchResult with schedule
        """
        if not self._init_solver():
            return SearchResult(
                success=False,
                failure_reason="OR-Tools not installed",
            )

        from ortools.sat.python import cp_model

        # Create variables
        horizon = sum(t["duration"] for t in tasks) + max(t.get("deadline", 0) for t in tasks)
        task_vars = {}

        for task in tasks:
            name = task["name"]
            duration = task["duration"]
            start = self._model.NewIntVar(0, horizon, f"start_{name}")
            end = self._model.NewIntVar(0, horizon, f"end_{name}")
            interval = self._model.NewIntervalVar(start, duration, end, f"interval_{name}")
            task_vars[name] = {"start": start, "end": end, "interval": interval}

            # Deadline constraint
            if "deadline" in task:
                self._model.Add(end <= task["deadline"])

        # Add constraints
        for constraint in constraints:
            if constraint["type"] == "before":
                t1 = constraint["task1"]
                t2 = constraint["task2"]
                self._model.Add(task_vars[t1]["end"] <= task_vars[t2]["start"])

        # Minimize makespan
        all_ends = [task_vars[t["name"]]["end"] for t in tasks]
        makespan = self._model.NewIntVar(0, horizon, "makespan")
        self._model.AddMaxEquality(makespan, all_ends)
        self._model.Minimize(makespan)

        # Solve
        status = self._solver.Solve(self._model)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            schedule = []
            for task in tasks:
                name = task["name"]
                start = self._solver.Value(task_vars[name]["start"])
                schedule.append({"task": name, "start": start})

            schedule.sort(key=lambda x: x["start"])

            return SearchResult(
                success=True,
                plan=[s["task"] for s in schedule],
                cost=self._solver.ObjectiveValue(),
                final_state=State(data={"schedule": schedule}),
            )

        return SearchResult(
            success=False,
            failure_reason="No feasible schedule found",
        )

    def solve_allocation(
        self,
        items: list[dict],
        bins: list[dict],
    ) -> SearchResult:
        """
        Solve a bin packing / resource allocation problem.

        Args:
            items: List of {"name": str, "size": int}
            bins: List of {"name": str, "capacity": int}

        Returns:
            SearchResult with allocation
        """
        if not self._init_solver():
            return SearchResult(
                success=False,
                failure_reason="OR-Tools not installed",
            )

        from ortools.sat.python import cp_model

        # Assignment variables: x[i][b] = 1 if item i is in bin b
        x = {}
        for item in items:
            for bin_ in bins:
                x[item["name"], bin_["name"]] = self._model.NewBoolVar(
                    f"x_{item['name']}_{bin_['name']}"
                )

        # Each item in exactly one bin
        for item in items:
            self._model.Add(
                sum(x[item["name"], bin_["name"]] for bin_ in bins) == 1
            )

        # Bin capacity constraints
        for bin_ in bins:
            self._model.Add(
                sum(
                    item["size"] * x[item["name"], bin_["name"]]
                    for item in items
                ) <= bin_["capacity"]
            )

        # Solve
        status = self._solver.Solve(self._model)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            allocation = {bin_["name"]: [] for bin_ in bins}
            for item in items:
                for bin_ in bins:
                    if self._solver.Value(x[item["name"], bin_["name"]]):
                        allocation[bin_["name"]].append(item["name"])
                        break

            return SearchResult(
                success=True,
                final_state=State(data={"allocation": allocation}),
            )

        return SearchResult(
            success=False,
            failure_reason="No feasible allocation found",
        )
