# AquaCrop-OSPy

Soil-Crop-Water model based on AquaCrop-OS.

![checks](https://badgen.net/github/checks/aquacropos/aquacrop)
![release](https://badgen.net/github/release/aquacropos/aquacrop)
![last-commit](https://badgen.net/github/last-commit/aquacropos/aquacrop)
![license](https://badgen.net/pypi/license/aquacrop)
![python-version](https://badgen.net/pypi/python/aquacrop)
[![image](https://pepy.tech/badge/aquacrop)](https://pepy.tech/project/aquacrop)
[![Downloads](https://pepy.tech/badge/aquacrop/month)](https://pepy.tech/project/aquacrop)


```python
from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent
from aquacrop.utils import prepare_weather, get_filepath

weather_file_path = get_filepath('tunis_climate.txt')
model_os = AquaCropModel(
            sim_start_time=f"{1979}/10/01",
            sim_end_time=f"{1985}/05/30",
            weather_df=prepare_weather(weather_file_path),
            soil=Soil(soil_type='SandyLoam'),
            crop=Crop('Wheat', planting_date='10/01'),
            initial_water_content=InitialWaterContent(value=['FC']),
        )
model_os.run_model(till_termination=True)
model_results = model_os.get_simulation_results().head()
print(model_results)
```

## About

AquaCrop-OSPy is an open-source Python crop-water model developed by Tim Foster and others (Tom Kelly and Chris Bowden) within the Agriculture, Water and Climate research group at the University of Manchester. The AquaCrop-OSPy code has been developed with support from the the University of Manchester, Daugherty Water for Food Global Institute, Imperial College London, along with input from the United Nations Food and Agriculture Organization's (FAO) AquaCrop Core Development Group. 

Please note that AquaCrop-OSPy is not an official implementation or version of the FAO AquaCrop model. AquaCrop-OSPy currently mirrors most features available in version 7.1 of the official FAO AquaCrop model, with the exception of routines for salinity and fertility stress, weed management, and perennial herbaceous crops that are still to be developed. AquaCrop-OSPy has been rigorously tested to verify that the model reproduces accurately the calculations and outputs performed by the official FAO AquaCrop model. However, some bugs or errors may still be found. Please use the Issues tab to raise any issues encountered with the AquaCrop-OSPy. More details about the official FAO AquaCrop model on which AquaCrop-OSPy is based can be obtained <a href=https://www.fao.org/aquacrop> here </a>.

For further information about the AquaCrop-OSPy model, you can consult the accompanying open-access journal paper on the code <a href=https://doi.org/10.1016/j.agwat.2021.106976> here </a>. 
There is also an extensive <a href=https://aquacropos.github.io/aquacrop/>documentation </a> for the model, along with a series of tutorials to help you get started with the Python code (see Quickstart below). AquaCrop-OSPy builds upon an earlier version of code developed in Matlab, more information about which can be found <a href=https://doi.org/10.1016/j.agwat.2016.11.015> here </a>. 

More information about the official FAO AquaCrop model on which AquaCrop-OSPy is based can be obtained <a href=https://www.fao.org/aquacrop> here </a>, where you can also access the official raw source AquaCrop code, compiled executables, and most recent code releases that are developed and provided by FAO.

## Install

```bash
pip install aquacrop
```

## Quickstart

A number of tutorials has been created (more to be added in future) to help users jump straight in and run their first simulation. Run these tutorials instantly on Google Colab:

1.  <a href=https://colab.research.google.com/github/aquacropos/aquacrop/blob/master/docs/notebooks/AquaCrop_OSPy_Notebook_1.ipynb>Running an AquaCrop-OSPy model</a>
2.  <a href=https://colab.research.google.com/github/aquacropos/aquacrop/blob/master/docs/notebooks/AquaCrop_OSPy_Notebook_2.ipynb>Estimation of irrigation water demands</a>
3.  <a href=https://colab.research.google.com/github/aquacropos/aquacrop/blob/master/docs/notebooks/AquaCrop_OSPy_Notebook_3.ipynb>Optimisation of irrigation management strategies</a>
4.  <a href=https://colab.research.google.com/github/aquacropos/aquacrop/blob/master/docs/notebooks/AquaCrop_OSPy_Notebook_4.ipynb>Projection of climate change impacts</a>


## Installation troubleshooting
If you receive an error message such as "No module named aquacrop.scripts.initiate_library" or "ModuleNotFoundError: No module named 'aquacrop.solution.solution_root_zone_water'", please try the following troubleshooting steps:

1. Run "python -m aquacrop.scripts.initiate_library" in your terminal, if this generates an error such as "RuntimeError: Attempted to compile AOT function without the compiler used by numpy.distutils present. Cannot find suitable msvc.", then you need to download and install an MSVC compiler such as the one included in Visual Studio build tools (see https://www.youtube.com/watch?v=p_R3tXSq0KI).

2. If Step 1 doesn't help, then you can run aquacrop in development mode using the code below. This will turn off some function compilation, resulting in minor increases in runtime: <br>
```import os```<br>
```os.environ['DEVELOPMENT'] = 'DEVELOPMENT'```
