import pandas as pd
import pytest

from backtester.signals.combine import combine_scores


def test_combine_scores_averages_columns() -> None:
    data = pd.DataFrame({"a_raw_score": [1.0, 2.0], "b_raw_score": [3.0, 4.0]})

    result = combine_scores(data, ["a_raw_score", "b_raw_score"])

    assert result["composite_raw_score"].tolist() == [2.0, 3.0]


def test_combine_scores_renormalizes_over_available_columns() -> None:
    # row 0 is missing a_raw_score -> composite should just be b_raw_score for
    # that row, not NaN, matching the guide's "renormalize among available".
    data = pd.DataFrame({"a_raw_score": [None, 2.0], "b_raw_score": [3.0, 4.0]})

    result = combine_scores(data, ["a_raw_score", "b_raw_score"])

    assert result["composite_raw_score"].tolist() == [3.0, 3.0]


def test_combine_scores_custom_output_column() -> None:
    data = pd.DataFrame({"a_raw_score": [1.0], "b_raw_score": [3.0]})

    result = combine_scores(data, ["a_raw_score", "b_raw_score"], output_column="my_signal")

    assert "my_signal" in result.columns
    assert "composite_raw_score" not in result.columns


def test_combine_scores_preserves_original_columns() -> None:
    data = pd.DataFrame({"a_raw_score": [1.0], "b_raw_score": [3.0]})

    result = combine_scores(data, ["a_raw_score", "b_raw_score"])

    assert result["a_raw_score"].tolist() == [1.0]
    assert result["b_raw_score"].tolist() == [3.0]


def test_raises_on_unknown_column() -> None:
    data = pd.DataFrame({"a_raw_score": [1.0]})

    with pytest.raises(ValueError, match="unknown column"):
        combine_scores(data, ["a_raw_score", "not_a_column"])
