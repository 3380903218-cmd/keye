with timeout of 45 seconds
    set sourceAlias to (POSIX file "/Users/arourouwed/Desktop/NUS/2026-1/HY6101/seminar 11/HY6101_Combined_Essay2_English.docx") as alias
    tell application "Microsoft Word"
        open file name (sourceAlias as text) read only true add to recent files false revert true
        set essayDoc to document "HY6101_Combined_Essay2_English.docx"
        set essayText to content of text object of essayDoc
        if text 1 thru 22 of essayText is not "From Keeping Documents" then error "Word did not load the English translation."
        set print revisions of essayDoc to false
        set show revisions and comments of view of active window to false
        repaginate essayDoc
        set pageCount to compute statistics essayDoc statistic statistic pages
        set noteCount to count of footnotes of essayDoc
        save as essayDoc file name "/Users/arourouwed/Desktop/NUS/2026-1/HY6101/.essay2_english_20261026/english_render.pdf" file format format PDF
        return "pages=" & pageCount & "; footnotes=" & noteCount
    end tell
end timeout
