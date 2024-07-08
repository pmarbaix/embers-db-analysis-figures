import numpy as np
import matplotlib.pyplot as plt
import src.helpers as hlp
import settings_configs
from embermaker.embergraph import EmberGraph
from embermaker import ember as emb
from itertools import groupby

def mean_percentiles(**kwargs):
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

    # Define GMT (= 'hazard' metric) levels for which to calculate
    hazlevs = np.arange(0.0, 4, 0.05)

    # Create storage for the "aggregated ember(s)" (an ember may be created for each data subset)
    aggreg_bes = []

    # Loop over data subsets (defined in the settings)
    for dset in hlp.DSets(settings):
        hlp.report.write(f"Source {dset["idset"]}: {dset['name']}", title=1)

        # Get data for the current subset (dset)
        data = hlp.getdata(dset)
        lbes = data['embers']  # The list of burning embers in this data subset

        # Prepare figure
        ax.set(xlabel='Global mean temperature change (GMT)')
        ax.set_title(dset["title"], pad=36, fontsize=9)
        plt.subplots_adjust(top=0.86, left=0.2, right=0.98)
        plt.ylim((-0.1, 3.1))

        # Optionally remove embers that are not "complete" = which were not assessed for the full range of hazlevs
        if 'remove_incomplete' in dset:
            lbes = hlp.rem_incomplete(lbes, hazlevs[-1])

        if 'wchapter' in dset['options']:  # Optional 'per chapter' weighting: this will provide the chapter + fig n°
            figures = data['figures']  # A list of embers providing information on the main figure containing them
        else:
            figures = None
            # if no weighting, report the list of embers (with weighing, this will be done when weights ar calculated)
            hlp.report.embers_list(lbes)

        # Calculate risk percentiles and averages:
        risk_p10, risk_p50, risk_p90, risk_avgs = aggreg(lbes, hazlevs, exprisk=dset.get('exprisk', False),
                                                         ax=ax, dset=dset, figures=figures)

        # Coloured background
        soften_col = dset['soften_col'] if 'soften_col' in dset else None
        hlp.embers_col_background(xlim=(float(hazlevs[0]), float(hazlevs[-1])), soften_col=soften_col)

        # Plot
        if 'mean' in dset['options']:
            # Plot mean
            ax.plot(hazlevs, risk_avgs, color=dset['style'][0], linestyle='-')
        if 'median' in dset['options']:
            # and/or the median
            ax.plot(hazlevs, risk_p50, color=dset['style'][0], linestyle='--')
            emberbase = risk_p50  # if median is shown, it will be the choice for the ember
        else:
            emberbase = risk_avgs
        # Plot percentiles
        if 'p10-p90' in dset['options']:
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
        # High to very high
        # Note: max risk is generally not reached on average! => avoid undefined levels + add true max risk:
        translevels: dict = \
            {pcent: aggreghaz(2.0 + val) for pcent, val in calc_for_percent.items() if 2.0 + val < maxrisk}
        if 'tmax' not in translevels:
            per = f"p{int((maxrisk - 2.0) * 100)}"
            translevels[per] = aggreghaz(maxrisk)
            translevels['tmax'] = 5.0  # A max is needed so that the transition's range (vertical bar) has an end
        abe.trans_create(name='high to very high', confidence='undefined', **translevels)
        # print("High to very high: " + str([f"{ky}: {tr:.2f}°C" for ky, tr in translevels.items()]))
        abe.group = dset['title']
        aggreg_bes.append(abe)

    # Create the aggregated ember graph, if embers were created, and draw
    if aggreg_bes and 'ember' in settings['options']:
        outfile = 'out/ember_' + settings['out_file']
        agr = EmberGraph(outfile, grformat="PDF")
        agr.gp['haz_name_std'] = 'GMT'  # Needed because it is set for the ember (above)
        agr.gp['haz_axis_top'] = 4.0
        agr.gp['gr_fnt_size'] = 10
        agr.gp['conf_lines_ends'] = 'bar'  # 'bar', 'arrow', or 'datum' (or None)
        agr.gp['leg_pos'] = 'none'  # No risk levels legend
        agr.add(aggreg_bes)
        agr.draw()

    # Finalise the x-y percentile and/or median plots
    plt.rcParams['svg.fonttype'] = 'none'
    fig.savefig(f"out/{settings['out_file']}.pdf", format="pdf")
    plt.show()
    hlp.report.close()


def aggreg(lbes, hazlevs: np.array, ax=None, dset=None, exprisk=False, figures=None):
    """
    Draws the requested percentiles and/or mean among the set of embers (lbes), for each hazard level in hazls.
    :param lbes: list of burning embers
    :param hazlevs: list of hazard levels for which to calculate aggregated values
    :param ax: matplotlib axes
    :param dset: settings for the current data subset
    :param exprisk: whether to use an exponential risk index (2**<received index>)
    :param figures: figure list containing data about each figure, for weighting; None => each ember has a weight of 1
    :return: p10, median, p90, average
    """
    risk_tots = np.zeros(len(hazlevs))
    risk_avgs = np.zeros(len(hazlevs))
    risk_p10 = np.zeros(len(hazlevs))
    risk_p50 = np.zeros(len(hazlevs))
    risk_p90 = np.zeros(len(hazlevs))

    rmean_std = []
    nemb = 0

    if figures:
        hlp.report.write(f"Weighting per chapter/figure (n total={len(lbes)})", title=2)
        hlp.report.table_head("Weighting group", "Embers", "Weight")
        # Calculate weights: 'equal weight per chapter/figure' option
        # (weighting per chapter is the rule, per figure is applied to SRCCL and SR1.5, due to differences in scope)
        # Create a dict that will link the id of each ember (the key) to the label of its weighting group:
        be_groups = dict()
        for be in lbes:
            # Get information about the main figure containing ember be:
            figinfo: dict = hlp.dict_by_id(figures, be.meta['mainfigure_id'])
            # Generate and set the group label for each ember
            if figinfo['biblioreference.cite_key'] in ('SRCCL', 'SR1.5'):  # Exception: split by figure
                be_groups[be.id] = figinfo['biblioreference.cite_key'] + '-' + str(figinfo['number'])
            else:
                be_groups[be.id] = figinfo['biblioreference.cite_key']

        groups_list = list(be_groups.values())
        for group_key, be_set in groupby(lbes, lambda be: be_groups[be.id]):
            weight = 1.0 / groups_list.count(group_key)
            names = ""
            for be in be_set:
                be.ext['weight'] = weight
                names += f"{be.longname}({be.id});<br>"
            hlp.report.table_write(group_key, names, f"{weight:5.2f}")
    else:
        for be in lbes:
            be.ext['weight'] = 1.0

    # Calculate mean and percentiles among all embers, for each hazard level (x axis values)
    extend = []
    for lev, hazl in enumerate(hazlevs):
        # For each hazard level, lists of ember-related data will be generated for the 'included' embers (see below)
        risk_hazl = []
        weights = []
        names = []
        for be in lbes:
            # Include the data only if we have indications that it was assessed up to that 'hazard' level:
            #   - haz_valid[1] indicates that it is valid above the current level, or
            #   - a transition was assessed above the current level (= accepted even if above haz_valid[1])
            # With or without weighting (weight=1), 'removing' embers does not change the weight of other embers
            #   (figures share the same haz_valid[1]: in most cases, all embers of a group are removed together).
            trmax = np.max(be.levels_values('hazl'))
            if max(trmax, be.haz_valid[1]) >= hazl:
                if hazl > be.haz_valid[1] and be.id not in extend:
                    hlp.report.write(f"Extended validity for ember '{be.longname}': {be.haz_valid[1]} -> {trmax}")
                    extend.append(be.id)
                intrisk = hlp.rfn(be, hazl)
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
            hlp.weighted_percentile(risk_hazl, (10.0, 50.0, 90.0), weights=weights))

        if abs(hazl-3.0) < 0.02:  # At 3°C, print information about what is "in" p10 and p90.
            names_risk = list(zip(names, risk_hazl))
            names_risk.sort(key=lambda nr: nr[1])
            hlp.report.write(f"Information about percentiles at 3°C", title=2)
            hlp.report.write(f"Risk level at p10:{risk_p10[lev]:4.1f};"
                             f"\t p50:{risk_p50[lev]:4.1f};\t p90:{risk_p90[lev]:4.1f}")
            report_percentile(10, risk_p10[lev], names_risk)
            report_percentile(90, risk_p90[lev], names_risk)

        if exprisk:
            risk_avgs[lev] = np.log2(risk_tots[lev] / np.sum(weights))
        else:
            risk_avgs[lev] = risk_tots[lev] / np.sum(weights)

        if nemb != len(risk_hazl):
            nemb = len(risk_hazl)
            # Show n= when the number of embers changes
            if ax:
                ax.text(hazl, 3.38 - dset["idset"] / 9, f"n={nemb}", color=dset['style'][0],
                        fontsize=8, horizontalalignment='left')
                ax.text(0.2, 2.8 - dset["idset"] / 6, f"{dset['name']}", color=dset['style'][0],
                        fontsize=9, horizontalalignment='left')

    hlp.report.write(f"Mean over the hazard levels of the standard deviation of the risk levels: "
                     f"{np.mean(rmean_std):.4f}; max over hazard levels: {np.max(rmean_std):.4f}")

    return risk_p10, risk_p50, risk_p90, risk_avgs


def report_percentile(percentile, prisk, names_risk):
    """
    Reports information on embers above or below the given percentile
    :param percentile:
    :param prisk:
    :param names_risk: a list of tuples (ember name, risk at the considered GMT)
    :return:
    """
    side = "<=" if percentile < 50 else ">="
    hlp.report.write(f"Embers {side} p{percentile}", title=3)
    hlp.report.table_head("Embers", "Risk level")
    for risk, group in groupby(names_risk, lambda x: x[1]):
        if (risk <= prisk and percentile < 50) or (risk >= prisk and percentile > 50):
            hlp.report.table_write(*('<br> '.join(nr[0] for nr in group), f"{risk:4.2f}"))
    hlp.report.write(f"{len([1 for namris in names_risk if namris[1] == prisk])} embers strictly at p{percentile}")
