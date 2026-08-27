import math

import pytest

from blueqat_mcp.server import build_circuit, circuit_statevector, simulate_circuit


BELL_GATES = [
    {"gate": "h", "targets": [0]},
    {"gate": "cx", "targets": [0, 1]},
]


def test_bell_statevector() -> None:
    result = circuit_statevector(BELL_GATES)

    assert result["qubits"] == 2
    assert [entry["basis"] for entry in result["amplitudes"]] == ["00", "11"]
    assert all(
        math.isclose(entry["real"], 1 / math.sqrt(2), rel_tol=1e-7)
        for entry in result["amplitudes"]
    )


def test_bell_shots_only_contain_correlated_results() -> None:
    result = simulate_circuit(BELL_GATES, shots=200)

    assert set(result["counts"]) <= {"00", "11"}
    assert sum(result["counts"].values()) == 200


def test_rejects_unsupported_gate() -> None:
    with pytest.raises(ValueError, match="Unsupported gate"):
        build_circuit([{"gate": "custom", "targets": [0]}])


def test_rejects_excessive_qubits() -> None:
    with pytest.raises(ValueError, match="between 1 and 20"):
        build_circuit([{"gate": "x", "targets": [20]}])
