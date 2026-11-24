# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Fit and replay a cost prediction against declared numeric features."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import polars as pl


def _matrix(observations: pl.DataFrame, features: tuple[str, ...]) -> np.ndarray:
    if (
        not features
        or len(features) != len(set(features))
        or any(
            name not in observations.schema
            or not observations.schema[name].is_numeric()
            for name in features
        )
    ):
        raise ValueError("Prediction requires distinct numeric feature columns")
    data = observations.select(features).to_numpy().astype(np.float64)
    if not np.isfinite(data).all():
        raise ValueError("Prediction inputs must be finite and nonmissing")
    return np.column_stack((np.ones(observations.height), data))


@dataclass(frozen=True)
class CostModel:
    """A fitted linear model with stable feature order and response identity."""

    features: tuple[str, ...]
    response: str
    coefficients: tuple[float, ...]

    def predict(self, observations: pl.DataFrame) -> pl.Series:
        """Return a cost projection for every input row in its original order."""
        values = _matrix(observations, self.features) @ np.asarray(self.coefficients)
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError(
                "Model predicts a nonfinite or negative cost for the supplied rows"
            )
        return pl.Series(f"predicted_{self.response}", values)


def fit_cost_model(
    observations: pl.DataFrame, *, features: tuple[str, ...], response: str
) -> CostModel:
    """Fit an identifiable intercept and slope for each declared feature."""
    if (
        response in features
        or response not in observations.schema
        or not observations.schema[response].is_numeric()
    ):
        raise ValueError(
            "The numeric cost response must be separate from fitted features"
        )
    matrix = _matrix(observations, features)
    cost = observations[response].to_numpy().astype(np.float64)
    if not np.isfinite(cost).all() or (cost < 0).any():
        raise ValueError("Training costs must be finite, nonnegative and nonmissing")
    coefficients, _, rank, _ = np.linalg.lstsq(matrix, cost, rcond=None)
    if rank != matrix.shape[1] or observations.height <= matrix.shape[1]:
        raise ValueError(
            "Training data must identify the model with residual degrees of freedom"
        )
    return CostModel(features, response, tuple(float(value) for value in coefficients))
