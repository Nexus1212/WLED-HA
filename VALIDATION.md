# Validierung: zwei Sekunden Standard-Wartezeit

Am 22.11.2026 lokal geprüft:

- Alle 29 Python-Tests mit `python -m unittest discover -s tests -v` bestanden.
  Die Zeitsteuerungs- und Adaptertests erwarten jetzt zwei Sekunden.
- Bestehende Tests bestätigen sofortige passende READY-Freigaben, ignorierte
  falsche/veraltete/doppelte Antworten, Abbruch durch OFF und Entladen,
  Zusammenführen weiterer ON-Befehle sowie unabhängige Segmente.
- `python -m compileall -q custom_components` erfolgreich.
- `node tests/test-node-red.js` erfolgreich: Routing, Request-ID-Erhalt,
  Freigabe-Payload und Verkabelung des Beispiels geprüft.
- `git diff --check` ohne Befund.

Die Zeitsteuerung wird kontrolliert simuliert; keine Prüfung mit einem laufenden
Home Assistant oder realen WLED-/KNX-Geräten. Die produktive Änderung beschränkt
sich auf die Wartezeit-Konstante; READY-, Abbruch- und Korrelationslogik sind unverändert.

# Validierung 0.2.0

Am 27.10.2026 lokal geprüft:

- Alle 28 Python-Tests in `tests/` bestanden, einschließlich frühzeitiger,
  doppelter, falscher, verspäteter und nach Ausschalten empfangener Freigaben.
- Python-Syntax aller Integrationsdateien mit `compileall` geprüft.
- Node-RED-Beispiele sind gültiges JSON; alle Verbindungsziele existieren.
- Die tatsächlichen Function-Knoten des neuen Flows mit Node.js geprüft:
  Segmentfilter, gespeicherte Request-ID, Antwortformat und fehlende IDs.
- Dashboard-YAML geparst; Entitätszuordnungen und Popup-Struktur geprüft.
- Effektliste enthält genau 29 eindeutige Namen, Solid zuerst.

Die Tests führen die Produktionslogik mit kontrollierter Zeit und die echte
Segment-Klasse mit Testdoubles aus. Home Assistant selbst und reale WLED-/KNX-
Geräte wurden durch diese Tests nicht gestartet bzw. bedient. Die Grundfunktion
von 0.1.0 wurde vom Anwender erfolgreich getestet. Die neue optionale Freigabe,
der Flow-Import und die Darstellung des Popups müssen noch in der Zielumgebung
geprüft werden. Der GitHub-Workflow prüft Syntax
und Verhalten erneut, sofern GitHub Actions für das Repository ausführbar ist.
