import sys
import requests
from embermaker import ember as emb
from embermaker.embergraph import EmberGraph, ColourPalette
from embermaker.readembers import embers_from_json
import embermaker.helpers as hlp
import matplotlib.pyplot as plt
import json
import helpers
from settings_general import API_URL, TOKEN
logger = hlp.Logger()

try:
    config_choice = sys.argv[1]
except IndexError:
    logger.addfail(f"This script needs a configuration choice as argument - none was provided.")
    exit()

try:
    settings = helpers.getsettings(sys.argv)
    runset = helpers.getset(settings, 0)  # Settings for the datasets (its sources, name...) - only source 0 used here!

except KeyError:
    logger.addfail(f"Configuration not found in edp_paper_settings.py for '{config_choice}' (=your first argument).")
    exit()

res = requests.get(f"{API_URL}/edb/api/combined_data"
                   f"?select_embers={runset['ids'] if 'ids' in runset else ''}"
                   f"&keywords="
                   f"&source={runset['source'] if 'source' in runset else ''}",
                   headers={"Authorization": f"Token {TOKEN}"})

# Convert the json received as bytes data to Python objects:
try:
    data = json.loads(res.content)
except json.JSONDecodeError:
    print(res.content)
    exit()

if 'error' in data:
    raise Exception(f"The ember database server could not process the request: {data['error']}")

if len(data['embers']) == 0:
    raise ValueError(f"No embers found for settings '{config_choice}', source '{runset['source']}'")

# Convert the json ember data to Ember objects
lbes = embers_from_json(data['embers'])

# Get information about related figures
figures = data['embers_figures']

# Save to file, for information / backup
received_json = json.dumps(data, indent=4, ensure_ascii=False)
with open(f"out/{runset['out_file']}_embers.json", "w", encoding='utf8') as outfile:
   outfile.write(received_json)

# Convert hazard metric to GMST if possible, otherwise remove the ember
for be in lbes:
    try:
        be.convert_haz('GMST', logger=logger)
    except LookupError:
        lbes.remove(be)
        logger.addwarn(f"Removed ember {be} because hazard variable is {be.haz_name_std}")

for be in lbes:
    fig = figures[str(be.id)]
    print(f"- {fig['source_key']} - Fig. {fig['number']}: {be}")

print(f"#embers: {len(lbes)}; request: {data['filters']}")

# Create an ember graph
outfile = (f"out/{runset['out_file']}_embers.svg")

egr = EmberGraph(outfile, grformat="SVG")

# risk_hazl = np.arange(0.5, 3.0, 0.05)
# risk_tots = np.zeros(len(risk_hazl))
# risk_avgs = np.zeros(len(risk_hazl))
# risk_p10 = np.zeros(len(risk_hazl))
# risk_p50 = np.zeros(len(risk_hazl))
# risk_p90 = np.zeros(len(risk_hazl))
#
# for be in lbes:
#     be.egr = egr
#     # Todo: consider moving this; Embers are embergraph.Elements, and they are not 'entirely
#     #       defined' until there is an associated ColourPalette, which is in egr.
#
#     # Store risk and level data = get it only once:
#     be.name = be.longname if be.longname else be.name
#     be.ext['risk'] = be.levels_values('risk')
#     be.ext['hazl'] = be.levels_values('hazl')
#     be.ext['riskfn'] = lambda inthazl: np.interp(inthazl, be.ext['hazl'], be.ext['risk'])
#
# olbes = lbes
# lbes  = []
# rem_incomplete = True
# for be in olbes:
#     if rem_incomplete and max(np.max(be.ext['hazl']),be.haz_valid[1]) < risk_hazl[-1]:
#         logger.addwarn(f"Removed ember {be} / no assessment GMST > {max(np.max(be.ext['hazl']),be.haz_valid[1])}")
#         olbes.remove(be)
#     else:
#         lbes.append(be)
# # lbes = olbes
#
# logger.addwarn(f"#remaining embers: {len(lbes)}")
#
# percentile_method = 'linear'
# for lev, inthazl in enumerate(risk_hazl):
#     risk_inthazl = []
#     for be in lbes:
#         intrisk: float = be.ext['riskfn'](inthazl)
#         if max(np.max(be.ext['hazl']),be.haz_valid[1]) >= inthazl:
#             risk_tots[lev] += intrisk
#             risk_inthazl.append(intrisk)
#         else:
#             if np.abs(inthazl-2.5) < 0.001:
#                 print(f'At 2.5, {be} had no data')
#
#     risk_inthazl: np.array = np.sort(risk_inthazl)
#
#     # https://numpy.org/doc/stable/reference/generated/numpy.percentile.html
#     risk_p10[lev] = np.percentile(risk_inthazl, 10, method=percentile_method)
#     risk_p50[lev] = np.percentile(risk_inthazl, 50, method=percentile_method)
#     risk_p90[lev] = np.percentile(risk_inthazl, 90, method=percentile_method)
#     risk_avgs[lev] = risk_tots[lev] / len(risk_inthazl)
#
# for be in lbes:
#     if max(np.max(be.ext['hazl']),be.haz_valid[1]) <= risk_hazl[-1]:
#         logger.addwarn(f"Should have removed ember {be} / lack of data: {np.max(be.ext['hazl'])}")
#
# doprint = False
# if doprint:
#     for ilv in range(len(risk_hazl)):
#         print(f"Warming: {risk_hazl[ilv]:4.1f}°C, \tAverage risk index: {risk_avgs[ilv]:5.2f}, "
#               f"\tp10: {risk_p10[ilv]:5.1f}, \tp90: {risk_p90[ilv]:5.2f}")
#
# fig, ax = plt.subplots()
# ax.plot(risk_hazl, risk_p10, color='black', linestyle="--")
# ax.plot(risk_hazl, risk_avgs)
# # ax.plot(risk_hazl, risk_p50)
# ax.plot(risk_hazl, risk_p90, color='black', linestyle="--")
# ax.grid()
# ax.set(xlabel='GMST', ylabel='Risk level (1= moderate, 3= very high)',
#        title=runset["title"])
#
# fig.savefig(f"out/{runset['out_file']}.png")
# plt.show()

sort_by = ""
if sort_by == "hazard":
    # Sort embers based on their risk level for hazard = 2.0 (°C)
    lbes.sort(key=emb.get_skeyrisk(sorthazl=2.0), reverse=True)
    # Sort embers based on their risk level for hazard = 1.5 (°C)
    lbes.sort(key=emb.get_skeyrisk(sorthazl=1.5), reverse=True)
elif sort_by == "temp":
    # Sort embers based on their temperature for a given risk index
    lbes.sort(key=emb.get_skeyrisk(sortrlev=1.5))

# Create a group of embers containing all embers (without sorting by group or name)
gbes = emb.EmberGroup(name=f"Embers sorted by {sort_by}")
gbes.add(lbes)

# Add groups of embers (and the embers it contains), to the graph:
egr.add(gbes)

# Customize parameters
egr.gp['conf_lines_ends'] = 'arrow'  # 'bar', 'arrow', or 'datum' (or None)
egr.gp['haz_axis_top'] = 4.0

# Actually produce the diagram
outfile = egr.draw()

print(outfile)
