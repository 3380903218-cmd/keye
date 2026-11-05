# Reader-first edition, 2.5.0

Historical layout note. Release 2.6.0 restores QGIS and Gephi as directly visible principal results; see [the current arrangement](RESULTS_SHOWCASE.md). The optional-network arrangement described below is superseded.

The previous page placed many choices before the visitor: playback, years, layers, event selection, node search and evidence inspection. This edition gives the principal findings a continuous reading order. Interaction supplements the reading rather than being necessary to reveal it.

## Reading and optional exploration

1. The introduction and photographs establish the place and research question. The cover has one reading action.
2. The route chapter states the London, Paris and Beijing destinations directly. Four route buttons and three map controls remain available. Playback, years, layers, presentation mode and detailed record lists share one optional disclosure below the map. Closing it pauses active playback.
3. The knowledge chapter displays three complete examples: the Beijing–Lanzhou telegram, the London cataloguing team and Pelliot’s inspection memorandum. Each gives the relevant names and roles, the main claim, a visible uncertainty statement and page-level source references. No button, select box, accordion or node click is required to read these examples. The earlier separate telegram panel is removed.
4. The complete Gephi network occupies one optional disclosure after these examples. Its default is the full graph. The existing event guides, search, filtering, source inspection and downloads remain available. Opening the workspace fits the graph to its newly visible area, without resetting the visitor’s selections. Links to content inside a closed workspace open its parent disclosure.
5. Collecting institutions and preservation records remain directly readable. Collection cards retain their official catalogue links; repeated “locate on map” actions and the collection subsection menu are removed.

The original paper-note/scroll guide and straight connectors remain in the optional network workspace. Photographs, their viewer, attribution and bilingual captions are retained. Image-view labels appear on hover or keyboard focus rather than competing with every caption.

## Evidence boundaries

The three readable examples use existing event IDs `MAP_KE012`, `KE005` and `KE007`, representing 2, 5 and 4 original incident relationships respectively. Their role lists summarise those records; they do not add direct person-to-person edges. Visible citations use:

- Telegram: `EV021`, Qin Hualin (2018), p. 48. Dispatch and addressed institution do not establish receipt or execution dates.
- Cataloguing: `EV015`, Wang, Wen and Whitfield (2020), p. 20; `EV054`, Helen Wang (1998), pp. 215–216; `EV056`, Dotson and Doney (2025), p. 37, note 28. The broader Stein collection is not treated as entirely Dunhuang material, and individual manuscript-number assignments are not inferred.
- Memorandum: `EV046`, Stein (1921), volume II, pp. 916–917. Exact drafting date/location and identity with the separately archived proposal remain unresolved.

These are presentation summaries of previously verified project records, not new research findings or a new source audit. Historical data, original Gephi positions and the GEXF file remain unchanged: 122 nodes, 136 edges, 42 events, 21 network source entries and 49 evidence records. The collection and preservation source-check date remains 29 October 2026.

## Implementation and checks

`reader-first.js` renders the three narrative examples from the project snapshot and preserves optional-tool behaviour. `reader-first.css` provides a reading layout without adding external dependencies. The revised HTML groups the original controls and removes repeated entry points.

`reader-first-verification.json` checks both languages at seven window sizes, including a 1280×600 desktop viewport and 320×640 phone viewport. It checks the closed default state, readable cases, original edge/evidence membership, reduced visible controls, map sizing, optional playback and pause, keyboard opening, search, role evidence, language retention and deep links. The guide regression separately checks all 42 original event projections. Public and offline delivery receipts record the deployed release; they do not imply a new human usability test or another access test from mainland China.
