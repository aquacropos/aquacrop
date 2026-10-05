# Manual / exploratory scripts

These files are **not** part of the automated test suite and are not collected
by pytest (`tests/manual` is excluded in `pytest.ini`). They are kept for
reference and interactive exploration.

- `custom_crop_testing.ipynb`, `datetime_tests.ipynb`,
  `v7_Comparison_exercises.ipynb` — exploratory notebooks.
- `custom_soil_testing.py`, `groundwater_testing.py`, `off_season_testing.py` —
  plotting / exploration scripts (they print and draw figures, they do not
  assert). If a specific expected behaviour from one of these should be
  guaranteed, promote it into a real assertion-based test under `tests/`.
- `fshape_r_testing.py`, `scratch.py` — small scratch calculations.
- `pytest_testing.py` — superseded by `tests/test_irrigation.py`
  (`test_rainfed_strategy` covers the same Maize rainfed scenario).
- `brussels_future.txt` — climate data used by the comparison notebook.
