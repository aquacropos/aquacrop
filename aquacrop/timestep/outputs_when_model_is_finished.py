import pandas as pd


def outputs_when_model_is_finished(
    model_is_finished, flux_output, water_output, growth_outputs, steps_are_finished
):
    """
    Function that return the model output when model is finished.
    """
    if model_is_finished is True or steps_are_finished is True:
        # ClockStruct.step_start_time = ClockStruct.step_end_time
        # ClockStruct.step_end_time = ClockStruct.step_end_time + np.timedelta64(1, "D")
        flux_output_df = pd.DataFrame(
            flux_output,
            columns=[
                "time_step_counter",
                "season_counter",
                "dap",
                "Wr",
                "z_gw",
                "surface_storage",
                "IrrDay",
                "Infl",
                "Runoff",
                "DeepPerc",
                "CR",
                "GwIn",
                "Es",
                "EsPot",
                "Tr",
                "TrPot",
            ],
        )

        water_output_df = pd.DataFrame(
            water_output,
            columns=["time_step_counter", "growing_season", "dap"]
            + ["th" + str(i) for i in range(1, water_output.shape[1] - 2)],
        )

        growth_outputs_df = pd.DataFrame(
            growth_outputs,
            columns=[
                "time_step_counter",
                "season_counter",
                "dap",
                "gdd",
                "gdd_cum",
                "z_root",
                "canopy_cover",
                "canopy_cover_ns",
                "biomass",
                "biomass_ns",
                "harvest_index",
                "harvest_index_adj",
                "yield_",
            ],
        )

        return flux_output_df, water_output_df, growth_outputs_df

    return False
