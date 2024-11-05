import numpy as np
import embermaker.helpers as embhlp
from itertools import groupby
from collections import Counter
import src.helpers as hlp
import settings_configs
import re
import pandas as pd
logger = embhlp.Logger()  # Standard log function in EmberMaker


def get_fig_sortkey(biblioreferences):
    def fig_sortkey(fig):
        """
        Sort key for figures in a chronological + chapter report order
        :param fig: figure
        :return: sortkey
        """
        fignum = fig['number']
        # Get the number of this figure within is chapter, if any (= *.number)
        figkeys = fignum.split(".")
        figinrep = figkeys[1] if len(figkeys) > 1 else 0
        figinrep = int(re.sub('[^0-9]', '', str(figinrep)))
        rep = [br for br in biblioreferences if br['cite_key'] == fig['biblioreference_cite_key']][0]
        chapter = rep['chapter']
        if chapter is None:  # Try to get an integer from the first part of the figure number
            try:  # Reject CCPs ect. et end of list, after chapters
                chapter = int(re.sub('[^0-9]', '', str(figkeys[0]))) + 100
            except ValueError:
                chapter = 100
        sortkey = [int('RFC' in fig['shortname']), rep['year'], chapter, figinrep]
        return sortkey
    return fig_sortkey


def embers_table(**kwargs):
    """
    Generates a summary table for 'all' embers, by chapter.
    'All' normally refers to the "included" embers, that is, those with the included field >= 0;
    To change the inclusion rule, use the 'included' parameter within settings_configs.py (see config "Full").
    :param kwargs:
    :return:
    """
    # Get settings from edb_paper_settings, according to the choices made in keyword arguments (see getsettings)
    settings = settings_configs.get_settings(**kwargs)
    # Create global report file (Markdown)
    # Note: this is the generic processing report, its content is not the same as the summary table generated here.
    #       the processing report list all embers included in the table + shows conversions to GMT
    hlp.report_start(settings)
    dset = settings  # The summary table include all embers: no subset here (unlike in other processing scripts)

    # Get data for the current subset and the list of burning embers (lbes)
    dset["conv_gmt"] = "if_possible"
    data = hlp.getdata(dset)
    lbes = data['embers']
    biblioreferences = data['biblioreferences']
    hlp.report.embers_list(lbes)

    embers = data['embers']
    embers_figids = [be.meta['mainfigure_id'] for be in embers]
    # Remove any figure which would not include any ember taken into account here
    # (in practice: this removes the SRCCL - "sup mat" figures, which are not in the report,
    #  and the TAR SPM; this will need to be adjusted if new embers beyond AR6 are added)
    figures = [fig for fig in data['figures'] if fig['id'] in embers_figids]
    scenarios = data['scenarios']

    dbes = {be.id: be for be in lbes}

    fig_sortkey = get_fig_sortkey(biblioreferences)
    figures.sort(key=fig_sortkey)
    # Create the summary table (Simple md files are crated by the small "Report" class)
    tableout = hlp.Report(settings['out_file']+'_out.md')
    tableout.table_head("Report: main figure", "*shortname* <br/> (title)", "#other adapt.", "#high adapt.", "#total",
                        "High risk at mean T (min, max)")

    # Store 'grand total' for showing at the end of the table
    gt_o_adap = 0
    gt_h_adap = 0
    gt_c_all = 0

    # Loop over figures = lines in the summary table
    hlp.report.table_head("Report", "Figure number", "Source")
    for fig in figures:
        hlp.report.table_write(fig['biblioreference_cite_key'], fig['number'], fig['biblioreference'])
        be_ids = [be.id for be in embers if be.meta['mainfigure_id'] == fig['id']]
        n_other_adap = 0
        n_high_adap = 0
        c_all = 0
        hr_bot = np.Inf
        hr_top = np.NINF
        hr_mid = []
        be_gmt = True
        be_haz_names = set()

        for beid in be_ids:
            try:
                be = dbes[beid]
            except KeyError:
                logger.addwarn(f"Could not find ember! id: {beid} figure: {fig}")
                continue
            c_all += 1
            hr_mid.append(hlp.hfn(be, 1.5))
            hr_bot = min(hr_bot, hlp.hfn(be, 1.0001))
            hr_top = max(hr_top, hlp.hfn(be, 1.9999))
            if be.meta['scenario_id']:
                if hlp.dict_by_id(scenarios, be.meta['scenario_id'])["name"] == "High adaptation":
                    n_high_adap += 1
                else:
                    n_other_adap += 1
            if be.haz_name_std != "GMT":
                be_gmt = False
                be_haz_names.add(be.haz_name_std)
        if be_gmt:
            hr_message = f" {np.mean(hr_mid):5.2f} ({hr_bot:4.2f}-{hr_top:4.2f})"
        else:
            hr_message = f"Not temperature {list(be_haz_names)}"
        tableout.table_write(f"{fig['biblioreference_cite_key']}:<br/> fig. {fig['number']}",
                             f"*{fig['shortname']}* <br/> ({fig['title']})",
                             n_other_adap, n_high_adap, c_all, hr_message)
        gt_o_adap += n_other_adap
        gt_h_adap += n_high_adap
        gt_c_all += c_all
    tableout.table_write("Total", "", gt_o_adap, gt_h_adap, gt_c_all, "")
    tableout.close(total=False)


def embers_rkr_table(**kwargs):
    """
    Produces a summary table for embers grouped by key risk (RKR) category.
    The table contains the "included" embers, that is, those with the included field >= 0;
    To change the inclusion rule, use the 'included' parameter within settings_configs.py (see config "Full").
    :param kwargs:
    :return:
    """
    # Get settings from edb_paper_settings, according to the choices made in keyword arguments (see getsettings)
    settings = settings_configs.get_settings(**kwargs)
    # Create global report file (Markdown)
    # Note: this is the generic processing report, its content is not the same as the summary table generated here.
    #       the processing report list all embers included in the table + shows conversions to GMT
    hlp.report_start(settings)
    dset = settings  # The summary table include all embers: no subset here (unlike in other processing scripts)

    # Get data for the current subset and the list of burning embers (lbes)
    dset["conv_gmt"] = "if_possible"

    data = hlp.getdata(dset)

    embers = data['embers']
    figures = data['figures']
    bibrefs = data['biblioreferences']
    bibrefs.sort(key=lambda br: int(br['year'])*100+(br['chapter'] if br['chapter'] is not None else 0))

    for be in embers:
        if '\n' in be.keywords:
            # This should not happen: it would be handled correctly, but calls for removing line-ends within the DB.
            # In the future, the Embers DB should remove unexpected characters automatically.
            # (they were never *visible* in the online CREE but some were found, and they are hard to remove manually)
            print(f'DB anomaly: there is a line-end character in the list of keywords for '
                  f'"{be.longname}" ({be.keywords.replace('\n', '¶')})')
            be.keywords = be.keywords.strip('\n')
    embers.sort(key=hlp.rkr_sortkey)
    gbes = [(g[0], list(g[1])) for g in groupby(embers, hlp.rkr_sortkey)]
    
    # Create the summary table
    tableout = hlp.Report(settings['out_file']+'_out.md')
    tableout.table_head("RKR category", "#Embers", "Adapt. variants",
                        "High risk at mean T (min, max)")

    # Store 'grand total' (gt_) for showing at the end of the table
    gt_c_all = 0
    gt_risks_multi = 0
    gt_risks_tot = 0

    # Embers count by (RKR, chapter):
    rkr_chap_cnt = pd.DataFrame(np.zeros((len(gbes), len(bibrefs)), dtype=int),
                                index=[hlp.RKRCATS6[g[0]] for g in gbes],  columns=[b['id'] for b in bibrefs])

    # Loop over RKRs = lines in the summary table
    hlp.report.table_head("Main RKR category", "Additional categories", "Ember long_name", "Source", "ID")
    for idx, gbe in gbes:
        cat = hlp.RKRCATS6[idx]

        c_all = 0
        hr_mid = []
        non_gmt_names = []
        bibrefs_ids = []

        for be in gbe:
            all_rkrcats = [kw for kw in be.keywords.split(',') if 'RKR' in kw]
            if len(all_rkrcats) > 1:
                add_cats = ', '.join(all_rkrcats[1:])
            else:
                add_cats = '-'
            hlp.report.table_write(cat, add_cats, be.longname,
                                   hlp.dict_by_id(figures, be.meta["mainfigure_id"])['biblioreference_cite_key'],
                                   be.id)
            c_all += 1
            # Calcultate GMT at the mid-point of the transition to high risk,
            if be.haz_name_std == "GMT":
                hr_mid.append(hlp.hfn(be, 1.5))
                # Note: the first version calculated to full range for this transition (= start -> end of transition);
                # this was removed in the revised paper for simplicity / to avoid potential confusion.
                # What is now calculated is the min/max of the *mid-point* (only) across embers in a category.
            else:
                non_gmt_names.append(be.haz_name_std)

            figid = be.meta['mainfigure_id']
            bibref_id = hlp.dict_by_id(figures, figid)['biblioreference_id']
            bibrefs_ids.append(bibref_id)
            rkr_chap_cnt.at[cat, bibref_id] += 1

        # Count sets of embers about the same risk under different scenarios (= adaptation, for now)
        scens_count = Counter([be.meta['scenariogroup_id'] for be in gbe])
        risks_nomulti = 0
        risks_multi = 0
        # Store an example ember within each scenario group, to check groups (only in the processing report):
        scenid_be_info = {be.meta['scenariogroup_id']: (be.longname, be.id) for be in gbe}

        for scg in scens_count:
            if scens_count[scg] == 1 or scg is None:
                # There is no scenario OR only 1 ember in the scenario group => each is one risk w/o scenario
                risks_nomulti += scens_count[scg]
            else:
                # The scenario group contains more than one ember => it was assessed with scenario variants
                risks_multi += 1
                # Report the id and name of an ember within this group, for information.
                hlp.report.table_write('', f"Adapt. variants:", scenid_be_info[scg][0], '', scenid_be_info[scg][1])
        # Total number of assessed risks (= each with no variant or with >1 scenario variants)
        risks_tot = risks_nomulti + risks_multi

        # mean [median] (min-max), across embers, of the mid-point within the moderate to high risk transition
        hr_message = (f" {np.mean(hr_mid):3.1f} [{np.median(hr_mid):3.1f}] "
                      f"({np.min(hr_mid):4.1f}-{np.max(hr_mid):4.1f})")
        if non_gmt_names:
            non_gmt_msg = ', '.join([f'{item[0]} x {item[1]}' for item in Counter(non_gmt_names).items()])
            hr_message += f" Excluded: {non_gmt_msg}"

        tableout.table_write(f"{cat}", c_all, f'{risks_multi} / {risks_tot}', hr_message)
        # totals
        gt_c_all += c_all
        gt_risks_multi += risks_multi
        gt_risks_tot += risks_tot

    # Delete empty columns (bibrefs which do not directly include embers, =reports containing chapters)
    rkr_chap_cnt.drop('RFC', inplace=True)  # Ignore RFC
    rkr_chap_cnt = rkr_chap_cnt.loc[:, (rkr_chap_cnt != 0).any(axis=0)]  # Ignore empty columns
    tableout.table_write("Total", gt_c_all, f'{gt_risks_multi} / {gt_risks_tot}', "")

    tableout.write(" ")
    cols = [hlp.dict_by_id(bibrefs, bid)['cite_key'] for bid in rkr_chap_cnt.columns]
    tableout.table_head("RKR category", *cols, 'All chapters')
    for cat in rkr_chap_cnt.index:
        rowvals = rkr_chap_cnt.loc[cat, :]
        tableout.table_write(cat, *rowvals, rowvals.sum())
    colsum = rkr_chap_cnt.sum(axis=0)  # Sum over the rows (index / 0)
    tableout.table_write("All RKRs", *colsum, colsum.sum())
    tableout.close(total=False)
