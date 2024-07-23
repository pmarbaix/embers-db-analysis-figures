# Data analyses and figures based on the 'burning embers' database

This repository contains the code needed to reproduce the figures and tables from ([Marbaix et al. 2024b](#2)).
It was tested with python 3.11 and 3.12.

## Basic use

- We suggest creating a python (3.11 or 3.12) virtual environment and activating it.

- Get the project files, either
   - from Zenodo. The access is restricted until ([Marbaix et al. 2024b](#2)) is published or at least
     under public review; then the DOI will be https://doi.org/10.5281/zenodo.12799901
   - from GitHub, for example by running `git clone https://github.com/pmarbaix/embers-db-analysis-figures.git`. 
   - This access will be opened approximately at the same time as files are made public on Zenodo.

- Run ```pip install -r requirements.txt```

- Copy `settings_data_access.py.template` to `settings_data_access.py` and adjust the parameters to your needs:

    - For `datasource`, chose either `remote` or `file`. 
    - To reproduce the figures from ([Marbaix et al. 2024b](#2)), one only needs to set the following:
    ```
    datasource = "file"
    FILE = path_name_for_the_file_downloaded_from_Marbaix_etal_2024
    ```

- Run `python make_figures.py all`. This should give you all figures and tables (you might have to close
  the window showing each figure before getting the next one). All will be stored in a subdirectory named 'out'.

To get data from the online API at https://climrisk.org instead of the file archive, see `Embers_retrieve_API.md`

## Structure

`settings_data_access` defines the data source - it must be defined before any use of this code.

`make_figures.py` contains a list of function calls to build each of the figures in [Marbaix et al. (2024b)](#2).
Depending on how it is called, it may build all or a subset of these figures (more information is provided in the file).

`settings_configs.py` defines 'configurations' to run each of the figure-building functions. 
This file is mainly used to select which data is going to be used for each part of a plot;
additional arguments may provide names and colours used on a plot to illustrate the selected data.
The key "multi" has a specific role: its value must be a list, which will specify subsets of data for separate analysis,
such as to get lines representing each data subsets in a plot.

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