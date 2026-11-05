# Data and interpretation

## Snapshots

The route map contains 17 reference places, 19 source relationships of which 18 are displayed, and five collecting institutions grouped by city. One Pelliot summary is excluded to avoid mixing incompatible scales; an explicitly labelled Beijing collection-level overview is included.

The Gephi snapshot contains **122 nodes, 136 directed relationships, 42 events, 21 source entries and 49 evidence records**. `network-provenance.json` records the exact user-export hash; `dist/assets/dunhuang-network.gexf` preserves that export. `data-provenance.json` records the route inputs and display decisions. No local filesystem paths, hosting credentials or institutional login sessions are needed to run this site.

## Read the graph carefully

The relationship guide opens with KE007, the inspection memorandum activity (5 nodes and 4 original edges). Pelliot’s nine knowledge-related activities remain selectable. The guide uses only edges directly attached to the chosen event and labels the recorded roles. **Full Gephi network (122)** restores the complete 122-node, 136-edge snapshot. The guide does not create pairwise links between co-participants, delete records or modify the downloadable GEXF. See [guide rules](docs/RELATIONSHIP_GUIDE.md).

- **Positions:** the network is relational, not geographical. Compact view translates disconnected components without creating connecting edges.
- **Sizes:** relative sizes reflect the connection counts used in the saved Gephi export. They do not rank historical importance.
- **Arrows:** read the associated relation and role. Participation in an event is not automatically a physical transfer or direct communication.
- **Layers:** material circulation and knowledge transmission are edge attributes. Shared people remain visible when filtering a layer.
- **Dates:** the year filter is cumulative from the earliest recorded year of a range. A document date is not automatically the date of every action it describes.
- **States:** reported activity, a proposal, a promise and work in progress remain distinct.
- **Scope:** general Stein-collection work, site photography and expedition preparation are labelled separately from strict Dunhuang-material links.
- **Sources:** later accounts may share the same underlying primary document. Source count is not a confidence weight.
- **Objects:** batches, individual manuscripts, images, works and printed manifestations remain separate analytical entities.

## Historical circulation and present holdings

The 1900–1910 historical network does not supply a complete custody chain for every manuscript currently in an institution. Paris arrival in 1909 is distinguished from manuscript-department entry in 1910. British Museum storage is not treated as formal accession. Current collection references were checked on 28 October 2026 and constitute a case-study snapshot, not a complete world inventory.

The website links to institutional collection pages. An institution holding an object does not imply that it is permanently on public display. Coordinates are city or site references rather than reconstructions of historical storage rooms or handover premises.

## Updating the exhibition

The original evidence workbooks and source PDFs remain in the research workspace. To update this public snapshot, export the reviewed data and Gephi graph there, carry the resulting public files into `dist/`, update the source hashes, run `python3 tools/verify_static.py`, and check both language views and the GitHub project subpath before publication. Do not replace qualified historical dates with invented exact dates.


## Preservation and completeness (2.2)

Six dated references support the separate preservation section. Paper condition, textual completeness, historical rebinding, catalogue units and image legibility are distinguished. Examples from 2009–2025 are not presented as a synchronous 2026 survey or an institutional ranking. See [the claim matrix and limits](docs/PRESERVATION.md). The Gephi and historical route snapshots remain unchanged.
