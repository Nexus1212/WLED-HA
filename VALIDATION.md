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
