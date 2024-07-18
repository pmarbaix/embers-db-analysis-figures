import numpy as np
import embermaker.helpers as embhlp
import src.helpers as hlp
import settings_configs
import re
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
        if chapter is None: # Try to get an integer from the first part of the figure number
            try: # Reject CCPs ect. et end of list, after chapters
                chapter = int(re.sub('[^0-9]', '', str(figkeys[0]))) + 100
            except ValueError:
                chapter = 100
        sortkey = [int('RFC' in fig['shortname']), rep['year'], chapter, figinrep]
        return sortkey
    return fig_sortkey

def embers_table(**kwargs):
    """
    Generates a summary table for 'all' embers.
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
        be_ids = [be.id for be in embers if be.meta['mainfigure_id'] == fig['id'] ]
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