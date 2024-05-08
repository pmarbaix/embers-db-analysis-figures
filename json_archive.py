"""
Usage : python json_archive.py <settings name in settings_datasets_configs.py> [<optional graph type>]
"""
import sys
import requests
import helpers
from settings_general import API_URL, TOKEN


# Get settings from settings_datasets_configs.py
settings = helpers.getsettings(sys.argv)

# Loop over data subsets (defined in settings_datasets_configs.py)
# ---------------------------------------------------------
nsets = helpers.nsets(settings)
for iis in range(nsets):
    dset = helpers.getset(settings, iis)  # Settings for one of the datasets (its sources, name...)

    # Get dataset from the server
    response = requests.get(f"{API_URL}/edb/api/combined_data"
                       f"?select_embers={dset['ids']}"
                       f"&keywords={dset['keywords']}"
                       f"&source={dset['source'] if 'source' in dset else ''}",
                       headers={"Authorization": f"Token {TOKEN}"})

    # Extract ember data and convert to Ember objects from Embermaker
    data = helpers.extractdata(response, dump=True, conv_gmst="never")

