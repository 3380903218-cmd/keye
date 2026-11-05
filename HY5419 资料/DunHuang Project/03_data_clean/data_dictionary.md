# Pilot data dictionary

## Scope
1900-1910, focusing on documented custody and transfer events for Cave 17, the Stein path, and the Qing transmission-to-Beijing path. The main graph contains 9 directed events and 7 nodes. Pelliot is retained as an extension file.

## Rules
- Every main edge has at least one `SourceRef` that resolves to `sources.csv`.
- `Relationship` is the researcher's controlled coding; `SourceWording` preserves wording from the source.
- `YearStart` and `YearEnd` preserve uncertainty.
- Quantity is descriptive only; no edge weight is inferred from bundles/cases.
- Direction indicates documented movement or custody from Source to Target. It does not encode legal ownership, consent, responsibility, or cultural affiliation.
- Main graph uses `Weight=1` implicitly for all edges; repeated acquisition events remain separate rows.

## Gephi import
Import `nodes.csv` as Nodes table and `edges.csv` as Edges table. Set graph type to Directed. Use NodeType for color and Degree for exploratory size.
