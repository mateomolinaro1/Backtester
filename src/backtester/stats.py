"""Shared cross-sectional statistics helpers.

Used by both outlier treatment and signal scoring, which both need the same
robust median/MAD computation grouped by date -- extracted here once it was
actually needed in two places, not preemptively.
"""

from __future__ import annotations

import pandas as pd

#: Consistency scaling factor making MAD comparable to the standard deviation
#: under Gaussianity (1 / Phi^-1(0.75)).
MAD_SCALE = 1.4826


def cross_sectional_median_mad(series: pd.Series, groups: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Per-group median and MAD (median absolute deviation from that median),
    broadcast back to each row's group -- i.e. ``result[i]`` is the statistic for
    the group ``groups[i]`` belongs to, not a single scalar.
    """
    median = series.groupby(groups).transform("median")
    mad = (series - median).abs().groupby(groups).transform("median")
    return median, mad
