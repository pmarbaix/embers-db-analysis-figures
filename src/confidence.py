import numpy as np
import src.helpers as hlp
import settings_configs


def confidence(**kwargs):
    """
    Table of confidence levels (Markdown)
    """
    # Get settings from edb_paper_settings, according to the choices made in keyword arguments (see getsettings)
    settings = settings_configs.get_settings(**kwargs)
    # Create global report file (Markdown)
    hlp.report_start(settings)

    # Create the summary table (Simple md files are crated by the small "Report" class)
    tableout = hlp.Report('out/' + settings['out_file'] + '_out.md')
    bins = 0.5 + np.arange(5)
    tableout.write(f"Confidence range bins limits: {bins}")

    # Loop over data subsets (defined in the settings)
    for dset in hlp.DSets(settings):
        hlp.report.write(f"Source {dset['idset']}: {dset['name']}", title=1)
        tableout.write(f"{dset['name']}", title=1)

        # Get data for the current subset (dset)
        data = hlp.getdata(dset)
        lbes = data['embers']  # The list of burning embers in this data subset

        tableout.table_head("# transition", "mean temp", "mean conf", "n low conf", "n med conf", "n high conf",
                            "n very high conf", "n total")

        for itr in range(3):
            # First restrict to embers which have transition itr, ignoring any that would not have a conf. level
            # (we are aware of only one transition with no stated confidence level - Figure 3.18 of SR1.5/bivalves,
            #  but it is a transition which is not shown in the report because > 2.5°C -> ignoring is ok).
            bes = [be for be in lbes if len(be.trans) > itr and be.trans[itr].confidence_index]
            # Check that we are not mixing transitions (precaution!)
            trnames = {be.trans[itr].name for be in bes}  # => a set, which should contain only 1 element
            hlp.report.write(f"Transition {itr} is {trnames}")
            if len(trnames) != 1:
                raise ValueError(f"Transition {itr} appears to refer to different names across embers")
            # Get confidence index for these
            confs = [be.trans[itr].confidence_index for be in bes]
            # Get corresponding hazard level for mean and median (at risk levels 0.5, 1.5, and 2.5)
            haz = [hlp.hfn(be, itr + 0.5) for be in bes]
            haz50 = np.percentile(haz, 50.0, method='linear')
            # Count embers in each bin
            hist = np.histogram(confs, bins=bins)  # bins are also created for 'low to med' etc.

            # To check that there is no ember with intermediary confidence levels (e.g. medium to high), use:
            # [be.longname for be in bes if be.trans[itr].confidence_index % 1]

            # Additional investigation: list embers in the "low confidence" bin:
            lowconf = [be.longname for be in bes if be.trans[itr].confidence_index < 1.5]
            hlp.report.write(f"Embers for which transition {itr} is assessed with low confidence:")
            hlp.report.write(f"{'\n'.join(lowconf)}")

            tableout.table_write(f"{itr}", f"{np.mean(haz):.2f} ({haz50})", f"{np.mean(confs):.2f}",
                                 *[str(h) for h in hist[0]],
                                 f"{len(confs)}"
                                 )

        tableout.write("")

    tableout.close(total=False)
