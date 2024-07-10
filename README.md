# Code for the analysis and figures in "Climate change risks illustrated by the IPCC burning embers"

This repository contains the code needed to reproduce the figures and tables from ([Marbaix et al. 2024b](#2)).

## Basic use

Run ```pip install -r requirements-dev.txt```

Copy `settings_data_access.py.template` to `settings_data_access.py` and adjust the parameters to your local needs:

For `datasource`, chose either `remote` or `file`. 
To reproduce the figures from ([Marbaix et al. 2024b](#2)), use the following:

datasource = "file"
FILE = <path to the file downloaded from [Marbaix et al. (2024)](#1)>

Then run `python make_figures.py all`

To get data from the online API at https://climrisk.org instead of the file archive, see `Embers_retrieve_API.md`

## Structure

`settings_data_access` defines the data source - it must be defined before any use of this code.

`make_figures.py` contains a list of function calls to build each of the figures in [Marbaix et al. (2024b)](#2).
Depending on how it is called, it may build all or a subset of these figures (more information is provided in the file).

`settings_configs.py` defines 'configurations' to run each of the figure-building functions. 
This file is mainly used to select which data is going to be used for each part of a plot;
additional arguments may provide names and colours used on a plot to illustrate the selected data.
The key "multi" has a specific role: its value must be a list, which will specify subset of data for separate analysis,
such as to get lines representing each data subset in a plot.

`src` is a python package which contains the code to draw figures and get the data provided in summary tables.
To find how each module is used to get the figures and tables, see `make_figures.py`. As its name indicates,
`json_archive.py` gets the data from the online API to build a new archive file.

## References

<a id="1">Marbaix et al. (2024)</a>
Marbaix, P., A. K. Magnan, V. Muccione, P. W. Thorne, Z. Zommers (2024)
*Climate change risks illustrated by the IPCC burning embers: dataset*.
Zenodo. [doi.org/10.5281/zenodo.12626977](https://doi.org/10.5281/zenodo.12626977).

<a id="2">Marbaix et al. (2024b)</a> 
Marbaix, P., A. K. Magnan, V. Muccione, P. W. Thorne, Z. Zommers (2024).
*Climate change risks illustrated by the IPCC 'burning embers'*.
Prepared for submission to [ESSD](https://www.earth-system-science-data.net).