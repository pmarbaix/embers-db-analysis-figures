from typing import Iterator
import json
import numpy as np
import requests
from embermaker.embergraph import EmberGraph
from embermaker.readembers import embers_from_json
from embermaker.helpers import Logger
import matplotlib.pyplot as plt
from matplotlib import colors
import logging
from bisect import bisect_right
from settings_data_access import API_URL, TOKEN, FILE
from os import path
import re

# Create a dumb ember graph because this provides access to the risk level index (e.g. for interpolation);
# (the origin of this is that risk names, indexes, and colours are defined at the graph level in EmberMaker;
#  this may change in a future version of EmberMaker, if it gets a specific management of risk level definitions)
egr = EmberGraph()


def weighted_percentile(values, p, weights=None):
    """ Weighted percentiles,
    https://stackoverflow.com/questions/21844024/weighted-percentile-using-numpy
    There are different methods/definitions; the one applied here differs from numpy, as explained at the end of
    https://en.wikipedia.org/wiki/Percentile#Definition_of_the_Weighted_Percentile_method
    Note: the Python package statsmodels is an alternative, as explained in stackoverflow above:
    https://www.statsmodels.org/stable/generated/statsmodels.stats.weightstats.DescrStatsW.html (again different method)
    :param values: numpy.array with data
    :param p: scalar or sequence of p-th percentile(s) for which to compute the percentile value
    :param weights: array-like of the same length as `array`
    :return: numpy.array with computed percentiles.
    """
    values = np.array(values)
    percent = np.array(p) / 100.0  # percentiles, from 0 to 100 as in Numpy
    if weights is None:
        weights = np.ones(len(values))
    weights = np.array(weights)
    assert np.all(percent >= 0) and np.all(percent <= 1), \
        'percentiles should be in [0, 100]'

    sorter = np.argsort(values)
    values = values[sorter]
    weights = weights[sorter]

    wrank = np.cumsum(weights) - 0.5 * weights  # (C = 1/2)
    wrank /= np.sum(weights)
    return np.interp(percent, wrank, values)


class DSets:
    """
    An iterator over the data subsets (dsets) given the current full settings;
    provides the settings which applies to a given dset (= global settings + settings from a given element in 'multi')
    """
    def __init__(self, settings):
        self.settings = settings
        self.idset = 0
        self.ndsets = len(settings['multi']) if 'multi' in settings else 1

    def __iter__(self) -> Iterator[dict]:
        return self

    def __next__(self) -> dict:
        if self.idset >= self.ndsets:
            raise StopIteration
        if 'multi' in self.settings:
            curmult = self.settings['multi'][self.idset]
            dset = dict(self.settings, **curmult)
            dset.pop('multi', None)
        else:
            dset = self.settings
        dset['ndsets'] = self.ndsets
        dset['idset'] = self.idset
        styles = [('black', '-'), ('blue', '-'), ('green', '-'),
                  ('black', '--'), ('blue', '--'), ('green', '--')]  # Default line styles
        setdefaults(dset,
                    {'name': '',
                     'ids': '',
                     'keywords': '',
                     'scenario': '',
                     'style': styles[self.idset] if self.idset < 6 else styles[0]})
        self.idset += 1
        return dset


def setdefaults(idict, defs):
    """
    Sets defaults for the current settings:
    For all keys which are in 'defs' but not in 'idict', copy the key/value from defs to idict
    :param idict:
    :param defs:
    :return:
    """
    for ky, df in defs.items():
        if ky not in idict:
            idict[ky] = df


def request_param_str(dset, param: str):
    """Adds the given parameter, if it is available, to the request parameters (as string)"""
    if param in dset:
        if request_param_str.first:
            prefix = '?'
            request_param_str.first = False
        else:
            prefix = '&'
        return prefix + f"{param}={dset[param]}"
    else:
        return ""


def jsonfile_save(filename, data):
    received_json = json.dumps(data, indent=4, ensure_ascii=False)
    filename = path.splitext(filename)[0] + '.json'
    with open(filename, "w", encoding='utf8') as outfile:
        outfile.write(received_json)


class Response:
    def __init__(self, json_data):
        self.ok = True
        self.content = json_data


def stringmatch(criteria, text):
    """
    Returns True if the string matches the given criteria.
    For example, criteria "fox AND NOT dog" would return False on "The quick brown fox... the lazy dog".
    Supported are: AND, OR, NOT (upper case), quotes ('') and brackets
    Example of complex criteria: "ecosystems AND NOT ('ecosystem services' OR fishing OR aquaculture)"
    :param text: the text to check for matches according to the criteria
    :param criteria: the search criteria
    :return:
    """
    if not criteria:
        return True
    # Parse the criteria to get a list of tuples: [(<string to find>,<operator>), ...]
    pexp = re.findall(r"(|\b[^']*?\b|\'.*?\') *(\(|\)|\bAND\b|\bOR\b|\bNOT\b|$)", criteria)
    lstr = ""
    text = text.lower()
    for ex in pexp:
        tx = ex[0].strip().strip("'")
        if tx:
            fnd = str(tx.lower() in text) + " "
        else:
            fnd = ""
        lstr += " " + fnd + ex[1].lower()
    try:
        return eval(lstr)
    except SyntaxError:
        logging.fatal(f"Stringmatch failed to apply '{criteria}' to '{text}'")
        exit()


def jsonfile_get(filename, **kwargs):
    """
    Returns the filtered content of a json file according to the combination of criteria defined in dset
    :param filename: Full name of the json input file
    :param **kwargs: Search/filter criteria (see Embers_retreive_API.md).
                     In this software, it is usually provided as part of the 'data set parameters' (dset).
    :return: A dict of ember-related data, containing embers and other data read from the input file.
    """
    with open(filename, "r") as file:
        jsondata = json.load(file)

    # Filtering based on the inclusion_level is done first, because embers removed here can't be re-introduced
    # even by explicitly required them trough providing their id in 'emberids' below (same rule as in the API).
    # Note: bug fix on 17 July 2024 = add default inclusion level = 0, as done in the API (this was missing for files)
    ilev = int(kwargs["inclusion"]) if "inclusion" in kwargs else 0
    jsondata["embers"] = [be for be in jsondata["embers"] if int(be["inclusion_level"]) >= ilev]

    # If ember ids were provided, get the list of corresponding embers;
    # Unlike the other filter criteria, emberids *add* embers to the retained set => temporarily stored in 'bes'
    if "emberids" in kwargs:
        src = kwargs["emberids"].split('-')
        bes = [be for be in jsondata["embers"] if str(be["id"]) in src]
    else:
        bes = None  # list of embers to add after filtering.

    # Filter the received embers according to the other criteria (each criteria reduces the selected set)
    filtered = False
    if "longname" in kwargs:
        src = kwargs["longname"]
        jsondata["embers"] = [be for be in jsondata["embers"] if stringmatch(src, be["longname"])]
        filtered = True

    if "source" in kwargs:
        src = kwargs["source"]
        figs = jsondata["figures"]
        figids = [fig["id"] for fig in figs if stringmatch(src, fig["biblioreference.cite_key"])]
        if stringmatch(src, ""):
            figids.append(None)
        jsondata["embers"] = [be for be in jsondata["embers"] if be["mainfigure_id"] in figids]
        filtered = True

    if "keywords" in kwargs:
        kws = kwargs["keywords"]
        jsondata["embers"] = [be for be in jsondata["embers"] if stringmatch(kws, be["keywords"])]
        filtered = True

    if "scenario" in kwargs:
        scf = kwargs["scenario"]
        scens = jsondata["scenarios"]
        scids = [scen["id"] for scen in scens if stringmatch(scf, scen["name"])]
        if stringmatch(scf, ""):
            scids.append(None)
        jsondata["embers"] = [be for be in jsondata["embers"] if be["scenario_id"] in scids]
        filtered = True

    if bes:
        if filtered:
            jsondata["embers"] = jsondata["embers"] + [be for be in bes if be not in jsondata["embers"]]
        else:
            jsondata["embers"] = bes

    if jsondata["meta"]:
        jsondata["meta"]["embers_count"] = len(jsondata["embers"])

    return Response(jsondata)


def getdata(dset, as_embers=True, desc=False):
    """
    Gets data from server or file, as indicated in settings_data_access.py
    :param dset: the settings defining which data to retrieve, and how to process it for this a datat subset (dset),
                 as defined in settings_configs.py
    :param as_embers: if True, converts the data to ember objects
    :param desc: if True, includes the description of embers and transitions
    :return: a dict containing data.
    """
    report.write("Embers selection:", title=2)
    for crit in ['emberids', 'source', 'keywords', 'scenario', 'longname']:
        if crit in dset and dset[crit]:
            report.write(f"{crit.capitalize()}: {dset[crit]}")
            logging.debug(f"{crit.capitalize()}: {dset[crit]}")

    request_param_str.first = True
    if API_URL:
        request = (f"{API_URL}/api/combined_data"
                   + request_param_str(dset, 'emberids')
                   + request_param_str(dset, 'source')
                   + request_param_str(dset, 'keywords')
                   + request_param_str(dset, 'scenario')
                   + request_param_str(dset, 'longname')
                   + request_param_str(dset, 'inclusion')
                   + (request_param_str({"desc": ""}, 'desc') if desc else ""))

        response = requests.get(request, headers={"Authorization": f"Token {TOKEN}"})
    else:
        request = f"Read from file, {dset}"
        response = jsonfile_get(FILE, **dset)

    if response.ok:
        report.write(f"Data received from: {API_URL}")
    else:
        try:
            rd = json.loads(response.content)
        except json.decoder.JSONDecodeError:
            rd = {}
        if "detail" in rd:
            msg = rd["detail"]
        elif "error" in rd:
            msg = rd["error"]
        else:
            msg = f"Unknown error. Did you provide a valid url in settings_data_access.py?"
        msg = f"Data request '{request}' failed. Error message: {msg}"
        report.write(msg)
        report.close()
        raise ConnectionError(msg)

    if as_embers:
        # As a rule, the hazard variable will be converted to GMT.
        conv_gmt = dset["conv_gmt"] if "conv_gmt" in dset else "compulsory"
        try:
            # Extract ember data and convert to Ember objects from Embermaker
            return extractdata(response.content, conv_gmt=conv_gmt)
        except LookupError:
            raise LookupError(f"No data for {dset}")
    else:
        return json.loads(response.content) if type(response.content) is not dict else response.content


def extractdata(jsondata, conv_gmt: str = 'compulsory'):
    """
    Processes the burning embers received from the database API to get 'EmberMaker' drawable embers, +a link to figures
    :param jsondata: json data as string or byte string, or an equivalent dict containing the data to process.
    :param conv_gmt: Whether the hazard unit should be converted to GMT;
                    must be in ['compulsory', 'if_possible', 'never']
                    WARNING: if 'compulsory' is not used, this function may return inconsistent data, such as
                    a mix of sea-level rise in meters rise and warming in °C.
    :return:
    """
    if conv_gmt not in ['compulsory', 'if_possible', 'never']:
        raise ValueError(f"conv_gmt must be 'compulsory', 'if_possible' or 'never', not {conv_gmt}")

    # Convert the json received as bytes data to Python objects:
    if type(jsondata) in (str, bytes):
        try:
            data = json.loads(jsondata)
        except json.JSONDecodeError:
            raise ValueError(f"Could not process the received json data; type: {type(jsondata)}.")
    elif type(jsondata) is dict:
        data = jsondata
    else:
        raise ValueError(f"Could not process the received data; type: {type(jsondata)}.")

    if "error" in data:
        raise Exception(data["error"])
    report.write(f"Data extraction date: {data['meta']['extraction_date']}")

    # Convert the json ember data to Ember objects
    lbes = embers_from_json(data['embers'])
    logging.info(f"ExtractData: Received {len(lbes)} ember(s).")

    logger = Logger()

    # Convert hazard metric to GMT if possible, otherwise remove the ember
    if 'never' in conv_gmt.lower():
        report.write(f"WARNING: conversion to a common variable or unit is not active; inconsistencies may occur.")
    else:
        for be in lbes.copy():
            be.egr = egr  # Gives ember access to the risk level indexes, for interpolation etc.
            try:
                be.convert_haz('GMT', logger=logger)
            except LookupError:
                if 'compulsory' in conv_gmt.lower():
                    lbes.remove(be)
                    report.write(f"Removed ember '{be}' because hazard variable is {be.haz_name_std}")
                else:
                    report.write(f"Ember '{be}' has the hazard variable {be.haz_name_std}, "
                                 f"which could not be converted to GMT.")

        conv_log = logger.getlog(0)
        if conv_log:
            report.write(f"Unit conversion log:\n {'<br> '.join(conv_log)}")
    logging.info(f"ExtractData: Retained {len(lbes)} ember(s) after conversion to GMT.")
    if len(lbes) == 0:
        raise LookupError("ExtractData: no ember matches the provided criteria")

    figures = data['figures']
    return {'embers': lbes, 'figures': figures, 'scenarios': data['scenarios'],
            'biblioreferences': data['biblioreferences']}


def embers_col_background(xlim: tuple[float, float] = None, ylim: tuple[float, float] = None, dir='vertic',
                          soften_col: int = None):
    """
    Draws a light-coloured gradient following the ember risk level colours.
    This
    :param xlim:
    :param ylim:
    :param dir: 'vertic' (default) or 'horiz'
    :param soften_col: soften colors; 1 - full colour, 2 - moderate softening, 3 (default) - high softening...
                       (there is no upper bound: increasing values result in less colour and more white)
    :return:
    """
    if xlim is None:
        logging.critical("xlim is required")
        return
    if ylim is None:
        ylim = (-1.5, 4.5)
    if soften_col is None or soften_col < 1:
        soften_col = 3

    # Set array to map colours to, according to direction
    if dir == 'vertic':
        basarr = np.array(((1., 1.), (0., 0.)))
    else:
        basarr = np.array(((0., 1.), (0., 1.)))

    cols = np.array([(1, 1, 1), (0.98, 0.92, 0), (1, 0.2, 0), (0.5, 0, 0.3)])
    cols = (soften_col - 1.0) / soften_col + cols / soften_col  # Soften colors
    cmap = colors.LinearSegmentedColormap.from_list('embers', cols, N=255)
    plt.imshow(basarr,
               extent=(xlim[0], xlim[1], ylim[0], ylim[1]),
               cmap=cmap,
               interpolation='bilinear',
               vmin=0, vmax=1.0,
               aspect='auto'
               )


class Emberdata:
    """
    Todo: remove? (not actually used?)
    """
    def __init__(self, response):
        try:
            self.data = json.loads(response.content)
        except json.JSONDecodeError:
            logging.critical(response.content)
            exit()

    def get_figures(self):
        return self.data['figures']

    def get_embers_data(self):
        return self.data['embers']


def dict_by_id(dicts, id=None):
    """
    Gets a dict from a list of dicts such that dict['id'] = id.
    :param dicts: a list of dict objects
    :param id: the required id
    :return: the corresponding dict
    """
    if id:
        return [dt for dt in dicts if dt['id'] == id][0]
    else:
        return None


def rfn(be, hazl, conf=False):
    """
    Interpolates between levels in a BE to get risk as a function of hazard;
    Optionally returns the (lowest) confidence level within the interpolation interval
    (confidence of the transition if hazl is in a transition, otherwise lowest confidence of the 2 nearest transitions)
    :param be:
    :param hazl: the hazard value to interpolate to
    :param conf: whether to return the confidence level
    :return: risk
    """

    try:
        risk = np.interp(hazl, be.levels_values('hazl'), be.levels_values('risk'))
    except ValueError:
        raise ValueError(f"Risk could not be interpolated for the given hazard level (rfn) '{be.name}'; "
                         f"n levels: {len(be.levels_values('hazl'))}")

    if not conf:
        return risk

    lvs = be.levels()
    idx1 = bisect_right([lv['hazl'] for lv in lvs], hazl)
    idx1 = min(idx1, len(lvs) - 1)
    idx0 = max(idx1 - 1, 0)
    if lvs[idx0] == hazl:
        idx1 = idx0
    try:
        cf0 = lvs[idx0].trans.confidence[0]
        cf1 = lvs[idx1].trans.confidence[0]
        clevs = ['L', 'LM', 'M', 'MH', 'H', 'HVH', 'VH']
        cid0 = clevs.index(cf0)
        cid1 = clevs.index(cf1)
        cid = min(cid0, cid1)
    except IndexError:
        cid = -1
    return risk, cid  # Between 0 and 6, min


def hfn(be, rlev):
    return np.interp(rlev, be.levels_values('risk'), be.levels_values('hazl'))
    # Note: there was a version of this function with right= 3.2 for testing.


def rem_incomplete(lbes, mxhaz):
    newlbes = []
    for be in lbes:
        if max(np.max(be.levels_values('hazl')), be.haz_valid[1]) < mxhaz:
            logging.warning(
                f"Removed ember {be} / no assessment for GMT > "
                f"{max(np.max(be.levels_values('hazl')), be.haz_valid[1])}")
        else:
            newlbes.append(be)
    logging.warning(f"#remaining embers: {len(lbes)}")
    return newlbes


def get_skey_kw(keywords: list, limit: int = None):
    """
    Generates a sort key function for sorting objects (in principle, embers) by up to
    2 keywords within a list of keywords.
    The two first matching keywords of the sorted objects will be considered,
    with the first one used for the main sorting level.
    :param keywords: an ordered list of keywords to look for within ember keywords
    :param limit: the number of object keywords to consider. If None, all keywords are considered.
    :return:
    """
    # Standardize the sorting list
    kws = [kw.lower().strip() for kw in keywords]

    def skey_kw(be):
        bekws = [bekw.strip() for bekw in be.keywords.lower().split(',')]
        if limit:
            bekws = bekws[:limit]
        # Former method, giving priority to the first keywords in the provided list
        # fkw = [kw for kw in keywords if kw.lower().strip() in bekws]
        fkw = [bekw for bekw in bekws if bekw in kws]

        sid = 0
        if len(fkw) > 2:
            sid += keywords.index(fkw[2])
        if len(fkw) > 1:
            sid += keywords.index(fkw[1]) * 100
        if len(fkw) > 0:
            sid += keywords.index(fkw[0]) * 10000
        else:
            return -1
        return sid

    return skey_kw


def get_skey_longname(regions: list):
    """
    Generates a sort key function for sorting by keywords within a list of keywords
    :param regions:
    :return:
    """
    def skey(be):
        # We need to look for region names 'word by word' because 'arctic' is contained in 'antarctic' :-)
        bekws = [bekw.strip() for bekw in be.longname.lower().replace(':', '').split(' ')]
        fkw = [kw for kw in regions if kw.lower().strip() in bekws]

        if len(fkw) >= 1:
            return regions.index(fkw[0])
        else:
            return -1

    return skey


class Report:
    """
    Helps in generating processing reports in Markdown format
    """
    def __init__(self, filename):
        self.nembers = 0
        if filename:
            filename = path.splitext(filename)[0] + '.md'
            self.file = open(filename, 'w')
        else:
            self.file = None

    def write(self, txt: str, title: int = 0):
        """
        :param txt: the text to write
        :param title: the level of title / subtitle
        """
        if title == 1:
            print(txt)
        if title and title < 5:
            prefix = "#" * title + " "
        else:
            prefix = ""
        if self.file:
            self.file.write(f"\n{prefix}{txt}\n")

    def table_head(self, *headers):
        if self.file:
            self.file.write(f'\n| {" | ".join(headers)}\n')
            self.file.write(f'| {" --- | " * len(headers)}\n')

    def table_write(self, *content):
        if self.file:
            self.file.write(f'| {" | ".join([str(c) for c in content])}\n')

    def embers_list(self, lbes, onlyids=False):
        self.nembers += len(lbes)
        if onlyids:
            self.write(f'Ember ids (n={len(lbes)}):', title=3)
            self.write(', '.join([str(be.id) for be in lbes]))
        else:
            self.write(f'Ember names and ids (n={len(lbes)}):', title=3)
            self.write('<br>'.join([be.longname + " (" + str(be.id) + ")" for be in lbes]))

    def close(self, total=True):
        if total:
            self.write(f'Total number of embers listed in this report: {self.nembers}', title=3)
        if self.file:
            self.file.close()


def report_start(settings):
    global report
    report = Report(f"out/{settings['out_file']}")
    title = settings['title'].replace('\n', ' ')
    report.write(f"{title}", title=1)


# We use only one "global" report, which is easy to refer to, by importing helpers
report = Report(None)
