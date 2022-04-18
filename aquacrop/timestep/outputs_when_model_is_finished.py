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
                "DAP",
                "Wr",
                "zGW",
                "SurfaceStorage",
                "IrrDay",
                "Infl",
                "Runoff",
                "DeepPerc",
                "CR",
                "GwIn",
                "Es",
                "EsPot",
                "Tr",
                "P",
            ],
        )

        water_output_df = pd.DataFrame(
            water_output,
            columns=["time_step_counter", "GrowingSeason", "DAP"]
            + ["th" + str(i) for i in range(1, water_output.shape[1] - 2)],
        )

        growth_outputs_df = pd.DataFrame(
            growth_outputs,
            columns=[
                "time_step_counter",
                "season_counter",
                "DAP",
                "GDD",
                "GDDcum",
                "Zroot",
                "CC",
                "CC_NS",
                "B",
                "B_NS",
                "HI",
                "HIadj",
                "Y",
            ],
        )

        return flux_output_df, water_output_df, growth_outputs_df

    return flux_output, water_output, growth_outputs
