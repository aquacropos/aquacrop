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

AquaCrop-OSPy is a python implementation of the popular crop-water model AquaCrop, built from the AquaCrop-OS source code. 

AquaCrop-OS, an open source version of FAO’s multi-crop model, was released in August 2016 and is the result of collaboration between researchers at the University of Manchester, Water for Food Global Institute, U.N. Food and Agriculture Organization, and Imperial College London.

AquaCrop-OSPy has been designed in way that users can conduct cutting edge research with only basic python experience. In particular for the design and testing of irrigation stratgeies.

AquaCrop-OSPy is currently up to date with AquaCrop FAO version 6.0, with exception of some features not yet included in Python code (salinity and fertility stress, and weed management)

Open access journal article <a href=https://doi.org/10.1016/j.agwat.2021.106976> here </a>

It is built upon the AquaCropOS crop-growth model written in Matlab (<a href=https://doi.org/10.1016/j.agwat.2016.11.015> paper </a>, <a href=https://www.aquacropos.com/> webpage </a>) which itself itself is based on the FAO AquaCrop model <a href=http://www.fao.org/aquacrop/en/>Webpage </a>. Comparisons to both base models are shown <a href=https://aquacropos.github.io/aquacrop/comparison.html> here. </a>

A <a href=https://github.com/aquacropos/aquacrop/discussions>forum </a> has also been created so that users of AquaCrop-OSPy and AquaCrop-OS can discuss research, bugs and future development.

There is also an extensive <a href=https://aquacropos.github.io/aquacrop/>documentation </a> for the model

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

2. If Step 1 doesn't help, then you can run aquacrop in pure python (this will be slower) using: <br>
```import os```<br>
```os.environ['DEVELOPMENT'] = 'DEVELOPMENT'```

More information, including screenshots and gifs, can be found at The University of Manchester's [article](https://www.manchester.ac.uk/discover/news/manchester-scientists-launch-new-interactive-tool-for-agricultural-water-management-and-climate-risk-assessment/), Tim Foster's medium [post](https://medium.com/@agwater/aquaplan-a-new-interactive-tool-for-agricultural-water-management-and-climate-risk-assessment-82c50cb10144), or twitter [thread](https://twitter.com/tim_foster_88/status/1557728807758737408).

A seperate [category](https://github.com/aquacropos/aquacrop/discussions/categories/aquaplan) inside the AquaCrop-OSPy forum has been created to discuss
AquaPlan, including any issues, questions, or suggestions.

