with timeout of 45 seconds
    tell application "Microsoft Word"
        open file name "/Users/arourouwed/Desktop/NUS/2026-1/HY6101/seminar 11/HY6101_Combined_Essay2_中文版.docx" read only true add to recent files false revert true
        set essayDoc to document "HY6101_Combined_Essay2_中文版.docx"
        set documentText to content of text object of essayDoc
        if text 1 thru 11 of documentText does not contain "从保管文件到理解历史" then error "Word did not load the current revised document."
        set print revisions of essayDoc to false
        set show revisions and comments of view of active window to false
        set show comments of view of active window to false
        repaginate essayDoc
        set pageCount to compute statistics essayDoc statistic statistic pages
        save as essayDoc file name "/Users/arourouwed/Desktop/NUS/2026-1/HY6101/.essay2_revision_20261025/revision_render_final.pdf" file format format PDF
        return "pages=" & pageCount
    end tell
end timeout
