with timeout of 45 seconds
    tell application "Microsoft Word"
        open file name "/Users/arourouwed/Desktop/NUS/2026-1/HY6101/seminar 11/HY6101_Combined_Essay2_中文版.docx" read only true add to recent files false revert true
        set essayDoc to document "HY6101_Combined_Essay2_中文版.docx"
        set print revisions of essayDoc to false
        set show revisions and comments of view of active window to false
        set show comments of view of active window to false
        repaginate essayDoc
        set pageCount to compute statistics essayDoc statistic statistic pages
        save as essayDoc file name "/Users/arourouwed/Desktop/NUS/2026-1/HY6101/.essay2_revision_20261024/revision_render_04.pdf" file format format PDF
        return "pages=" & pageCount
    end tell
end timeout
