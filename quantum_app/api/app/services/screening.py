from app.services.molecular import (
    CANDIDATES,
    calculate_descriptors,
    molecular_suitability,
)
from app.services.quantum import profile_fidelity


DISCLAIMER = (
    "Educational simulation with fictional identifiers and synthetic labels. "
    "It does not predict efficacy, safety, or clinical outcomes."
)


def _rank_condition(
    target_profile: tuple[float, ...], safety_weight: float
) -> dict[str, list[dict]]:
    ranked = []
    for candidate in CANDIDATES:
        descriptors = calculate_descriptors(candidate.smiles)
        quantum_fidelity = profile_fidelity(candidate.profile, target_profile)
        target_fit = 1 - sum(
            abs(actual - target)
            for actual, target in zip(candidate.profile, target_profile)
        ) / len(target_profile)
        suitability = molecular_suitability(descriptors)
        efficacy_weight = 1 - safety_weight
        contributions = {
            "target_fit": 0.35 * efficacy_weight * target_fit,
            "quantum_fidelity": 0.35 * efficacy_weight * quantum_fidelity,
            "molecular_suitability": 0.10 * efficacy_weight * suitability,
            "safety": 0.20 * safety_weight * candidate.safety,
        }
        ranked.append(
            {
                "id": candidate.id,
                "score": round(sum(contributions.values()), 6),
                "quantum_fidelity": round(quantum_fidelity, 6),
                "descriptors": descriptors,
                "explanation": {
                    name: round(value, 6)
                    for name, value in contributions.items()
                },
            }
        )
    ranked.sort(key=lambda item: item["score"], reverse=True)
    for rank, candidate in enumerate(ranked, start=1):
        candidate["rank"] = rank
    return {"candidates": ranked}


def screen_twin(
    alpha_profile: tuple[float, ...],
    beta_profile: tuple[float, ...],
    alpha_safety: float,
    beta_safety: float,
) -> dict:
    alpha = _rank_condition(alpha_profile, alpha_safety)
    beta = _rank_condition(beta_profile, beta_safety)
    alpha_ranks = {
        candidate["id"]: candidate["rank"] for candidate in alpha["candidates"]
    }
    beta_ranks = {
        candidate["id"]: candidate["rank"] for candidate in beta["candidates"]
    }
    alpha_order = [alpha_ranks[candidate.id] for candidate in CANDIDATES]
    beta_order = [beta_ranks[candidate.id] for candidate in CANDIDATES]
    count = len(alpha_order)
    squared_differences = sum(
        (alpha_rank - beta_rank) ** 2
        for alpha_rank, beta_rank in zip(alpha_order, beta_order)
    )
    rho = 1 - (6 * squared_differences) / (count * (count**2 - 1))
    return {
        "alpha": alpha,
        "beta": beta,
        "comparison": {
            "spearman_rho": round(rho, 6),
            "same_leader": (
                alpha["candidates"][0]["id"] == beta["candidates"][0]["id"]
            ),
        },
    }
