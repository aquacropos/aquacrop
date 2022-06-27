from subprocess import call


def compile_all_AOT_files():
    """
    Numba AOT compile functions to improve speed
    
    """
    try:
        from ..solution.solution_aeration_stress import aeration_stress
        from ..solution.solution_water_stress import water_stress
        from ..solution.solution_evap_layer_water_content import (
            evap_layer_water_content,
        )
        from ..solution.solution_root_zone_water import root_zone_water
        from ..solution.solution_cc_development import cc_development
        from ..solution.solution_update_CCx_CDC import update_CCx_CDC
        from ..solution.solution_cc_required_time import cc_required_time
        from ..solution.solution_temperature_stress import temperature_stress
        from ..solution.solution_HIadj_pre_anthesis import HIadj_pre_anthesis
        from ..solution.solution_HIadj_post_anthesis import HIadj_post_anthesis
        from ..solution.solution_HIadj_pollination import HIadj_pollination
        from ..solution.solution_growing_degree_day import growing_degree_day
        from ..solution.solution_drainage import drainage
        from ..solution.solution_rainfall_partition import rainfall_partition
        from ..solution.solution_check_groundwater_table import check_groundwater_table
        from ..solution.solution_soil_evaporation import soil_evaporation
        from ..solution.solution_root_development import root_development
        from ..solution.solution_infiltration import infiltration
        from ..solution.solution_HIref_current_day import HIref_current_day
        from ..solution.solution_biomass_accumulation import biomass_accumulation

    except:
        print("\033[1;32m Compiling modules... This could take some time.")
        print(
            " Note: The compilation is only necessary the first time that the library is used."
        )
        call(["python", "-m", "aquacrop.scripts.initiate_library"])
