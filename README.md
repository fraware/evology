# Evolutionary market ecology

### Testing 

![Runs](https://github.com/aymericvie/evology/actions/workflows/oop.yml/badge.svg?branch=master)

### Description

Evology is a market ecology model in which investment funds of various strategies interact endogenously in a simulated stock market. 

### Development and roadmap
We are currently in version 1.1.
Here is the [roadmap](https://doc.clickup.com/4645365/d/4drfn-1722/evologyroadmap) for the next updates & features.

### How to use

* First, you need a few packages. To install the needed libraries, run ```setup.py```.
* The code is in Cython, so you need to compile the files.
```
cd evology/code
python setup.py build_ext --inplace
```
* Run ```python main.pyx``` to start the simulation, and use ```analysis.py```to watch the results. You can change the population size, simulation duration, initial composition of the market, the interest rate, whether fund flows are active, the random seed, and whether wealth is constant in the system.

### Code formatting
We use ```black``` to auto-format the code. After installing with ```pip install black```, go the the ```evology``` folder and run ```black evology``` to auto-format the full folder.

### Credits and funding

Code developed by Aymeric Vié with support from Doyne Farmer, Maarten Scholl, Publius Dirac and Louis Vié. This research has been supported by the EPSRC Centre for Doctoral Training in Mathematics of Random Systems: Analysis, Modelling and Simulation (EP/S023925/1)
