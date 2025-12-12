"""
Initialise cutting (grazing/mowing) management.

Validates/normalises input dates and precomputes a fast per-day lookup mask
aligned to the simulation clock.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, Union, List

import numpy as np
import pandas as pd

from ..entities.cuttingManagement import CutMngtStruct

if TYPE_CHECKING:
    from aquacrop.entities.clockStruct import ClockStruct
    from aquacrop.entities.cuttingManagement import CuttingManagement
    from aquacrop.entities.paramStruct import ParamStruct


def _normalise_cut_dates(
    cut_dates: Sequence[Union[str, np.datetime64]],
    sim_start: pd.Timestamp,
    sim_end: pd.Timestamp,
    min_interval_days: int = 0,
) -> pd.DatetimeIndex:
    """
    Parse, sort, clip to bounds, and de-duplicate cut dates.
    """
    if cut_dates is None or len(cut_dates) == 0:
        return pd.DatetimeIndex([])

    dates = pd.to_datetime(list(cut_dates))
    dates = pd.DatetimeIndex(dates).normalize().sort_values()

    # Clip to simulation bounds (inclusive)
    dates = dates[(dates >= sim_start) & (dates <= sim_end)]

    # De-duplicate / enforce minimum interval
    if min_interval_days and min_interval_days > 0 and len(dates) > 0:
        filtered: List[pd.Timestamp] = []
        last_kept: pd.Timestamp | None = None
        for d in dates:
            if last_kept is None or (d - last_kept).days >= min_interval_days:
                filtered.append(d)
                last_kept = d
        dates = pd.DatetimeIndex(filtered)
    else:
        dates = dates.drop_duplicates()

    return dates


def read_cutting_management(
    param_struct: "ParamStruct",
    cut_mngt: "CuttingManagement | None",
    clock_struct: "ClockStruct",
) -> "ParamStruct":
    """
    Store cutting management variables as CutMngtStruct and precompute schedule.
    """
    sim_len = len(clock_struct.time_span)
    cut_struct = CutMngtStruct(sim_len)

    if cut_mngt is None:
        param_struct.CutMngt = cut_struct
        param_struct.FallowCutMngt = CutMngtStruct(sim_len)
        return param_struct

    if getattr(cut_mngt, "method", "fixed_dates") != "fixed_dates":
        raise ValueError("CuttingManagement.method must be 'fixed_dates' for now.")

    residual_cc = float(cut_mngt.residual_cc)
    remove_fraction = float(cut_mngt.remove_fraction)
    min_interval_days = int(getattr(cut_mngt, "min_interval_days", 0) or 0)

    if not (0.0 <= residual_cc <= 1.0):
        raise ValueError("CuttingManagement.residual_cc must be between 0 and 1.")
    if not (0.0 <= remove_fraction <= 1.0):
        raise ValueError("CuttingManagement.remove_fraction must be between 0 and 1.")
    if min_interval_days < 0:
        raise ValueError("CuttingManagement.min_interval_days must be >= 0.")

    sim_start = pd.Timestamp(clock_struct.simulation_start_date).normalize()
    sim_end = pd.Timestamp(clock_struct.simulation_end_date).normalize()

    dates = _normalise_cut_dates(
        cut_mngt.cut_dates, sim_start, sim_end, min_interval_days=min_interval_days
    )

    cut_mask = np.zeros(sim_len, dtype=bool)
    if len(dates) > 0:
        idx = clock_struct.time_span.get_indexer(dates)
        idx = idx[idx >= 0]
        cut_mask[idx] = True

    # Copy scalar settings into struct
    for a, v in cut_mngt.__dict__.items():
        if hasattr(cut_struct, a):
            setattr(cut_struct, a, v)

    cut_struct.residual_cc = residual_cc
    cut_struct.remove_fraction = remove_fraction
    cut_struct.min_interval_days = min_interval_days
    cut_struct.cut_mask = cut_mask

    param_struct.CutMngt = cut_struct
    param_struct.FallowCutMngt = CutMngtStruct(sim_len)

    return param_struct

