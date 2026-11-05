tell application "Microsoft Word"
    set priorAlerts to display alerts
    set display alerts to alerts none
    try
        with timeout of 30 seconds
            set sourceAlias to (POSIX file "/Users/arourouwed/Desktop/NUS/2026-1/HY6101/seminar 11/HY6101_Combined_Essay2_English.docx") as alias
            open file name (sourceAlias as text) read only true add to recent files false revert true
            set d to document "HY6101_Combined_Essay2_English.docx"
            activate object d
            repaginate d
            set pageCount to compute statistics d statistic statistic pages
            set noteCount to count of footnotes of d
            save as d file name "/Users/arourouwed/Desktop/NUS/2026-1/HY6101/.essay2_english_20261026/english_render_23pt.pdf" file format format PDF
        end timeout
        set display alerts to priorAlerts
        return "pages=" & pageCount & "; footnotes=" & noteCount
    on error errText number errNum
        set display alerts to priorAlerts
        error errText number errNum
    end try
end tell
