"""Create English display labels without changing the historical network."""
from pathlib import Path
import csv
import hashlib
import json
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent
G = 'http://www.gexf.net/1.2draft'
V = G + '/viz'
NS = {'g': G, 'v': V}
ET.register_namespace('', G)
ET.register_namespace('viz', V)

# Stable IDs are the join keys; English labels are editorial translations.
# Batch names and work titles remain analytical descriptions, not catalogue titles.
LABELS = {
    'N002': ('Wang Yuanlu', 'Wang Yuanlu'),
    'N004': ('Jiang Xiaowan', 'Jiang Xiaowan'),
    'N005': ('Aurel Stein', 'Aurel Stein'),
    'N006': ('Stein expedition', 'Stein expedition'),
    'N007': ('British Museum', 'British Museum'),
    'N009': ('Jingshi Library', 'Jingshi Library (Capital Library, Beijing)'),
    'N010': ('Shaan-Gan Governor-General', 'Office of the Governor-General of Shaanxi and Gansu'),
    'N011': ('Qing Ministry of Education', 'Qing Ministry of Education (Xuebu)'),
    'N012': ('Paul Pelliot', 'Paul Pelliot'),
    'N013': ('Pelliot expedition', 'Pelliot expedition'),
    'N014': ('National Library, Paris', 'National Library, Paris (Bibliotheque nationale)'),
    'N015': ('Ibrahim Beg', 'Ibrahim Beg'),
    'N016': ('Tila Bai', 'Tila Bai'),
    'N017': ('F. H. Andrews', 'Frederick Henry Andrews'),
    'B0001': ('B0001 First acquisition batch', "Materials associated with Stein's first acquisition agreement"),
    'B0002': ('B0002 Additional Mogao batch', "Materials associated with Stein's additional acquisition at Mogao"),
    'B0003': ('B0003 Anxi batch', 'Materials associated with the additional acquisition batch received at Anxi'),
    'B0004': ('B0004 BM deposit batch', "Materials associated with Stein's physical deposit at the British Museum"),
    'B0005': ('B0005 Pelliot acquisition batch', 'Manuscripts acquired by the Pelliot expedition from Wang Yuanlu'),
    'B0006': ('B0006 Jingshi main batch', 'Materials in the eighteen-case main batch collected for Jingshi Library'),
    'B0007': ('B0007 Jingshi supplementary batch', 'Materials in the supplementary batch received by Jingshi Library'),
    'B0008': ('B0008 Khotan working set', 'Materials associated with listing, numbering and indexing in Khotan in 1908'),
    'B0009': ('B0009 Andrews working set', 'Stein materials handled by Andrews after their arrival in Britain in 1909; scope unresolved'),
    'B0010': ('B0010 London inspection set', 'Chinese manuscripts from the Stein collection inspected by Pelliot in London in 1910'),
    'B0011': ('B0011 Paris catalogue consignment', 'First instalment sent to Paris for cataloguing in autumn 1910; members and receipt unresolved'),
    'B0012': ('B0012 Beijing display set', 'Small selection of manuscripts shown by Pelliot in Beijing in 1909'),
    'O0001': ('O0001 Or.8210/S.316', 'Manuscript Or.8210/S.316 discussed in source S03'),
    'O0002': ('O0002 Sample scroll', 'Sample scroll submitted in 1909; identification suggested by S19, not independently verified'),
    'R0001': ('R0001 Manuscript photographs', 'Group of manuscript photographs reported in the sources; individual images unidentified'),
    'W001': ('W001 Inspection memorandum', "Pelliot's memorandum on his inspection of Stein's Chinese manuscripts (working title)"),
    'W002': ('W002 Manuscript index slips', "Manuscript index slips prepared by Jiang Xiaowan (working title; original not located)"),
    'W003': ('W003 Stein notebook', 'Stein notebook MSS Stein 272/59'),
    'DH001': ('DH001 First acquisition', "Stein's first acquisition agreement"),
    'DH002': ('DH002 Additional Mogao acquisition', "Stein's additional acquisition at Mogao"),
    'DH003': ('DH003 Anxi acquisition batch', 'Additional acquisition batch received at Anxi'),
    'DH004': ('DH004 British Museum deposit', 'Physical deposit of Stein materials at the British Museum; not formal accession'),
    'DH005': ('DH005 Pelliot acquisition', 'Pelliot expedition acquisition of manuscripts from Wang Yuanlu'),
    'DH006': ('DH006 Paris library receipt', 'Arrival of Pelliot manuscripts in Paris and receipt by the National Library'),
    'DH007': ('DH007 Sample submission', 'Submission of a sample scroll by the Shaan-Gan Governor-General office to the Qing Ministry of Education'),
    'DH008': ('DH008 Jingshi main-batch receipt', 'Collection of the eighteen-case main batch by Jingshi Library'),
    'DH009': ('DH009 Jingshi supplementary receipt', 'Receipt of the supplementary batch by Jingshi Library'),
    'KE001': ('KE001 Initial listing', 'Initial listing of manuscripts'),
    'KE002': ('[Review] KE002 Manuscript numbering', 'Manuscript numbering; attribution inferred by the researcher, requiring verification'),
    'KE003': ('KE003 Index-slip compilation', 'Compilation of manuscript index slips'),
    'KE004': ('KE004 Notebook recording', 'Recording a manuscript in a notebook'),
    'KE005': ('[Review] KE005 Unpacking and listing', 'Unpacking, sorting and listing Stein materials; scope requiring verification'),
    'KE006': ('KE006 Manuscript inspection', 'Inspection of manuscripts by Pelliot'),
    'KE007': ('KE007 Inspection memorandum', 'Preparation of an inspection memorandum'),
    'KE008': ('KE008 Cataloguing (intention)', 'Conditional expression of willingness to catalogue; not completed cataloguing'),
    'KE009': ('KE009 Display and examination', 'Display and examination of manuscripts'),
    'KE010': ('KE010 Photography', 'Photography of manuscripts; individual images and photographers unresolved'),
    'PE001': ('[Review] PE001 Catalogue consignment', 'Temporary dispatch of manuscripts for cataloguing; sender, receipt and return requiring verification'),
}
EDGE_LABELS = {
    'subject_of_event': 'Subject of event',
    'transfer_from': 'Transfer source',
    'transfer_to': 'Recipient',
    'participant_in_event': 'Participant',
    'produces_work': 'Recorded work',
    'produces_representation': 'Photographic representation',
    'dispatch_destination': 'Intended dispatch destination',
}
LAYER_LABELS = {
    '实物流转': 'Physical circulation',
    '知识传播': 'Knowledge dissemination',
    '实物流转;知识传播': 'Physical circulation;Knowledge dissemination',
    '两层关联': 'Cross-layer record',
}
VIEWS = [
    ('双层传播网络.gexf', '双层传播网络_英文标签.gexf'),
    ('实物流转层/实物流转层.gexf', '实物流转层/实物流转层_英文标签.gexf'),
    ('知识传播层/知识传播层.gexf', '知识传播层/知识传播层_英文标签.gexf'),
    ('含待核记录/双层传播网络_含待核.gexf', '含待核记录/双层传播网络_含待核_英文标签.gexf'),
]


def values(element):
    return {v.get('for'): v.get('value') for v in element.findall('g:attvalues/g:attvalue', NS)}


def add_values(element, extra):
    container = element.find('g:attvalues', NS)
    if container is None:
        container = ET.SubElement(element, f'{{{G}}}attvalues')
    for key, value in extra.items():
        ET.SubElement(container, f'{{{G}}}attvalue', {'for': key, 'value': value})


def declarations(graph, kind, keys):
    container = graph.find(f'g:attributes[@class="{kind}"]', NS)
    for key in keys:
        ET.SubElement(container, f'{{{G}}}attribute', {'id': key, 'title': key, 'type': 'string'})


def write_csv(path, rows):
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def layer_label(value):
    return ';'.join(LAYER_LABELS[part] for part in value.split(';'))


def convert(relative_in, relative_out):
    source = SOURCE / relative_in
    before_hash = sha(source)
    original = ET.parse(source)
    tree = ET.parse(source)
    graph = tree.getroot().find('g:graph', NS)
    declarations(graph, 'node', ['LabelZh', 'LabelEn', 'FullLabelZh', 'FullLabelEn', 'LayerEn'])
    declarations(graph, 'edge', ['LabelZh', 'LayerEn'])
    nodes = graph.findall('g:nodes/g:node', NS)
    edges = graph.findall('g:edges/g:edge', NS)
    for node in nodes:
        short, full = LABELS[node.get('id')]
        old = values(node)
        add_values(node, {'LabelZh': node.get('label'), 'LabelEn': short,
                          'FullLabelZh': old.get('FullLabel', node.get('label')),
                          'FullLabelEn': full, 'LayerEn': layer_label(old['Layer'])})
        node.set('label', short)
        # FullLabel remains the original Chinese text; FullLabelEn holds translation.
    for edge in edges:
        old = values(edge)
        add_values(edge, {'LabelZh': edge.get('label', ''), 'LayerEn': layer_label(old['Layer'])})
        edge.set('label', EDGE_LABELS[old['Relation']])
    description = tree.getroot().find('g:meta/g:description', NS)
    description.text += ' English display labels added; original Chinese names and all historical attributes preserved.'
    output = HERE / relative_out
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space='  ')
    tree.write(output, encoding='utf-8', xml_declaration=True)

    # Verify node IDs, relationships, weights, every existing attribute and all viz data.
    loaded = ET.parse(output)
    for tag in ['node', 'edge']:
        old_elements = original.findall(f'g:graph/g:{tag}s/g:{tag}', NS)
        new_elements = loaded.findall(f'g:graph/g:{tag}s/g:{tag}', NS)
        assert len(old_elements) == len(new_elements)
        for old, new in zip(old_elements, new_elements):
            assert {k: v for k, v in old.attrib.items() if k != 'label'} == {k: v for k, v in new.attrib.items() if k != 'label'}
            assert all(values(new).get(k) == v for k, v in values(old).items())
            assert old.find('v:position', NS).attrib == new.find('v:position', NS).attrib if tag == 'node' else True
            for visual in ['color', 'size']:
                a, b = old.find(f'v:{visual}', NS), new.find(f'v:{visual}', NS)
                assert (None if a is None else a.attrib) == (None if b is None else b.attrib)
            assert new.get('label').isascii()
    assert sha(source) == before_hash
    write_csv(output.parent / 'nodes.csv', [dict(Id=n.get('id'), Label=n.get('label'), **values(n)) for n in nodes])
    write_csv(output.parent / 'edges.csv', [dict(Id=e.get('id'), Source=e.get('source'), Target=e.get('target'),
                                              Type='Directed', Weight=e.get('weight'), Label=e.get('label'), **values(e)) for e in edges])
    result = {'source': str(source), 'source_sha256': before_hash, 'output': str(output), 'sha256': sha(output),
              'nodes': len(nodes), 'edges': len(edges), 'original_attributes_and_topology': 'unchanged',
              'ascii_display_labels': 'passed'}
    try:
        import networkx as nx
        old_graph = nx.read_gexf(source)
        new_graph = nx.read_gexf(output)
        assert set(old_graph) == set(new_graph)
        assert set(old_graph.edges()) == set(new_graph.edges())
        assert all(old_graph.edges[e]['weight'] == new_graph.edges[e]['weight'] for e in old_graph.edges())
        result['independent_parser'] = f'NetworkX {nx.__version__}: passed'
    except ImportError:
        result['independent_parser'] = 'not available'
    return result


if __name__ == '__main__':
    report = {'date': '2026-10-13', 'status': 'passed', 'GephiGUIImport': 'not_exercised',
              'scope': 'English display labels; no historical data or graph structure changed',
              'views': [convert(a, b) for a, b in VIEWS]}
    rows = []
    for node in ET.parse(SOURCE / '含待核记录/双层传播网络_含待核.gexf').findall('g:graph/g:nodes/g:node', NS):
        short, full = LABELS[node.get('id')]
        rows.append({'Id': node.get('id'), 'LabelZh': node.get('label'), 'FullLabelZh': values(node)['FullLabel'],
                     'LabelEn': short, 'FullLabelEn': full, 'NodeType': values(node)['NodeType']})
    write_csv(HERE / '中英文节点名称对照.csv', rows)
    (HERE / '英文标签校验记录.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for view in report['views']:
        print(Path(view['output']).relative_to(HERE), view['nodes'], view['edges'], view['independent_parser'])
