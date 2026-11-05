# -*- coding: utf-8 -*-
"""Verified additions from the three NUS PDFs. Executed by curate_ready.py."""
pdfs={r['SourceId']:r for r in json.loads((ROOT/'sources/NUS_verified_PDFs.json').read_text())}
p06=Path(pdfs['G06']['file']);p10=Path(pdfs['G10']['file'])
for number,pageno in [(49,5),(50,13),(51,15),(52,15)]:
 record=evidence['EV%03d'%number]
 record.update(file=pdfs['L06']['file'],source_sha256=pdfs['L06']['sha256'],pages=[pageno],printed='印刷%d；PDF%d；原节名／注号见来源正文'%(pageno+95,pageno))
ev(53,'G10','印刷36；章节PDF10','作者将Stein箱件到达英国博物馆记为1909年1月。','与G13b所记1909年8月移入地下室的口径并列；默认只采用1909年，不择一精确月份。',p10,'January 1909')
ev(54,'G06','印刷215–216；PDF9–10','Lorimer于1909年10月中旬开始在英国博物馆整理Stein收藏；Droop同时期参与编目。','这是一般Stein材料处理，不把每件材料等同敦煌写本；不据周二叙述自行算出精确入职日。',p06,'mid-October')
ev(55,'G06','印刷216注44；PDF10','Andrews于1909年11月14日致信Stein报告助手编目和拆箱工作的进展。','报告日期不是所有编目动作发生日；信中提及助手不等于助手参与通信。',p06,'14-11-09','研究所引信函')
ev(56,'G10','印刷37及注28；章节PDF11','Stein在1909年11月20日信中让Andrews指导Droop和Lorimer并分派日常整理工作。','引文支持指导安排，不据此把某件写本的具体编号归给某人。',p10,'Nov. 20, 1909','研究所引信函')
ev(57,'G10','印刷36、53；章节PDF10、27','Stein的部分藏文敦煌写本1910年已存放于剑桥大学图书馆，7月8日信提及此事。','送抵日不明；批次为组级分析记录，不逐件补馆藏号。',p10,'July 8, 1910')
ev(58,'G10','印刷36、53；章节PDF10、27','Ridding与Thomas在1910年开始记录这些藏文写本；Ridding在剑桥进行编目。','Thomas的职责地在伦敦；不推定两人始终同处剑桥，也不把1914年加入的La Vallée Poussin提前。',p10,'began documenting the manuscripts in 1910')
ev(59,'G10','印刷53及注42；章节PDF27','1910年7月8日Stein信提出允许Ridding把至多三捆材料带回家工作。','记录请求本身；不把许可条件当作当天已经发生的实物搬运。',p10,'maximum of three bundles','研究所引信函中的请求')
ev(60,'G10','印刷38；章节PDF12，图9','Andrews在1909年7月22日于装箱清单上记下拆箱状态。','清单制作、补注、箱件拆开与写本编号不是同一动作；箱数不等于卷数。',p10,'July 22, 1909')
ev(61,'G10','印刷38；章节PDF12，图9','同一清单另有1910年1月7日拆箱状态补注。','此处未独立确定补注人，不因相邻叙述就强指Andrews。',p10,'January 7, 1910')

# A genuine source disagreement is expressed by coarser time, not a task for the user.
events['DH004'].update(DateText='1909年：材料存放英国博物馆；具体月份口径有异',DatePrecision='year_with_disputed_month',EvidenceIds='EV011;EV015;EV053',NotesZH='G10印刷36记1月到达BM，G13b章内2记8月移入地下室；本版采用共同年份1909，不混同到货、存放与正式入藏。')
for e in edges:
 if e['EventId']=='DH004':e['EvidenceIds']='EV011;EV053';e['NotesZH']=events['DH004']['NotesZH']
events['KE005'].update(Label='Unpacking and cataloguing Stein materials in London',LabelZH='伦敦Stein材料拆箱、编目与列单',EvidenceIds='EV015;EV054;EV060',NotesZH='Andrews主持；Lorimer于1909年10月中旬加入，Droop同期工作。一般Stein材料不等于全为敦煌写本。',Place='伦敦／英国博物馆整理工作区')
nodes['W001'].update(EvidenceIds='EV046',NotesZH='Stein原书印刷917页的备忘录摘文已核；原档全件未取得，不强认其与另见编目方案档号同一。')
nodes['B0009'].update(NotesZH='本组范围是论文所述Stein finds，并非逐件已核为敦煌写本；本版通过G06、G10补入整理团队的具名工作记录。')
nodes['N017'].update(NotesZH='Andrews主持伦敦Stein材料的拆箱与整理；姓名使用Frederick Henry Andrews，不据文献生年差异改动身份。')
addnode('N044','弗洛伦斯·洛里默','Florence Mary Glen Lorimer','Person','EV054','1909年10月中旬在BM开始整理Stein收藏；入职日仅取作者月中表述。')
addnode('N056','约翰·珀西瓦尔·德鲁普','John Percival Droop','Person','EV054;EV056','全名见G10印刷36；G06印刷216记其与Lorimer参与编目。')
edge('N044','KE005','KE005','participant_in_event','cataloguing_assistant','EV054','参与期从1909年10月中旬起；不代表年初已在岗。')
edge('N056','KE005','KE005','participant_in_event','cataloguing_assistant','EV054;EV056','1909年10月已加入；具体每项写本工作不逐件指派。')

addnode('W010','Andrews致Stein编目进展信（1909-11-14）','Andrews progress letter, 14 November 1909','Work','EV055','Bodleian MS Stein 37:219；据G06引文与注44。')
addevent('LETTER19091114','Andrews向Stein报告编目进展','Andrews reports cataloguing progress to Stein','progress_report_letter','1909-11-14（信函日期）',1909,'EV055','伦敦',notes='记录信函报告行为；Lorimer、Droop是信中所述工作人员，并非本条发信人。',precision='document_date',scope='General Stein collection context')
edge('N017','LETTER19091114','LETTER19091114','participant_in_event','sender','EV055')
edge('LETTER19091114','N005','LETTER19091114','addressed_to','addressed_recipient','EV055')
edge('LETTER19091114','W010','LETTER19091114','produces_work','letter','EV055')
addnode('W011','Stein致Andrews工作指导信（1909-11-20）','Stein instruction letter, 20 November 1909','Work','EV056','Bodleian MS Stein 37/225；按G10注28。')
addevent('LETTER19091120','Stein致信Andrews安排助手工作','Stein instructs Andrews about assistants’ work','work_instruction_letter','1909-11-20（信函日期）',1909,'EV056',notes='只收录指示；不把后续每一编号归属视为已证实。',precision='document_date',scope='General Stein collection context')
edge('N005','LETTER19091120','LETTER19091120','participant_in_event','sender','EV056')
edge('LETTER19091120','N017','LETTER19091120','addressed_to','addressed_recipient','EV056')
edge('LETTER19091120','W011','LETTER19091120','produces_work','letter','EV056')

addnode('N046','剑桥大学图书馆','Cambridge University Library','Institution','EV057;EV059','1910年藏文敦煌写本存放及工作场所；不等于永久所有权转移。')
addnode('N047','卡罗琳·玛丽·里丁','Caroline Mary Ridding','Person','EV058;EV059')
addnode('N054','弗雷德里克·威廉·托马斯','Frederick William Thomas','Person','EV058','India Office Library馆员；不推定与Ridding始终同处剑桥。')
addnode('B0013','1910年剑桥存放与整理的藏文敦煌写本组','Tibetan Dunhuang manuscripts deposited at Cambridge','Collection','EV057;EV058','分析组而非新取得批次；具体馆藏号未逐件匹配。')
addevent('DH_CAM1910','部分藏文敦煌写本存放于剑桥大学图书馆','Tibetan Dunhuang manuscripts deposited at Cambridge','temporary_deposit','1910年；7月8日信已提及存放',1910,'EV057','剑桥／剑桥大学图书馆','Physical circulation','B0013','确切送抵日未详；不是1910年新购入，也不主张永久入藏。',precision='year_with_terminus')
edge('B0013','DH_CAM1910','DH_CAM1910','subject_of_event','manuscript_group','EV057')
edge('DH_CAM1910','N046','DH_CAM1910','deposit_at','temporary_deposit_location','EV057')
edge('B0013','B0004','DH_CAM1910','subset_of_collection','analytical_subset','EV057','组级关联，不据此推定每一写本的完整运输路线。')
addevent('CAT_CAM1910','Ridding与Thomas记录藏文敦煌写本','Ridding and Thomas document Tibetan Dunhuang manuscripts','manuscript_documentation','1910年（Ridding至8月已开始编目）',1910,'EV058','剑桥（Ridding工作）；伦敦（Thomas职责）',objects='B0013',notes='记录正在进行的工作；1914年La Vallée Poussin加入属后续，不提前到1910。',state='Work in progress')
edge('B0013','CAT_CAM1910','CAT_CAM1910','subject_of_event','tibetan_manuscripts','EV058')
edge('N047','CAT_CAM1910','CAT_CAM1910','participant_in_event','cataloguer','EV058')
edge('N054','CAT_CAM1910','CAT_CAM1910','participant_in_event','documenter_and_librarian','EV058')

addnode('W012','Stein关于Ridding在家工作的信（1910-07-08）','Stein letter concerning Ridding’s home work, 8 July 1910','Work','EV059','据G10印刷53及Wang/Perkins2008页37；未补未知收件人。')
addevent('REQUEST19100708','Stein提出Ridding可带少量写本回家工作','Stein requests limited home access for Ridding','home_access_request','1910-07-08（信函日期）',1910,'EV059',objects='B0013',notes='至多三捆是请求条件，不作为已执行的当天运输。',precision='document_date',state='Proposal made')
edge('N005','REQUEST19100708','REQUEST19100708','participant_in_event','requester','EV059')
edge('B0013','REQUEST19100708','REQUEST19100708','subject_of_event','manuscripts_under_request','EV059')
edge('REQUEST19100708','W012','REQUEST19100708','documented_in','request_letter','EV059')

addnode('W013','1908年装箱清单及后续拆箱补注','Packing list with later unpacking annotations','Work','EV060;EV061','MSS Stein 37/119–120；箱、捆、卷分单位，原清单与后加批注分日期。')
addevent('NOTE19090722','Andrews在清单补记拆箱状态','Andrews annotates unpacking status','packing_list_annotation','1909-07-22（清单补注日期）',1909,'EV060','伦敦',notes='记录清单补注，不当作新取得或全部材料已拆箱。',precision='document_date',scope='General Stein collection context')
edge('N017','NOTE19090722','NOTE19090722','participant_in_event','annotator','EV060')
edge('NOTE19090722','W013','NOTE19090722','annotates_work','unpacking_note','EV060')
addevent('NOTE19100107','装箱清单再记拆箱状态','Further unpacking-status annotation','packing_list_annotation','1910-01-07（清单补注日期）',1910,'EV061','伦敦',notes='本段未明确补注人；没有将该条硬归Andrews。',precision='document_date',scope='General Stein collection context')
edge('NOTE19100107','W013','NOTE19100107','annotates_work','unpacking_note','EV061')

# Already established later events are retained as scope decisions, not uncertainties.
excluded.append(dict(RecordId='G10_LAVALLEE1914',EventId='FOLLOWUP_1914',What='La Vallée Poussin于1914年加入藏文编目',Reason='正文已核：G10印刷36–37、53。事实属于1914年以后，未提前塞入1900–1910默认图。',EvidenceIds='EV058'))
