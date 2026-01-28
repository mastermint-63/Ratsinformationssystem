#!/bin/bash
# Ratstermine Dashboard - Automatische Aktualisierung

cd "$(dirname "$0")"

# Termine abrufen
OUTPUT=$(/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 app.py --no-browser 2>&1)

# Anzahl Termine aus Output extrahieren
TERMINE=$(echo "$OUTPUT" | grep -o '[0-9]* Dateien generiert' | grep -o '[0-9]*')

# macOS Benachrichtigung anzeigen
osascript -e "display notification \"$TERMINE Monate aktualisiert\" with title \"Ratstermine\" subtitle \"Klicke zum Öffnen\" sound name \"Glass\""

echo "Aktualisiert: $(date)"
echo "$OUTPUT"
