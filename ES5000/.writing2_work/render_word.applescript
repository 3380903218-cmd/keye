tell application "Microsoft Word"
    set openedByTask to false
    if not (exists document "G6_WANG XIWEN_p-s essay.docx") then
        open file name "/Users/arourouwed/Desktop/NUS/2026-1/ES5000/writing 2/G6_WANG XIWEN_p-s essay.docx" read only true add to recent files false
        set openedByTask to true
    end if
    set taskDocument to document "G6_WANG XIWEN_p-s essay.docx"
    repaginate taskDocument
    set pageTotal to compute statistics taskDocument statistic statistic pages
    set bodyStart to start of content of text object of paragraph 5 of taskDocument
    set bodyEnd to end of content of text object of paragraph 9 of taskDocument
    set essayRange to create range taskDocument start bodyStart end bodyEnd
    set bodyWords to compute text range statistics essayRange statistic statistic words
    activate object taskDocument
    if name of active document is not "G6_WANG XIWEN_p-s essay.docx" then error "Wrong active document for export."
    save as taskDocument file name "/Users/arourouwed/Desktop/NUS/2026-1/ES5000/.writing2_work/word_preview.pdf" file format format PDF add to recent files false
    if openedByTask then close taskDocument saving no
    return "pages=" & pageTotal & "; body_words=" & bodyWords
end tell
