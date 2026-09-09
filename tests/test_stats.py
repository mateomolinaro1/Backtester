import pandas as pd

from backtester.stats import cross_sectional_median_mad


def test_median_and_mad_computed_per_group() -> None:
    series = pd.Series([1.0, 3.0, 5.0, 100.0, 200.0, 300.0])
    groups = pd.Series(["a", "a", "a", "b", "b", "b"])

    median, mad = cross_sectional_median_mad(series, groups)

    # group "a": median=3, |1-3|=2, |3-3|=0, |5-3|=2 -> MAD = median(2,0,2) = 2
    assert median.iloc[:3].tolist() == [3.0, 3.0, 3.0]
    assert mad.iloc[:3].tolist() == [2.0, 2.0, 2.0]
    # group "b": median=200, MAD = median(100,0,100) = 100
    assert median.iloc[3:].tolist() == [200.0, 200.0, 200.0]
    assert mad.iloc[3:].tolist() == [100.0, 100.0, 100.0]


def test_mad_is_zero_when_all_values_identical() -> None:
    series = pd.Series([5.0, 5.0, 5.0])
    groups = pd.Series(["a", "a", "a"])

    _, mad = cross_sectional_median_mad(series, groups)

    assert (mad == 0).all()
