with timeout of 30 seconds
    set sourceAlias to (POSIX file "/Users/arourouwed/Desktop/NUS/2026-1/HY6101/seminar 11/HY6101_Combined_Essay2_English.docx") as alias
    set targetPath to (POSIX file "/Users/arourouwed/Desktop/NUS/2026-1/HY6101/seminar 11/_HY6101_English_preview_20261026.pdf") as text
    tell application "Microsoft Word"
        open file name (sourceAlias as text) read only false add to recent files false revert true
        set d to document "HY6101_Combined_Essay2_English.docx"
        set print revisions of d to false
        repaginate d
        save as d file name targetPath file format format PDF
        return "exported"
    end tell
end timeout
