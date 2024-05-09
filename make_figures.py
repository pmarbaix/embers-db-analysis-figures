from mean_percentiles import mean_percentiles
from cumulative import cumulative

dofigure = [1]

if 1 in dofigure:
    # Figure 3(a) and 3(d): Global vs regional - mean & median (AR6+SRs, excluding high adaptation and RFCs)
    mean_percentiles(settings_choice = "SRs+AR6_global_regional", type="percentiles", subtype="mean median")

if 2 in dofigure:
    # Figure 3(b): Global vs regional - percentiles (AR6+SRs, excluding high adaptation and RFCs)
    mean_percentiles(settings_choice = "SRs+AR6_global_regional", type="percentiles", subtype="")

if 3 in dofigure:
    # Figure 3(c): Cumulative distribution of mid-points within transitions (AR6+SRs, excluding WARNING RFCs)
    cumulative(settings_choice = "SRs+AR6noRFC", type="cumulative", subtype="")

if 4 in dofigure:
    # TBD
    pass

if 5 in dofigure:
    # Figure 4: Ecosystems - others w/o high adaptation - others with high adaptation (AR6+SRs):
    mean_percentiles(settings_choice = "ecosystems_low-adapt_high-adapt", type="percentiles", subtype="mean median")


