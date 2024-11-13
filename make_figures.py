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
from src.embers_table import embers_table, embers_rkr_table
from src.confidence import confidence
from settings_data_access import datasource
from os.path import join

# Default list of figures to build:
do_figures = ['7v2', '8', 'tab3v2']


def make_figures(figures=None, out_path=None):
    all = False
    if not figures:
        figures = do_figures
    elif figures == 'all':
        all = True
    else:
        figures = [figures]

    # out_path: the full path including the beginning of the file name, which will be extended
    if not out_path:
        out_path = f"./out/{datasource}/"

    fig = '5ad'
    if fig in figures or all:
        mean_percentiles(settings_choice="SRs+AR6_global_regional", options=['mean', 'median', 'ember'],
                         out_path=join(out_path, fig),
                         title="Figure 5(a)+(d): Global vs reg. mean & med.(AR6+SRs, excl. high adapt. and RFCs)")

    fig = '5b'
    if fig in figures or all:
        mean_percentiles(settings_choice="SRs+AR6_global_regional", options=['p10-p90'], out_path=join(out_path, fig),
                         title="Figure 5(b): Global vs regional p10 & p90 (AR6+SRs, excluding high adapt. and RFCs)")

    fig = '5c'
    if fig in figures or all:
        cumulative(settings_choice="SRs+AR6noRFCnoHighAdapt", out_path=join(out_path, fig),
                   title="Figure 5(c): Cumulative distribution of\n"
                   "transitions mid-points (AR6+SRs, excl. RFCs & high adapt.)")

    fig = '5c-alt'
    if fig in figures or all:
        cumulative(settings_choice="SRs+AR6noRFC", out_path=join(out_path, fig),
                   title="Figure 5(c) - ALT:Cumulative distribution of\ntransitions mid-points (AR6+SRs, excl. RFCs)")

    fig = '5ef'
    if fig in figures or all:
        mean_percentiles(settings_choice="SRs+AR6_global_regional", options=['mean', 'median', 'ember', 'wchapter'],
                         out_path=join(out_path, fig), title="Figure 5(e)+(f) - Global vs regional + chapter weighting")

    fig = '6'
    if fig in figures or all:
        mean_percentiles(settings_choice="ecosystems_low-adapt_high-adapt", options=['mean', 'median', 'ember'],
                         out_path=join(out_path, fig),
                         title="Figure 6(a)+(b): Ecosystems - others w/o high adapt. - "
                               "others with high adapt. (AR6+SRs)")

    fig = '6c'
    if fig in figures or all:
        mean_percentiles(settings_choice="SRs_vs_AR6-ecosystems", options=['mean', 'median'],
                         out_path=join(out_path, fig),
                         title="Figure 6(c): Ecosystems: compare SRs to AR6")

    fig = '6d'
    if fig in figures or all:
        mean_percentiles(settings_choice="SRs_vs_AR6-others-no_high-adapt", options=['mean', 'median'],
                         out_path=join(out_path, fig),
                         title="Figure 6(d): Other systems: compare SRs to AR6")

    fig = '6c-sup'
    if fig in figures or all:
        mean_percentiles(settings_choice="ecosystems_low-adapt_high-adapt_AR6", options=['mean', 'median'],
                         out_path=join(out_path, fig),
                         title="Figure 6(sup2): compare SRs to AR6 for human systems\n and ecosystem services, "
                               "no/mod adaptation")

    fig = '7'
    if fig in figures or all:
        overview(settings_choice="overview_systems", out_path=join(out_path, fig),
                 title="Figure 7: Overview - systems")
    fig = '7v2'
    if fig in figures or all:
        overview(settings_choice="overview_RKRs", out_path=join(out_path, fig),
                 title="Figure 7v2: Overview - RKRs")

    fig = '8'
    if fig in figures or all:
        overview(settings_choice="overview_regions", out_path=join(out_path, fig),
                 title="Figure 8: Overview - regional")
    fig = '8-sup'
    if fig in figures or all:
        overview(settings_choice="overview_reg_3.5", out_path=join(out_path, fig),
                 title="Figure 8: Overview - regional - 1.5, 2.5, 3.5°C")

    fig = 'tab3'
    if fig in figures or all:
        embers_table(settings_choice="All_included", out_path=join(out_path, fig),
                     title="Table 3")  # Preprint version (Chapters)

    fig = 'tab3v2'
    if fig in figures or all:
        embers_rkr_table(settings_choice="All_included", out_path=join(out_path, fig),
                         title="Table 3 - version 2")  # Revised manuscript version (RKRs)

    fig = 'tab4'
    if fig in figures or all:
        confidence(settings_choice="SRs+AR6_global_regional", out_path=join(out_path, fig),
                   title="Table 4")

    print("Job completed! Note that a 'processing report' is provided with each figure (.md = Markdown format). "
          "\nFor tables, there are two .md files: the table itself + the processing report.")


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
