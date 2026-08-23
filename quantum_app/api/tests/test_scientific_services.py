import pytest

from app.services.molecular import calculate_descriptors
from app.services.quantum import profile_fidelity
from app.services.screening import screen_twin


def test_rdkit_descriptors_are_calculated():
    descriptors = calculate_descriptors("CCO")
    assert descriptors["molecular_weight"] > 40
    assert descriptors["h_bond_donors"] == 1


def test_qiskit_fidelity_is_one_for_same_profile():
    profile = (0.4, 0.6, 0.5, 0.7)
    assert profile_fidelity(profile, profile) == pytest.approx(1.0)


def test_twin_screening_ranks_all_candidates():
    result = screen_twin(
        (0.65, 0.75, 0.60, 0.55),
        (0.45, 0.60, 0.80, 0.70),
        0.35,
        0.60,
    )
    assert len(result["alpha"]["candidates"]) == 5
    assert result["alpha"]["candidates"][0]["rank"] == 1
    assert -1 <= result["comparison"]["spearman_rho"] <= 1
