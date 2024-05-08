"""
Settings to produce each type of figure: choice of sources, filtering by keywords, etc.

      This file is mainly used to select WHICH DATA is going to be used for each part of a plot.
      the additional arguments are used to indicate HOW it is going to be processed to produce what kind of plot.

The key 'multi' has a specific role: it must contain a list of choices to be processed as (sub)datasets;
the value of each item in this list is a dict written in the same way as the main keywords
(that is, with a source, keyword filter if desired, name, etc.). The main key/values apply to all 'multi's.
'multi' is the basis for eg. a graph with mutliple lines comparing subsets of data.
"""
import copy


def paper_settings(argv):
    type_arg = "percentiles" if len(argv) <= 2 else argv[2]  # Default type is 'percentiles'
    subtype_arg = "" if len(argv) <= 3 else argv[3]
    settings = {
        "AR6_WGII": {
            "source": "AR6",
            "title": "AR6 - all",
            "out_file": "AR6_all",
        },
        "All": {
            "title": "All",
            "out_file": "all",
        },
        "AR6_regional": {
            "source": "AR6-WGII-Chapter9 OR AR6-WGII-Chapter11 OR AR6-WGII-Chapter13 OR AR6-WGII-Chapter14 "
                      "OR AR6-WGII-CCP4 OR AR6-WGII-CCP6",
            "title": "AR6 - regional chapters",
            "out_file": "AR6_reg",
        },
        "AR6_global": {
            "source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR AR6-WGII-Chapter16",
            "title": "AR6 - global chapters",
            "out_file": "AR6_glob",
        },

        "AR6_RFCs": {
            "source": ["AR6-WGII-Chapter16"],
            "title": "AR6 - RFCs",
            "out_file": "AR6_RFCs",
        },
        "AR6_compare_global_regional": {
            "multi": [
                {"source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR AR6-WGII-Chapter16",
                 "name": "Global"},
                {"source": "AR6-WGII-Chapter9 OR AR6-WGII-Chapter11 OR AR6-WGII-Chapter13 OR AR6-WGII-Chapter14"
                           " OR AR6-WGII-CCP4 OR AR6-WGII-CCP6",
                 "name": "Regional"}
            ],
            "title": "AR6 - compare global to regional (blue)",
            "out_file": "AR6_reg_glob",
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
        "AR6_vs_SRs-global": {
            "source": ["SRCCL OR SR1.5-Chapter3 OR SROCC",
                       "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7"],
            "title": "Compare SRs to AR6 (blue) (all global only, w/o RFCs)",
            "out_file": "AR6_vs_SRs-global",
        },
        "SRs+AR6_global_noRFC_regional": {
            "multi": [{"source": "AR6-WGII-Chapter9 OR AR6-WGII-Chapter11 OR AR6-WGII-Chapter13 OR AR6-WGII-Chapter14"
                                 " OR AR6-WGII-CCP4 OR AR6-WGII-CCP6",
                       "name": "Regional", "style": ("blue", "-")},
                      {"source": "AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC",
                       "name": "Global", "style": ("black", "-")}
                      ],
            "multi": None, # Block this setting because filter-out-sc below is no longer valid
            "keywords": "!RFC",
            "filter-out-scenario-ids": [3],
            "title": f"SR1.5/SRCCL/SROCC/AR6: global (w/o RFCs) / regional (blue) "
                     f"{type_arg if type_arg == 'exprisk' else ''}",
            "out_file": f"SRs+AR6_glob_noRFC{type_arg}_filter_{subtype_arg}",

            "exprisk": type_arg == "exprisk",
            "type": "percentiles"
        },

        "SRs+AR6_global_noRFC_regional_cumu": {
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
            "out_file": f"SRs+AR6_glob_noRFC{type_arg}",
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
            "out_file": f"compare_regional_{type_arg}",
        },
        "eco_human_adapt-sys": {
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
            "title": f"Ecosystems / others, exc. high adaptation / high adaptation {subtype_arg}",
            "out_file": f"compare_eco-human-sys{subtype_arg}",
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

        "ecosystems": {
            "source": ["AR6-WGII-Chapter2 OR AR6-WGII-Chapter7 OR SRCCL OR SR1.5-Chapter3 OR SROCC"
                       "AR6-WGII-Chapter9 OR AR6-WGII-Chapter11 OR AR6-WGII-Chapter13 OR AR6-WGII-Chapter14"
                       " OR AR6-WGII-CCP4 OR AR6-WGII-CCP6"],
            "keywords": "ecosystems AND !RFC",
            "title": "ecosystems (excluding RFCs)",
            "out_file": "ecosystems",
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
            "title": f"Compare SRs to AR6 {subtype_arg}",
            "out_file": f"Compare SRs to AR6{subtype_arg}",
        },
        "TEST": {
            "source": "SR1.5",
            "out_file": "test",
        },

        "TEST2": {
            "source": "",
            "multi": [{"name": "ecosystems",
                       "keywords": "('ecosystems' AND NOT 'ecosystem services')",
                       "style": ('black', '-')},
                      {"name": "others (excl. high ad.)",
                       "keywords": "('ecosystem services' OR NOT 'ecosystems')",
                       "style": ('blue', '-')},
                      ],  # Total: 165 = same as all embers which are included + have a T scale
            "title": f"TEST",
            "out_file": f"test_{subtype_arg}",
        },

    }

    # Add variants based on the above ones
    settings["overview_reg_3.5"] = copy.deepcopy(settings["overview_reg"])
    settings["overview_reg_3.5"]["GMT"] = [1.5, 2.5, 3.5]
    settings["overview_reg_3.5"]["out_file"] = "SRs+AR6_noRFC_overview_reg3.5"

    sel_settings = settings[argv[1]]
    if 'out_file' not in sel_settings:  # Default outfile, for easier identification of the settings within f name.
        sel_settings['out_file'] = argv[1] + '_' + type_arg
    if 'type' not in sel_settings:  # Default graph type (the 2nd arg)
        sel_settings['type'] = type_arg
    if 'wchapter' in argv:  # Weighting by chapter option
        sel_settings['title'] = sel_settings['title'] + ' (weight/chapter)' if 'title' in sel_settings \
            else 'Weight by chapter'
        sel_settings['out_file'] += '-wchapter'
        sel_settings['wchapter'] = 'True'
    sel_settings['subtype'] = subtype_arg
    return sel_settings
