# SCRC Spearman correlation realtime calculator #

This programm helps to calculate and visualize spearman correlation for EEG relation

### Dependencies ###

* Python 2.6+
* NumPy
* PyCUDA
* TkInter (Linux/Mac only)

### Instructions ###

Repo containts two main applications:

1. Spearman correlation realtime calculator
2. Input file generator

### SCRC ###

Capable to calculate relation power between EEG electrodes' signals
How to run:

1. run ```run.bat``` on Windows or ```sudo sh run.sh``` on Linux/Mac
2. connect to remote server via socket or read data from file

### Input file generator ###

Used for test input data generation
How to run:
run from root app folder ```python lib/file_generator.py```

* use -f to set file name
* use -n to set electrodes number