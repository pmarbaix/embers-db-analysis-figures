import numpy as np
import matplotlib.pyplot as plt
import src.helpers as hlp
import settings_configs

def cumulative(**kwargs):
    """
    Cumulative distribution of mid-points within transitions.
    Arguments are passed to get_settings:
    - settings_choice: the name of the desired settings within settings_config.py
    - a list of options, added to the settings
    """

    # Get settings from edb_paper_settings, according to the choices made in keyword arguments (see getsettings)
    settings = settings_configs.get_settings(**kwargs)
    # Create global report file (Markdown)
    hlp.report_start(settings)
    # Create plot
    fig, ax = plt.subplots()

    # Loop over data subsets (defined in the settings)
    for dset in hlp.DSets(settings):
        if dset["ndsets"] > 1:
            hlp.report.write(f"Source {dset["idset"]}: {dset['name']}", title=1)

        # Get data for the current subset and the list of burning embers (lbes)
        data = hlp.getdata(dset)
        lbes = data['embers']
        hlp.report.embers_list(lbes)

        # This diagram is based on the transition mid-points ('median') for each transition.
        # associate each of these to a colour and linestyle:
        rlev = [
            (0.5, '#DC0', '-'),
            (1.5, 'red', '-'),
            (2.5, 'purple', '-')
        ]
        if "range" in dset["options"] and dset["ndsets"] == 1:
            rlev.append((1.001, '#DC0', '--'))
            rlev.append((1.999, 'red', '--'))

        # Loop over the risk levels for which a distribution is plotted
        for rl in rlev:
            haz_chg = []
            hlp.report.write(f"Processing risk level {rl[0]}", title=2)

            for be in lbes:
                # Hazard level corresponding to the risk level rl[0] (= associated to the currently prepared curve)
                haz = hlp.hfn(be, rl[0])
                # maxass = maximum hazard level for which there is an indication that the assessment considered it:
                #   - haz_valid[1] is the stated top of the assessment, but
                #   - a transition above haz_valid[1] is also regarded as an indication that it was considered.
                #     (= better than entirely removing the ember).
                maxass = max(np.max(be.levels_values('hazl')), be.haz_valid[1])
                if haz < maxass:
                    haz_chg.append(haz)
                else:
                    hlp.report.write(f"Ember '{be.longname}' ({be.id}) excluded because max."
                                     f" risk level is {hlp.rfn(be, maxass)} (max. hazard = {maxass}°C).")
            hlp.report.write(f"Total number of embers included: {len(haz_chg)}")

            haz_chg = np.sort(haz_chg)
            neb = 0
            xx = []
            yy = []
            for hc in haz_chg:
                xx.append(hc)
                yy.append(neb)
                neb += 100.0 / len(lbes)
                xx.append(hc)
                yy.append(neb)
            lstyle = ('-', '--')[dset["idset"]] if dset["ndsets"] > 1 else rl[2]
            ax.plot(xx, yy, color=rl[1], linestyle=lstyle)

    # Finalise the graph
    plt.ylim((-0, 100))
    plt.xlim((0, 4))
    ax.set(ylabel='% Embers', xlabel='Global mean temperature increase (GMT)',
           title=settings["title"])

    plt.rcParams['svg.fonttype'] = 'none'
    fig.savefig(f"out/{settings['out_file']}.pdf", format="pdf")
    plt.show()
    hlp.report.close()
