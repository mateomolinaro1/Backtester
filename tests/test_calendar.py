import pandas as pd
import pytest

from backtester.calendar import align_to_calendar


def _dates(n: int, start: str = "2020-01-01") -> pd.DatetimeIndex:
    return pd.bdate_range(start, periods=n)


def test_gap_within_tolerance_is_filled() -> None:
    calendar = _dates(30)
    series = pd.Series(0.0001, index=calendar.delete([10, 11]))

    result, report = align_to_calendar(series, calendar, max_ffill=5)

    assert result.notna().all()
    assert result.iloc[10] == pytest.approx(0.0001)
    assert result.iloc[11] == pytest.approx(0.0001)
    assert report.n_calendar_dates == 30
    assert report.n_missing_before_fill == 2
    assert report.n_filled == 2
    assert report.n_missing_after_fill == 0


def test_gap_beyond_tolerance_stays_null() -> None:
    calendar = _dates(30)
    # 6 consecutive missing rows exceeds max_ffill=5.
    series = pd.Series(0.0001, index=calendar.delete([10, 11, 12, 13, 14, 15]))

    result, report = align_to_calendar(series, calendar, max_ffill=5)

    assert result.iloc[10:15].notna().all()  # first 5 filled
    assert pd.isna(result.iloc[15])  # 6th exceeds the limit
    assert report.n_filled == 5
    assert report.n_missing_after_fill == 1


def test_fill_uses_last_available_prior_value() -> None:
    calendar = _dates(10)
    series = pd.Series([0.01, 0.02], index=[calendar[0], calendar[3]])
    # calendar[1], calendar[2] missing entirely -- should fill from calendar[0]'s value.

    result, _ = align_to_calendar(series, calendar, max_ffill=5)

    assert result.iloc[1] == pytest.approx(0.01)
    assert result.iloc[2] == pytest.approx(0.01)
    assert result.iloc[3] == pytest.approx(0.02)


def test_no_prior_value_to_fill_from_stays_null() -> None:
    calendar = _dates(10)
    series = pd.Series(0.01, index=calendar[3:])  # nothing before calendar[3]

    result, report = align_to_calendar(series, calendar, max_ffill=5)

    assert result.iloc[:3].isna().all()  # no prior value exists to fill from
    assert report.n_missing_after_fill == 3


def test_max_ffill_none_disables_filling() -> None:
    calendar = _dates(10)
    series = pd.Series(0.01, index=calendar.delete([3]))

    result, report = align_to_calendar(series, calendar, max_ffill=None)

    assert pd.isna(result.iloc[3])
    assert report.n_filled == 0
    assert report.n_missing_after_fill == 1


def test_max_ffill_zero_disables_filling() -> None:
    calendar = _dates(10)
    series = pd.Series(0.01, index=calendar.delete([3]))

    result, report = align_to_calendar(series, calendar, max_ffill=0)

    assert pd.isna(result.iloc[3])
    assert report.n_filled == 0


def test_series_already_fully_covering_calendar_is_unaffected() -> None:
    calendar = _dates(10)
    series = pd.Series(range(10), index=calendar, dtype=float)

    result, report = align_to_calendar(series, calendar, max_ffill=5)

    pd.testing.assert_series_equal(result, series, check_names=False)
    assert report.n_missing_before_fill == 0
    assert report.n_filled == 0


def test_raises_when_series_not_datetime_indexed() -> None:
    calendar = _dates(5)
    series = pd.Series([0.01] * 5)  # RangeIndex, not DatetimeIndex

    with pytest.raises(ValueError, match="series must be indexed by date"):
        align_to_calendar(series, calendar)


def test_raises_on_duplicate_dates_in_series() -> None:
    calendar = _dates(5)
    series = pd.Series(0.01, index=calendar.insert(0, calendar[0]))

    with pytest.raises(ValueError, match="series has duplicate dates"):
        align_to_calendar(series, calendar)