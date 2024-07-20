"""
Settings to produce each type of figure: choice of sources, filtering by keywords, etc.

      This file is mainly used to select WHICH DATA is going to be used for each part of a plot.
      the additional arguments are used to indicate HOW it is going to be processed to produce what kind of plot.

The key 'multi' has a specific role: it must contain a list of choices to be processed separately, as data subsets;
it is the basis for graphs showing for example the mean for each subset.
the value of each item in this list is a dict using the same keywords as the parameters defined outside 'multi'
(e.g. source (= report), title of the graphic...). Keywords outside 'multi' apply to all data subsets.
"""
from copy import deepcopy
import inspect
from os import path, makedirs


def get_settings(settings_choice: str = None, options: list = None, title=None, out_path=None):
    """
    Get settings from edb_paper_settings, selecting a configuration from python call args or CLI.

    :param settings_choice: the name of the desired settings
    :param options: a list of options, added to the returned settings
      - wchapter: apply figure+chapter weighting (if unset, all embers have the same weight)
      - mean: whether to calculate mean values
      - ...
    :param title: A title for the diagram
    :param out_path: the base path for the output files
    :returns: selected settings (dict)
    """
    dtype = inspect.stack()[1][3]  # The 'type' of diagram is the name of the function calling get_settings
    options = options if options else []
    options_str = '-'.join(options) if options else ''

    settings = {
        "AR6-WGII": {
            "source": "AR6-WGII",
            "title": "AR6 - all",
            "out_file": "AR6_all",
        },
        "All_included": {
            "inclusion": 0,  # This is the default: get all with inclusion level >= 0
            "title": "All embers (except for those excluded from all processing)",
            "out_file": "Included_embers",
        },
        "Full": {
            "inclusion": -3,  # Get strictly all embers
            "title": "All embers - including those not included in figures (!)",
            "out_file": "All_embers",
        },
        "SRs+AR6_global_regional": {  # Paper
            "multi": [{"source": "AR6-WGII-Chapter9 OR AR6-WGII-Chapter11 OR AR6-WGII-Chapter13 OR AR6-WGII-Chapter14"
                                 " OR AR6-WGII-CCP4 OR AR6-WGII-CCP6",
                       "name": "Regional", "style": ("blue", "-")},
                      {"source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC",
                       "name": "Global", "style": ("black", "-")}
                      ],
            "keywords": "NOT RFC",
            "scenario": "NOT 'high adaptation'",
            "title": f"SR1.5/SRCCL/SROCC/AR6: global vs regional (without high adapt.)",
            "out_file": f"SRs+AR6_glob_noRFCnoHighAdapt",
        },
        "SRs+AR6noRFC": {   # Documentation for paper
            "source": " SR1.5-Chapter3 OR SRCCL OR SROCC OR AR6-WGII-Chapter2 OR AR6-WGII",
            "keywords": "NOT RFC",
            "title": "SR1.5/SRCCL/SROCC/AR6: all (w/o RFCs)",
        },
        "SRs+AR6noRFCnoHighAdapt": {   # Paper
            "source": " SR1.5-Chapter3 OR SRCCL OR SROCC OR AR6-WGII-Chapter2 OR AR6-WGII",
            "keywords": "NOT RFC",
            "scenario": "NOT 'high adaptation'",
            "title": "SR1.5/SRCCL/SROCC/AR6: all (w/o RFCs & high adapt.)",
        },
        "compare_regions": {
            "multi": [{"source": "AR6-WGII-Chapter9",
                       "style": ('black', '-'), "name": "Africa"},
                      {"source": "AR6-WGII-Chapter11",
                       "style": ('blue', '-'), "name": "Australasia"},
                      {"source": "AR6-WGII-Chapter13",
                       "style": ('red', '-'), "name": "Europe"},
                      {"source": "AR6-WGII-Chapter14",
                       "style": ('orange', '-'), "name": "North-America"},
                      {"source": "AR6-WGII-CCP4",
                       "style": ('green', '-'), "name": "Mediterranean"},
                      {"source": "AR6-WGII-Chapter11",
                       "style": ('grey', '-'), "name": "Polar regions"},
                      ],
            "title": "Africa(black), Australasia(blue), Europe(red), North-America(orange), Mediterranean(green),"
                     "Polar regions(grey)",
            "out_file": f"compare_regional_{dtype}",
        },
        "ecosystems_low-adapt_high-adapt": {  # Paper
            "source": " SR1.5-Chapter3 OR SRCCL OR SROCC OR AR6-WGII-Chapter2 OR AR6-WGII",
            "multi": [{"name": "Ecosystems",
                       "keywords": "'ecosystems' AND NOT 'ecosystem services' AND NOT 'RFC'",
                       "style": ('#084', '-')},
                      {"name": "Others w/o high adaptation",
                       "keywords": "('ecosystem services' OR NOT 'ecosystems') AND NOT 'RFC'",
                       "scenario": "NOT 'high adaptation'",
                       "style": ('black', '-')},
                      {"name": "Other with high adaptation",
                       "keywords": "('ecosystem services' OR NOT 'ecosystems') AND NOT 'RFC'",
                       "scenario": "'high adaptation'",
                       "style": ('#02C', '-')},
                      ],
            "title": f"Ecosystems / others, exc. high adaptation / high adaptation {options_str}",
            "out_file": f"compare_eco-human-sys",
        },
        "ecosystems_low-adapt_high-adapt_AR6": {  # Paper
            "source": "AR6-WGII",
            "multi": [{"name": "Ecosystems",
                       "keywords": "'ecosystems' AND NOT 'ecosystem services' AND NOT 'RFC'",
                       "style": ('#084', '-')},
                      {"name": "Others w/o high adaptation",
                       "keywords": "('ecosystem services' OR NOT 'ecosystems') AND NOT 'RFC'",
                       "scenario": "NOT 'high adaptation'",
                       "style": ('black', '-')},
                      {"name": "Others with high adaptation",
                       "keywords": "('ecosystem services' OR NOT 'ecosystems') AND NOT 'RFC'",
                       "scenario": "'high adaptation'",
                       "style": ('#02C', '-')},
                      ],
            "title": f"Ecosystems / others, exc. high adapt. / high adapt - AR6 only {options_str}",
            "out_file": f"compare_eco-human-sys_AR6",
        },
        "SRs_vs_AR6-ecosystems": {    # Paper
            "multi": [{"name": "SR1.5/SROCC/SRCCL - ecosystems",
                       "source": "SRCCL OR SR1.5 OR SROCC",
                       "keywords": "'ecosystems' AND NOT 'ecosystem services' AND NOT 'RFC'",
                       "style": ('#084', '-')},
                      {"name": "AR6 - ecosystems",
                       "source": "AR6",
                       "keywords": "'ecosystems' AND NOT 'ecosystem services' AND NOT 'RFC'",
                       "style": ('black', '-')},
                      ],
            "title": f"Compare SRs to AR6 {options_str}",
        },
        "SRs_vs_AR6-others-no_high-adapt": {  # Paper-alt
            "multi": [{"name": "SR1.5/SROCC/SRCCL - other systems w/o high adaptation",
                       "source": "SRCCL OR SR1.5 OR SROCC",
                       "keywords": "('ecosystem services' OR NOT 'ecosystems') AND NOT 'RFC'",
                       "scenario": "NOT 'high adaptation'",
                       "style": ('#084', '-')},
                      {"name": "AR6 - other systems w/o high adaptation",
                       "source": "AR6",
                       "keywords": "('ecosystem services' OR NOT 'ecosystems') AND NOT 'RFC'",
                       "scenario": "NOT 'high adaptation'",
                       "style": ('black', '-')},
                      ],
            "title": f"Compare SRs to AR6 {options_str}",
        },
        "overview_systems": {   # Paper
            "multi": [
                {"source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC",
                 "keywords": "ecosystems AND NOT RFC AND NOT 'ecosystem services' AND NOT 'human' AND NOT 'ocean' AND NOT 'coast'",
                 "name": "\n\nLand ecosystems",
                 "color": (0, 0.7, 0)},
                {"source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC",
                 "keywords": "ecosystems AND NOT RFC AND NOT 'ecosystem services' AND NOT 'human' AND ('ocean' OR 'coast')",
                 "name": "\n\nOcean and coastal \n ecosystems",
                 "color": (0, 0, 0.8)},
                {"source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC",
                 "keywords": "(NOT ecosystems OR 'ecosystem services' OR 'human') AND NOT RFC",
                 "longname": "NOT 'Arctic:' AND NOT 'permafrost degradation'",  # Moved to the regional figure below
                 "name": "\nHuman systems\nand ecosystem services",
                 "color": (0.8, 0.0, 0.1)},
            ],
            "sort_keywords": ['health', 'food', 'ecosystem services', 'land', 'forests', 'coast', 'ocean', 'water',
                              'animal', 'sdg', 'tourism', 'permafrost'],
            "out_file": "SRs+AR6_noRFC_overview_systems",
            "soften_col": 2.2,
            "GMT": [1.5, 2.0, 2.5]
        },
        "overview_regions": {   # Paper
            "multi": [
                {"source": "AR6-WGII-CCP6", "color": (0.16, 0, 0.87), "name": "Antarctica",
                    "keywords": "Antarctic"},
                {"source": "AR6-WGII-Chapter11", "color": (0.2, 0.2, 0.2), "name": "\nAustralia and New-Zealand"},
                {"source": "AR6-WGII-Chapter9", "color": (0.65, 0.39, 0.19), "name": "Africa"},
                {"source": "AR6-WGII-CCP4", "color": (0.86, 0, 0.94), "name": "Mediterranean region"},
                {"source": "AR6-WGII-Chapter13", "color": (0.92, 0, 0.06), "name": "Europe"},
                {"source": "AR6-WGII-Chapter14", "color": (0.05, 0.35, 0.05), "name": "North-America"},
                {"source": "AR6-WGII-CCP6", "color": (0.16, 0, 0.87), "name": "Arctic",
                    "keywords": "Arctic",  # The embers of the CCP6 devoted to Arctic (others ar Antarctica, above)
                    "emberids": '27-42'},  # Additional embers about Arctic from SR1.5 and SRCCL Figure 7.1
            ],
            "sort_keywords": ['health', 'food', 'land', 'forests', 'coast', 'ocean', 'water', 'tourism'],
            "hide_chapter": True,
            "hide_category": ['Europe:', 'North America:', 'Arctic:', 'Africa:', 'Mediterranean region:',
                              'Antarctic:', 'in Australia'],  # Those are words from the names that would be redundant
            "out_file": "SRs+AR6_noRFC_overview_reg2.5",
            "soften_col": 2.2,
            "GMT": [1.5, 2.0, 2.5]
        },
        "AR6-RFCs": {
            "source": "AR6-WGII-Chapter16",
            "multi": [
                {"longname": "1.", "color": "#B30", "linestyle": "-"},
                {"longname": "2.", "color": "blue", "linestyle": "--"},
                {"longname": "3.", "color": "green", "linestyle": "-"},
                {"longname": "4.", "color": "#F88", "linestyle": "-"},
                {"longname": "5.", "color": "purple", "linestyle": "--"}
            ],
            "out_file": "AR6_RFCs",
        },
        "TEST": {
            "inclusion": 0,
            "out_file": "TEST",
        },
    }

    # Add variants based on the above ones
    settings["overview_reg_3.5"] = deepcopy(settings["overview_regions"])
    settings["overview_reg_3.5"]["GMT"] = [1.5, 2.5, 3.5]
    settings["overview_reg_3.5"]["out_file"] = "SRs+AR6_noRFC_overview_reg3.5"

    # Get chosen settings
    selected_settings = settings[settings_choice]

    # Define outfile for easy identification of the settings within f name.
    if 'out_file' in selected_settings:
        basename = selected_settings["out_file"].strip()
    else:
        basename = settings_choice.strip()
    out_path = out_path if out_path else "./out/fig"
    settings_in_filename = "_" + dtype + (('_' + options_str) if options_str else '')
    separname = "_" if path.split(out_path)[1] else ""
    selected_settings['out_file'] = (out_path + separname + basename + settings_in_filename).replace(' ', '')

    # Title
    if title:
        selected_settings['title'] = title
    elif 'wchapter' in options:
        selected_settings['title'] = selected_settings['title'] + ' (weight/chapter)'

    # Create out directory if it does not exist
    outdir = path.split(out_path)[0]
    if not path.exists(outdir):
        makedirs(outdir)

    selected_settings['type'] = dtype
    selected_settings['options'] = options

    return selected_settings
