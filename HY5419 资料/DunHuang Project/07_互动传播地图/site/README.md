# Dunhuang / In Motion

An English-first, bilingual static exhibition for the HY5419 Dunhuang project. Open `dist/index.html` directly, or serve `dist/` with any static HTTP server. No build, package installation, API key or external map service is required. The map, illustration and data are local assets.

The interface offers narrative-stage playback, route and layer filters, pan/zoom, keyboard access, collection details, source links, a relationship list and downloadable exhibition data. The map uses schematic relationships; it does not reconstruct historical roads or simulate daily cargo locations.

`data.js` is the exhibition snapshot: 17 reference places, 19 source relationships (18 displayed; one Pelliot summary excluded), and five collection institutions grouped by three cities. Historical cargo and current holding institutions are separate views. Related paintings are distinguished from manuscripts. The Beijing overview is an explicitly added collection-level relationship, with unresolved intermediate handovers preserved.

The source worksheet CSVs remain unchanged. `data-provenance.json` records their hashes. `tools/prepare_data.py` can regenerate the exhibition snapshot when run from its original position in the research project; it requires the original route CSVs. It does not write back to the research workbooks.

Base geography: Natural Earth, public domain. Reference coordinates: GeoNames and OpenStreetMap contributors (see project source CSVs). Archival illustration: British Library, Or.8210/P.2, via Wikimedia Commons, CC0 1.0. The illustration is not a newly generated reconstruction. Official collection/source links are included in the page.

The Site remains owner-private. Publishing and source synchronisation follow the Sites plugin workflow. Hosting identity lives in `.openai/hosting.json`; it is not inferred from the slug.

The default presentation language is English. The header’s EN / 中文 button switches the complete exhibition interface, map labels, narrative and collection details without resetting the selected stage or route. Both hosted and standalone versions use the same default.

## Gephi network — v1.1.0, 29 October 2026

The Network section imports the user's Gephi 0.11.3 export: 122 nodes, 136 directed relationships and 42 events, joined to 21 source entries and 49 evidence records. `dist/assets/dunhuang-network.gexf` is a byte-for-byte copy of that export. `network-provenance.json` records the source hashes. English event summaries and evidence limitations accompany the original Chinese research notes; they add no new historical claims.

The default compact view translates the five disconnected components closer together, preserving the layout within each component. Uncheck “Compact component view” to inspect the original exported coordinates. No new edges are drawn between disconnected components. Node sizes and colours, and edge colours, come from the user export. The downloaded GEXF always retains its original positions.

Search in either language, click nodes or edges to inspect their recorded roles and evidence, filter edges by layer, restrict to Dunhuang material, or focus on a selected neighbourhood. The year slider is cumulative by earliest recorded year; it is not a simulation of daily movement or proof that a proposed action occurred. The English/Chinese switch preserves network selection and filters. Known shared event IDs can navigate back to the existing route map. A keyboard-accessible node list provides an alternative to direct graph interaction.

Network source preparation: `python tools/prepare_network.py`, from the original research project location. It reads the saved Gephi export and curated evidence JSON without writing to either. After source changes, `python tools/build_offline.py` also updates the standalone exhibition, including its network and GEXF download. Browser verification scripts and reports are in the parent exhibition directory.
