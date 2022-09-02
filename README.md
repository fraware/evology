# Evolutionary market ecology

### Testing 

![Runs](https://github.com/aymericvie/evology/actions/workflows/oop.yml/badge.svg?branch=master)

### Description

Evology is a market ecology model in which investment funds of various strategies interact endogenously in a simulated stock market. 

### How to use

* First, you need a few packages. To install the needed libraries, run ```setup.py```.
* The code is in Cython, so you need to compile the files.
```
cd evology/code
python setup.py build_ext --inplace
```
* Run ```python main.pyx``` to start the simulation, and use ```analysis.py```to watch the results.

### Code formatting
We use ```black``` to auto-format the code. After installing with ```pip install black```, go the the ```evology``` folder and run ```black evology``` to auto-format the full folder.

### Credits and funding

Code developed by Aymeric Vié with support from Doyne Farmer, Maarten Scholl, Publius Dirac and Louis Vié. This research has been supported by the EPSRC Centre for Doctoral Training in Mathematics of Random Systems: Analysis, Modelling and Simulation (EP/S023925/1)
