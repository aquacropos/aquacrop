"""
Cutting (grazing/mowing) management entity.

This mirrors the existing management-entity pattern (e.g. IrrigationManagement,
FieldMngt), but is tailored for multi-cut pasture within a single season.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence, Optional, Union

import numpy as np


@dataclass
class CuttingManagement:
    """
    Defines a cutting/grazing schedule within a continuous growing season.

    Parameters
    ----------
    method : str
        Scheduling method. Minimal version supports "fixed_dates" only.
    cut_dates : Sequence[Union[str, np.datetime64]]
        Dates on which cuts occur.
    residual_cc : float
        Canopy cover remaining after cutting (0..1).
    remove_fraction : float
        Fraction of standing above-ground biomass removed (0..1).
    reset_regrowth : bool
        If True, reset regrowth counters so phenology restarts.
    min_interval_days : int
        Minimum spacing between cuts. Used to de-duplicate messy schedules.
    export_as_yield : bool
        If True, add removed biomass to DryYield accumulator.
    """

    method: str = "fixed_dates"
    cut_dates: Sequence[Union[str, np.datetime64]] = field(default_factory=list)
    residual_cc: float = 0.2
    remove_fraction: float = 0.5
    reset_regrowth: bool = True
    min_interval_days: int = 0
    export_as_yield: bool = False


class CutMngtStruct:
    """
    Numba-friendly cutting management container.
    """

    def __init__(self, sim_len: int):
        self.method = "fixed_dates"
        self.cut_mask = np.zeros(sim_len, dtype=bool)
        self.residual_cc = 0.0
        self.remove_fraction = 0.0
        self.reset_regrowth = False
        self.min_interval_days = 0
        self.export_as_yield = False

