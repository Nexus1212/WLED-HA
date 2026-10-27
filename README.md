# WLED – unveränderte Vergleichsbasis

Dieser Branch enthält die 19 unveränderten Dateien der offiziellen WLED-Integration aus Home Assistant Core **2026.10.4**. Alle Originaldateien sind anhand der Git-Blob-Hashes in `UPSTREAM.json` geprüft. Nur der Pfad wurde auf `custom_components/wled/` abgebildet.

**Referenzbranch, nicht über HACS installieren.** Die installierbare Version liegt auf `main`.

## Originalvergleich

[Original → unsere Anpassungen (zeilenweise)](https://github.com/Nexus1212/WLED-HA/compare/upstream-2026.10.4...vergleich-anpassungen)

Der Branch `vergleich-anpassungen` enthält einen geprüften Schnappschuss von `main` (Commit `c59c7daaa8111f06923222b6c52eb0497e0ce619`), dessen Dateistand direkt auf dieser Originalbasis aufsetzt. Dadurch erkennt GitHub die tatsächlichen Unterschiede. Die Historie und Dateien von `main` bleiben unverändert. Nach späteren Änderungen an `main` muss der Vergleichsbranch entsprechend aktualisiert werden.

**Rot:** entfernte Originalzeilen. **Grün:** unsere Ergänzungen. Für die eigentliche Integration im Dateibaum `custom_components/wled/` öffnen.

- 17 Originaldateien unverändert.
- `light.py` und `manifest.json` geändert.
- `segment_commands.py` und zwei Übersetzungen neu.
- Weitere Ergänzungen: Dokumentation, HACS-Konfiguration, Tests und Node-RED-Beispiel.

Offizielle Quelle: https://github.com/home-assistant/core/tree/2026.10.4/homeassistant/components/wled

Apache License 2.0, siehe `LICENSE.md`.
