"""Build the annotated reading list and its evidence records from checked metadata."""
from pathlib import Path
import csv
import hashlib
import json
import re
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'literature_data.json').read_text(encoding='utf-8'))
DATE = '2026-10-15'


def write_table(name, rows, delimiter='\t', fieldnames=None, bom=False):
    fields = fieldnames or list(rows[0])
    with (ROOT / name).open('w', encoding='utf-8-sig' if bom else 'utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def citation(d):
    authors = '；'.join(d['authors'])
    volume = d['volume']
    if d['issue']:
        volume += '(' + d['issue'] + ')'
    return f"{authors}. {d['year']}. {d['title']}[J]. {d['journal']}, {volume}: {d['pages']}."


sources, evidence, screening, bibliography = [], [], [], []
for index, d in enumerate(DATA, 1):
    present = bool(d['file']) and (ROOT / d['file']).is_file()
    d['full_text_status'] = 'present' if present else 'unavailable'
    d['citation'] = citation(d)
    sources.append({
        'source_id': d['id'], 'citation': d['citation'], 'stable_id': d['doi'] or d['url'],
        'version': ('2010转载正文；原刊未取得' if d['id'] == 'L03' else
                    '原刊扫描节选；153–161页' if d['id'] == 'L09' else
                    '期刊正文134–143页；未含另列160页英文摘要' if d['id'] == 'L05' else
                    '机构仓储摘要与正式书目信息；无正文' if not present else '期刊版'),
        'evidence_role': 'background' if d['id'] in {'L06', 'L09'} else 'original_study',
        'full_text_status': d['full_text_status'], 'full_text_path': d['file'] if present else '',
        'sha256': sha(ROOT / d['file']) if present else '',
        'notes': d['limit'] + '；已有来源对应：' + (d['legacy_id'] or '本次独立L编号，不修改S系列')
    })
    evidence.append({
        'evidence_id': f"E{index:02d}", 'claim_id': f"C{index:02d}", 'claim_text': d['claim'],
        'claim_status': 'fact', 'source_id': d['id'], 'source_role': sources[-1]['evidence_role'],
        'locator': d['locator'], 'evidence_excerpt': d['contribution'],
        'scope': '对所列研究内容和方法的有限概括；不替代原始历史档案',
        'direction': 'supports', 'strength': 'direct',
        'intended_use': 'method' if d['id'] == 'L10' else 'interpretation',
        'notes': d['limit']
    })
    search_id = {'L01': 'Q08', 'L02': 'Q09', 'L03': 'Q05', 'L04': 'Q07', 'L05': 'Q03',
                 'L06': 'Q02', 'L07': 'Q03', 'L08': 'Q06', 'L09': 'Q05', 'L10': 'Q05'}[d['id']]
    screening.append({
        'record_id': 'R_' + d['id'], 'search_id': search_id, 'source_id': d['id'],
        'title': d['title'], 'year': d['year'], 'stage': 'full_text' if present else 'abstract',
        'decision': 'include', 'decision_round': '1', 'current': 'true', 'supersedes': '',
        'reason': d['theme'] + '；' + d['use'], 'evidence_role': sources[-1]['evidence_role'],
        'notes': d['relationship'] + '；' + d['limit']
    })
    fields = [
        ('author', ' and '.join(a if ',' in a else '{' + a + '}' for a in d['authors'])),
        ('title', d['title']), ('journal', d['journal']), ('year', d['year']),
        ('volume', d['volume']), ('number', d['issue']), ('pages', d['pages'].replace('–', '--')),
        ('doi', d['doi']), ('url', d['url']), ('note', d['limit'])
    ]
    bibliography.append('@article{' + d['id'] + ',\n' + '\n'.join(
        f'  {key} = {{{value}}},' for key, value in fields if value) + '\n}\n')

exclusions = [
    ('X01', 'Q01', 'Doumy同题Accepted Manuscript（S02）', '2025', 'full_text', '与L01为同一研究的不同版本，不重复计为第二篇'),
    ('X02', 'Q01', 'The Nature of the Dunhuang Library Cave and the Reasons for its Sealing', '1999', 'full_text', '已有重要背景研究，主要讨论封藏问题；本轮10篇优先近现代流散与知识传播'),
    ('X03', 'Q01', 'Rewriting the Silk Road: a New Chapter for Dunhuang Manuscript Studies', '2025', 'full_text', '已有背景研究，主要为中古文书研究综述，不能直接说明1900年后的流转'),
    ('X04', 'Q01', 'Serindia, vol.2', '1921', 'full_text', '保留为项目一手史料；不计入本次10篇二手研究'),
    ('X05', 'Q01', 'Trois ans dans la haute Asie', '1910', 'full_text', '保留为项目一手史料；不计入本次10篇二手研究'),
    ('X06', 'Q02', 'Confronting Indiana Jones', '', 'title', '发现的是未确认正式出版身份的引用线索；不冒充已核实期刊论文'),
    ('X07', 'Q04', 'From digitisation to digital repatriation: A case study of International Dunhuang Project', '2025', 'abstract', '书章线索，本轮优先已核身份的期刊研究；未把二级聚合页的错误刊名直接纳入'),
    ('X08', 'Q07', '杏雨书屋藏敦煌《大般若经》写本缀合研究', '2020', 'abstract', '保留为物质证据归因争论的后续对读线索，全文本轮未核；相反解释在L04限制项中明确保留')
]
for rid, qid, title, year, stage, reason in exclusions:
    screening.append({'record_id': rid, 'search_id': qid, 'source_id': '', 'title': title, 'year': year,
                      'stage': stage, 'decision': 'exclude', 'decision_round': '1', 'current': 'true',
                      'supersedes': '', 'reason': reason, 'evidence_role': '',
                      'notes': '排除仅指未列入本轮十篇，不作无价值或不存在的判断'})

searches = []
for path in sorted((ROOT / 'sources').glob('lit_search_*.json')):
    raw = json.loads(path.read_text())
    number = int(path.stem.rsplit('_', 1)[1])
    searches.append({'search_id': f'Q{number:02d}', 'source': '内置web：发现检索＋期刊/机构页面核验',
                     'executed_date': DATE, 'query': json.dumps(raw['query'], ensure_ascii=False),
                     'filters': '中英文；期刊研究优先；不设出版年份下限',
                     'boundary': '保存本批返回结果；不是全库穷尽检索', 'raw_count': '', 'saved_count': '',
                     'output_path': str(path.relative_to(ROOT)), 'status': 'partial',
                     'notes': '搜索引擎未给出可审计的全库总数，故不补造命中数；同时复用既有本地研究'})

write_table('source-manifest.tsv', sources)
write_table('evidence-matrix.tsv', evidence)
write_table('screening-ledger.tsv', screening)
write_table('search-ledger.tsv', searches)
(ROOT / 'references.bib').write_text('\n'.join(bibliography), encoding='utf-8')

rows = []
for d in DATA:
    rows.append({'编号': d['id'], '作者': '；'.join(d['authors']), '年份': d['year'], '题名': d['title'],
                 '期刊': d['journal'], '卷': d['volume'], '期': d['issue'], '页码': d['pages'],
                 'DOI': d['doi'], '访问入口': d['url'], '语言': d['language'], '主题': d['theme'],
                 '已有或新增': d['relationship'], '阅读优先级': d['priority'], '主要贡献': d['contribution'],
                 '本项目用途': d['use'], '证据定位': d['locator'], '限制': d['limit'],
                 '全文状态': d['full_text_status'], '本地正文': d['file'], '旧来源ID': d['legacy_id']})
write_table('10篇文献整理表.csv', rows, delimiter=',', bom=True)

lines = [
    '# 敦煌写本实物流转与知识传播：10篇文献及阅读提纲', '',
    '检索与核验日期：2026年10月15日（新加坡）。本清单供HY5419简短叙述性文献综述使用，包含中文5篇、英文5篇，全部为期刊论文；4项已有研究重新精选，6项为本次新增。', '',
    '**资料状态：8篇PDF、1篇转载正文，另1篇保留机构仓储摘要和访问入口。** “取得正文”不表示逐条历史事件都已回溯原档；Cabos（L06）正文未取得；方广锠（L03）仅有转载；潘晟（L05）PDF含134–143页中文正文，不含书目另列160页英文摘要。', '',
    '优先阅读顺序建议：L01 → L02 → L05 → L07 → L03 → L04。L08选读近现代来源部分；L09、L10放到数字化与方法背景；L06补全文后再做深入论证。', '',
    '## 逐篇阅读', ''
]
for d in DATA:
    lines.extend([f"### {d['id']}　{d['theme']}", '', d['citation'], '',
                  f"**为什么读：** {d['contribution']}", '', f"**怎样用于本项目：** {d['use']}", '',
                  f"**先看哪里：** {d['locator']}。", '', f"**使用限制：** {d['limit']}", '',
                  f"**与现有资料的关系：** {d['relationship']}；旧来源：{d['legacy_id'] or '无，本次独立编号'}。", '',
                  f"[期刊或机构入口]({d['url']})" + (f"；[DOI](https://doi.org/{d['doi']})" if d['doi'] else '') +
                  (f"；[本地正文]({d['file']})" if d['full_text_status'] == 'present' else '；本次未取得正文。'), ''])

lines.extend([
    '## 简单文献综述怎样组织', '',
    '建议以“**敦煌写本从实物流散到知识传播：行动者、媒介与证据**”为工作题目，写成三个相互衔接的部分，而不是逐篇罗列摘要。', '',
    '**第一部分：实物如何被选择、转移和重新收藏。** 将L01、L02的地方行动者和取得／编号讨论，与L03、L04的北京接收及流散归因讨论对读。概括这组研究如何通过叙述、档案和物质痕迹重建来源，同时区分观察、转述与责任推定。', '',
    '**第二部分：实物移动怎样伴随消息、图像和学术判断的传播。** 以L05区分事件发生与其被知晓，以L07讨论图版刊布对旧藏关系的保存和选择，以L08说明保存、识别和编目如何参与材料意义的形成；L06只在摘要支持的范围内列为摄影研究方向，补读正文后再展开。', '',
    '**第三部分：数字关联能怎样呈现这些关系。** 以L09说明早期跨机构合作和数据库的目标，以L10补充实体、属性、关系分开表达的方法。研究对象和数字图像应分别登记，不能把数字可访问性当成实物归还，也不能把图像相似或语义相关当成历史人物之间实际传播。', '',
    '你的项目可提出一个有限而清楚的切入点：**围绕1900–1910年的具体事件，把已识别的实物转移与整理、查看、摄影和记录活动并列，用来源、角色及不确定性字段连接两层。** 这是基于本次文献组合的研究设计建议；本次定向检索不足以证明这一做法从未有人研究。', '',
    '1930年代刊布与1990年代以后数字化研究用于比较和方法背景，不据此自动扩大现有Gephi数据的时间范围。论文发表、计划和已完成活动应分别记录。', '',
    '## 获取与引用说明', '',
    '- `10篇文献整理表.csv`可用Excel打开；`references.bib`可导入Zotero等文献管理软件。',
    '- `full-text/`按L01–L10对应，只保存已验证的正文文件；L06没有占位PDF。原整期扫描和带前置页的来源副本放在`sources/originals/`，不是额外两篇研究。',
    '- L07网页元数据省略副题，参考文献按期刊PDF补全；L09标题按扫描正文写全，正文153–161页与CrossRef一致，未将162页广告计入。',
    '- L08按期刊版题名“In The Met”和作者Michelle C. Wang、Xin Wen、Susan Whitfield著录；旧机构条目存在不同题名和姓名排列，均按同一DOI只计一项研究。',
    '- 方广锠一文年份为2009，2010是转载时间。原刊与原档尚待取得；引用具体档案录文时需注明转引。',
    '- 本次没有更改旧综述、S系列来源登记或Gephi数据；本包L编号只用于这份阅读清单。',
    '- 本包是定向推荐清单。检索原始记录、筛选理由和证据定位分别见search-ledger.tsv、screening-ledger.tsv、evidence-matrix.tsv；书目和正文身份见source-manifest.tsv。', ''
])
(ROOT / '10篇核心文献与综述提纲.md').write_text('\n'.join(lines), encoding='utf-8')

assert len(DATA) == 10 and len({d['id'] for d in DATA}) == 10
assert len({d['doi'] for d in DATA if d['doi']}) == 9
assert sum(d['language'] == '中文' for d in DATA) == 5
assert sum(d['full_text_status'] == 'present' for d in DATA) == 9
expected = {d['file'] for d in DATA if d['full_text_status'] == 'present'}
actual = {str(p.relative_to(ROOT)) for p in (ROOT / 'full-text').iterdir() if p.is_file()}
assert expected == actual, (expected, actual)
report = {'date': DATE, 'status': 'passed', 'selected': 10, 'Chinese': 5, 'English': 5,
          'existing_reselected': 4, 'new': 6, 'pdf_files': 8, 'reprinted_html': 1, 'unavailable_full_text': ['L06'],
          'note': 'Structural validation does not authenticate all historical assertions. L03 is a reprint; L05 English abstract on160 not included; L06 is abstract-only.',
          'sources': [{'id': s['source_id'], 'path': s['full_text_path'], 'sha256': s['sha256']} for s in sources]}
(ROOT / 'package-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'sources'}, ensure_ascii=False))
