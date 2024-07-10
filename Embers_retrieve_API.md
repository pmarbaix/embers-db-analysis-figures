# Data access through API and archive file

## 1. Data access options

The 'burning embers' data used in the Climate Risk Ember Explorer can be accessed in two ways:

- from the online database, through a simple API, as explained in section 2.
- from a file archive file available from Zenodo [Marbaix et al. 2024](#1); 
  the main benefit is that you can refer to a specific version of the data (section 3).

In both cases, you may filter the data to get a subset of the embers based on search criteria which you define.
If you access through the API, the criteria should be sent as parameters of the request.
If you take the data from a file archive, this repository contains a helper function to read the file and apply
the same search criteria.

The result is provided in [JSON](https://en.wikipedia.org/wiki/JSON) format 
(described here: [json.org](https://json.org)).
This format is based on human-readable text; to have an idea of how it is defined, have a look at the archive 
file ([Marbaix et al. 2024](#1)).
This format is easy to use in programming languages used for data analysis, including Python and R.
For example, in Python, one would import the built-in module `json` and call methods such as 
`json.loads(received_content)`.

All figures from [Marbaix et al. (2024b)](#2) can be produced in both ways, with code 
provided in this repository (see README.md).

## 2. API Access point & token

There is a single access point to request data:
https://climrisk.org/edb/api/combined_data

Access will require a token which identifies the user. 
However, a "public token" will be available for the duration of the review of a paper which makes use of this
data: [Marbaix et al. (2024)](#1). The public token will be (or is) available in the Supplement to this paper.

Requests may include one or more of the 'filter' parameters (search criteria) presented in section 4.
When data is requested through the API, the filtering is handled by PostgreSQL's text search functions. 

### API-specific parameters

There are two parameters which only work with the API access:

- `list`: if present, restricts the output to a list of embers, containing only the id and longname of each ember.

- `desc`: if present, include the description field for embers and the explanation fields for transitions
  (the default is to omit those fields, which are generally not needed for analyses; this parameter
  has no effect if `list`is also set).

### Example

You may use [cURL](https://en.wikipedia.org/wiki/CURL) to test data retrieval. For example,

```
curl "https://climrisk.org/edb/api/combined_data?source=AR6_WGII_Chapter16" -H "Authorization: Token
{token}"
```

would retrieve the data for the 5 "Reasons for concern" embers as assessed in IPCC AR6, in JSON format. 
To have a look at a very short and more 'human-readable' output, try

```
curl "https://climrisk.org/edb/api/combined_data?list=&source=AR6_WGII_Chapter16" -H "Accept: application/json; indent=4" -H "Accept: application/json; indent=4" -H "Authorization: Token
{token}"
```

Note: `indent=4` is what makes the output formatted in a 'human-readable' way (as the archive file).

## 3. Reading an archive file

As JSON is based on text, it is easy to read from various programming languages. In Python, it could be for example:

```
import json
with open("path/to/your/file", "r") as file:
    jsondata = json.load(file)
```
To read and filter the embers data according to the search criteria defined in section 4, 
you may use the function `jsonfile_get(filename, **kwargs)` provided in the `src` package, with the desired
filtering parmeters (from section 4 below) provided as keyword arguments. For example,

```
from src.helpers import jsonfile_get
filename = 'path_to_a_copy_of/archive_file_from_zenodo.json'
jsonfile_get(filename, source="AR6-WGII-Chapter16").content['embers']
```
Notes: 
- while we will make all the possible to retain the existing functionality of the online access API
  (section 2) while possibly extending it, the name and details of 'helper' functions provided here could change in the future.
  These are provided as tools to reproduce the figures in [Marbaix et al. (2024b)](#2) as well as examples.
- `jsonfile_get` filters the embers with a view to follow the same approach as in the online API, but 
  it does not use the exact same code: it is based on python filtering, while the API relies on PostgreSQL
  for filtering. When producing the figures for [Marbaix et al. (2024b)](#2), the selection of embers is exactly
  the same with each of these approaches; however, there is no guarantee that it would remain true for any possible 
  search criteria.
- `jsonfile_get` only filters *the embers*: it reduces the set of embers found in the input file to what is
  requested, but always provides the full list ember groups, figures, etc.

## 4. Filters
A specific subset of the data can be obtained by specifying one or more of the following 
search criteria (filters) within the parameters of the request:

| Parameter  | Explanation                                                                                            | 
|------------|--------------------------------------------------------------------------------------------------------|
| emberids   | Unique identifiers of embers to include, separated by hyphens ('-'). For example, emberids=98-102-104. | 
| longname   | Restrict to embers which contain the given text in their "longname"                                    | 
| keywords   | Restrict to embers which contain the given text in their keywords                                      | 
| source     | Restrict to embers which contain the given text in the citation key of their source (report)           | 
| scenario   | Restrict to embers which contain the given text in the name of the considered scenario                 | 
| inclusion  | Restrict to embers which have an inclusion level equal or greater than the given number                | 


## References
<a id="1">Marbaix et al. (2024)</a>
Marbaix, P., A. K. Magnan, V. Muccione, P. W. Thorne, Z. Zommers (2024)
*Climate change risks illustrated by the IPCC burning embers: dataset*.
Zenodo. [doi.org/10.5281/zenodo.12626977](https://doi.org/10.5281/zenodo.12626977).

<a id="2">Marbaix et al. (2024b)</a> 
Marbaix, P., A. K. Magnan, V. Muccione, P. W. Thorne, Z. Zommers (2024).
*Climate change risks illustrated by the IPCC 'burning embers'*.
Prepared for submission to [ESSD](https://www.earth-system-science-data.net).