# Current progress audit (2026-09-13)

## Completed in the supplied materials
- Research design: main question, pilot question, working hypothesis, public value, inclusion/exclusion rules.
- Evidence base: 7 locally downloaded full texts / primary OCR package; source manifest and evidence matrix; Pelliot official HTML route recorded.
- Data model: nodes / edges / sources fields and controlled relationship logic specified in the progress plan.
- Presentation requirements: six-page maximum structure, 7-minute timing, challenges, and three peer-feedback questions.

## Added in this work session
- `03_data_clean/nodes.csv`: 7 main pilot nodes.
- `03_data_clean/edges.csv`: 9 directed, source-linked pilot events for the Stein + Qing routes.
- `03_data_clean/sources.csv`: 5 source records resolving all main edge SourceRefs.
- `03_data_clean/data_dictionary.md`: import and interpretation rules.
- `03_data_clean/nodes_extension_pelliot.csv` and `edges_extension_pelliot.csv`: optional Pelliot extension, excluded from the main graph.
- `04_gephi/dunhuang_pilot_stein_qing.gexf`: Gephi-importable graph.
- `04_gephi/dunhuang_pilot_stein_qing.svg`: static presentation export of the same 7-node/9-event pilot.
- `04_gephi/gephi_parameters_v1.txt`: settings and reproducibility record.
- `06_notes/source_close_reading_stein_1907.md`: source-wording close reading.
- `05_presentation/HY5419_7分钟汇报_中文版_纯文字.txt`: timed Chinese script.

## Current quantitative check
7 main nodes; 9 main events; 5 source records; 0 broken node or SourceRef links. Main degree leaders are the Stein Central Asian Expedition (degree 6) and Wang Yuanlu (degree 5), followed by the Qing central government and the British Museum (degree 2). These are exploratory sample statistics only.

## Material limitation
The installed `/Applications/Gephi.app` is an Intel x86_64 build, while this machine is arm64 and has no usable Rosetta translation in the current environment. The graph file and CSVs are ready to import into Gephi on a compatible machine; the supplied SVG is a static export made from the same auditable rows for immediate presentation use.
