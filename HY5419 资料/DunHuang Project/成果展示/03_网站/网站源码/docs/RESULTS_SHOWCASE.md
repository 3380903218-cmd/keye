# QGIS and Gephi results, release 2.6.0

Historical arrangement. Release 2.7.0 integrates the figures into a reading sequence, makes the route view the default map and retains the original QGIS export as a regional reference. See [the current reading and research design](NARRATIVE_READING.md). The complete Gephi graph remains directly visible.

The principal purpose of the exhibition is to present the project’s QGIS and Gephi work. Both results are directly visible in the main page. The Gephi result is not placed inside an optional reading or exploration disclosure.

## Principal figures

- **QGIS:** the original regional map is the default map view. Its complete page is rendered proportionally, with the original legend, sources and OpenStreetMap attribution. The downloadable one-page PDF is copied byte for byte from the author’s export. A neighbouring “Animated routes” tab retains the web route map and its playback and record tools. The two views are labelled separately: the regional export is the earlier authored map, while the web animation includes subsequently verified project records.
- **Gephi:** all 122 nodes and 136 relationships appear by default before the supporting case explanations. The graph retains the author’s exported positions within connected groups; compact view only translates disconnected components. The original GEXF remains available. Node selection reveals its record beneath the plot. Search, filtering and case-guide controls share a closed tool panel; closing that panel does not hide the figure. A visible return action restores the full graph after an explicit switch to a case guide.

The cover and persistent navigation identify the two results and link directly to their display areas. Contextual photographs follow the two principal results. Case explanations and long source records support the figures rather than preceding or replacing them. Collection and preservation content remains available afterward.

## Data and artifact boundaries

No historical nodes, edges, event dates, coordinates or evidence records are added or altered. The dataset retains 42 events, 21 network source entries and 49 evidence records. The QGIS PDF is a project output, not an additional research source. The full-page preview is a raster rendering with no crop or content alteration; the original image-based export is retained for download. Provenance and SHA-256 values are recorded in `asset-provenance.json` and the publication manifest.

Both the PDF and its preview are local assets, embedded in the two standalone offline exports. The original QGIS map contains an OpenStreetMap basemap; its attribution remains inside the map and beside the displayed figure. The original map is in English, while the web captions, controls and alt text switch between English and Chinese.

## Verification

`results-verification.json` checks default, ungated visibility of both results, the complete Gephi dataset, figure bounds, tool defaults, navigation, map modes, layer filters, search, inspection, returning from a guide, language retention and map/network cross-links at seven viewport sizes in both languages. Offline checks also compare the embedded PDF bytes to the original export. Guide regression checks retain all 42 event projections. These checks are distinct from a new human usability review or mainland-network test.
