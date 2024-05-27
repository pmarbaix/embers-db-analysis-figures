import numpy as np
import embermaker.helpers as embhlp
import src.helpers as hlp
import settings_configs
import re
logger = embhlp.Logger()  # Standard log function in EmberMaker


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
    hlp.report.embers_list(lbes)

    embers = data['embers']
    figures = data['figures']
    scenarios = data['scenarios']

    dbes = {str(be.id): be for be in lbes}

    def fig_sort_key(fig):
        fignum = fig['number']
        figkeys = re.split(r'(\d+)', fignum)
        figkeys.append('0')
        figkeys.append('0')
        keylist = [(int(key) if key.isdigit() else key) for key in figkeys]
        reports = ['TAR-WGII-Chapter19', 'Smith09', 'AR5-WGII-Chapter19', 'AR5-SYR',
                   'SR1.5-Chapter3', 'SRCCL-Chapter7', 'SRCCL-Chapter7-SM', 'SROCC-Chapter5',
                   'AR6-WGII-Chapter2', 'AR6-WGII-Chapter7', 'AR6-WGII-Chapter9',
                   'AR6-WGII-Chapter11', 'AR6-WGII-Chapter13', 'AR6-WGII-Chapter14', 'AR6-WGII-Chapter16',
                   'AR6-WGII-CCP4', 'AR6-WGII-CCP6',
                   ]
        reportidx = reports.index(fig['biblioreference.cite_key'])
        keylist = [int('RFC' in fig['shortname']), reportidx, keylist[3]]
        return keylist

    figures.sort(key=fig_sort_key)
    # Create the summary table (Simple md files are crated by the small "Report" class)
    tableout = hlp.Report('out/'+settings['out_file']+'_out.md')
    tableout.table_head(["Report: main figure", "*shortname* <br/> (title)", "#other adapt.", "#high adapt.", "#total",
                          "High risk at mean T (min, max)"])

    # Store 'grand total' for showing at the end of the table
    gt_o_adap = 0
    gt_h_adap = 0
    gt_c_all = 0

    # Loop over figures = lines in the summary table
    for fig in figures:
        be_ids = [be.id for be in embers if  be.meta['mainfigure_id'] == fig['id'] ]
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
        tableout.table_write([f"{fig['reference']['cite_key']}:<br/> fig. {fig['number']}",
                              f"*{fig['shortname']}* <br/> ({fig['title']})",
                              n_other_adap, n_high_adap, c_all, hr_message])
        gt_o_adap += n_other_adap
        gt_h_adap += n_high_adap
        gt_c_all += c_all
    tableout.table_write(["Total", "", gt_o_adap, gt_h_adap, gt_c_all, ""])
    tableout.close(total=False)