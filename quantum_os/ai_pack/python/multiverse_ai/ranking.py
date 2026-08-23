from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


FEATURES = (
    "target_fit",
    "quantum_fidelity",
    "molecular_suitability",
    "synthetic_safety",
)


def synthetic_training_data(
    samples: int = 500, seed: int = 20260823
) -> tuple[np.ndarray, np.ndarray]:
    if samples < 20:
        raise ValueError("samples must be at least 20")
    generator = np.random.default_rng(seed)
    features = generator.uniform(0, 1, size=(samples, len(FEATURES)))
    interactions = features[:, 0] * features[:, 1]
    noise = generator.normal(0, 0.015, samples)
    labels = (
        0.31 * features[:, 0]
        + 0.29 * features[:, 1]
        + 0.16 * features[:, 2]
        + 0.19 * features[:, 3]
        + 0.05 * interactions
        + noise
    )
    return features, np.clip(labels, 0, 1)


@dataclass
class ExplainableRanker:
    alpha: float = 0.1
    seed: int = 20260823

    def fit(self, samples: int = 500) -> dict[str, float]:
        features, labels = synthetic_training_data(samples, self.seed)
        train_x, test_x, train_y, test_y = train_test_split(
            features, labels, test_size=0.2, random_state=self.seed
        )
        self.model = Ridge(alpha=self.alpha)
        self.model.fit(train_x, train_y)
        predictions = self.model.predict(test_x)
        return {
            "r2": float(r2_score(test_y, predictions)),
            "mae": float(mean_absolute_error(test_y, predictions)),
        }

    def explain(self, values: dict[str, float]) -> dict[str, object]:
        if not hasattr(self, "model"):
            raise RuntimeError("fit must be called before explain")
        vector = np.array([[float(values[name]) for name in FEATURES]])
        contributions = {
            name: float(value * coefficient)
            for name, value, coefficient in zip(
                FEATURES, vector[0], self.model.coef_
            )
        }
        return {
            "prediction": float(np.clip(self.model.predict(vector)[0], 0, 1)),
            "intercept": float(self.model.intercept_),
            "contributions": contributions,
            "primary_driver": max(
                contributions, key=lambda name: abs(contributions[name])
            ),
            "warning": (
                "Synthetic educational model; not biological or clinical evidence."
            ),
        }
