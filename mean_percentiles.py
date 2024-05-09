import numpy as np
import matplotlib.pyplot as plt
import helpers
import settings_configs
from embermaker.embergraph import EmberGraph
from embermaker import ember as emb
from sys import exit, argv


def mean_percentiles(**kwargs):
    """
    Percentiles, mean and median plots
    """
    # Get settings from edb_paper_settings, according to the choices made in keyword arguments (see getsettings)
    settings = settings_configs.get_settings(**kwargs)

    # Create plot
    fig, ax = plt.subplots()

    # Define GMT (= 'hazard' metric) levels for which to calculate
    hazlevs = np.arange(0.0, 4, 0.05)

    # Create storage for the "aggregated ember(s)" (an ember may be created for each data subset)
    aggreg_bes = []

    # Loop over data subsets (defined in the settings)
    for dset in helpers.DSets(settings):
        print(f"Processing source: {dset["idset"]} => {dset['name']}")

        # Get data for the current subset (dset)
        data = helpers.getdata(dset)
        lbes = data['lbes']  # The list of burning embers in this data subset

        # Prepare figure
        ax.set(xlabel='Global mean temperature change (GMT)')
        ax.set_title(dset["title"], pad=36, fontsize=9)
        plt.subplots_adjust(top=0.86, left=0.2, right=0.98)
        plt.ylim((-0.1, 3.1))

        # Optionally remove embers that are not "complete" = which were not assessed for the full range of hazlevs
        if 'remove_incomplete' in dset:
            lbes = helpers.rem_incomplete(lbes, hazlevs[-1])

        if 'wchapter' in dset:  # Optional 'per chapter' weighting
            emb_figs = data['emb_figs']
        else:
            emb_figs = None

        print(f'Full list of embers longnames and ids {[be.longname + " (" + str(be.id) + ")" for be in lbes]}')

        # Calculate risk percentiles and averages:
        risk_p10, risk_p50, risk_p90, risk_avgs = aggreg(lbes, hazlevs, exprisk=dset.get('exprisk', False),
                                                         ax=ax, dset=dset, emb_figs=emb_figs)

        # Coloured background
        helpers.embers_col_background(xlim=(float(hazlevs[0]), float(hazlevs[-1])))

        # Plot
        if 'mean' in dset['subtype']:
            # Plot mean
            ax.plot(hazlevs, risk_avgs, color=dset['style'][0], linestyle='-')
        if 'median' in dset['subtype']:
            # and/or the median
            ax.plot(hazlevs, risk_p50, color=dset['style'][0], linestyle='--')
            emberbase = risk_p50  # if median is shown, it will be the choice for the ember
        else:
            emberbase = risk_avgs
        # Plot percentiles
        if dset["ndsets"] <= 2 and len(dset['subtype']) < 2:  # add these percentiles if plot is not 'crowded' w. lines.
            ax.plot(hazlevs, risk_p10, color=dset['style'][0], linestyle="--")
            ax.plot(hazlevs, risk_p90, color=dset['style'][0], linestyle="--")

        ax.grid(axis='x', color='0.65')

        # 'Aggregated ember'
        # - - - - - - - - -
        abe = emb.Ember(name=dset['name'], haz_valid=[0, 4], haz_name_std='GMT')

        def aggreghaz(risk):
            return np.interp(risk, emberbase, hazlevs)
        calc_for_percent = {'tmin': 0.001, 'p5': 0.05, 'p10': 0.1, 'p20': 0.2, 'p30': 0.3, 'p40': 0.4, 'p50': 0.5,
                            'p60': 0.6, 'p70': 0.7, 'p80': 0.8, 'p90': 0.9, 'p95': 0.95, 'tmax': 0.999}
        maxrisk = emberbase[-1]

        # Undetectable to moderate (calculate levels within the transition + add transition to burning ember)
        translevels = {per: aggreghaz(val) for per, val in calc_for_percent.items()}
        abe.trans_create(name='undetectable to moderate', confidence='undefined', **translevels)
        # Modertate to high
        translevels = {per: aggreghaz(1.0 + val) for per, val in calc_for_percent.items()}
        abe.trans_create(name='moderate to high', confidence='undefined', **translevels)
        print("Moderate to high: " + str([f"{ky}: {tr:.2f}°C" for ky, tr in translevels.items()]))
        # High to very high
        # Note: max risk is generally not reached on average! => avoid undefined levels + add true max risk:
        translevels: dict = \
            {pcent: aggreghaz(2.0 + val) for pcent, val in calc_for_percent.items() if 2.0 + val < maxrisk}
        if 'tmax' not in translevels:
            per = f"p{int((maxrisk - 2.0) * 100)}"
            translevels[per] = aggreghaz(maxrisk)
            translevels['tmax'] = 5.0  # A max is needed so that the transition's range (vertical bar) has an end
        abe.trans_create(name='high to very high', confidence='undefined', **translevels)
        print("High to very high: " + str([f"{ky}: {tr:.2f}°C" for ky, tr in translevels.items()]))
        abe.group = dset['title']
        aggreg_bes.append(abe)

    # Create the aggregated ember graph, if embers were created, and draw
    if aggreg_bes:
        outfile = 'out/ember_' + settings['out_file']
        agr = EmberGraph(outfile, grformat="PDF")
        agr.gp['haz_axis_top'] = 4.0
        agr.gp['conf_lines_ends'] = 'arrow'  # 'bar', 'arrow', or 'datum' (or None)
        agr.gp['leg_pos'] = 'none'  # No risk levels legend
        agr.add(aggreg_bes)
        agr.draw()

    # Finalise the x-y percentile and/or median plots
    plt.rcParams['svg.fonttype'] = 'none'
    fig.savefig(f"out/{settings['out_file']}.svg", format="svg")
    plt.show()


def aggreg(lbes, hazlevs: np.array, ax=None, dset=None, exprisk=False, emb_figs=None):
    """
    Draws the requested percentiles and/or mean among the set of embers (lbes), for each hazard level in hazls.
    :param lbes: list of burning embers
    :param hazlevs: list of hazard levels for which to calculate aggregated values
    :param ax: matplotlib axes
    :param dset: settings for the current data subset
    :param exprisk: whether to use an exponential risk index (2**<received index>)
    :param emb_figs: chapter figures - for weighting by average Todo: revise
    :return: p10, median, p90, average
    """
    risk_tots = np.zeros(len(hazlevs))
    risk_avgs = np.zeros(len(hazlevs))
    risk_p10 = np.zeros(len(hazlevs))
    risk_p50 = np.zeros(len(hazlevs))
    risk_p90 = np.zeros(len(hazlevs))

    rmean_std = []
    nemb = 0

    # Calculate weights: 'equal weight per chapter' option
    if emb_figs:
        print(f"INFO: equalisation of weights per chapter is active!")
        sources = {}
        for be in lbes:   # Get weighting groups (= chapters, with exceptions!)
            figinfo = emb_figs[str(be.id)]
            if figinfo['source_key'] in ('SRCCL', 'SR1.5'):  # Exception: split by figure
                subdivby = '-' + str(figinfo['number'])
            else:
                subdivby = ''
            sources[be.id] = figinfo['source_key']+subdivby

        sources_list = list(sources.values())
        new_source_print = ""
        for be in lbes:
            source = sources[be.id]
            # print(f"{source} > {be}")  # For testing: chapter name > ember name
            be.ext['weight'] = 1.0 / (sources_list.count(source))
            if source != new_source_print:
                print(f"{source} > weight of embers: {be.ext['weight']:5.2f}")
                new_source_print = source
            print(f"   Ember: {be}")
    else:
        for be in lbes:
            be.ext['weight'] = 1.0

    for lev, hazl in enumerate(hazlevs):
        risk_hazl = []
        weights = []
        names = []
        for be in lbes:
            intrisk = helpers.rfn(be, hazl)
            # Include the data only if we have indications that it was assessed up to that 'hazard' level
            if max(np.max(be.levels_values('hazl')), be.haz_valid[1]) >= hazl:
                if exprisk:
                    risk_tots[lev] += 2**intrisk * be.ext['weight']
                else:
                    risk_tots[lev] += intrisk * be.ext['weight']
                # Percentiles are not affected by using an exp scale or not => no need to calculate using exp:
                risk_hazl.append(intrisk)
                weights.append(be.ext['weight'])
                names.append(be.longname)

        rmean_std.append(np.std(risk_hazl)/np.sqrt(len(lbes)))

        risk_p10[lev], risk_p50[lev], risk_p90[lev] = (
            helpers.weighted_percentile(risk_hazl, (10.0, 50.0, 90.0), weights=weights))

        if abs(hazl-3.0) < 0.02:  # At 3°C, print information about what is "in" p10 and p90.
            names_risk = list(zip(names, risk_hazl))
            names_risk.sort(key=lambda nr: nr[1])
            print(f"Percentiles at 3°C: {risk_p10[lev], risk_p50[lev], risk_p90[lev]}")
            print(f"<= p10: {[namris for namris in names_risk if namris[1] <= risk_p10[lev]]}")
            print(f"Of which "
                  f"{len([1 for namris in names_risk if namris[1] == risk_p10[lev]])} embers strictly at p10")
            print(f">= p90: {[namris for namris in names_risk if namris[1] >= risk_p90[lev]]}")
            print(f"Of which "
                  f"{len([1 for namris in names_risk if namris[1] == risk_p90[lev]])} embers strictly at p90")

        if exprisk:
            risk_avgs[lev] = np.log2(risk_tots[lev] / np.sum(weights))
        else:
            risk_avgs[lev] = risk_tots[lev] / np.sum(weights)

        if nemb != len(risk_hazl):
            nemb = len(risk_hazl)
            print(f"At {hazl}°C, the number of available embers is: {nemb}")
            if ax:
                ax.text(hazl, 3.38 - dset["idset"] / 9, f"n={nemb}", color=dset['style'][0],
                        fontsize=8, horizontalalignment='left')
                ax.text(0.2, 2.8 - dset["idset"] / 6, f"{dset['name']}", color=dset['style'][0],
                        fontsize=9, horizontalalignment='left')

    print(f"Standard deviation of the mean value of risk levels: {np.mean(rmean_std):.4f}; "
          f"max: {np.max(rmean_std):.4f}")

    for be in lbes:
        maxeval = max(np.max(be.levels_values('hazl')), be.haz_valid[1])
        if maxeval <= hazlevs[-1]:
            print(f"INFO: Ember {be} remains in spite of lack of data (available up to {maxeval})")

    return risk_p10, risk_p50, risk_p90, risk_avgs


if __name__ == '__main__':
    exit(mean_percentiles(kwargs=argv))
