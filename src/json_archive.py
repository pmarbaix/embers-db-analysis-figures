"""
Usage : python json_archive.py
"""
import helpers as hlp
import settings_configs
from sys import argv


def json_archive(settings_choice="All_inclusion-OK"):
    """
    Generates a summary table for 'all' embers.
    'All_inclusion-OK' refers to the "included" embers, that is, those with the inclusion field >= 0;
    To get strictly all embers, set the 'inclusion' parameter to -3, within settings_configs.py (see config "Full").
    """
    # Get settings from edb_paper_settings, according to the choices made in keyword arguments (see getsettings)
    settings = settings_configs.get_settings(settings_choice=settings_choice, out_path="./out/")

    # Get data for the current subset and the list of burning embers
    # as_embers = False => do not convert the data to Ember objects (keep JSON-like)
    # desc = True => include the description field for embers and the explanation for transitions
    data = hlp.getdata(settings, as_embers=False, desc=True)

    # Write JSON file
    hlp.jsonfile_save(settings['out_file'], data)

if __name__ == "__main__":
    json_archive(settings_choice=argv[1])
