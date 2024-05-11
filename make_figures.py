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
from mean_percentiles import mean_percentiles
from cumulative import cumulative

# Default list of figures to build:
do_figures = [32]

def make_figures(figures = None):
    if not figures:
        figures = do_figures
    elif figures == 'all':
        figures = range(100)
    else:
        figures = [int(figures)]

    if 31 in figures:
        mean_percentiles(settings_choice="SRs+AR6_global_regional", options=['mean', 'median'],
            title="Figure 3(a) and 3(d): Global vs reg. mean & med.(AR6+SRs, excl. high adapt. and RFCs)")

    if 32 in figures:
        mean_percentiles(settings_choice="SRs+AR6_global_regional", options=['p10-p90'],
            title="Figure 3(b): Global vs regional p10 & p90 (AR6+SRs, excluding high adapt. and RFCs)")

    if 33 in figures:
        cumulative(settings_choice="SRs+AR6noRFC",
            title="Figure 3(c): Cumulative distribution of\ntransitions mid-points (AR6+SRs, excl. RFCs)")

    if 34 in figures:
        cumulative(settings_choice="SRs+AR6noRFCnoHighAdapt",
            title="Figure 3(c) - alt.: Cumulative distribution of\n"
                  "transitions mid-points (AR6+SRs, excl. RFCs & high adapt.)")

    if 4 in figures:
        mean_percentiles(settings_choice="SRs+AR6_global_regional", options=['mean', 'median', 'wchapter'],
            title="Figure 4 - Global vs regional + chapter weighting")

    if 5 in figures:
        mean_percentiles(settings_choice="ecosystems_low-adapt_high-adapt", options=['mean', 'median'],
            title="Figure 5: Ecosystems - others w/o high adapt. - others with high adapt. (AR6+SRs)")


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
        make_figures(figures = argv[1])
    else:
        make_figures()