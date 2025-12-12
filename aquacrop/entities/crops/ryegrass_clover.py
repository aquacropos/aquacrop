"""
Minimal NZ pasture crop parameters (ryegrass + clover).

AquaCrop is fundamentally a single-crop model. This module provides a pragmatic
"effective crop" parameter set intended to approximate a perennial ryegrass
(Lolium perenne) + white clover (Trifolium repens) sward.

These defaults are deliberately minimal and are not presented as a validated
calibration. They are supplied so you can run a working baseline inside
AquaCrop-OSPy and then calibrate against local observations (canopy cover,
seasonal DM production, site-specific water stress response).
"""

# NOTE: Keys here match the attributes expected by aquacrop.entities.crop.Crop.
# Any keys not specified will fall back to the hard-coded defaults in Crop.__init__.

ryegrass_clover_params = {
    # Identity
    "Name": "RyegrassClover",

    # Crop classification
    # 1 = Leafy vegetable, 2 = Root/tuber, 3 = Fruit/grain
    # Pasture is best represented as "leafy" (harvestable product is biomass).
    "CropType": 1,
    "PlantMethod": 1,     # 0 transplanted, 1 sown
    "CalendarType": 2,    # 1 calendar days, 2 growing degree days

    # Phenology (GDD). Set very large senescence/maturity so growth continues
    # unless the user terminates via harvest_date or simulation end.
    "Emergence": 50,
    "MaxRooting": 800,
    "Senescence": 9999,
    "Maturity": 9999,

    # Yield/harvest index settings.
    # For a leafy crop, yield is effectively biomass.
    "HIini": 1.0,
    "HI0": 1.0,
    # Provide non-zero, safe defaults even if not used for CropType=1
    "HIstart": 0,
    "YldForm": 1,
    "Flowering": -999,

    # Harvest dry matter content (%). ~20% DM typical of pasture.
    "YldWC": 20,

    # Temperature response (cool-season C3 pasture)
    "Tbase": 3,
    "Tupp": 30,

    # Rooting depth (m)
    "Zmin": 0.3,
    "Zmax": 1.2,

    # Canopy development
    "CCx": 0.98,
    "CGC": 0.015,
    "CDC": 0.005,
    "CGC_CD": 0.015,
    "CDC_CD": 0.005,

    # Initial canopy at emergence is computed internally as:
    # CC0 = PlantPop * SeedSize * 1e-8
    # Use values that approximate an established sward rather than sparse seedlings.
    "SeedSize": 2.0,
    "PlantPop": 1_000_000,

    # Transpiration and biomass productivity
    "Kcb": 1.05,
    "fage": 0.15,
    "WP": 17.0,     # C3-like water productivity (g/m2)
    "WPy": 100,

    # Water stress thresholds (fractions of TAW depletion)
    "p_up1": 0.35,
    "p_lo1": 0.75,
    "p_up2": 0.55,
    "p_lo2": 0.85,
    "p_up3": 0.65,
    "p_lo3": 0.95,
    "p_up4": 0.75,
    "p_lo4": 1.0,

    # Shape factors for water stress response
    "fshape_w1": 2.5,
    "fshape_w2": 2.5,
    "fshape_w3": 2.5,
    "fshape_w4": 2.5,

    # Pasture is effectively indeterminate
    "Determinant": 0,
}

