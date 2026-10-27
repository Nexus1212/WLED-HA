# Validierung 0.1.0

Am 27.10.2026 lokal geprüft:

- Alle 18 Tests in `tests/` bestanden.
- Python-Syntax aller Integrationsdateien mit `compileall` geprüft.
- Node-RED-Beispiel ist gültiges JSON; alle Verbindungsziele existieren.
- Effektliste enthält genau 29 eindeutige Namen, Solid zuerst.

Die Tests führen die Produktionslogik mit kontrollierter Zeit und die echte
Segment-Klasse mit Testdoubles aus. Home Assistant selbst und reale WLED-/KNX-
Geräte wurden nicht gestartet bzw. bedient. HACS-Installation und Node-RED-Import
müssen noch in der Zielumgebung geprüft werden. Der GitHub-Workflow prüft Syntax
und Verhalten erneut, sofern GitHub Actions für das Repository ausführbar ist.
