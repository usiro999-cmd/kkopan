import cmath
import math
import random
from dataclasses import dataclass


MAX_QUBITS = 8

SINGLE_QUBIT_GATES = {
    "H": (
        (1 / math.sqrt(2), 1 / math.sqrt(2)),
        (1 / math.sqrt(2), -1 / math.sqrt(2)),
    ),
    "X": ((0, 1), (1, 0)),
    "Y": ((0, -1j), (1j, 0)),
    "Z": ((1, 0), (0, -1)),
    "S": ((1, 0), (0, 1j)),
    "T": ((1, 0), (0, cmath.exp(1j * math.pi / 4))),
}


@dataclass(frozen=True)
class SimulationResult:
    amplitudes: list[complex]
    probabilities: list[float]


def _validate_qubit(qubit: object, num_qubits: int, field: str = "qubit") -> int:
    if isinstance(qubit, bool) or not isinstance(qubit, int):
        raise ValueError(f"{field} must be an integer")
    if not 0 <= qubit < num_qubits:
        raise ValueError(f"{field} must be between 0 and {num_qubits - 1}")
    return qubit


def _apply_single_qubit_gate(
    state: list[complex],
    qubit: int,
    matrix: tuple[tuple[complex, complex], tuple[complex, complex]],
) -> None:
    mask = 1 << qubit
    for index in range(len(state)):
        if index & mask:
            continue
        paired = index | mask
        zero, one = state[index], state[paired]
        state[index] = matrix[0][0] * zero + matrix[0][1] * one
        state[paired] = matrix[1][0] * zero + matrix[1][1] * one


def _rotation_y(angle: float) -> tuple[tuple[float, float], tuple[float, float]]:
    half = angle / 2
    return ((math.cos(half), -math.sin(half)), (math.sin(half), math.cos(half)))


def _apply_cnot(state: list[complex], control: int, target: int) -> None:
    control_mask = 1 << control
    target_mask = 1 << target
    for index in range(len(state)):
        if index & control_mask and not index & target_mask:
            paired = index | target_mask
            state[index], state[paired] = state[paired], state[index]


def simulate(num_qubits: int, gates: list[dict[str, object]]) -> SimulationResult:
    if isinstance(num_qubits, bool) or not isinstance(num_qubits, int):
        raise ValueError("num_qubits must be an integer")
    if not 1 <= num_qubits <= MAX_QUBITS:
        raise ValueError(f"num_qubits must be between 1 and {MAX_QUBITS}")
    if not isinstance(gates, list):
        raise ValueError("gates must be a list")

    state = [0j] * (1 << num_qubits)
    state[0] = 1 + 0j

    for gate in gates:
        if not isinstance(gate, dict):
            raise ValueError("each gate must be an object")
        name = gate.get("gate")
        if not isinstance(name, str):
            raise ValueError("gate name must be a string")
        name = name.upper()

        if name in SINGLE_QUBIT_GATES:
            qubit = _validate_qubit(gate.get("qubit"), num_qubits)
            _apply_single_qubit_gate(state, qubit, SINGLE_QUBIT_GATES[name])
        elif name == "RY":
            qubit = _validate_qubit(gate.get("qubit"), num_qubits)
            angle = gate.get("angle")
            if isinstance(angle, bool) or not isinstance(angle, (int, float)):
                raise ValueError("RY angle must be a number")
            _apply_single_qubit_gate(state, qubit, _rotation_y(float(angle)))
        elif name == "CX":
            control = _validate_qubit(gate.get("control"), num_qubits, "control")
            target = _validate_qubit(gate.get("target"), num_qubits, "target")
            if control == target:
                raise ValueError("CX control and target must be different")
            _apply_cnot(state, control, target)
        else:
            raise ValueError(f"unsupported gate: {name}")

    probabilities = [abs(amplitude) ** 2 for amplitude in state]
    return SimulationResult(state, probabilities)


def sample_measurements(
    probabilities: list[float], num_qubits: int, shots: int = 1024
) -> dict[str, int]:
    if not 1 <= shots <= 100_000:
        raise ValueError("shots must be between 1 and 100000")
    outcomes = random.choices(range(len(probabilities)), weights=probabilities, k=shots)
    counts: dict[str, int] = {}
    for outcome in outcomes:
        label = format(outcome, f"0{num_qubits}b")
        counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items()))
