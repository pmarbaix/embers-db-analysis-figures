"""
Starting point for producing figures.
Figure production can be triggered in different ways.
An easy way to experiment is to run this script without arguments after filling the list 'do_figures' below.
To build all figures, run make_figures 'all'. For other command-line options, see at the end of this script.

All usages of this script require:
 - that the dependencies in requirements.txt are satisfied
 - that settings_data_access.py is properly configured

 For more information, see README.md
"""
from sys import exit, argv
from src.mean_percentiles import mean_percentiles
from src.cumulative import cumulative
from src.overview import overview
from src.embers_table import embers_table
from src.confidence import confidence

# Default list of figures to build:
do_figures = ['tab2']


def make_figures(figures=None):
    all = False
    if not figures:
        figures = do_figures
    elif figures == 'all':
        all = True
    else:
        figures = [figures]

    if '5a' in figures or all:
        mean_percentiles(settings_choice="SRs+AR6_global_regional", options=['mean', 'median', 'ember'],
            title="Figure 3(a)+(d): Global vs reg. mean & med.(AR6+SRs, excl. high adapt. and RFCs)")

    if '5b' in figures or all:
        mean_percentiles(settings_choice="SRs+AR6_global_regional", options=['p10-p90'],
            title="Figure 3(b): Global vs regional p10 & p90 (AR6+SRs, excluding high adapt. and RFCs)")

    if '5c' in figures or all:
        cumulative(settings_choice="SRs+AR6noRFCnoHighAdapt",
            title="Figure 3(c) - alt.: Cumulative distribution of\n"
                  "transitions mid-points (AR6+SRs, excl. RFCs & high adapt.)")

    if '5c-alt' in figures or all:
        cumulative(settings_choice="SRs+AR6noRFC",
            title="Cumulative distribution of\ntransitions mid-points (AR6+SRs, excl. RFCs)")

    if '5e' in figures or all:
        mean_percentiles(settings_choice="SRs+AR6_global_regional", options=['mean', 'median', 'ember', 'wchapter'],
            title="Figure 3(e)+(f) - Global vs regional + chapter weighting")

    if '6' in figures or all:
        mean_percentiles(settings_choice="ecosystems_low-adapt_high-adapt", options=['mean', 'median', 'ember'],
            title="Figure 4(a)+(b): Ecosystems - others w/o high adapt. - others with high adapt. (AR6+SRs)")

    if '6c' in figures or all:
        mean_percentiles(settings_choice="SRs_vs_AR6-ecosystems", options=['mean', 'median'],
            title="Figure 4(c): Ecosystems: compare SRs to AR6")

    if '6d' in figures or all:
        mean_percentiles(settings_choice="SRs_vs_AR6-others-no_high-adapt", options=['mean', 'median'],
            title="Figure 4(d): Other systems: compare SRs to AR6")

    if '6c-sup' in figures or all:
        mean_percentiles(settings_choice="ecosystems_low-adapt_high-adapt_AR6", options=['mean', 'median'],
            title="Figure 4(sup2): compare SRs to AR6 for human systems\n and ecosystem services, no/mod adaptation")

    if '7' in figures or all:
        overview(settings_choice="overview_systems",
            title="Figure 5: Overview - systems")

    if '8' in figures or all:
        overview(settings_choice="overview_regions",
            title="Figure 6: Overview - regional")

    if '8-sup' in figures or all:
        overview(settings_choice="overview_reg_3.5",
            title="Figure 6: Overview - regional - 1.5, 2.5, 3.5°C")

    if 'tab2' in figures or all:
        embers_table(settings_choice="All_included",
            title="Table 2")

    if 'tab4' in figures or all:
        confidence(settings_choice="SRs+AR6_global_regional",
            title="Table 4")


    print("Job completed! Note that a 'processing report' is provided with each figure (.md = Markdown format).")


# Optional start from command-line, with arguments
# Usage:   python make_figures.py  <function to run> <settings_choice> [<option 1> [<option 2>] ...]
# Example: python make_figures.py  mean_percentiles SRs+AR6_global_regional mean median
# Alternatively, python make_figures.py <number> would produce a figure based on the numbering in make_figures().
if __name__ == "__main__":
    if len(argv) > 2:
        cmd = f"{argv[1]}(settings_choice='{argv[2]}', options={argv[3:]})"
        print(cmd)
        exec(cmd)
        exit()
    elif len(argv) == 2:
        make_figures(figures=argv[1])
    else:
        make_figures()
