from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from blueqat import Circuit
from blueqat.gate import Measurement
from mcp.server.fastmcp import FastMCP

MAX_GATES = 500
MAX_QUBITS = 20
MAX_SHOTS = 10_000

GATE_SIGNATURES = {
    "h": (1, 0),
    "x": (1, 0),
    "y": (1, 0),
    "z": (1, 0),
    "s": (1, 0),
    "t": (1, 0),
    "rx": (1, 1),
    "ry": (1, 1),
    "rz": (1, 1),
    "phase": (1, 1),
    "cx": (2, 0),
    "cz": (2, 0),
    "swap": (2, 0),
    "ccx": (3, 0),
}

mcp = FastMCP(
    "Blueqat",
    instructions=(
        "Build and simulate constrained Blueqat quantum circuits. "
        "Only documented gate objects are accepted; Python code is never executed."
    ),
)


def _validate_index(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("Every target must be a non-negative integer.")
    if value < 0:
        raise ValueError("Every target must be a non-negative integer.")
    return value


def _validate_number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Gate parameters must be finite numbers.")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Gate parameters must be finite numbers.")
    return number


def build_circuit(gates: Sequence[dict[str, Any]], qubits: int | None = None) -> Circuit:
    if not isinstance(gates, list):
        raise ValueError("gates must be a JSON array.")
    if len(gates) > MAX_GATES:
        raise ValueError(f"A circuit may contain at most {MAX_GATES} gates.")

    normalized: list[tuple[str, list[int], list[float]]] = []
    largest_target = -1
    for position, gate in enumerate(gates):
        if not isinstance(gate, dict):
            raise ValueError(f"Gate {position} must be an object.")
        name_value = gate.get("gate")
        if not isinstance(name_value, str):
            raise ValueError(f"Gate {position} requires a string 'gate' field.")
        name = name_value.lower()

        targets_value = gate.get("targets")
        params_value = gate.get("params", [])
        if not isinstance(targets_value, list) or not isinstance(params_value, list):
            raise ValueError(f"Gate {position} targets and params must be arrays.")

        targets = [_validate_index(value) for value in targets_value]
        params = [_validate_number(value) for value in params_value]
        if name == "measure":
            if not targets or params:
                raise ValueError("measure requires at least one target and no params.")
        elif name in GATE_SIGNATURES:
            target_count, param_count = GATE_SIGNATURES[name]
            if len(targets) != target_count or len(params) != param_count:
                raise ValueError(
                    f"{name} requires {target_count} targets and {param_count} params."
                )
            if len(set(targets)) != len(targets):
                raise ValueError(f"{name} targets must be distinct.")
        else:
            allowed = ", ".join([*GATE_SIGNATURES, "measure"])
            raise ValueError(f"Unsupported gate '{name}'. Allowed gates: {allowed}.")

        largest_target = max(largest_target, *targets)
        normalized.append((name, targets, params))

    inferred_qubits = largest_target + 1
    if qubits is None:
        qubits = inferred_qubits
    if isinstance(qubits, bool) or not isinstance(qubits, int):
        raise ValueError("qubits must be an integer.")
    if qubits < inferred_qubits or qubits < 1 or qubits > MAX_QUBITS:
        raise ValueError(
            f"qubits must cover every target and be between 1 and {MAX_QUBITS}."
        )

    circuit = Circuit(qubits)
    for name, targets, params in normalized:
        selector: int | tuple[int, ...]
        selector = targets[0] if len(targets) == 1 else tuple(targets)
        if name == "measure":
            circuit.m[selector]
        elif params:
            getattr(circuit, name)(*params)[selector]
        else:
            getattr(circuit, name)[selector]
    return circuit


def _counts(circuit: Circuit, shots: int) -> dict[str, int]:
    measured = circuit.copy()
    if not any(isinstance(operation, Measurement) for operation in measured.ops):
        measured.m[:]
    result = measured.run(backend="numpy", shots=shots)
    return dict(sorted(result.items()))


@mcp.tool()
def simulate_circuit(
    gates: list[dict[str, Any]], shots: int = 1024, qubits: int | None = None
) -> dict[str, Any]:
    """Run a Blueqat circuit and return measurement counts and OpenQASM 2.

    Each gate is an object such as {"gate":"h","targets":[0]} or
    {"gate":"rx","targets":[0],"params":[1.5708]}. If no measure gate is
    supplied, all qubits are measured. shots must be from 1 through 10000.
    """
    if isinstance(shots, bool) or not isinstance(shots, int):
        raise ValueError("shots must be an integer.")
    if shots < 1 or shots > MAX_SHOTS:
        raise ValueError(f"shots must be between 1 and {MAX_SHOTS}.")

    circuit = build_circuit(gates, qubits)
    return {
        "backend": "numpy",
        "qubits": circuit.n_qubits,
        "shots": shots,
        "counts": _counts(circuit, shots),
        "qasm": circuit.to_qasm(),
    }


@mcp.tool()
def circuit_statevector(
    gates: list[dict[str, Any]], qubits: int | None = None
) -> dict[str, Any]:
    """Return the Blueqat statevector before measurement.

    Measurement gates are rejected because a deterministic pre-measurement
    statevector is returned.
    """
    if any(
        isinstance(gate, dict) and str(gate.get("gate", "")).lower() == "measure"
        for gate in gates
    ):
        raise ValueError("Statevector circuits cannot contain measure gates.")
    circuit = build_circuit(gates, qubits)
    vector = circuit.run(backend="numpy")
    amplitudes = [
        {
            "basis": format(index, f"0{circuit.n_qubits}b"),
            "real": value.real,
            "imag": value.imag,
        }
        for index, value in enumerate(vector)
        if abs(value) > 1e-12
    ]
    return {
        "backend": "numpy",
        "qubits": circuit.n_qubits,
        "amplitudes": amplitudes,
        "qasm": circuit.to_qasm(),
    }


@mcp.tool()
def export_qasm(
    gates: list[dict[str, Any]], qubits: int | None = None
) -> dict[str, Any]:
    """Validate a circuit and export it as OpenQASM 2."""
    circuit = build_circuit(gates, qubits)
    return {"qubits": circuit.n_qubits, "qasm": circuit.to_qasm()}


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
