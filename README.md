# WLED – unveränderte Vergleichsbasis

Dieser Branch enthält die 19 unveränderten Dateien der offiziellen WLED-Integration aus Home Assistant Core **2026.10.4**. Die Dateiinhalte entsprechen den in `UPSTREAM.json` dokumentierten Git-Blobs. Nur der Ordnerpfad wurde von `homeassistant/components/wled/` auf `custom_components/wled/` abgebildet, damit GitHub die Dateien direkt vergleichen kann.

**Nur als Referenz verwenden. Diesen Branch nicht über HACS installieren.** Die angepasste, installierbare Version liegt auf `main`.

## Original mit unserer Version vergleichen

[Zeilenvergleich: Original → main](https://github.com/Nexus1212/WLED-HA/compare/upstream-2026.10.4..main)

Der Link verwendet bewusst **zwei Punkte** (`..`): Er vergleicht die beiden Dateistände direkt, unabhängig von ihrem gemeinsamen Vorfahren. Die Git-Historie von `main` wurde nicht umgeschrieben.

- **Rot:** Originalzeilen, die entfernt oder ersetzt wurden.
- **Grün:** Hinzugefügte Zeilen unserer Anpassung.
- Unter `custom_components/wled/`: Änderungen der eigentlichen Integration.
- Weitere neue Dateien: Tests, Node-RED-Beispiel, HACS-Konfiguration und Dokumentation.

Zum Zeitpunkt der Einrichtung: 17 Originaldateien unverändert; `light.py` und `manifest.json` geändert; `segment_commands.py` sowie zwei Übersetzungsdateien hinzugefügt.

Offizielle Quelle: https://github.com/home-assistant/core/tree/2026.10.4/homeassistant/components/wled

Lizenz: Apache 2.0, siehe `LICENSE.md`.
