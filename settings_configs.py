"""
Settings to produce each type of figure: choice of sources, filtering by keywords, etc.

      This file is mainly used to select WHICH DATA is going to be used for each part of a plot.
      the additional arguments are used to indicate HOW it is going to be processed to produce what kind of plot.

The key 'multi' has a specific role: it must contain a list of choices to be processed separately, as data subsets;
it is the basis for graphs showing for example the mean for each subset.
the value of each item in this list is a dict using the same keywords as the parameters defined outside 'multi'
(e.g. source (= report), title of the graphic...). Keywords outside 'multi' apply to all data subsets.
"""
import copy

def get_settings(settings_choice:str = None, type=None, subtype=None, wchapter=False):
    """
    Get settings from edb_paper_settings, selecting a configuration from python call args or CLI.
    :param settings_choice: the name of the desired settingsd
    :param type: the default type of diagram, used if the settings below do not define a type
    :param subtype: the default subtype of diagram, used if the settings below do not define a type
    :param wchapter: wether figure+chapter weighting should be used (False means all embers have the same weight)
    :returns: selected settings (dict)
    """
    settings = {
        "AR6_WGII": {
            "source": "AR6",
            "title": "AR6 - all",
            "out_file": "AR6_all",
        },
        "AR6_global_noRFC_regional": {
            "multi": [
                {"source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7",
                 "name": "Global"},
                {"source": "AR6-WGII-Chapter9 OR AR6-WGII-Chapter11 OR AR6-WGII-Chapter13 OR AR6-WGII-Chapter14"
                           " OR AR6-WGII-CCP4 OR AR6-WGII-CCP6",
                 "name": "Regional"}
            ],
            "title": "AR6 - compare regional (blue) to blobal (black, without RFCs)",
            "out_file": "AR6_glob_noRFC_reg",
        },
        "SRs+AR6_global_regional": {
            "multi": [{"source": "AR6-WGII-Chapter9 OR AR6-WGII-Chapter11 OR AR6-WGII-Chapter13 OR AR6-WGII-Chapter14"
                                 " OR AR6-WGII-CCP4 OR AR6-WGII-CCP6",
                       "name": "Regional", "style": ("blue", "-")},
                      {"source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC",
                       "name": "Global", "style": ("black", "-")}
                      ],
            "keywords": "!RFC",
            "scenario": "NOT 'high adaptation'",
            "title": f"SR1.5/SRCCL/SROCC/AR6: global (w/o RFCs) / regional (blue) "
                     f"{type if type == 'exprisk' else ''}",
            "out_file": f"SRs+AR6_glob_noRFCnoHighAdapt{type}_{subtype}",
            "exprisk": type == "exprisk"
        },
        "SRs+AR6_global_regional_cumu": {
            "multi": [{"source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC",
                       "name": "Global"},
                      {"source": "AR6-WGII-Chapter9 OR AR6-WGII-Chapter11 OR AR6-WGII-Chapter13 OR AR6-WGII-Chapter14"
                                 " OR AR6-WGII-CCP4 OR AR6-WGII-CCP6",
                       "name": "Regional"}
                      ],
            "keywords": "!RFC",
            "title": "SR1.5/SRCCL/SROCC/AR6: compare global (w/o RFCs) to regional (dashes)",
            "out_file": "SRs+AR6_glob_noRFC_reg_cumu",
            "type": "cumulative"
        },
        "SRs+AR6_G_noRFC": {
            "source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC",
            "keywords": "!RFC",
            "title": "SR1.5/SRCCL/SROCC/AR6: global (w/o RFCs)",
            "out_file": f"SRs+AR6_glob_noRFC{type}",
        },
        "SRs+AR6noRFC_noinc": {
            "source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC"
                      "AR6-WGII-Chapter9 OR AR6-WGII-Chapter11 OR AR6-WGII-Chapter13 OR AR6-WGII-Chapter14"
                      " OR AR6-WGII-CCP4 OR AR6-WGII-CCP6",
            "keywords": "!RFC",
            "title": "SR1.5/SRCCL/SROCC/AR6: all w complete data (w/o RFCs)",
            "remove_incomplete": True
        },
        "SRs+AR6noRFC": {
            "source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC"
                      "AR6-WGII-Chapter9 OR AR6-WGII-Chapter11 OR AR6-WGII-Chapter13 OR AR6-WGII-Chapter14"
                      " OR AR6-WGII-CCP4 OR AR6-WGII-CCP6",
            "keywords": "!RFC",
            "title": "SR1.5/SRCCL/SROCC/AR6: all (w/o RFCs)",
        },
        "compare_regional": {
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
            "out_file": f"compare_regional_{type}",
        },
        "ecosystems_low-adapt_high-adapt": {
            "source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC"
                      " OR AR6-WGII-Chapter9 OR AR6-WGII-Chapter11 OR AR6-WGII-Chapter13 OR AR6-WGII-Chapter14"
                      " OR AR6-WGII-CCP4 OR AR6-WGII-CCP6",
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
            "title": f"Ecosystems / others, exc. high adaptation / high adaptation {subtype}",
            "out_file": f"compare_eco-human-sys{subtype}",
        },
        "histogram": {
            "source": ["AR6-WGII-Chapter9 OR AR6-WGII-Chapter11 OR AR6-WGII-Chapter13 OR AR6-WGII-Chapter14"
                       " OR AR6-WGII-CCP4 OR AR6-WGII-CCP6"],
            "keywords": "!RFC",
            "title": "SR1.5/SRCCL/SROCC/AR6: regional)",
            "out_file": "histo",
        },

        "overview_glob": {
            "multi": [
                {"source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC",
                 "keywords": "ecosystems AND !RFC AND !'ecosystem services' AND !'human' AND !'ocean' AND !'coast'",
                 "name": "\n\nLand ecosystems",
                 "color": (0, 0.7, 0)},
                {"source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC",
                 "keywords": "ecosystems AND !RFC AND !'ecosystem services' AND !'human' AND ('ocean' OR 'coast')",
                 "name": "\n\nOcean and coastal \n ecosystems",
                 "color": (0, 0, 0.8)},
                {"source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC",
                 "keywords": "(!ecosystems OR 'ecosystem services' OR 'human') AND !RFC",
                 "name": "\nHuman systems\nand ecosystem services",
                 "color": (0.8, 0.0, 0.1)},
            ],
            "sort_keywords": ['health', 'food', 'ecosystem services', 'land', 'forests', 'coast', 'ocean', 'water',
                              'animal', 'sdg', 'tourism', 'permafrost'],
            "title": "SR1.5/SRCCL/SROCC/AR6 - global",
            "out_file": "SRs+AR6_noRFC_overview_glob",
            "type": "overview",
            "GMT": [1.5, 2.0, 2.5]
        },

        "overview_reg": {
            "multi": [
                {"source": "AR6-WGII-CCP6", "color": (0.16, 0, 0.87), "name": "Antarctica",
                    "keywords": "Antarctic"},
                {"source": "AR6-WGII-Chapter11", "color": (0.2, 0.2, 0.2), "name": "\n\n\nAustralia and New-Zealand"},
                {"source": "AR6-WGII-Chapter9", "color": (0.65, 0.39, 0.19), "name": "Africa"},
                {"source": "AR6-WGII-CCP4", "color": (0.86, 0, 0.94), "name": "Mediterranean region"},
                {"source": "AR6-WGII-Chapter13", "color": (0.92, 0, 0.06), "name": "Europe"},
                {"source": "AR6-WGII-Chapter14", "color": (0.05, 0.35, 0.05), "name": "North-America"},
                {"source": "AR6-WGII-CCP6", "color": (0.16, 0, 0.87), "name": "Arctic",
                    "keywords": "Arctic"},
            ],
            "sort_keywords": ['health', 'food', 'land', 'forests', 'coast', 'ocean', 'water', 'tourism'],
            "hide_chapter": True,
            "hide_category": ['Europe:', 'North America:', 'Arctic:', 'Africa:', 'Mediterranean region:',
                              'Antarctic:', 'in Australia'],  # Those are words from the names that would be redundant
            "title": "AR6 - regional",
            "out_file": "SRs+AR6_noRFC_overview_reg2.5",
            "type": "overview",
            "GMT": [1.5, 2.0, 2.5]
        },
        "SRs_vs_AR6":{
            "multi": [{"name": "SR1.5/SROCC/SRCCL - ecosystems",
                       "source": "SRCCL OR SR1.5-Chapter3 OR SROCC",
                       "keywords": "'ecosystems' AND NOT 'ecosystem services' AND NOT 'RFC'",
                       "style": ('#084', '-')},
                      {"name": "AR6 - ecosystems",
                       "source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7"
                            " OR AR6-WGII-Chapter9 OR AR6-WGII-Chapter11 OR AR6-WGII-Chapter13 OR AR6-WGII-Chapter14"
                            " OR AR6-WGII-CCP4 OR AR6-WGII-CCP6",
                       "keywords": "'ecosystems' AND NOT 'ecosystem services' AND NOT 'RFC'",
                       "style": ('black', '-')},
                      ],
            # "no-gmt-conv": True,
            "title": f"Compare SRs to AR6 {subtype}",
            "out_file": f"Compare SRs to AR6{subtype}",
        },
    }

    # Add variants based on the above ones
    settings["overview_reg_3.5"] = copy.deepcopy(settings["overview_reg"])
    settings["overview_reg_3.5"]["GMT"] = [1.5, 2.5, 3.5]
    settings["overview_reg_3.5"]["out_file"] = "SRs+AR6_noRFC_overview_reg3.5"

    # Get chosen settings
    selected_settings = settings[settings_choice]

    # Default outfile, for easier identification of the settings within f name.
    if 'out_file' not in selected_settings:
        selected_settings['out_file'] = settings_choice + '_' + type

    # Default graph type
    if 'type' not in selected_settings:
        selected_settings['type'] = type

    # Weighting by chapter option
    if wchapter:
        selected_settings['title'] = selected_settings['title'] + ' (weight/chapter)' if 'title' in selected_settings \
            else 'Weight by chapter'
        selected_settings['out_file'] += '-wchapter'
        selected_settings['wchapter'] = 'True'

    selected_settings['subtype'] = subtype
    return selected_settings
