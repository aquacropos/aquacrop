"""
Shared pytest fixtures and configuration for the AquaCrop-OSPy test suite.

Two things are centralised here so they don't have to be repeated in every
test module:

- The weather data is loaded once per session (the climate files are large),
   and exposed as fixtures.

Numerical outputs are compared with a tolerance rather than exact equality.
Different operating systems, Python versions, and numpy/BLAS builds produce
sub-ULP differences in floating-point reductions, which is what caused the
original exact-equality tests to fail intermittently across the CI matrix.
``MODEL_TOL`` absorbs that drift while still catching real regressions; use it
as ``value == pytest.approx(expected, **MODEL_TOL)``.
"""
import os


import pytest

from aquacrop import Soil
from aquacrop.utils import prepare_weather, get_filepath

# Relative tolerance of 0.1% with a small absolute floor for near-zero values.
MODEL_TOL = {"rel": 1e-3, "abs": 1e-3}


@pytest.fixture(scope="session")
def tunis_weather():
    """Tunis climate series (used by most Wheat scenarios)."""
    return prepare_weather(get_filepath("tunis_climate.txt"))


@pytest.fixture(scope="session")
def champion_weather():
    """Champion climate series (used by the Maize irrigation scenarios)."""
    return prepare_weather(get_filepath("champion_climate.txt"))


@pytest.fixture
def sandy_loam():
    """A fresh SandyLoam soil per test (the model can mutate soil state)."""
    return Soil(soil_type="SandyLoam")
