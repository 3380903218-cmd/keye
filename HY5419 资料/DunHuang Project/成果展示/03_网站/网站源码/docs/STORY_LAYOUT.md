# Story edition 2.1

The visitor should understand the research question before encountering the full data interface. The reading sequence is:

1. **Cover and question.** A locally stored image of the Diamond Sutra introduces Dunhuang manuscripts. The opening text distinguishes material circulation from knowledge transmission.
2. **Material circulation.** A route and its explanation appear together. The initial Stein view can be changed to Pelliot, the Qing government, or a comparison of all routes. The timeline, evidence and present-holdings view remain available.
3. **Knowledge transmission.** A dated telegram illustrates why a communication arrow differs from a shipment. The event-centred relationship guide starts with Stein requesting a memorandum and Pelliot writing it; names and roles are shown in separate cards. Other activities, London collection work, the telegram and the full Gephi graph are explicit alternatives. Global bilingual search can find any node.
4. **Collections today.** Five institutions are grouped into London, Paris and Beijing. Library manuscripts and museum paintings remain distinct.
5. **Sources and method.** The argument is followed by the existing research limits, source list and downloads.

## Presentation decisions

- Persistent chapter navigation, with a visible current chapter and a next-chapter link.
- Main narrative text at 18–23 CSS pixels; map explanations at 17–18 pixels; section headings at 33–50 pixels. Controls and secondary notes use a smaller scale, while mobile search inputs remain 16 pixels.
- Advanced filters, layout controls, long interpretation notes and record lists are expandable. They are not prerequisites for reading the story.
- Guide cards show full names and role text. In the full graph, labels retain collision avoidance; names remain available through selection, the inspector and the accessible node list.
- English and Chinese share the same layout. Language switching retains selections and updates the shareable URL.
- Scrolling updates navigation, but never changes map or graph filters. There is no forced scrolling or automatically starting playback.
- All core assets remain local, including map geometry, Gephi data, manuscript image and fonts supplied by the visitor’s system.

## Reference and research boundary

The arrangement is informed by the cover, persistent chapter navigation and text–visual sequence in [Storying on the Coquille River](https://storymaps.arcgis.com/stories/3678bc6932c74332b0d57adf3434aa55), inspected on 29 October 2026 through its rendered page and public ArcGIS story data. No reference-site images or narrative passages are reused.

This release changes presentation and guided entry points. The route dataset, network dataset and downloadable original GEXF remain unchanged. It adds no new historical stops, transfers or object-level provenance matches. The full graph preserves the original Gephi layout within each connected group. The event guide rearranges the same recorded links for reading, as described in `RELATIONSHIP_GUIDE.md`.

## Verification

See `relation-guide-verification.json` for the current guide and full-graph checks, including all 42 event projections. `story-layout-verification.json` and `copy-verification.json` retain the earlier layout and copy checks. The family access report refers to an earlier release on the same GitHub Pages host; it is not a new human usability test of this redesign.
