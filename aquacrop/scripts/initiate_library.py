from subprocess import call
from tqdm import tqdm

modules_to_compile = [
    "aquacrop.solution.water_stress",
    "aquacrop.solution.evap_layer_water_content",
    "aquacrop.solution.root_zone_water",
    "aquacrop.solution.cc_development",
    "aquacrop.solution.update_CCx_CDC",
    "aquacrop.solution.cc_required_time",
    "aquacrop.solution.aeration_stress",
    "aquacrop.solution.HIadj_pre_anthesis",
    "aquacrop.solution.HIadj_post_anthesis",
    "aquacrop.solution.HIadj_pollination",
    "aquacrop.solution.growing_degree_day",
    "aquacrop.solution.drainage",
    "aquacrop.solution.rainfall_partition",
    "aquacrop.solution.check_groundwater_table",
    "aquacrop.solution.soil_evaporation",
    "aquacrop.solution.root_development",
    "aquacrop.solution.infiltration",
    "aquacrop.solution.HIref_current_day",
    "aquacrop.solution.temperature_stress",
    "aquacrop.solution.biomass_accumulation"]

for mod in tqdm(modules_to_compile):
    call(["python", "-m", mod])