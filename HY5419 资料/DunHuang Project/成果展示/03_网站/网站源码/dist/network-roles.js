/* Display translations for recorded roles. They do not add or reverse edges. */
(() => {
  'use strict';
  const labels={
    '对象／批次关联':['Materials concerned','所涉材料'],
    '接收行动／机构':['Recipient / receiving institution','接收方／收存机构'],
    '转出／拨送主体;转出／拨送主体（按事件定义）':['Dispatching party','转出／拨送方'],
    negotiator:['Negotiation','参与交涉'],transport_assistant:['Transport assistance','协助运输'],
    'negotiator;transport_assistant':['Negotiation and transport assistance','参与交涉、协助运输'],
    acquiring_expedition_leader:['Leader of acquiring expedition','取得材料的考察队负责人'],
    'carrier;unloader_at_Anxi':['Carrying and unloading at Anxi','驮运及安西卸载'],unloader_at_Anxi:['Unloading at Anxi','在安西卸载'],
    'selector;negotiator':['Selection and negotiation','选择材料、参与交涉'],expedition_collection_source:['Related expedition collection','相关考察收藏'],
    '初步列单参与':['Initial listing','参与初步列单'],
    '所记载的记录／载体成果':['Recorded document / output','形成的文书'],
    '索引卡制作（据转引）':['Index-card preparation (as cited)','制作索引卡（据转引）'],
    '笔记记录者':['Notebook recorder','记录笔记'], '整理者':['Collection arrangement','整理材料'],
    '检查者':['Manuscript examination','检查写本'], '请求者':['Requesting party','提出请求'],
    '备忘录作者（据S07）':['Memorandum author','撰写备忘录'],
    '有条件表示编目意向':['Conditional cataloguing proposal','提出附条件编目方案'],
    '展示提供者／叙述者':['Providing / describing the display','提供展示／叙述展示情况'],
    '文中照片组':['Photographs in the publication','文中所用照片'],
    '所称送寄目的方;所称送寄对象':['Intended dispatch recipient','所称送寄对象'],
    attendee:['Attendance','出席活动'],sender:['Sender','发出文书'],addressed_recipient:['Addressed recipient','文书指向的接收方'],
    publisher:['Publisher','出版机构'],published_report:['Published report','发表的报告'],credited_author:['Credited author','署名作者'],
    periodical_version:['Periodical version','期刊版本'],pamphlet_circulation:['Pamphlet circulation','流通的小册子'],
    diarist:['Diary author','日记作者'],diary_entry:['Diary entry','日记条目'],carrier:['Carrying materials','运送材料'],
    employing_institution:['Employing institution','雇用机构'],promisor:['Recorded promise','作出承诺'],requester:['Requesting party','提出请求'],
    manuscript_collection:['Manuscript collection','写本收藏'],photographer:['Photographer','拍摄照片'],expedition_context:['Expedition context','相关考察背景'],
    site_photographs:['Site photographs','遗址照片'],correspondent:['Correspondence','往来通信'],speaker:['Speaker','发表讲演'],
    projected_photographs:['Projected photographs','放映的照片'],author:['Author','作者'],printed_report:['Printed report','印刷报告'],
    photo_engravings:['Photographic engravings','照相制版图像'],credited_photographer:['Credited photographer','署名摄影者'],
    reported_funds_recipient:['Reported recipient of funds','信中所述收款人'],letter_evidence:['Recorded in a letter','记载于信函'],
    pamphlet_author:['Pamphlet author','小册子作者'],recorded_imprint:['Recorded imprint','记载的出版信息'],
    cataloguing_assistant:['Cataloguing assistance','协助编目'],letter:['Letter','相关信函'],manuscript_group:['Manuscript group','所涉写本组'],
    temporary_deposit_location:['Temporary deposit location','临时存放地点'],analytical_subset:['Collection subset','收藏子集'],
    tibetan_manuscripts:['Tibetan manuscripts','藏文写本'],cataloguer:['Cataloguing','编目'],documenter_and_librarian:['Documentation and library work','记录与图书馆工作'],
    manuscripts_under_request:['Manuscripts concerned by the request','请求所涉写本'],request_letter:['Request letter','提出请求的信函'],
    annotator:['Annotation','补注文书'],unpacking_note:['Unpacking note','拆箱记录']
  };
  window.DUNHUANG_RELATION_TEXT=(edge,lang,fallback='')=>{
    if(edge.attributes.RoleEN)return edge.attributes[lang==='zh'?'RoleZH':'RoleEN'];
    const role=edge.attributes.Role||'',item=labels[role];
    return item?item[lang==='zh'?1:0]:fallback||edge.label||role;
  };
})();
