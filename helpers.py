from sys import exc_info
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
from settings_data_access import API_URL, TOKEN
import sys

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

def savejson(file, data):
    received_json = json.dumps(data, indent=4, ensure_ascii=False)
    with open(file, "w", encoding='utf8') as outfile:
       outfile.write(received_json)


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
        self.idset +=1
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

def getdata(dset):
    """
    Gets data from server or file, as indicated in settings_data_access.py
    :param dset: the settings defining which data to retrieve, and how to process it for this a datat subset (dset),
                 as defined in settings_configs.py
    :return: a dict containing data.
    """

    response = requests.get(f"{API_URL}/edb/api/combined_data"
                            f"?select_embers={dset['ids']}"
                            f"&keywords={dset['keywords']}"
                            f"&scenario={dset['scenario']}"
                            f"&source={dset['source']}",
                            headers={"Authorization": f"Token {TOKEN}"})

    # As a rule, the hazard variable will be converted to GMT.
    conv_gmt = dset["conv_gmt"] if "conv_gmt" in dset else "compulsory"
    # Extract ember data and convert to Ember objects from Embermaker
    return extractdata(response, dump=False, conv_gmt = conv_gmt)

def extractdata(response, conv_gmt: str = 'compulsory', dump = False):
    """
    Processes the burning embers received from the database API to get 'EmberMaker' drawable embers, +a link to figures
    :param response:
    :param conv_gmt: Whether the hazard unit should be converted to GMT;
                      must be in ['compulsory', 'if_possible', 'never']
    :return:
    """
    if conv_gmt not in ['compulsory', 'if_possible', 'never']:
        raise ValueError(f"conv_gmt must be 'compulsory', 'if_possible' or 'never', not {conv_gmt}")

    # Convert the json received as bytes data to Python objects:
    try:
        data = json.loads(response.content)
    except json.JSONDecodeError:
        print(response.content)
        exit()

    if "error" in data:
        raise Exception(data["error"])

    # Optionally save the data
    if dump:
        savejson(f"out/test_embers.json", data)

    # Convert the json ember data to Ember objects
    lbes = embers_from_json(data['embers'])
    print(f"Getdata: Received {len(lbes)} ember(s).")

    # Get information about related figures
    emb_figs = data['embers_figures']
    logger = Logger()

    # Convert hazard metric to GMT if possible, otherwise remove the ember
    if 'never' not in conv_gmt.lower():
        for be in lbes.copy():
            be.egr = egr  # Gives ember access to the risk level indexes, for interpolation etc.
            try:
                be.convert_haz('GMT', logger=logger)
            except LookupError:
                if 'compulsory' in conv_gmt.lower():
                    lbes.remove(be)
                    print(f"Removed ember {be} because hazard variable is {be.haz_name_std}")

        print(f"Getdata: Unit conversion log (if any): {logger.getlog(0)}")
        print(f"Getdata: Retained {len(lbes)} ember(s) after conversion to GMT.")
    else:
        print(f"Getdata: Did not perform conversion to GMT")

    figures = data['figures']
    return {'lbes': lbes, 'emb_figs': emb_figs, 'figures': figures, 'scenarios': data['scenarios']}

def embers_col_background(xlim: tuple[float, float] = None, ylim: tuple[float, float] = None, dir = 'vertic'):
    """
    Draws a light-coloured gradient following the ember risk level colours.
    This
    :param xlim:
    :param ylim:
    :param dir: 'vertic' (default) or 'horiz'
    :return:
    """
    if xlim == None:
        logging.critical("xlim is required")
        return
    if ylim == None:
        ylim = (-1.5,4.5)

    # Set array to map colours to, according to direction
    if dir == 'vertic':
        basarr = np.array(((1., 1.), (0., 0.)))
    else:
        basarr = np.array(((0., 1.), (0., 1.)))

    cols = np.array([(1, 1, 1), (0.98, 0.92, 0), (1, 0.2, 0), (0.5, 0, 0.3)])
    cols = 2/3.0 + cols / 3.0 # Soften colors
    cmap = colors.LinearSegmentedColormap.from_list('embers', cols, N=255)
    plt.imshow(basarr,
               extent=(*xlim, *ylim),
               cmap=cmap,
               interpolation='bilinear',
               vmin=0, vmax=1.0,
               aspect='auto'
            )


class Emberdata:
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

    def get_embers_figures(self):
        return self.data['embers_figures']


def dict_by_id(dicts, id=None):
    """
    Gets a dict from a list of dict where dict['id'] = id
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
    return risk, cid # Between 0 and 6, min


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


def get_skey_kw(keywords: list, limit:int = None):
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
        bekws = [bekw.strip() for bekw in be.longname.lower().replace(':','').split(' ')]
        fkw = [kw for kw in regions if kw.lower().strip() in bekws]

        if len(fkw) >= 1:
            return regions.index(fkw[0])
        else:
            return -1

    return skey