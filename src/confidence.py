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
        hlp.report.write(f"Source {dset["idset"]}: {dset['name']}", title=1)
        tableout.write(f"{dset['name']}", title=1)

        # Get data for the current subset (dset)
        data = hlp.getdata(dset)
        lbes = data['embers']  # The list of burning embers in this data subset

        tableout.table_head("# transition", "mean temp", "mean conf", "n low conf", "n med conf", "n high conf",
                            "n very high conf", "n total")

        for itr in range(3):
            # Embers which have transition itr, ignoring any that would not have a conf. level
            # (we are aware of only one transition with no stated confidence level - Figure 3.18 of SR1.5/bivalves,
            #  but it is a transition which is not shown in the report because > 2.5°C -> ignoring is ok).
            tbe = [be for be in lbes if len(be.trans) > itr and be.trans[itr].confidence_index]
            trs = [be.trans[itr].confidence_index for be in tbe]
            haz = [hlp.hfn(be, itr + 0.5) for be in tbe]
            haz50 = np.percentile(haz, 50.0, method='linear')
            hist = np.histogram(trs, bins=bins)  # bins are also created for 'low to med' etc.

            tableout.table_write(f"{itr}", f"{np.mean(haz):.2f} ({haz50})", f"{np.mean(trs):.2f}",
                                 *[str(h) for h in hist[0]],
                                 f"{len(trs)}"
                                 )

        tableout.write("")

    tableout.close(total=False)
