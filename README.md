# 🕯️ Adventskranz – Home Assistant Integration & Custom Dashboard-Karte

<p align="center">
  <img src="custom_components/adventskranz/brand/logo.png" alt="Adventskranz Logo" width="220" />
</p>

Eine virtueller Adventskranz für Home Assistant Integration als **Custom Lovelace Dashboard-Karte**.  
Die Erweiterung berechnet automatisch für das aktuelle Jahr die 4 Adventssonntage und zeigt passend zum Datum den jeweiligen Zustand des Adventskranzes an.

---

## ✨ Funktionen

1. **Automatische Datumsberechnung (6 Phasen):**
   - **Phase 0 (`01.01.` bis Tag vor dem 1. Advent):** *Vor dem 1. Advent* (4 neue Kerzen)
   - **Phase 1 (ab `1. Advent`):** *1. Advent* (1 brennende Kerze)
   - **Phase 2 (ab `2. Advent`):** *2. Advent* (2 brennende Kerzen)
   - **Phase 3 (ab `3. Advent`):** *3. Advent* (3 brennende Kerzen)
   - **Phase 4 (ab `4. Advent`):** *4. Advent* (4 brennende Kerzen)
   - **Phase 5 (ab `Sonntag nach dem 4. Advent` bis `31.12.`):** *Nach dem 4. Advent* (4 abgebrannte Kerzen)

2. **All-in-One Installation:**
   - Liefert die **Custom Card (`adventskranz-card.js`)** und die **6 PNG-Grafiken (`advent_0.png` bis `advent_5.png`)** automatisch nach `/config/www/adventskranz/` aus.
   - Registriert die Dashboard-Ressource (`/local/adventskranz/adventskranz-card.js`) beim Einrichten der Integration automatisch in Lovelace.

3. **Komfortable Dashboard-Karte (`custom:adventskranz-card`):**
   - Vollständiger **visueller Editor** im Dashboard
   - **Transparenter Modus** (blendet Karten-Hintergrund, Rahmen und Schatten auf Wunsch komplett aus)
   - **Optionale Status-Anzeige** (z. B. *„Vor dem 1. Advent“*, *„1. Advent“*)
   - **Integrierter Datums-Simulator & Testmodus** (beliebiges Test-Datum wählbar, inklusive Vorschau der berechneten Adventssonntage des gewählten Jahres)
   - Eigene PNG-Grafiken jederzeit über `/config/www/adventskranz/` oder im visuellen Editor anpassbar

4. **Home Assistant Entitäten für Automationen:**
   - `sensor.adventskranz_status`: Aktueller Textstatus + Attribute (`phase`, `candles_lit`, `burned_down`, berechnete Adventsdaten des Jahres)
   - `sensor.adventskranz_phase`: Numerische Phase (`0` bis `5`)
   - `sensor.adventskranz_brennende_kerzen`: Anzahl aktuell brennender Kerzen (`0` bis `4`)
   - `select.adventskranz_modus`: Umschalter zwischen Datums-Automatik, Datums-Simulation und direkter Phasen-Wahl
   - `date.adventskranz_test_datum`: Frei wählbares Test-Datum zur globalen Simulation der Datumsberechnung

---

## 📦 Installation

### Option A: Über HACS (Empfohlen)

1. Öffne **HACS** in deinem Home Assistant.
2. Klicke oben rechts auf das **Drei-Punkte-Menü (⋮)** → **Benutzerdefinierte Repositories**.
3. Trage die URL `https://github.com/Ti-Gra-Ha/ha-adventskranz` ein und wähle als Typ **Integration**.
4. Suche in HACS nach **Adventskranz**, klicke auf **Herunterladen** und starte Home Assistant neu.
5. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen** und wähle **Adventskranz**.

### Option B: Manuelle Installation

1. Kopiere den Ordner `custom_components/adventskranz` in dein Home Assistant Verzeichnis `/config/custom_components/adventskranz`.
2. Starte Home Assistant neu.
3. Füge unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** die Integration **Adventskranz** hinzu.

*(Beim Einrichten der Integration werden die 6 PNG-Bilder und die Dashboard-Karte automatisch nach `/config/www/adventskranz/` kopiert und als Dashboard-Ressource registriert.)*

---

## 🖼️ Verwendung der Dashboard-Karte

Lade dein Dashboard nach dem Hinzufügen der Integration einmal mit **Strg + F5** neu.  
Anschließend kannst du über **Karte hinzufügen → Adventskranz Karte** die Karte direkt über den visuellen Editor konfigurieren oder folgenden YAML-Code verwenden:

```yaml
type: custom:adventskranz-card
title: ""
show_status: true
transparent: true
use_sensor: true
test_date: ""
test_phase: auto
max_width: 100%
```

### Eigene Grafiken verwenden
Wenn du eigene Grafiken nutzen möchtest, kannst du entweder die Dateien `advent_0.png` bis `advent_5.png` im Ordner `/config/www/adventskranz/` ersetzen oder im visuellen Editor der Karte eigene Bildpfade eintragen.

### Hinweis
Bei den mitgelieferten Grafiken handelt es sich um KI-generierte Bilder (Nano Banana 2)
