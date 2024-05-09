import numpy as np
import matplotlib.pyplot as plt
import helpers
import settings_configs


def cumulative(**kwargs):
    """
    Cumulative distribution of mid-points within transitions
    """

    # Get settings from edb_paper_settings, according to the choices made in keyword arguments (see getsettings)
    settings = settings_configs.get_settings(**kwargs)

    # Create plot
    fig, ax = plt.subplots()

    for dset in helpers.DSets(settings):
        print(f"Processing source: {dset["idset"]} => {dset['name']}")

        # Get data for the current subset and the list of burning embers (lbes)
        data = helpers.getdata(dset)
        lbes = data['lbes']

        rlev = [
            (0.5, '#DC0', '-'),
            (1.5, 'red', '-'),
            (2.5, 'purple', '-')
        ]
        ismulti = len(dset['source']) > 1
        plotrange = False
        if not ismulti and plotrange:
            rlev.append((1.001, '#DC0', '--'))
            rlev.append((1.999, 'red', '--'))
        for rl in rlev:
            haz_chg = []
            for be in lbes:
                haz = helpers.hfn(be, rl[0])
                maxass = max(np.max(be.levels_values('hazl')), be.haz_valid[1])
                if helpers.rfn(be, haz) != rl[0]:
                    msg = 'not reached'
                    print(be.levels_values('hazl'))
                else:
                    msg = 'ok'
                print(f"Risk level: {be}, for rl {rl[0]}, got haz {haz} (rl {helpers.rfn(be, haz)}), {msg}")
                if haz < maxass:
                    haz_chg.append(haz)
                else:
                    print(f"{be.name} is limited to {maxass}°C, corresponding risk: {helpers.rfn(be, maxass)}")

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
            lstyle = ('-', '--')[dset["idset"]] if ismulti else rl[2]
            ax.plot(xx, yy, color=rl[1], linestyle=lstyle)

    # Finalise the graph
    plt.ylim((-0, 100))
    plt.xlim((0, 4))
    ax.set(ylabel='% Embers', xlabel='GMST',
           title=settings["title"])

    plt.rcParams['svg.fonttype'] = 'none'
    fig.savefig(f"out/{settings['out_file']}.svg", format="svg")
    plt.show()
