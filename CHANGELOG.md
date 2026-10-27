# Versionshistorie

## 0.2.0

- Optionale frühzeitige Freigabe per `wled_segment_turn_on_ready` mit Entity-ID und Request-ID.
- Ohne Freigabe weiterhin eine Sekunde Wartezeit; keine verpflichtende Relais-Rückmeldung.
- Doppelte/veraltete Antworten lösen keinen weiteren Einschaltbefehl aus.
- Fertiger Node-RED-Flow und Browser-Mod-Karte für Arbeitszimmer EG.
- 28 automatisierte Python-Verhaltenstests; zusätzliche Prüfung der Flow-Funktionen.

## 0.1.0

- Basis: Home Assistant Core 2026.10.4, WLED-Bibliothek 1.1.1.
- 29 ausgewählte Effekte, Solid an erster Stelle.
- Segment-Einschaltanforderung mit Ereignis und fester Wartezeit von einer Sekunde.
- Keine Relais-Rückmeldung; OFF bricht wartendes ON ab.
- HACS-Struktur, Node-RED-Beispiel, Übersetzungen und Verhaltenstests.
- Erster Teststand; noch keine Prüfung an realer Hardware.
