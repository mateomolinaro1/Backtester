import numpy as np
import pandas as pd
import pytest

from backtester.portfolio.types import LinearWeightMapping, TanhWeightMapping


def test_linear_mapping_is_identity() -> None:
    signal = pd.Series([-2.0, 0.0, 1.5])

    mapped = LinearWeightMapping().map(signal)

    pd.testing.assert_series_equal(mapped, signal)
    assert LinearWeightMapping().method_name == "linear"


def test_tanh_mapping_applies_kappa_scaled_tanh() -> None:
    signal = pd.Series([-2.0, 0.0, 1.5])

    mapped = TanhWeightMapping(kappa=2.0).map(signal)

    expected = np.tanh(2.0 * signal.to_numpy())
    np.testing.assert_allclose(mapped.to_numpy(), expected)
    assert TanhWeightMapping().method_name == "tanh"


def test_tanh_mapping_is_odd() -> None:
    signal = pd.Series([0.3, 1.1, 2.7])

    mapping = TanhWeightMapping(kappa=1.3)

    pd.testing.assert_series_equal(mapping.map(-signal), -mapping.map(signal))


def test_tanh_mapping_default_kappa_is_one() -> None:
    signal = pd.Series([1.0])

    mapped = TanhWeightMapping().map(signal)

    assert mapped.iloc[0] == pytest.approx(np.tanh(1.0))