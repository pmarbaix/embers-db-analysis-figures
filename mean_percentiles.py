"""
Usage : python edb_paper_xy.py <settings name in settings_datasets_configs.py> [<optional graph type>]
"""
import numpy as np
import embermaker.helpers as embhlp
import matplotlib.pyplot as plt
import helpers
from embermaker.embergraph import EmberGraph
from embermaker import ember as emb
from sys import exit

# import random
logger = embhlp.Logger()  # Standard log function in EmberMaker

# Create a dumb ember graph because we need a cpal (might be removed later)
egr = EmberGraph()
labes = []


def main(**kwargs):
    # Get settings from edb_paper_settings, according to the choices made in keyword arguments (see getsettings)
    settings = helpers.getsettings(**kwargs)

    # Define GMT (= 'hazard' metric) levels for which to calculate
    hazls = np.arange(0.0, 4, 0.05)

    # Create plot
    fig, ax = plt.subplots()
    plt.subplots_adjust(top=0.86, left=0.2, right=0.98)
    ax.set(xlabel='Global mean temperature change (GMT)')
    ax.set_title(settings["title"], pad=36, fontsize=9)
    plt.ylim((-0.1, 3.1))

    # Loop over data subsets (defined in the settings)
    # ------------------------------------------------
    dsets = helpers.DSets(settings)
    for iis, dset in enumerate(dsets):
        print(f"Processing source: {iis} => {dset['name']}")

        # Get data for the current subset (dset), from the server or file
        data = helpers.getdata(dset)
        lbes = data['lbes']

        # Optionally remove embers that are not "complete", that is, which were not assessed for our full graph range
        if dset and 'remove_incomplete' in dset:
            lbes = rem_incomplete(lbes, hazls[-1])

        if dset["type"] == "percentiles":
            labes = percentiles(data, lbes, dset, hazls, fig, iis)
        else:
            labes = None

    plt.rcParams['svg.fonttype'] = 'none'
    fig.savefig(f"out/{settings['out_file']}.svg", format="svg")
    plt.show()

    # Create the ember graph, if any embers were created, and draw
    if labes:
        outfile = 'out/ember_' + settings['out_file']
        agr = EmberGraph(outfile, grformat="PDF")
        agr.gp['haz_axis_top'] = 4.0
        agr.gp['conf_lines_ends'] = 'arrow'  # 'bar', 'arrow', or 'datum' (or None)
        agr.gp['leg_pos'] = 'none'
        agr.add(labes)
        agr.draw()

def percentiles(data, lbes, dset, hazls, fig, iis):
    # Percentiles, mean and median diagrams
    # -------------------------------------
    ax = fig.axes[0]
    if 'wchapter' in dset:  # Optional 'per chapter' weighting
        emb_figs = data['emb_figs']
    else:
        emb_figs = None

    print(f'Full list of embers longnames and ids {[be.longname + " (" + str(be.id) + ")" for be in lbes]}')

    # Calculate risk percentiles and averages:
    risk_p10, risk_p50, risk_p90, risk_avgs = aggreg(lbes, hazls, exprisk=dset.get('exprisk', False),
                                                     ax=ax, iis=iis, dset=dset, emb_figs=emb_figs)

    # Coloured background
    helpers.embers_col_background(xlim=(float(hazls[0]), float(hazls[-1])))

    # Plot
    if 'mean' in dset['subtype']:
        # Plot mean
        ax.plot(hazls, risk_avgs, color=dset['style'][0], linestyle='-')
    if 'median' in dset['subtype']:
        # and/or the median
        ax.plot(hazls, risk_p50, color=dset['style'][0], linestyle='--')
        emberbase = risk_p50  # if median is shown, it will be the choice for the ember
    else:
        emberbase = risk_avgs
    # Plot percentiles
    if dset["ndsets"] <= 2 and len(dset['subtype']) < 2:  # add these percentiles if plot is not 'crowded' w. lines.
        ax.plot(hazls, risk_p10, color=dset['style'][0], linestyle="--")
        ax.plot(hazls, risk_p90, color=dset['style'][0], linestyle="--")

    ax.grid(axis='x', color='0.65')

    # 'Aggregated ember'
    # - - - - - - - - -
    abe = emb.Ember(name=dset['name'], haz_valid=[0, 4], haz_name_std='GMT')

    aghaz = lambda risk: np.interp(risk, emberbase, hazls)
    percentiles = {'tmin': 0.001, 'p5': 0.05, 'p10': 0.1, 'p20': 0.2, 'p30': 0.3, 'p40': 0.4, 'p50': 0.5,
                   'p60': 0.6, 'p70': 0.7, 'p80': 0.8, 'p90': 0.9, 'p95': 0.95, 'tmax': 0.999}
    maxrisk = emberbase[-1]

    # Undetectable to moderate (calculate levels within the transition + add transition to burning ember)
    translevels = {per: aghaz(val) for per, val in percentiles.items()}
    abe.trans_create(name='undetectable to moderate', confidence='undefined', **translevels)
    # Modertate to high
    translevels = {per: aghaz(1.0 + val) for per, val in percentiles.items()}
    abe.trans_create(name='moderate to high', confidence='undefined', **translevels)
    print("Moderate to high: " + str([f"{ky}: {tr:.2f}{egr.gp['haz_unit']}" for ky, tr in translevels.items()]))
    # High to very high
    # Note: max risk is generally not reached on average! => avoid undefined levels + add true max risk:
    translevels: dict = {pcent: aghaz(2.0 + val) for pcent, val in percentiles.items() if 2.0 + val < maxrisk}
    if 'tmax' not in translevels:
        per = f"p{int((maxrisk - 2.0) * 100)}"
        translevels[per] = aghaz(maxrisk)
        translevels['tmax'] = 5.0  # A max is needed so that the transition's range (vertical bar) has an end
    abe.trans_create(name='high to very high', confidence='undefined', **translevels)
    print("High to very high: " + str([f"{ky}: {tr:.2f}{egr.gp['haz_unit']}" for ky, tr in translevels.items()]))
    abe.group = dset['title']
    labes.append(abe)

    return labes

def aggreg(lbes, hazls: np.array, ax=None, iis=0, dset=None, exprisk=False, emb_figs=None):
    """
    :param lbes:
    :param hazls:
    :param exprisk: Whether to use an exponential risk index (2**<received index>)
    :return:
    """

    risk_tots = np.zeros(len(hazls))
    risk_avgs = np.zeros(len(hazls))
    risk_p10 = np.zeros(len(hazls))
    risk_p50 = np.zeros(len(hazls))
    risk_p90 = np.zeros(len(hazls))

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
                print(f"{source} > weight of embers: { be.ext['weight']:5.2f}")  # For testing: chapter name > ember name
                new_source_print = source
            print(f"   Ember: {be}")
    else:
        for be in lbes:
            be.ext['weight'] = 1.0

    for lev, hazl in enumerate(hazls):
        risk_hazl = []
        weights = []
        names=[]
        for be in lbes:
            intrisk = rfn(be, hazl)
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

        # https://numpy.org/doc/stable/reference/generated/numpy.percentile.html
        #risk_p10[lev], risk_p50[lev], risk_p90[lev] = (
        #    np.percentile(risk_hazl, (10.0, 50.0, 90.0), method='linear'))
        risk_p10[lev], risk_p50[lev], risk_p90[lev] = (
            helpers.weighted_percentile(risk_hazl, (10.0, 50.0, 90.0), weights=weights))

        if abs(hazl-3.0) < 0.02:  # At 3°C, print information about what is "in" p10 and p90.
            names_risk = list(zip(names, risk_hazl))
            names_risk.sort(key= lambda nr: nr[1])
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
                ax.text(hazl, 3.38 - iis/9, f"n={nemb}", color=dset['style'][0],
                        fontsize=8, horizontalalignment='left')
                ax.text(0.2, 2.8 - iis/6, f"{dset['name']}", color=dset['style'][0],
                        fontsize=9, horizontalalignment='left')


    print(f"Standard deviation of the mean value of risk levels: {np.mean(rmean_std):.4f}; "
          f"max: {np.max(rmean_std):.4f}")

    for be in lbes:
        maxeval = max(np.max(be.levels_values('hazl')), be.haz_valid[1])
        if maxeval <= hazls[-1]:
            print(f"INFO: Ember {be} remains in spite of lack of data (available up to {maxeval})")

    return risk_p10, risk_p50, risk_p90, risk_avgs

def rfn(be, hazl):
    be.egr = egr
    try:
        return np.interp(hazl, be.levels_values('hazl'), be.levels_values('risk'))
    except ValueError:
        raise ValueError(f"Risk could not be interpolated for the given hazard level (rfn) '{be.name}'; "
                         f"n levels: {len(be.levels_values('hazl'))}")

def hfn(be, rlev):
    be.egr = egr
    return np.interp(rlev, be.levels_values('risk'), be.levels_values('hazl'))

def rem_incomplete(lbes, mxhaz):
    newlbes = []
    for be in lbes:
        if max(np.max(be.levels_values('hazl')), be.haz_valid[1]) < mxhaz:
            logger.addwarn(
                f"Removed ember {be} / no assessment for GMT > "
                f"{max(np.max(be.levels_values('hazl')), be.haz_valid[1])}")
        else:
            newlbes.append(be)
    logger.addwarn(f"#remaining embers: {len(lbes)}")
    return newlbes

if __name__ == '__main__':
    exit(main())
