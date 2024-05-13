from embermaker import ember as emb
from embermaker.embergraph import EmberGraph, ColourPalette
from embermaker.readembers import embers_from_json
import embermaker.helpers as emaker_hlp
import settings_configs
import json
import helpers as hlp
logger = emaker_hlp.Logger()

def draw_all_embers(**kwargs):
    # Get settings from edb_paper_settings, according to the choices made in keyword arguments (see getsettings)
    dset = settings_configs.get_settings(**kwargs)
    # Create global report file (Markdown)
    hlp.report_start(dset)
    hlp.report.write(f"Source {dset["idset"]}: {dset['name']}", title=1)

    # Get data for the current subset (dset)
    data = hlp.getdata(dset)
    lbes = data['lbes']  # The list of burning embers in this data subset

    # Convert the json ember data to Ember objects
    lbes = embers_from_json(data['embers'])

    # Get information about related figures
    figures = data['embers_figures']

    # Save to file, for information / backup
    received_json = json.dumps(data, indent=4, ensure_ascii=False)
    with open(f"out/{dset['out_file']}_embers.json", "w", encoding='utf8') as outfile:
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
    outfile = (f"out/{dset['out_file']}_embers.svg")

    egr = EmberGraph(outfile, grformat="SVG")

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

