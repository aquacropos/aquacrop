"""
Model run lifecycle tests.

Consolidates what were previously six separate files:
  test_model_till_termination.py, test_model_step_finished.py,
  test_model_step_not_finished.py, test_model_step_less_than_1.py,
  test_model_not_running.py, and test_speed.py.

All exercise an AquaCrop model built on the Tunis Wheat setup, run either to
termination or for a fixed number of steps. Each scenario is built and run once
via a module-scoped fixture, then asserted against from several small tests.
"""
import time

import pytest

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent
from .conftest import MODEL_TOL

NOT_RUN_MESSAGE = (
    "You cannot get results without running the model. "
    "Please execute the run_model() method."
)


def _build_model(weather, soil, sim_start, sim_end):
    return AquaCropModel(
        sim_start_time=sim_start,
        sim_end_time=sim_end,
        weather_df=weather,
        soil=soil,
        crop=Crop("Wheat", planting_date="10/01"),
        initial_water_content=InitialWaterContent(value=["FC"]),
    )


# ---------------------------------------------------------------------------
# Run to termination (was test_model_till_termination.py + test_speed.py)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def till_termination_model(tunis_weather):
    soil = Soil(soil_type="SandyLoam")
    model = _build_model(tunis_weather, soil, "1979/10/01", "1980/05/30")
    model.run_model(till_termination=True)
    return model


class TestRunTillTermination:
    def test_final_statistics(self, till_termination_model):
        final_statistics = till_termination_model.get_simulation_results().head()
        assert final_statistics["Dry yield (tonne/ha)"][0] == pytest.approx(8.94, **MODEL_TOL)

    def test_crop_growth(self, till_termination_model):
        crop_growth = till_termination_model.get_crop_growth().head()
        assert crop_growth["gdd"][4] == pytest.approx(22.5, **MODEL_TOL)
        assert crop_growth["gdd_cum"][4] == pytest.approx(104, **MODEL_TOL)

    def test_water_flux(self, till_termination_model):
        water_flux = till_termination_model.get_water_flux().head()
        assert water_flux["Wr"][4] == pytest.approx(57.56, **MODEL_TOL)
        assert water_flux["EsPot"][4] == pytest.approx(3.96, **MODEL_TOL)

    def test_water_storage(self, till_termination_model):
        water_storage = till_termination_model.get_water_storage().head()
        assert water_storage["th1"][3] == pytest.approx(0.146497, **MODEL_TOL)

    def test_additional_information(self, till_termination_model):
        info = till_termination_model.get_additional_information()
        assert info["has_model_finished"] is True

    def test_speed(self, tunis_weather, sandy_loam):
        """Smoke test that a full run completes (was test_speed.py)."""
        model = _build_model(tunis_weather, sandy_loam, "1979/10/01", "1980/05/30")
        start = time.time()
        model.run_model(till_termination=True)
        elapsed = time.time() - start
        assert model.get_additional_information()["has_model_finished"] is True
        assert elapsed < 60  # generous ceiling; mainly guards against hangs


# ---------------------------------------------------------------------------
# Stepping with enough steps to finish (was test_model_step_finished.py)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def step_finished_model(tunis_weather):
    soil = Soil(soil_type="SandyLoam")
    model = _build_model(tunis_weather, soil, "1982/10/01", "1983/05/30")
    model.run_model(num_steps=5000)
    return model


class TestRunByStepFinished:
    def test_final_statistics(self, step_finished_model):
        final_statistics = step_finished_model.get_simulation_results().head()
        assert final_statistics["Dry yield (tonne/ha)"][0] == pytest.approx(8.81, **MODEL_TOL)

    def test_crop_growth(self, step_finished_model):
        crop_growth = step_finished_model.get_crop_growth().head()
        assert crop_growth["gdd"][4] == pytest.approx(19, **MODEL_TOL)
        assert crop_growth["gdd_cum"][4] == pytest.approx(106.35, **MODEL_TOL)

    def test_water_flux(self, step_finished_model):
        water_flux = step_finished_model.get_water_flux().head()
        assert water_flux["Wr"][4] == pytest.approx(56.06, **MODEL_TOL)
        assert water_flux["EsPot"][4] == pytest.approx(4.29, **MODEL_TOL)

    def test_water_storage(self, step_finished_model):
        water_storage = step_finished_model.get_water_storage().head()
        assert water_storage["th1"][3] == pytest.approx(0.146171, **MODEL_TOL)

    def test_additional_information(self, step_finished_model):
        info = step_finished_model.get_additional_information()
        assert info["has_model_finished"] is True


# ---------------------------------------------------------------------------
# Stepping that stops early (was test_model_step_not_finished.py)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def step_unfinished_model(tunis_weather):
    soil = Soil(soil_type="SandyLoam")
    model = _build_model(tunis_weather, soil, "1979/10/01", "1980/05/30")
    model.run_model(num_steps=3, process_outputs=True)
    return model


class TestRunByStepNotFinished:
    def test_final_statistics_is_false(self, step_unfinished_model):
        assert step_unfinished_model.get_simulation_results() is False

    def test_crop_growth(self, step_unfinished_model):
        crop_growth = step_unfinished_model.get_crop_growth().head()
        assert crop_growth["gdd"][2] == pytest.approx(20, **MODEL_TOL)
        assert crop_growth["gdd_cum"][4] == pytest.approx(0.0, **MODEL_TOL)

    def test_water_flux(self, step_unfinished_model):
        water_flux = step_unfinished_model.get_water_flux().head()
        assert water_flux["Wr"][2] == pytest.approx(59.98, **MODEL_TOL)
        assert water_flux["EsPot"][2] == pytest.approx(3.19, **MODEL_TOL)

    def test_water_storage(self, step_unfinished_model):
        water_storage = step_unfinished_model.get_water_storage().head()
        assert water_storage["th1"][2] == pytest.approx(0.16, **MODEL_TOL)

    def test_additional_information(self, step_unfinished_model):
        info = step_unfinished_model.get_additional_information()
        assert info["has_model_finished"] is False


# ---------------------------------------------------------------------------
# Error paths (was test_model_step_less_than_1.py + test_model_not_running.py)
# ---------------------------------------------------------------------------
class TestRunErrors:
    def test_num_steps_less_than_1_raises(self, tunis_weather, sandy_loam):
        model = _build_model(tunis_weather, sandy_loam, "1979/10/01", "1980/05/30")
        with pytest.raises(Exception) as excinfo:
            model.run_model(num_steps=-1)
        assert "num_steps must be equal to or greater than 1." in str(excinfo.value)

    @pytest.mark.parametrize("getter", [
        "get_simulation_results",
        "get_crop_growth",
        "get_water_storage",
        "get_water_flux",
        "get_additional_information",
    ])
    def test_getters_raise_before_running(self, tunis_weather, sandy_loam, getter):
        model = _build_model(tunis_weather, sandy_loam, "1980/10/01", "1981/05/30")
        with pytest.raises(Exception) as excinfo:
            getattr(model, getter)()
        assert NOT_RUN_MESSAGE in str(excinfo.value)
