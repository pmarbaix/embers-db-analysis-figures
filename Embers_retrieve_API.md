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

The result is provided in [JSON](https://en.wikipedia.org/wiki/JSON) format.
This format is based on text; to have an idea of how it is defined, have a look at the archive 
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

- `desc`: if present, include the description field for embers and the explanation fields for transitions
  (the default is to omit those fields, which are generally not needed for analyses).

- `list`: if present, restricts the output to a list of embers, containing only the id and longname of each ember.

### Example

You may use [cURL](https://en.wikipedia.org/wiki/CURL) to test data retrival. For example,

```
curl "https://climrisk.org/edb/api/combined_data?source=AR6_WGII_Chapter16" -H "Authorization: Token
{token}"
```

would retrieve the data for the 5 "Reasons for concern" embers as assessed in IPCC AR6, in JSON format.

## 3. Reading an archive file



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