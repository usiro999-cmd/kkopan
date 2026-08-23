from multiverse_ai import ExplainableRanker


ranker = ExplainableRanker()
metrics = ranker.fit()
print("Validation metrics:", metrics)
print(
    ranker.explain(
        {
            "target_fit": 0.82,
            "quantum_fidelity": 0.91,
            "molecular_suitability": 0.68,
            "synthetic_safety": 0.74,
        }
    )
)
