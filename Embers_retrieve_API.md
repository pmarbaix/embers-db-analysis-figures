# Data access through API and archive file

## Data access options

The 'burning embers' data used in the Climate Risk Ember Explorer can be accessed in two ways:

- from a file archive file available from zenodo: [doi.org/10.5281/zenodo.12626977](doi.org/10.5281/zenodo.12626977)
  the main benefit is that you can refer to a specific version of the data.
- from the online database, through a simple API, as explained below.

In both cases, you may filter the data to get a subset of the embers based on search criteria which you define.
If you access through the API, the criteria should be sent as parameters of the request.
If you take the data from a file archive, this repository contains an helper function to read the file and apply
the same search criteria.

All figures from [Marbaix et al. (2024)](#1) can be produced in both ways (see README.md)

## API Access point & token

There is a single access point to request data:
https://climrisk.org/edb/api/combined_data

Access will require a token which identifies the user. 
However, a "public token" is available for the duration of the review of a paper which makes use of this
data: [Marbaix et al. (2024)](#1).
The public token is available in the Supplement to this paper.

Requests may include one or more of the following parameters.

### Filters
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

### Other parameters
`desc`: if present, include the description field for embers and the explanation fields for transitions.

`list`: if present, restricts the output to a list of embers, containing only the id and longname of each ember.

## Examples
More examples

## References
<a id="1">Marbaix et al. (2024)</a> 
Philippe Marbaix, Alexandre K. Magnan, Veruska Muccione, Peter W. Thorne, Zinta Zommers (2024).
'Climate change risks illustrated by the IPCC "burning embers"' 
Prepared for submission to [ESSD](https://www.earth-system-science-data.net).