# USB Write Blocker Test

Dieses Skript führt Tests durch, um die Funktionalität eines USB Write Blockers zu überprüfen.

## Voraussetzungen

Bevor Sie beginnen, stellen Sie sicher, dass Sie Folgendes installiert und vorbereitet haben:

1. Python 3.x
2. Alle erforderlichen Bibliotheken. Installieren Sie diese mit:
   ```
   pip install -r requirements.txt
   ```
3. MFTECmd: Laden Sie es von [Eric Zimmerman's Tools](https://ericzimmerman.github.io/#!index.md) herunter und installieren Sie es. Beachten Sie, dass MFTECmd .NET 6 benötigt.

## Vorbereitung des Testspeichermediums

- Formatieren Sie das Testspeichermedium als NTFS.
- Erstellen Sie eine Datei namens `testfile.txt` auf dem Speichermedium.
- **WICHTIG**: Stellen Sie sicher, dass sich keine wichtigen Daten auf dem Testspeichermedium befinden, da diese während des Tests gelöscht werden können!

## Verwendung

1. Öffnen Sie eine Kommandozeile mit Administratorrechten.
2. Navigieren Sie zum Verzeichnis, das das Skript enthält.
3. Führen Sie das Skript mit folgendem Befehl aus:
   ```
   python main.py [Laufwerksbuchstabe]: run_file_operations
   ```
   Beispiel:
   ```
   python main.py D: run_file_operations
   ```

## Funktionsweise

Das Skript führt folgende Operationen durch:
- Lesen einer Datei
- Modifizieren einer Datei
- Umbenennen einer Datei
- Löschen einer Datei
- Erstellen einer neuen Datei
- Ändern der Metadaten einer Datei

Nach jeder Operation wird die MFT (Master File Table) des Laufwerks analysiert, um festzustellen, ob Änderungen vorgenommen wurden.

## Ausgabe

Die Ergebnisse der Tests werden in einer Log-Datei im `logs`-Verzeichnis gespeichert. Der Dateiname enthält das aktuelle Datum und die Uhrzeit.

## Hinweis

Dieses Skript ist nur für Testzwecke gedacht. Verwenden Sie es nicht auf Laufwerken mit wichtigen Daten.