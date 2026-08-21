import math
from concurrent.futures import ThreadPoolExecutor

try:
    from .simulator import simulate
except ImportError:
    from simulator import simulate


TARGETS = ("D2", "5-HT2A", "NMDA", "M1")
DEFAULT_CANDIDATES = (
    {"id": "MV-QA17", "profile": (0.72, 0.81, 0.38, 0.44), "safety": 0.76},
    {"id": "MV-NX04", "profile": (0.58, 0.74, 0.69, 0.62), "safety": 0.68},
    {"id": "MV-SR22", "profile": (0.83, 0.57, 0.51, 0.35), "safety": 0.82},
    {"id": "MV-KT09", "profile": (0.46, 0.66, 0.77, 0.71), "safety": 0.72},
    {"id": "MV-PL31", "profile": (0.64, 0.78, 0.61, 0.55), "safety": 0.79},
)


def _validate_unit_interval(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")
    number = float(value)
    if not 0 <= number <= 1:
        raise ValueError(f"{field} must be between 0 and 1")
    return number


def _quantum_signature(profile: tuple[float, ...]) -> list[float]:
    gates = [
        {"gate": "RY", "qubit": index, "angle": value * math.pi}
        for index, value in enumerate(profile)
    ]
    gates.extend(
        {"gate": "CX", "control": index, "target": index + 1}
        for index in range(len(profile) - 1)
    )
    return simulate(len(profile), gates).probabilities


def _rank_candidate(
    candidate: dict[str, object], desired: tuple[float, ...], safety_weight: float
) -> dict[str, object]:
    profile = tuple(candidate["profile"])
    signature = _quantum_signature(profile)
    target_signature = _quantum_signature(desired)
    quantum_overlap = sum(
        math.sqrt(left * right)
        for left, right in zip(signature, target_signature)
    ) ** 2
    target_fit = 1 - sum(
        abs(actual - target) for actual, target in zip(profile, desired)
    ) / len(desired)
    safety = float(candidate["safety"])
    efficacy_weight = 1 - safety_weight
    score = efficacy_weight * (0.55 * target_fit + 0.45 * quantum_overlap)
    score += safety_weight * safety
    return {
        "id": candidate["id"],
        "score": round(score, 6),
        "target_fit": round(target_fit, 6),
        "quantum_overlap": round(quantum_overlap, 6),
        "safety": safety,
        "profile": dict(zip(TARGETS, profile)),
    }


def rank_candidates(data: object) -> dict[str, object]:
    if not isinstance(data, dict):
        raise ValueError("request body must be a JSON object")
    desired_data = data.get("desired_profile", {})
    if not isinstance(desired_data, dict):
        raise ValueError("desired_profile must be a JSON object")
    desired = tuple(
        _validate_unit_interval(desired_data.get(target, 0.5), target)
        for target in TARGETS
    )
    safety_weight = _validate_unit_interval(
        data.get("safety_weight", 0.35), "safety_weight"
    )

    with ThreadPoolExecutor(
        max_workers=len(DEFAULT_CANDIDATES), thread_name_prefix="drug-screen"
    ) as pool:
        ranked = list(
            pool.map(
                lambda candidate: _rank_candidate(
                    candidate, desired, safety_weight
                ),
                DEFAULT_CANDIDATES,
            )
        )
    ranked.sort(key=lambda candidate: candidate["score"], reverse=True)
    for rank, candidate in enumerate(ranked, start=1):
        candidate["rank"] = rank

    return {
        "candidates": ranked,
        "model": {
            "name": "Quantum-inspired multi-target ranking demo",
            "targets": list(TARGETS),
            "formula": (
                "(1-safety_weight) * (0.55*target_fit + "
                "0.45*quantum_overlap) + safety_weight*safety"
            ),
        },
        "disclaimer": (
            "Educational simulation using fictional compounds and synthetic "
            "scores. It does not predict efficacy, safety, or clinical outcomes."
        ),
    }


def rank_twin_profiles(data: object) -> dict[str, object]:
    if not isinstance(data, dict):
        raise ValueError("request body must be a JSON object")
    left = data.get("left")
    right = data.get("right")
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise ValueError("left and right profiles must be JSON objects")

    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="drug-twin") as pool:
        left_future = pool.submit(rank_candidates, left)
        right_future = pool.submit(rank_candidates, right)
        left_result = left_future.result()
        right_result = right_future.result()

    left_ranks = {
        candidate["id"]: candidate["rank"]
        for candidate in left_result["candidates"]
    }
    right_ranks = {
        candidate["id"]: candidate["rank"]
        for candidate in right_result["candidates"]
    }
    count = len(left_ranks)
    squared_rank_delta = sum(
        (left_ranks[candidate_id] - right_ranks[candidate_id]) ** 2
        for candidate_id in left_ranks
    )
    rank_correlation = (
        1 - (6 * squared_rank_delta) / (count * (count**2 - 1))
        if count > 1
        else 1.0
    )
    comparison = [
        {
            "id": candidate_id,
            "left_rank": left_ranks[candidate_id],
            "right_rank": right_ranks[candidate_id],
            "rank_delta": left_ranks[candidate_id] - right_ranks[candidate_id],
        }
        for candidate_id in left_ranks
    ]

    return {
        "left": left_result,
        "right": right_result,
        "comparison": {
            "rank_correlation": round(rank_correlation, 6),
            "same_leader": (
                left_result["candidates"][0]["id"]
                == right_result["candidates"][0]["id"]
            ),
            "candidates": comparison,
        },
        "disclaimer": left_result["disclaimer"],
    }
