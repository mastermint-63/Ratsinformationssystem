#!/bin/bash
# Ratstermine Dashboard - Automatische Aktualisierung mit GitHub Push

cd "$(dirname "$0")"
LOGFILE="$(pwd)/launchd.log"
DATUM=$(date +%Y-%m-%d)

echo "=========================================="
echo "Aktualisierung gestartet: $(date)"
echo "=========================================="

# Termine abrufen
OUTPUT=$(/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 app.py --no-browser 2>&1)
echo "$OUTPUT"

# Anzahl Termine aus Output extrahieren
MONATE=$(echo "$OUTPUT" | grep -o '[0-9]* Dateien generiert' | grep -o '[0-9]*')

# Zu GitHub pushen (nur wenn Änderungen vorhanden)
if git diff --quiet termine_*.html 2>/dev/null; then
    echo "Keine Änderungen - kein Push nötig"
    PUSH_STATUS="Keine Änderungen"
else
    echo "Änderungen gefunden - pushe zu GitHub..."
    git add termine_*.html index.html 2>/dev/null
    git commit -m "Termine aktualisiert $DATUM" 2>&1

    if git push 2>&1; then
        echo "Push erfolgreich!"
        PUSH_STATUS="GitHub aktualisiert"
    else
        echo "Push fehlgeschlagen!"
        PUSH_STATUS="Push fehlgeschlagen!"
    fi
fi

# Klickbare macOS Benachrichtigung mit terminal-notifier
/opt/homebrew/bin/terminal-notifier \
    -title "Ratstermine" \
    -subtitle "$MONATE Monate aktualisiert" \
    -message "$PUSH_STATUS - Klicke zum Log" \
    -sound Glass \
    -execute "osascript -e 'tell application \"Terminal\" to do script \"tail -30 \\\"$LOGFILE\\\"\"'"

# Warnung bei nicht erreichbaren Städten
FEHLER=$(echo "$OUTPUT" | grep '^FEHLER:')
if [ -n "$FEHLER" ]; then
    /opt/homebrew/bin/terminal-notifier \
        -title "⚠ Ratstermine Warnung" \
        -subtitle "Städte nicht erreichbar" \
        -message "$FEHLER" \
        -sound Basso \
        -execute "osascript -e 'tell application \"Terminal\" to do script \"tail -40 \\\"$LOGFILE\\\"\"'"
fi

echo ""
echo "Fertig: $(date)"
