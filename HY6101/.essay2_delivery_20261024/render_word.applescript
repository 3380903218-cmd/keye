with timeout of 45 seconds
    tell application "Microsoft Word"
        open file name "/Users/arourouwed/Desktop/NUS/2026-1/HY6101/seminar 11/HY6101_Combined_Essay2_中文版.docx" read only true add to recent files false
        set essayDoc to document "HY6101_Combined_Essay2_中文版.docx"
        repaginate essayDoc
        set pageCount to compute statistics essayDoc statistic statistic pages
        set eastAsianCount to compute statistics essayDoc statistic statistic east asian characters
        save as essayDoc file name "/Users/arourouwed/Desktop/NUS/2026-1/HY6101/.essay2_delivery_20261024/word_render_v2.pdf" file format format PDF
        close essayDoc saving no
        return "pages=" & pageCount & "; east_asian_characters=" & eastAsianCount
    end tell
end timeout
