# UBEM
This is an urban building energy model scripted in Python.


This model is developed under the reasech project for "Activity-Based Urban Building and Mobility Energy Modeling (UBMEM) for Planning of Future Cities" funded by the Swedish Energy Agency.

UBEM.py is a collection of functions and classes which can be used for modeling and simulation of buildings at different spatial and temporal resolutions.

The model is going to be published in:

[1] F. Johari, F. Shadram, J. Widén, Urban building energy modeling from geo-referenced energy performance certificate data: Development, calibration, and validation, 2023.

Any academic or educational use of the model should cite [1], for corporate use, contact Fatemeh Johari at fatemeh.johari@angstrom.uu.se

Requirements

To run the model, make sure that the required tools and packages are already installed on your computer.

1.EnergyPlus: https://github.com/NREL/EnergyPlus/releases/tag/v9.2.0

Python (you can use Anaconda and Spyder to run the model): https://www.anaconda.com/products/distribution
3.EPPY: https://pypi.org/project/eppy/

4.geopandas: https://geopandas.org/en/stable/getting_started.html

5.shapely: https://pypi.org/project/shapley/

After the installation is completed, open the "UBEM.py" file and run the codes.

If the model starts running, you should be able to see this on the consol:

SIMULATION IS RUNNING ...

Building 0 / 82

C:\EnergyPlusV9-2-0\energyplus.exe --weather X:\UBEM\input_data\SWE_Stockholm.Arlanda.024600_IWEC.epw --output-directory X:\UBEM --idd C:/EnergyPlusV9-2-0/Energy+.idd X:\UBEM\in.idf *

It is going to take about a few seconds to run the simulation for each building. In the given example file, there are 82 buildings.

After the simulation is completed, an excel file with all the results can be found in the results folder.
