# -*- coding: utf-8 -*-
"""Preserve the user's Gephi export and join its existing research evidence."""
from pathlib import Path
import collections, hashlib, json, math, shutil, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[1]
EXPORT=PROJECT/'04_gephi/双层传播网络_Gephi/Untitled.gexf'
RESEARCH=PROJECT/'文献/文献综述/Gephi传播网络_导入文件/web_network_data.json'
data=json.loads(RESEARCH.read_text())
xml=ET.parse(EXPORT).getroot()
local=lambda e:e.tag.rsplit('}',1)[-1]
def child(e,name):return next((n for n in e if local(n)==name),None)
graph=child(xml,'graph')
defs={a.attrib['class']:{v.attrib['id']:v.attrib['title'] for v in a} for a in graph if local(a)=='attributes'}
def attributes(item,kind):
    vals=child(item,'attvalues')
    return {defs[kind][v.attrib['for']]:v.attrib['value'] for v in (vals if vals is not None else [])}
def color(item):
    c=child(item,'color'); assert c is not None
    return '#'+''.join(f'{int(c.attrib[k]):02x}' for k in ['r','g','b'])
nodes=[]; edges=[]
for n in child(graph,'nodes'):
    a=attributes(n,'node'); p=child(n,'position'); s=child(n,'size')
    nodes.append(dict(id=n.attrib['id'],label=dict(en=n.attrib['label'],zh=a.get('LabelZH',n.attrib['label'])),type=a['NodeType'],layer=a['Layer'],x=float(p.attrib['x']),y=-float(p.attrib['y']),size=float(s.attrib['value']),color=color(n),attributes=a))
for e in child(graph,'edges'):
    a=attributes(e,'edge')
    edges.append(dict(id=e.attrib['id'],source=e.attrib['source'],target=e.attrib['target'],label=e.attrib.get('label',''),color=color(e),attributes=a))
assert len(nodes)==122 and len(edges)==136
assert {n['id'] for n in nodes}=={n['Id'] for n in data['nodes']}
assert {e['id'] for e in edges}=={e['Id'] for e in data['edges']}
assert all(math.isfinite(n['x']) and math.isfinite(n['y']) for n in nodes)
assert all(e['source'] in {n['id'] for n in nodes} and e['target'] in {n['id'] for n in nodes} for e in edges)

# English reading summaries of the existing Chinese research notes; no new claims.
event_text='''DH001|29 May–early 30 May 1907: agreement and night-time retrieval|Dunhuang / Mogao|The bundles are not 55 individual manuscripts. Negotiation and retrieval belong to one acquisition, not repeated transfers.
DH002|June 1907|Dunhuang / Mogao|The accounts give 20 and 13 bundles. Both are retained as variants; they do not establish two separate acquisitions.
DH003|Late September–early October 1907; unloading recorded for the evening of 4 October|Mogao to Anxi|Acquisition, transport and unloading are stages of one parent event. Hassan Akhun and Tila have different recorded roles.
DH004|1909; accounts differ on the month and stage|London / British Museum|One source reports arrival in January; another reports basement storage in August. Only the shared year is used. Deposit does not establish formal accession.
DH005|1908; examination and selection in March, handover date unresolved|Dunhuang / Mogao|Pelliot's stated reading and selection quantities are approximate. The expedition and its leader are not counted as two acquisitions.
DH006|Late 1909|Paris|Arrival in Paris is recorded separately from entry into the BnF manuscript department in 1910.
DH007|1909, inferred from a 1910 document referring to the previous year|Ministry of Education, Beijing; dispatch point unresolved|The later return of this sample is not a newly acquired additional manuscript. Unknown intermediate handovers are not reconstructed.
DH008|1910; before the cited Ministry document of the twelfth day of the eleventh lunar month|Beijing / Ministry of Education and Jingshi Library|The main batch is described as eighteen cases, not eighteen manuscripts. The precise receipt date and intermediate handovers remain unresolved.
DH009|15 December 1910, converted from Xuantong 2, lunar month 11, day 14|Beijing / Jingshi Library|The ledger records 22 scrolls and two scrapbooks. A previously submitted sample does not become a new twenty-third scroll. The original lunar date is retained in the research record.
KE001|July 1908|Khotan|The preliminary listing covered less than a third of the material. Listing, numbering and indexing are related work, not new acquisitions.
KE003|During packing at Khotan in 1908; exact day unresolved|Khotan|The reported index covers 1,318 items; its original has not been located. This is a work-coverage count, not an acquisition total.
KE004|27 June 1908, as quoted in research|Khotan, notebook context|The manuscript's date of 743 is distinct from its modern recording in 1908. Its inclusion in the later Paris consignment is not established.
KE005|1909; exact working period unresolved|London / British Museum working area|Andrews coordinated the work. Lorimer joined in mid-October, with Droop also working on the collection. General Stein material is not necessarily all Dunhuang manuscripts.
KE006|Early summer 1910; exact day unresolved|London / British Museum|Pelliot examined Stein materials in London. A later catalogue consignment is distinct from the material Pelliot acquired in 1908.
KE007|During the 1910 London inspection; exact drafting date unresolved|London inspection context; drafting location unconfirmed|Stein prints an extract of the memorandum. Its identity with a separately archived proposal is not assumed.
KE008|July 1910, memorandum context|Following the London inspection; drafting location unconfirmed|This records a proposal with conditions. It does not establish completed cataloguing or payment.
PE001|Autumn 1910; exact day unresolved|London to Paris, dispatch endpoints|Stein records dispatch for cataloguing. Receipt in 1910 and completed cataloguing are not thereby established.
KE009|August–September 1909, research context; exact day unresolved|Beijing|A small set was shown and examined. Individual visitors, manuscripts and later image matches are not fully established.
KE010|August–September 1909 context; exact photographic date unresolved|Beijing, examination context|The photographer and individual negative-to-manuscript matches remain unresolved. A photograph group is not the complete original manuscript collection.
MAP_KE011|Evening of 4 October 1909|Grand Hôtel des Wagons-Lits, Beijing|Eighteen named attendees form a documented minimum, not a claim to the total attendance. Shared attendance does not establish pairwise correspondence or manuscripts being present.
MAP_KE012|5 October 1909|Ministry of Education, Beijing → Governor-General's office, Lanzhou|Dispatch and intended institutional destination are recorded. Receipt and execution dates remain unresolved; this is not same-day shipment of manuscripts.
DH003_K01|26 September 1907 is a research inference; dispatch date not directly established|Anxi → Mogao, letter endpoints|The letter belongs to the Anxi acquisition process. Its date and the messenger's identity have different levels of certainty.
NEW_KA01|April 1907 in research; before the report of 20 May|Suzhou and the Shaanxi–Gansu administration|One step in a shared reported administrative chain, not a physical manuscript handover.
NEW_KA02|Before 20 May 1907; exact day unresolved|Governor-General → Ministry of Foreign Affairs|The newspaper's publication date is an upper boundary, not the telegram's exact dispatch date.
NEW_KA03|Before 20 May 1907; exact day unresolved|Beijing, diplomatic institutions|The reported note does not establish a British forwarding telegram, cessation of excavation or return of objects.
NEW_KP01|20 May 1907|Newspaper publication; the Beijing dateline is not used as a publication location|A publication event is distinct from the dates of the communications it reports. Individual readers are not inferred.
NEW_KP02|7 November 1909|Periodical publication; no city assigned|This records the published account. The identity of its text with the banquet pamphlet remains unresolved.
NEW_KE_YE19100123|23 January 1910|Diary entry; location not independently established|Ye records knowledge of British acquisitions without naming Stein. The source of the news and direct communication remain unknown.
NEW_KA_PROMISE1907|13 March 1907|Conversation context; precise location not independently established|Wang Jiayan's promise is recorded. It does not establish that the telegram was sent.
DH006_BNF1910|1910|Paris|BnF's institutional account identifies entry into the manuscript department. This is distinct from arrival in Paris in late 1909.
PH001|1908, Dunhuang expedition stage|Dunhuang / Mogao|Year precision accommodates differing arrival and departure accounts. Site photographs are not automatically photographs of every manuscript.
PHOTO_LETTERS1905|Correspondence during 1905–1906|Locations not independently established|The documented equipment correspondence is represented as a group. Individual letters and unknown dates are not invented.
LECTURE19091210|10 December 1909|Sorbonne, Paris|Projected expedition images and the later printed report are separate manifestations. Individual Dunhuang photographs are not all matched to the lecture.
PUB_S22_1910|1910|Paris|Publication of the illustrated report is distinct from the lecture's date in December 1909.
PHOTO_FUNDS19091226|26 December 1909, letter date; payment date unresolved|Paris|The 5,000 francs concerned photographic reproduction, not the separate 1910 cataloguing proposal. The payer and the identity behind Tongkang are not inferred.
LETTER19091114|14 November 1909, letter date|London|Andrews reports assistants' progress to Stein. Lorimer and Droop are discussed workers, not identified as senders of this letter.
LETTER19091120|20 November 1909, letter date|Endpoints not independently established|Stein gives working instructions. This does not establish who numbered each individual manuscript.
DH_CAM1910|1910; already deposited by the letter of 8 July|Cambridge / Cambridge University Library|The exact arrival date is unresolved. Temporary deposit does not establish purchase or permanent accession.
CAT_CAM1910|1910; Ridding had begun cataloguing by August|Cambridge for Ridding; London duties for Thomas|Work was in progress, not necessarily completed. Thomas is not assumed always to be in Cambridge; La Vallée Poussin joined later, in 1914.
REQUEST19100708|8 July 1910, letter date|Location not independently established|At most three bundles was a requested access condition, not proof of a same-day move to Ridding's home.
NOTE19090722|22 July 1909, packing-list annotation|London|A note on unpacking status is not a new acquisition or proof that every case was unpacked.
NOTE19100107|7 January 1910, packing-list annotation|London|The cited passage does not identify the annotator. It is not automatically attributed to Andrews.'''
event_en={}
for line in event_text.splitlines():
    eid,date,place,note=line.split('|');event_en[eid]=dict(date=date,place=place,note=note)
assert set(event_en)=={e['EventId'] for e in data['events']}

evidence_text='''EV001|Doumy interprets Wang Yuanlu as the first curator of the cave and its contents, emphasising his selection, custody and negotiating agency.|Curator is a historical interpretation, not a modern museum appointment or proof of ownership.
EV003|Jiang Xiaowan is described as negotiating with Wang Yuanlu and officials on Stein's behalf.|General mediation does not establish every role in each individual transaction.
EV043|An agreement was reached on 29 May, with material retrieved during the night into early 30 May.|Agreement, payment arrangements, retrieval and thanks are distinct. The date of thanks is not treated as proof of payment.
EV040|A purchase proposal was carried by a messenger to Mogao; the date of 26 September and identification of Jan-pao are research inferences.|The letter's action, date and messenger identity require separate assessment; the transliteration is not treated as a verified identity.
EV041|Tila and Ibrahim unloaded material at Anxi on the evening of 4 October, described in a diary entry dated 5 October.|The diary date is distinct from the action date. Tila is not automatically identified as an outbound carrier to Mogao.
EV042|Jiang Xiaowan travelled with silver and a party including Ibrahim Beg and Hassan Akhun, followed by transport of the material.|Hassan and Tila are different names; outward transport, return and unloading are distinct roles.
EV011|A source describes basement storage at the British Museum in August 1909 and Pelliot's first inspection there in 1910.|This concerns a storage stage, not necessarily arrival in London or formal accession. The underlying archive was not independently checked here.
EV053|Dotson and Doney date the arrival of Stein's cases at the British Museum to January 1909.|Another source dates basement storage to August. The dataset uses the shared year rather than choosing one precise month.
EV057|Some Tibetan Dunhuang manuscripts were deposited at Cambridge University Library by Stein's letter of 8 July 1910.|The arrival date is unresolved. This is a collection-level group without invented item-by-item shelfmarks.
EV048|The expedition material reached Paris in late 1909, after which manuscripts and artworks followed different institutional paths.|Paris arrival and the 1910 manuscript-department entry are separate stages, not a second acquisition.
EV044|BnF's collection history dates entry of Pelliot's Dunhuang manuscripts into its manuscript department to 1910.|Arrival in Paris, storage and institutional accession must be distinguished.
EV029|The Ministry documents and receipt ledger record eighteen cases, a supplementary 22 scrolls, and two scrapbooks.|Cases, scrolls and books are not added as equivalent units; a returned sample is not a new twenty-third scroll. Transcription is not independent archival inspection.
EV032|The article argues that moving from joins between fragments to deliberate tearing and then individual responsibility requires evidence at every step.|Cross-collection joins alone do not establish an edge alleging theft.
EV030|Fang identifies the original escort commissioner as He Yansheng and proposes matches between samples and supplementary scrolls.|The commissioner and shelfmark matches are research judgments; the original records and objects remain to be checked.
EV031|Xu proposes Fu Baoshu as a possible commissioner and questions the basis for identifying He Yansheng.|The dataset does not resolve the disagreement by inventing a named sender for the supplementary receipt.
EV045|Jiang Xiaowan undertook a preliminary listing in Khotan in July 1908, covering less than one third of the material.|Listing is not a new acquisition, and work coverage is not the size of the whole collection.
EV008|The article describes an index covering 1,318 items in case 91 and states that the list has not been found.|The count describes reported work coverage. The original index and its contents were not independently checked.
EV010|Unpacking and numbering associated with the case system began in 1909 and continued at least to 1914.|The work was not all completed in 1909. Later work lies beyond the core 1900–1910 period.
EV015|Andrews was employed by the India Office Library in 1909 to unpack, classify and list Stein finds.|Stein finds are not necessarily all Dunhuang manuscripts. A formal version and its manuscript copy do not provide independent corroboration.
EV016|The authors discuss possible routes by which a painted banner entered Andrews-related material and leave the question open.|A provenance hypothesis is not a confirmed custody chain; a painting is not automatically treated as a manuscript.
EV046|Pelliot wrote an inspection memorandum at Stein's request, and Stein prints extracts of it.|Its identity with the separately archived proposal, Or.13114/1 ff.37–44, is not assumed.
EV012|A July 1910 memorandum outlines Pelliot's cataloguing proposal, located as Or.13114/1 ff.37–44.|This proposal is not automatically identical to the inspection memorandum or evidence for its exact drafting date.
EV013|The proposal includes successive consignments to Paris, publication, payment of 5,000 francs on completion and publication rights.|Conditions do not establish payment or completion. The quantities describe the proposed cataloguing scope.
EV047|Stein records sending a first instalment of manuscripts to Paris for Pelliot's cataloguing in autumn 1910.|Dispatch is not receipt; a 1911 receipt date is not backdated as a dispatch date or proof of completed work.
EV017|Two attendees' diaries support the banquet on the evening of 4 October 1909 at the Grand Hôtel des Wagons-Lits.|This is distinct from earlier manuscript viewing. The original diary images were not checked here; attendance does not establish original manuscripts being present.
EV019|Qin uses Jiang Han's record of MacKimm to revisit the intermediary's identification and interpret his connecting role.|A name on an attendance list and a specific introduction have different evidential requirements; exact paths and dates remain unresolved.
EV033|Comparing early plates with present holdings can reveal omissions; missing printed lines alone do not establish loss of the original.|Objects, photographs, plates and catalogue records must be distinguished; comparison examples may extend beyond the core period.
EV034|Early plates can involve omissions, errors, distorted margins, hand copies and selective reproduction.|Photographs, copies and printed plates are not equivalent to the complete original object.
EV009|A notebook entry of 27 June 1908 links number 778, a manuscript date of 743, and Or.8210/S.316.|743 is the manuscript's date; 1908 is the recording date. Inclusion in a Paris consignment is not established.
EV054|Lorimer began work on the Stein collection in mid-October 1909, while Droop was also cataloguing.|This concerns the broader collection; an exact start day is not calculated from the narrative's reference to Tuesday.
EV060|Andrews annotated the packing list with unpacking status on 22 July 1909.|Making a list, annotating it, opening cases and numbering manuscripts are different actions. Cases are not scroll counts.
EV056|In a letter of 20 November 1909, Stein instructed Andrews to direct Droop and Lorimer's routine work.|The instruction does not identify who assigned each manuscript number.
EV022|The quoted diary entry for 13 March records Wang Jiayan agreeing to send Shengyun a telegram on Stein's behalf.|Agreement is not proof of dispatch; other predicted reports on the page are the researcher's inferences.
EV055|Andrews wrote to Stein on 14 November 1909 about assistants' cataloguing and unpacking progress.|The report date is not the date of every reported action. Mentioned assistants are not necessarily correspondents.
EV059|Stein's letter of 8 July 1910 requested permission for Ridding to take at most three bundles home to work on.|A request and its conditions do not prove that a physical move occurred that day.
EV021|On 5 October 1909, the Ministry telegraphed the Governor-General's office in Lanzhou about safeguarding and transporting the remaining manuscripts.|Dispatch and intended institutional destination are recorded; receipt and execution dates remain unresolved.
EV018|Jiang Han lists eighteen named attendees, including Pelliot, MacKimm and sixteen Chinese scholars, among them Wang Guowei.|This is a documented minimum rather than the total attendance; another account mentions more than twenty.
EV049|Nouette was the expedition photographer and corresponded with Pelliot about equipment during 1905–1906.|The correspondence is represented as a date range rather than invented individual letters and dates.
EV051|Pelliot's 1909 Sorbonne lecture displayed images, while the 1910 printed report reproduced Nouette's photographs.|Projection and print are separate manifestations; individual Dunhuang photographs are not all matched to the lecture.
EV052|A letter dated 26 December 1909 records 5,000 francs for photographic reproduction of Dunhuang material.|The letter date is not necessarily the payment date. The payer and the identity behind Tongkang remain unresolved.
EV050|The expedition made photographs at Dunhuang in 1908.|Different accounts give differing day boundaries, so the dataset uses the year. Site images are not photographs of every manuscript.
EV020|Qin distinguishes Dong Kang and Wang Shitong's organising roles from Luo Zhenyu's involvement in preparation but absence that evening.|Luo is not coded as an attendee. Organising attributions remain research interpretations.
EV026|The article discusses Luo's discovery account in Dongfang zazhi on 7 November 1909 and its omission of Stein.|This records the presentation of a particular text. Deliberate concealment is an interpretation, not an asserted interpersonal edge.
EV023|The Shenbao report of 20 May 1907 describes Chai's report, Shengyun's telegram and a Foreign Affairs note to the British minister.|Publication does not date each action. Original telegrams were not checked, and no cessation of excavation or object transfer is inferred.
EV025|Pan also quotes the Shenbao report about a request to stop excavation.|The same newspaper text is shared with G14; it is not a second independent primary telegram.
EV024|The author cannot establish whether Jordan's 6 July meeting at Foreign Affairs discussed Stein's archaeology.|No factual edge for that discussion is created; absence of located correspondence does not prove an event did not occur.
EV027|Ye Changchi's entry of 23 January 1910 mentions British acquisition of manuscripts without naming Stein.|The entry records awareness, not a known news source or direct Stein-to-Ye communication.
EV058|Ridding and Thomas began documenting the Tibetan manuscripts in 1910, with Ridding cataloguing in Cambridge.|Thomas had London duties; constant co-presence in Cambridge is not assumed. La Vallée Poussin's 1914 involvement is not moved into 1910.
EV061|The same packing list contains a further unpacking-status annotation dated 7 January 1910.|The annotator is not independently identified in this passage and is not automatically assumed to be Andrews.'''
ev_en={}
for line in evidence_text.splitlines():
    eid,claim,limit=line.split('|');ev_en[eid]=(claim,limit)
assert set(ev_en)=={e['id'] for e in data['evidence']}
events=[dict(e,english=event_en[e['EventId']]) for e in data['events']]
display_zh={
    'MAP_KE011':'18位具名与会者为可确认下限，不代表实际总人数；共同出席不等于逐对通信，也不证明原卷当晚在场。',
    'MAP_KE012':'记录学部发出电报及其目的机构；收讫与执行日期尚未落实，不等于当日实物发运。',
    'NEW_KA_PROMISE1907':'记录王家彦答应代斯坦因向升允发电；承诺不等于已发送，不补写未知的执行日期。',
}
for event in events:
    if event['EventId'] in display_zh:event['displayNoteZH']=display_zh[event['EventId']]
evidence=[dict(e,claimEN=ev_en[e['id']][0],limitEN=ev_en[e['id']][1]) for e in data['evidence']]
safe=dict(meta=dict(version='1.1.0',date='2026-10-29',period='1900–1910',sourceFile=EXPORT.name,sourceHash=hashlib.sha256(EXPORT.read_bytes()).hexdigest(),researchHash=hashlib.sha256(RESEARCH.read_bytes()).hexdigest()),nodes=nodes,edges=edges,events=events,evidence=evidence,sources=data['sources'])
assert '/Users/' not in json.dumps(safe,ensure_ascii=False)
(ROOT/'dist/network-data.js').write_text('window.DUNHUANG_NETWORK = '+json.dumps(safe,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
shutil.copyfile(EXPORT,ROOT/'dist/assets/dunhuang-network.gexf')
(ROOT/'network-provenance.json').write_text(json.dumps(dict(**safe['meta'],counts=dict(nodes=len(nodes),edges=len(edges),events=len(events),sources=len(data['sources']),evidence=len(evidence)),geometry='User Gephi 0.11.3 export; y inverted only for SVG screen coordinates',translations='English reading summaries of existing Chinese event notes and evidence; original Chinese retained',sourceFilesUnchanged=True),ensure_ascii=False,indent=2))
print('Prepared Gephi network:',len(nodes),'nodes,',len(edges),'edges; user positions, sizes and colours retained.')
