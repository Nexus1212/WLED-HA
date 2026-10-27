# WLED HA

Angepasste Home-Assistant-WLED-Integration auf Basis von **Core 2026.10.4**.
Version **0.2.1**. Die Grundfunktion von 0.1.0 wurde vom Anwender erfolgreich
getestet. Die optionale Freigabe und das neue Popup sind automatisiert bzw.
strukturell geprüft; ihr Test in der Zielinstallation steht noch aus.

## Änderungen

- Reduzierte Effektliste: 29 Namen, `Solid` zuerst; nicht vom Controller
  unterstützte Namen werden ausgeblendet. Die Firmware-Effekt-IDs bleiben erhalten.
- Beim Wechsel einer Segment-Leuchte von Aus nach An: Ereignis auslösen,
  **bis zu 1 Sekunde warten**, dann WLED einschalten. Auch bei bereits versorgtem Netzteil.
- **Keine verpflichtende Relais-Rückmeldung.** Eine passende optionale Freigabe
  aus Node-RED löst den WLED-Befehl früher aus. Ohne Antwort gilt weiterhin
  die Sekunde; ein ausgefallener Node-RED-Flow verhindert den Befehl nicht.
- Helligkeit, Farbe und Effekt bei eingeschaltetem Segment werden sofort geändert.
- Erneute Einschalt-/Farb-/Helligkeitsbefehle während der Sekunde werden zusammengeführt;
  sie starten die Wartezeit nicht neu. Ausschalten bricht den wartenden Befehl ab.
- Der HA-Service kehrt nach dem Planen zurück. Der Entitätszustand bleibt während
  der Wartezeit beim tatsächlichen WLED-Zustand. Fehler des späteren Befehls stehen
  im HA-Protokoll; sie können nicht mehr an den bereits beendeten Service zurückgehen.

## Installation

Diese Integration verwendet absichtlich die Domain `wled` und ersetzt die
eingebaute Integration **für alle WLED-Geräte**. Die bisherigen Unique IDs und
Konfigurationseinträge bleiben unverändert. Vorher ein HA-Backup erstellen.
Die bestehende WLED-Integration nicht löschen und die Controller nicht neu hinzufügen.

### Über HACS

Das Repository muss **öffentlich** sein. HACS unterstützt keine privaten Repositories.

1. HACS → Menü → Benutzerdefinierte Repositories.
2. `https://github.com/Nexus1212/WLED-HA`, Typ **Integration**, hinzufügen.
3. Herunterladen und Home Assistant neu starten.
4. Unter Geräte & Dienste die vorhandenen WLED-Geräte prüfen.

Ohne Release kann HACS den Standardzweig herunterladen. Spätere Änderungen
sollten als geprüfte, versionierte Releases veröffentlicht werden.

### Manuell, auch bei privatem Repository

Repository als ZIP herunterladen. Den vollständigen Ordner `custom_components/wled`
nach `/config/custom_components/wled` kopieren, anschließend HA neu starten.
Nicht nur `light.py` kopieren und keine Dateien im HA-Core-Container bearbeiten.

## Node-RED: Netzteil einschalten

Benötigt `node-red-contrib-home-assistant-websocket` und dessen vorhandene
Home-Assistant-Verbindung. Kein MQTT-Broker und kein WLED-HTTP-Knoten nötig.

1. **Events: all**: Event Type `wled_segment_turn_on_requested`.
2. Im Ereignis `data.entity_id` auswerten und dem Netzteil zuordnen.
3. **Action**: `switch.turn_on`, Ziel ist das Netzteil-Relais.

Ein importierbarer Beispiel-Flow liegt in `examples/node-red-relay.json`.
In beiden HA-Knoten den eigenen HA-Server wählen. Im Function-Knoten die
Segment-Entität und im Action-Knoten die Relais-Entität ersetzen. Der Flow
schaltet ausschließlich EIN und wartet auf keine Rückmeldung.

Ereignisdaten (Beispiel):

```yaml
event_type: wled_segment_turn_on_requested
data:
  entity_id: light.example_segment_1
  segment_id: 1
  config_entry_id: <HA-Konfigurationseintrag des Controllers>
  request_id: <eindeutige ID dieses Einschaltvorgangs>
```

Das normale `state_changed` nach `on` kommt für das vorgeschaltete Netzteil zu spät.
Das neue Ereignis wird vorher ausgelöst. Keine zusätzliche Sekunde in Node-RED einbauen.

## Optional vorzeitig freigeben (ab 0.2.0)

Node-RED kann vor Ablauf der Sekunde das HA-Ereignis
`wled_segment_turn_on_ready` senden. Es muss genau diese zwei Daten enthalten:

```yaml
entity_id: light.wled_2_segment_1
request_id: "<unverändert aus der Anforderung übernehmen>"
```

Die UUID gilt nur für den aktuellen Einschaltvorgang. Falsche, doppelte,
verspätete oder nach einem Ausschalten empfangene Antworten werden ignoriert.
Der Ereignis-Listener wird beim Entladen der Entität entfernt. Das Zeitlimit
beträgt weiterhin eine Sekunde; Node-RED kann es verkürzen, nicht verlängern.

Für das Arbeitszimmer liegt ein fertiger Flow in
[`examples/node-red-arbeitszimmer-ready.json`](examples/node-red-arbeitszimmer-ready.json):

1. Alten Relais-Flow für dieses Segment deaktivieren, dann JSON importieren.
2. In **Events: all**, **Action** und **Fire Event** den vorhandenen HA-Server wählen.
3. `light.wled_2_segment_1` und `switch.wled_netzteil_2` sind bereits eingetragen.
4. Deploy. Der Flow schaltet das Relais ein und sendet danach die Freigabe.

**Die erfolgreiche Action ist keine Bestätigung, dass das Relais physisch
geschaltet hat.** Wie gewünscht wird keine KNX-Rückmeldung verlangt. Wer die
vorzeitige Freigabe nicht möchte, entfernt einfach die Leitung vom Action-
zum Freigabe-Knoten. Vor der Freigabe lässt sich auch eine eigene kurze
Verzögerung oder Bedingung ergänzen; dabei `msg.wled_request` beibehalten.

Der bisherige Flow ohne Antwort funktioniert unverändert weiter. Antworten
nach Ablauf der Sekunde haben keine Wirkung. Kein automatisches Netzteil-AUS.

## Dashboard mit Farbe, Effekten, Geschwindigkeit und Intensität

[`examples/dashboard-arbeitszimmer.yaml`](examples/dashboard-arbeitszimmer.yaml)
ist eine vollständige manuelle Dashboard-Karte für das Arbeitszimmer EG.
Benötigt Browser Mod und **Light Entity Card** (`custom:light-entity-card`),
beide müssen installiert und ihre Frontend-Ressourcen geladen sein.

Dashboard bearbeiten → Karte hinzufügen → **Manuell** → YAML einfügen → Speichern.
Tippen auf die Kartenfläche öffnet das Popup nur auf dem bedienenden Browser;
das Icon schaltet das Licht. Es gibt keinen `features:`-Block auf der Kachel.

Das Popup zeigt Farbkreis, Helligkeit, die Effektliste der nativen Lichtentität,
Geschwindigkeit, Intensität und Farbpalette. Die beiden Zahlenregler steuern
`number.wled_2_segment_1_geschwindigkeit` und
`number.wled_2_segment_1_intensitat`. Sie sind dauerhaft sichtbar; ein Effekt
kann einzelne Parameter ignorieren. Es wird keine automatische Erkennung
unterstützter Effektparameter eingeführt.

Die neue Karte ersetzt weder global den eingebauten Lichtdialog noch verändert
sie vorhandene Dashboards automatisch. Bei „Custom element doesn't exist:
light-entity-card“ die Karte über HACS installieren und den Browser neu laden.

## Update von 0.1.0

In HACS das Repository öffnen und die aktuelle Version erneut herunterladen
(Standardzweig `main`, falls keine Release-Auswahl angeboten wird). Danach
Home Assistant neu starten. Bestehende WLED-Geräte nicht löschen. Flow und
Dashboard-YAML werden separat importiert; HACS installiert nur die Integration.

## Geltungsbereich

- Die Verzögerung gilt für `light.turn_on` auf den **Segment-Leuchten**.
- Die separate WLED-Hauptleuchte bleibt unverändert. Ihr Einschalten löst keine
  Segment-Verzögerung aus; ihr Ausschalten ersetzt nicht das Abbrechen einzelner
  wartender Segment-Befehle. Für diese Steuerung die Segment-Leuchten verwenden.
- WLED-Weboberfläche, Presets/Playlists, WLED-Synchronisation und andere direkte
  Controller-Aufrufe umgehen diese Segment-Service-Logik.
- Die Effektliste ist eine UI-Auswahl, keine Sperre gegen andere Effekte über
  WLED oder direkte Service-Aufrufe.
- Das Relais wird hier nicht automatisch ausgeschaltet. Dafür müssen später
  alle Verbraucher und noch wartende Einschaltanforderungen berücksichtigt werden.
- Alte MQTT/HTTP-Steuerflows für dasselbe Segment deaktivieren. Die Karte muss
  auf die native Segment-Leuchte zeigen, nicht auf die frühere MQTT-Leuchte.
- Die bisherigen WLED-Funktionen für Farben und Parameter bleiben wie im Original.
  Diese Anpassung fügt keine zusätzlichen Farbslots oder dynamischen Regler hinzu.

## Effekte

Solid, Blends, Candle Multi, Lake, Sine, Twinklefox, Twinkleup, Bpm, Chase 2,
Chunchun, Heartbeat, PS Chase, Chase, Loading, Scan, Scan Dual, Two Dots,
Fireworks 1D, Meteor, PS Fire 1D, PS Fireworks 1D, Flow Stripe, Glitter,
Palette, Rainbow, PS Sonic Boom, PS Sonic Stream, PS Starburst, Sunrise.

## Prüfung und Wartung

`python -m unittest discover -s tests -v` prüft die Produktionslogik für
Verzögerung, Zusammenführen, Abbruch, mehrere Segmente, optionale Freigaben und Effektfilter.
Die Tests benötigen keinen HA-Server. Die Adaptertests verwenden HA/WLED-Testdoubles;
sie ersetzen keinen vollständigen Integrationstest in Home Assistant.

Nach Installation zuerst ein Segment testen: Node-RED-Debug zeigt sofort das
Ereignis, WLED schaltet nach einer Sekunde ein. Danach während der Wartezeit
`light.turn_off` aufrufen und prüfen, dass das Segment aus bleibt.

Core-Updates aktualisieren diese Kopie nicht automatisch. Vor einem Versionswechsel
die Änderungen der offiziellen WLED-Integration prüfen und übernehmen.
`UPSTREAM.json` dokumentiert die Originaldateien. Keine Unterstützung für andere
HA-Versionen behaupten, bevor sie getestet wurden.

Rückbau: Integration über HACS entfernen bzw. den Ordner
`/config/custom_components/wled` aus `custom_components` heraus verschieben,
HA neu starten. Danach wird wieder die eingebaute WLED-Integration geladen.

## Herkunft und Lizenz

Die Originalintegration stammt von Home Assistant und dessen Mitwirkenden:
https://github.com/home-assistant/core/tree/2026.10.4/homeassistant/components/wled

Apache License 2.0, siehe `LICENSE.md`. Änderungen in diesem Repository:
`light.py`, `manifest.json`, `segment_commands.py`, eigenständige Übersetzungen,
Dokumentation und Tests. Keine offizielle Home-Assistant- oder WLED-Veröffentlichung.
