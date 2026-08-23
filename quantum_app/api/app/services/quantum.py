import math

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity


def encode_profile(profile: tuple[float, ...]) -> Statevector:
    circuit = QuantumCircuit(len(profile))
    for qubit, value in enumerate(profile):
        circuit.ry(math.pi * value, qubit)
    for qubit in range(len(profile) - 1):
        circuit.cx(qubit, qubit + 1)
    return Statevector.from_instruction(circuit)


def profile_fidelity(
    candidate_profile: tuple[float, ...], target_profile: tuple[float, ...]
) -> float:
    candidate_state = encode_profile(candidate_profile)
    target_state = encode_profile(target_profile)
    return float(state_fidelity(candidate_state, target_state))
