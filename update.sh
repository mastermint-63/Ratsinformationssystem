#!/bin/bash
# Ratstermine Dashboard - Automatische Aktualisierung

cd "$(dirname "$0")"
LOGFILE="$(pwd)/launchd.log"

# Termine abrufen
OUTPUT=$(/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 app.py --no-browser 2>&1)

# Anzahl Termine aus Output extrahieren
TERMINE=$(echo "$OUTPUT" | grep -o '[0-9]* Dateien generiert' | grep -o '[0-9]*')

# Klickbare macOS Benachrichtigung mit terminal-notifier
/opt/homebrew/bin/terminal-notifier \
    -title "Ratstermine" \
    -subtitle "$TERMINE Monate aktualisiert" \
    -message "Klicke zum Log öffnen" \
    -sound Glass \
    -execute "osascript -e 'tell application \"Terminal\" to do script \"tail -20 \\\"$LOGFILE\\\"\"'"

echo "Aktualisiert: $(date)"
echo "$OUTPUT"
