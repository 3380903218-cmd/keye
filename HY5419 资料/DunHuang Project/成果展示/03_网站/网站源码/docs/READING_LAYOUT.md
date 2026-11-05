# Reading layout, release 2.4.0

The previous desktop layout combined a large persistent header, fixed-height maps and an independently scrolling record panel. On shorter browser windows, the lower map controls and text continued beyond the visible area. An introductory three-column chapter menu also repeated the persistent header navigation.

## Arrangement

- Keep one persistent chapter navigation. Remove the repeated introductory menu, shorten the introduction and make the header 64 CSS pixels tall on desktop. The phone header uses two rows for the brand/language control and chapter links.
- Measure the actual header and control heights. Use the available viewport height for the route map and the full Gephi plot, retaining minimum usable plot sizes. Chapter links use a single anchor offset, so headings and workspaces clear the header.
- Put the route filters and timeline above the map. Show the complete selected record below the map, with its heading beside the explanation on desktop and above it on phones. Records have no independent scroll container or fixed maximum height.
- Put the Gephi legend below its full-width plot. Selected-node descriptions, relationships and source evidence expand beneath it. A nearby record link moves directly to that content.
- Keep the event guide’s selection control and three-column diagram together on normal desktop windows. Longer contextual explanations and evidence follow the diagram. On phones, the three steps form one vertical reading sequence.
- Retain the paper-note shapes, scroll and lotus detail, muted palette and straight connectors. Resize photographs proportionally without cropping or editing image bytes.

The purpose is to show each principal visual and its main controls together, while allowing long records to use ordinary page scrolling. A record with many participants, an expanded filter panel or larger user text can require more vertical space. Content is not hidden to force an entire chapter onto one screen.

## Data and interaction

This release does not change the historical datasets: 122 Gephi nodes, 136 edges, 42 events, 21 network sources and 49 evidence records. The downloadable GEXF and its original layout are unchanged. All three photographs, five collecting institutions and conservation examples remain available. The two language editions retain the same selections, role descriptions and source links.

Implementation is in `dist/reading-layout.css` and `dist/reading-layout.js`, with normal-flow record wrappers and updated internal anchors in the existing map and network scripts. The layout uses local CSS, JavaScript and images; it adds no remote service dependency.

## Verification

`reading-layout-verification.json` records browser checks at 1280×600, 1440×720, 1920×1080, 1024×768, 768×700, 390×844 and 320×640, in both languages. Checks cover anchor clearance, main plot bounds, readable guide names, normal-flow records, language switching and surviving evidence links. The default desktop guide is checked as a complete diagram; long activities remain naturally scrollable.

`relation-guide-verification.json` checks all 42 event projections against the original edge set and exercises guide, search, map and full-graph transitions. Separate offline and public-site receipts record the delivery checks. These automated checks do not replace a new human usability review or repeat the earlier family access test in China.
