"""
Usage : python overview.py <settings name in settings_configs.py>
"""
import matplotlib.pyplot as plt
import src.helpers as hlp
import settings_configs
import logging
from itertools import groupby


def overview(**kwargs):
    """
    Arguments are passed to get_settings:
    - settings_choice: the name of the desired settings within settings_config.py
    - a list of options, added to the settings
    """
    # Get settings from edb_paper_settings, according to the choices made in keyword arguments (see getsettings)
    settings = settings_configs.get_settings(**kwargs)
    # Create global report file (Markdown)
    hlp.report_start(settings)

    # Create plot
    fig = plt.figure(figsize=(4, 8))
    ax = plt.axes((0.54, 0.05, 0.44, 0.85))  # (left, bottom, width, height)
    plt.xlabel('Risk level', fontsize=6)
    for spine in ax.spines.values():
        spine.set_edgecolor(None)

    icount = 0
    # Loop over data subsets (defined in the settings)
    for dset in hlp.DSets(settings):
        clean_dset_name = dset['name'].replace('\n', ' ').replace('  ', ' ')
        hlp.report.write(f"Source {dset['idset']}: {clean_dset_name}", title=1)

        # Get data for the current subset (dset)
        data = hlp.getdata(dset)
        lbes = data['embers']  # The list of burning embers in this data subset
        scenarios = data['scenarios']
        hlp.report.embers_list(lbes, onlyids=True)

        # Sort and group embers
        # ---------------------
        # If nothing else makes a difference, sort by name
        lbes.sort(key=lambda abe: abe.name)

        # If there is a scenario (= adaptation related, so far), sort by scenario
        lbes.sort(key=lambda abe: hlp.dict_by_id(scenarios, id=abe.meta['scenario_id'])['adapt_index']
                  if abe.meta['scenario_id'] else -1)
        # Regroup embers in the same scenario group (= adaptation variants)
        lbes.sort(key=lambda abe: abe.meta['scenariogroup_id'] if abe.meta['scenariogroup_id'] else -1)

        # Sort by keywords defined in the settings, if any
        if 'sort_keywords' in dset:
            skey_kw = hlp.get_skey_kw(dset['sort_keywords'])
            lbes.sort(key=skey_kw)

        # Sort by representative key risk category, if required (= for regions!)
        if 'sort_RKRs' in dset:
            lbes.sort(key=hlp.rkr_sortkey)

        # Categorise by RKRs, if required (= for systems)
        if 'categorise_RKRs' in dset:
            lbes.sort(key=hlp.rkr_sortkey)
            gbes = [(g[0], list(g[1])) for g in groupby(lbes, hlp.rkr_sortkey)]
            for i, lbes in enumerate(reversed(gbes)):
                dset['name'], dset['color'] = hlp.RKRCATS6_INFO[hlp.RKRCATS6[lbes[0]]]
                icount = riskchart(lbes[1], dset=dset, ax=ax, istart=icount, data=data)
        else:
            # Draw
            icount = riskchart(lbes, dset=dset, ax=ax, istart=icount, data=data)

    ax.set_xlim(-0.1, 3.1)
    ax.set_ylim(0.5, icount + 0.5)

    # Background
    soften_col = settings['soften_col'] if 'soften_col' in settings else None
    hlp.embers_col_background(xlim=(-1, 4), ylim=ax.get_ylim(), dir='horiz', soften_col=soften_col)
    hlp.report.write(f"GMT levels shown: {settings['GMT']}")

    plt.rcParams['svg.fonttype'] = 'none'
    fig.savefig(f"{settings['out_file']}.pdf", format="pdf")
    plt.show()
    hlp.report.close()


def riskchart(lbes, dset=None, ax=None, istart=0, data=None):

    if dset is None or lbes is None or ax is None or data is None:
        raise ValueError("Missing information for riskchart()")
    if len(lbes) == 0:
        logging.warning("Riskchart was called with no embers")
        return 0

    curcolor = dset['color']
    scenarios = data['scenarios']
    figures = data['figures']
    pi0 = -1
    pi1 = -1
    pi2 = -1
    ppos = -1
    pgid = -1

    def colconf(index):
        if index >= 4:  # High or very high confidence
            lum = 0
        elif index >= 2:  # Medium or medium-high
            lum = 0.45
        elif index >= 0:  # Low or Low-medium
            lum = 0.7
        else:  # Error !
            lum = (0.9, 0, 0)
        if type(lum) is not tuple:
            lum = (lum, lum, lum)
        return lum

    # Show region name, if any:
    if dset['name']:
        plt.rcParams['font.family'] = 'Avenir Next Condensed'
        ax.text(-3.85,  istart + len(lbes) + 0.5, dset['name'], fontsize=7, color=curcolor,
                verticalalignment='top')

    hlp.report.write(f"Large risk change wrt. GMT ({dset['GMT'][0]}->{dset['GMT'][2]}°C) for:")
    seplineleft = -0.45
    plt.hlines(istart + len(lbes) + 0.5, seplineleft, 3.1, color="#AAA", linewidths=0.3, clip_on=False)
    for ibe, be in enumerate(lbes):

        i0, c0 = hlp.rfn(be, dset['GMT'][0], conf=True)
        i1, c1 = hlp.rfn(be, dset['GMT'][1], conf=True)
        i2, c2 = hlp.rfn(be, dset['GMT'][2], conf=True)
        ebpos = istart + len(lbes) - ibe

        if (i2 - i0) > 1.25:
            hlp.report.write(f"* {be.longname} - risk level change: {i0:5.2f}->{i2:5.2f} ")
        gid = be.meta['scenariogroup_id']
        plt.hlines(ebpos-0.5, seplineleft, 3.1, color="#AAA", linewidths=0.3, clip_on=False)
        name = ""
        citekey = hlp.dict_by_id(figures, be.meta['mainfigure_id'])['biblioreference_cite_key']
        convcite = {'AR6': 'A6', 'SR1': '1.5', 'SRO': 'O', 'SRC': 'L'}
        name_sfx = f'[{convcite[citekey[0:3]]}]' if 'hide_chapter' not in dset else ''
        if gid is None:
            name = be.longname
        elif pgid == gid:
            ax.plot((pi0, i0), (ppos, ebpos), color='#0006', zorder=3, linewidth=0.2, solid_capstyle='round')
            ax.plot((pi1, i1), (ppos, ebpos), color='#0006', zorder=3, linewidth=0.45, solid_capstyle='round')
            ax.plot((pi2, i2), (ppos, ebpos), color='#0006', zorder=3, linewidth=0.9, solid_capstyle='round')
        else:
            name = be.group

        if 'hide_category' in dset:
            for hide in dset['hide_category']:
                name = name.replace(hide, '')

        if name:
            name = f"{name.strip().capitalize()} {name_sfx}"
            if 'sort_RKRs' in dset:  # Add name of RKR category
                rkr_cat = hlp.RKRCATS6[hlp.rkr_sortkey(be)]
                name += f" ({rkr_cat[4] if len(rkr_cat) > 4 else rkr_cat[3:]})"

        if be.meta['scenario_id']:
            sc_id = be.meta['scenario_id']
            adapt_index = hlp.dict_by_id(scenarios, sc_id)['adapt_index']
            adapt = ['■', '■□', '■■', '■■□', '■■■'][int(adapt_index*2)-2]
            plt.rcParams['font.family'] = 'DejaVu Sans'
            ax.text(-0.42, ebpos, f"{adapt}", fontsize=4, color='#AAAAAA', verticalalignment='center',
                    horizontalalignment='left', zorder=2)

        # if i3 >= 0:
        #    ax.plot(i3, ebpos, 's', color=scolor, markeredgewidth=0.2, markeredgecolor="white", markersize=4)
        if i2 >= 0:
            ax.plot(i2, ebpos, 'o', color=colconf(c2), markeredgewidth=0.3, markeredgecolor="white", markersize=6)
        if i1 >= 0:
            ax.plot(i1, ebpos, 'o', color=colconf(c1), markeredgewidth=0.3, markeredgecolor="white", markersize=3.7)
        if i0 >= 0:
            ax.plot(i0, ebpos, 'o', color=colconf(c0), markeredgewidth=0.3, markeredgecolor="white", markersize=2)
        if name:
            plt.rcParams['font.family'] = 'Avenir Next Condensed'
            ax.text(-0.5, ebpos + 0.3, f"{name}", fontsize=4, color=curcolor,
                    horizontalalignment='right', verticalalignment='top', wrap=True, linespacing=0.95)
        pi0 = i0
        pi1 = i1
        pi2 = i2
        ppos = ebpos
        pgid = gid

    ax.vlines(-0.1, 0.5, istart + len(lbes) + 0.5, color="#AAA", linewidth=0.3, clip_on=False)
    ax.set_yticks([])
    ax.set_xticks([0, 1, 2, 3], labels=['Undetectable', 'Moderate', 'High', 'Very\nhigh'], fontsize=6)

    return istart + len(lbes)
