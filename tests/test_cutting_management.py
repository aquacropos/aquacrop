"""
Tests for CuttingManagement scheduling and cut application.
"""

import os
import unittest

import numpy as np
import pandas as pd

os.environ["DEVELOPMENT"] = "True"

from aquacrop.initialize.read_clocks_parameters import read_clock_parameters
from aquacrop.initialize.read_cutting_management import read_cutting_management
from aquacrop.entities.paramStruct import ParamStruct
from aquacrop.entities.cuttingManagement import CuttingManagement, CutMngtStruct
from aquacrop.entities.initParamVariables import InitialCondition
from aquacrop.timestep.apply_cutting import apply_cutting

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent


class TestCuttingManagement(unittest.TestCase):
    def test_schedule_parsing_sorts_clips_and_dedupes(self):
        clock = read_clock_parameters("2000/01/01", "2000/01/10")
        param_struct = ParamStruct()

        cut_mngt = CuttingManagement(
            cut_dates=[
                "2000/01/05",
                "1999/12/31",  # out of range
                "2000/01/03",
                "2000/01/03",  # duplicate
            ],
            min_interval_days=1,
        )

        param_struct = read_cutting_management(param_struct, cut_mngt, clock)
        mask = param_struct.CutMngt.cut_mask

        self.assertEqual(int(mask.sum()), 2)
        # Expected indices: 2000-01-03 (idx=2) and 2000-01-05 (idx=4)
        self.assertTrue(mask[2])
        self.assertTrue(mask[4])

    def test_apply_cut_transform_and_reset(self):
        new_cond = InitialCondition(num_comp=1)
        new_cond.biomass = 200.0
        new_cond.biomass_ns = 250.0
        new_cond.canopy_cover = 0.8
        new_cond.canopy_cover_ns = 0.9
        new_cond.dap = 15
        new_cond.gdd_cum = 300.0
        new_cond.delayed_cds = 2
        new_cond.delayed_gdds = 5
        new_cond.age_days = 10
        new_cond.age_days_ns = 9
        new_cond.ccx_act = 0.9
        new_cond.ccx_w = 0.9
        new_cond.DryYield = 1.0

        cut_struct = CutMngtStruct(sim_len=1)
        cut_struct.remove_fraction = 0.5
        cut_struct.residual_cc = 0.2
        cut_struct.reset_regrowth = True
        cut_struct.export_as_yield = True

        updated, removed = apply_cutting(new_cond, cut_struct, True)

        self.assertAlmostEqual(removed, 100.0)
        self.assertAlmostEqual(updated.biomass, 100.0)
        self.assertAlmostEqual(updated.biomass_ns, 125.0)
        self.assertAlmostEqual(updated.canopy_cover, 0.2)
        self.assertAlmostEqual(updated.canopy_cover_ns, 0.2)
        self.assertEqual(updated.dap, 0)
        self.assertEqual(updated.gdd_cum, 0)
        self.assertEqual(updated.delayed_cds, 0)
        self.assertEqual(updated.delayed_gdds, 0)
        self.assertEqual(updated.age_days, 0)
        self.assertEqual(updated.age_days_ns, 0)
        self.assertAlmostEqual(updated.DryYield, 2.0)  # +1 t/ha from removed biomass

    def test_regrowth_and_yield_accumulation_integration(self):
        sim_start = "2000/01/01"
        sim_end = "2000/02/15"
        dates = pd.date_range(sim_start, sim_end, freq="D")
        weather = pd.DataFrame(
            {
                "MinTemp": 10.0,
                "MaxTemp": 20.0,
                "Precipitation": 0.0,
                "ReferenceET": 3.0,
                "Date": dates,
            }
        )

        soil = Soil(soil_type="SandyLoam")
        crop = Crop("NZPasture", planting_date="01/01", harvest_date="12/31")
        iwc = InitialWaterContent(value=["FC"])

        cuts = CuttingManagement(
            cut_dates=["2000/01/10", "2000/01/20"],
            residual_cc=0.2,
            remove_fraction=0.5,
            reset_regrowth=True,
            export_as_yield=True,
        )

        model = AquaCropModel(
            sim_start_time=sim_start,
            sim_end_time=sim_end,
            weather_df=weather,
            soil=soil,
            crop=crop,
            initial_water_content=iwc,
            cutting_management=cuts,
        )
        model.run_model(till_termination=True)

        growth = model.get_crop_growth()

        idx1 = (pd.to_datetime("2000/01/10") - pd.to_datetime(sim_start)).days
        idx2 = (pd.to_datetime("2000/01/20") - pd.to_datetime(sim_start)).days

        def val_at(idx, col):
            return float(growth.loc[growth.time_step_counter == idx, col].iloc[0])

        cc1 = val_at(idx1, "canopy_cover")
        cc2 = val_at(idx2, "canopy_cover")
        cc2_prev = val_at(idx2 - 1, "canopy_cover")

        self.assertAlmostEqual(cc1, 0.2, places=6)
        self.assertAlmostEqual(cc2, 0.2, places=6)
        self.assertGreater(cc2_prev, cc2)

        # Regrowth should increase canopy after first cut
        self.assertGreater(val_at(idx1 + 2, "canopy_cover"), cc1)
        # After second cut, canopy should persist (not reset to zero)
        self.assertGreater(val_at(idx2 + 1, "canopy_cover"), 0.0)

        # DryYield accumulator should increase on cut days
        self.assertGreater(val_at(idx1, "DryYield"), val_at(idx1 - 1, "DryYield"))
        self.assertGreater(val_at(idx2, "DryYield"), val_at(idx2 - 1, "DryYield"))


if __name__ == "__main__":
    unittest.main()
