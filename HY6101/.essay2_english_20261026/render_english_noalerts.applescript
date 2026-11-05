tell application "Microsoft Word"
    set priorAlerts to display alerts
    set d to document "HY6101_Combined_Essay2_English.docx"
    activate object d
    set display alerts to alerts none
    try
        with timeout of 20 seconds
            save as d file name "/Users/arourouwed/Desktop/NUS/2026-1/HY6101/.essay2_english_20261026/english_render_noalerts.pdf" file format format PDF
        end timeout
        set display alerts to priorAlerts
        return "exported"
    on error errText number errNum
        set display alerts to priorAlerts
        return "export_failed: " & errNum & " " & errText
    end try
end tell
