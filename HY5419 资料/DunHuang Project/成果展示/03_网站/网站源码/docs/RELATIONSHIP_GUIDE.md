# Relationship guide 2.1

The entry view now explains one recorded activity at a time. It replaces the initial Pelliot ego graph, whose labels and unlabeled arrows made the relationships difficult to read.

## Default example

The default activity is **KE007: writing an inspection memorandum**. Its four original edges connect:

- Stein as the requester;
- Pelliot as the memorandum author;
- the Stein Chinese manuscripts examined in London as the materials concerned;
- the memorandum as a recorded document, with its working-title qualification retained.

The explanatory sentence is based on **EV046 / S07**, which records Pelliot writing at Stein’s request and Stein printing extracts. The original limit remains visible: identity with a separately archived proposal is not assumed. The exact drafting date and location remain unresolved.

## Display rules

The guide uses only edges directly incident to the selected event. Incoming nodes are shown under people/materials, the event is in the centre, and outgoing nodes appear under documents/images/destinations. Role text is translated from each edge’s existing `Role` attribute. Desktop connectors retain the recorded source and target; on mobile, arrows join the groups rather than chaining individual people together.

A card opens the evidence attached to that edge. The default evidence panel uses the event’s evidence IDs. Evidence locators and original record IDs remain available; the notes do not imply that a citation establishes every field independently.

Pelliot’s nine knowledge-related activities can be selected individually; the order is an editorial reading order, not an assertion of exact chronology. The memorandum example comes first. Additional entries cover London collection work and the Beijing–Lanzhou telegram. Global search can open other activities, or return to the full graph where no directly connected activity is available.

For the Beijing banquet, eighteen attendee edges remain separate links to the event. Six are initially visible, with the remaining names expandable. No person-to-person clique is created. For the telegram, the addressed institution is distinguished from confirmed receipt. Proposals and promises remain explicitly qualified; an absent outcome node is described as absent from the dataset, not proof that no outcome existed.

Short display names clarify activities and long collection labels. Full records are retained in the data snapshot and original GEXF. The memorandum output remains labelled as a working title.

## Full graph and exports

**Full Gephi network (122)** opens all 122 nodes and 136 edges. It retains the Gephi coordinates, colours and relative sizes within each component; the existing compact-view control still translates whole disconnected components. A selected relationship can be opened in this view, and an event can be read again in the guide.

This release does not change `data.js`, `network-data.js` or the downloadable GEXF. The new files are `network-guide.js`, `network-guide.css` and `network-roles.js`; all assets remain local.

## Verification

`relation-guide-verification.json` records checks across 320, 390, 768, 1024 and 1440 pixel widths in both languages. All 42 event projections are compared against the original edge endpoints. Checks also cover selected-edge evidence, keyboard operation, language retention, proposal status, eighteen banquet attendees, telegram direction, route-map linking, global search and both full-network layers.


## Exhibition styling (2.2.3)

The guide uses muted sage, ochre and brown, with a scroll-shaped activity panel. Paper-note cards use asymmetric corners and a small folded edge. The central activity uses a scroll outline, warm paper colour and an original, decorative lotus drawing. Cards are vertically centred within the three columns. Connections use thin straight strokes and open arrowheads; a selected card and its connection use the site’s terracotta accent. Keyboard focus remains distinct. These are display-only colours: the original Gephi node/edge colours, research snapshot, directions and downloadable GEXF are unchanged.
