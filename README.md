# 🕯️ Adventskranz – Home Assistant Integration & Custom Dashboard Card

<p align="center">
  <img src="custom_components/adventskranz/brand/logo.png" alt="Adventskranz Logo" width="220" />
</p>

<p align="center">
  <a href="#-deutsch">🇩🇪 Deutsch</a> • <a href="#-english">🇬🇧 English</a>
</p>

---

## 🇩🇪 Deutsch

Eine komplette **Home Assistant Integration** inklusive **Custom Lovelace Dashboard-Karte** und **6 mitgelieferten Adventskranz-Grafiken (PNG)**.  
Die Erweiterung berechnet automatisch für jedes Jahr die 4 Adventssonntage sowie den Sonntag nach dem 4. Advent und zeigt passend zum Datum den jeweiligen Zustand des Adventskranzes an.

### ✨ Funktionen

1. **Automatische Datumsberechnung (6 Phasen):**
   - **Phase 0 (`01.01.` bis Tag vor dem 1. Advent):** *Vor dem 1. Advent* (4 neue Kerzen)
   - **Phase 1 (ab `1. Advent`):** *1. Advent* (1 brennende Kerze)
   - **Phase 2 (ab `2. Advent`):** *2. Advent* (2 brennende Kerzen)
   - **Phase 3 (ab `3. Advent`):** *3. Advent* (3 brennende Kerzen)
   - **Phase 4 (ab `4. Advent`):** *4. Advent* (4 brennende Kerzen)
   - **Phase 5 (ab `Sonntag nach dem 4. Advent` bis `31.12.`):** *Nach dem 4. Advent* (4 abgebrannte Kerzen)

2. **All-in-One Installation:**
   - Stellt die **Custom Card (`adventskranz-card.js`)** und die **6 PNG-Grafiken (`advent_0.png` bis `advent_5.png`)** direkt aus dem Integrationsverzeichnis über `hass.http.async_register_static_paths` (`/adventskranz_static/...`) bereit – das `/config/www/`-Verzeichnis bleibt komplett sauber.
   - Registriert die Dashboard-Ressource (`/adventskranz_static/adventskranz-card.js`) beim Einrichten der Integration automatisch in Lovelace (und entfernt sie beim Deinstallieren der Integration wieder).

3. **Komfortable Dashboard-Karte (`custom:adventskranz-card`):**
   - Vollständiger **visueller Editor** im Dashboard
   - Volle Unterstützung für Größenänderung (Breite & Höhe) im Home Assistant **Sections- / Grid-Layout** (`getGridOptions`)
   - **Transparenter Modus** (blendet Karten-Hintergrund, Rahmen und Schatten auf Wunsch komplett aus)
   - **Optionale Status-Anzeige** (z. B. *„Vor dem 1. Advent“*, *„1. Advent“*)
   - **Integrierter Datums-Simulator & Testmodus** (beliebiges Test-Datum wählbar, inklusive Vorschau der berechneten Adventssonntage des gewählten Jahres)
   - Eigene PNG-Grafiken jederzeit im visuellen Editor anpassbar

4. **Home Assistant Entitäten für Automationen:**
   - `sensor.adventskranz_status`: Aktueller Textstatus + Attribute (`phase`, `candles_lit`, `burned_down`, berechnete Adventsdaten des Jahres)
   - `sensor.adventskranz_phase`: Numerische Phase (`0` bis `5`)
   - `sensor.adventskranz_brennende_kerzen`: Anzahl aktuell brennender Kerzen (`0` bis `4`)
   - `select.adventskranz_modus`: Umschalter zwischen Datums-Automatik, Datums-Simulation und direkter Phasen-Wahl
   - `date.adventskranz_test_datum`: Frei wählbares Test-Datum zur globalen Simulation der Datumsberechnung

### 📦 Installation

#### Option A: Über HACS (Empfohlen)
1. Öffne **HACS** in deinem Home Assistant.
2. Suche nach **Adventskranz** (oder füge `https://github.com/Ti-Gra-Ha/ha-adventskranz` unter **Drei-Punkte-Menü (⋮) → Benutzerdefinierte Repositories** als Typ **Integration** hinzu).
3. Klicke auf **Herunterladen** und starte Home Assistant neu.
4. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen** und wähle **Adventskranz**.

#### Option B: Manuelle Installation
1. Kopiere den Ordner `custom_components/adventskranz` in dein Home Assistant Verzeichnis `/config/custom_components/adventskranz`.
2. Starte Home Assistant neu.
3. Füge unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** die Integration **Adventskranz** hinzu.

*(Beim Einrichten der Integration werden die 6 PNG-Bilder und die Dashboard-Karte direkt über `/adventskranz_static/` bereitgestellt und automatisch als Dashboard-Ressource registriert.)*

### 🖼️ Verwendung der Dashboard-Karte

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
max_height: 100%
```

#### Eigene Grafiken verwenden
Standardmäßig lädt die Karte die mitgelieferten Grafiken über `/adventskranz_static/advent_0.png` bis `advent_5.png`. Wenn du eigene Grafiken nutzen möchtest, kannst du diese z. B. in `/config/www/` ablegen und die Pfade (`/local/...`) bequem im visuellen Editor der Karte anpassen.

---

## 🇬🇧 English

A complete **Home Assistant Integration** including a **Custom Lovelace Dashboard Card** and **6 bundled Advent wreath graphics (PNG)**.  
The integration automatically calculates the 4 Advent Sundays as well as the Sunday after the 4th Advent for any year and displays the corresponding state of the Advent wreath based on the current date.

### ✨ Features

1. **Automatic Date Calculation (6 Phases):**
   - **Phase 0 (`Jan 1` until the day before 1st Advent):** *Before 1st Advent* (4 new candles)
   - **Phase 1 (from `1st Advent`):** *1st Advent* (1 burning candle)
   - **Phase 2 (from `2nd Advent`):** *2nd Advent* (2 burning candles)
   - **Phase 3 (from `3rd Advent`):** *3rd Advent* (3 burning candles)
   - **Phase 4 (from `4th Advent`):** *4th Advent* (4 burning candles)
   - **Phase 5 (from `Sunday after 4th Advent` through `Dec 31`):** *After 4th Advent* (4 burned-down candles)

2. **All-in-One Installation:**
   - Serves the **Custom Card (`adventskranz-card.js`)** and the **6 PNG images (`advent_0.png` to `advent_5.png`)** directly from the integration folder via `hass.http.async_register_static_paths` (`/adventskranz_static/...`) — keeping your `/config/www/` directory completely untouched.
   - Automatically registers the dashboard resource (`/adventskranz_static/adventskranz-card.js`) in Lovelace when the integration is set up (and removes it when the integration is deleted).

3. **Feature-Rich Dashboard Card (`custom:adventskranz-card`):**
   - Full **visual UI editor** in the dashboard
   - Full support for width and height resizing in Home Assistant's **Sections / Grid layout** (`getGridOptions`)
   - **Transparent mode** (optionally hides card background, border, and shadow)
   - **Optional status badge**
   - **Built-in date simulator & test mode** (pick any test date with a live preview of the calculated Advent Sundays for that year, or force a specific phase)
   - Custom PNG paths can be configured anytime via the visual editor

4. **Home Assistant Entities for Automations:**
   - `sensor.adventskranz_status`: Current status text + attributes (`phase`, `candles_lit`, `burned_down`, calculated Advent dates for the current year)
   - `sensor.adventskranz_phase`: Numeric phase (`0` to `5`)
   - `sensor.adventskranz_brennende_kerzen`: Number of currently lit candles (`0` to `4`)
   - `select.adventskranz_modus`: Switch between automatic date calculation, date simulation, and manual phase override
   - `date.adventskranz_test_datum`: Selectable test date for global simulation of the date calculation

### 📦 Installation

#### Option A: Via HACS (Recommended)
1. Open **HACS** in your Home Assistant instance.
2. Search for **Adventskranz** (or add `https://github.com/Ti-Gra-Ha/ha-adventskranz` via the **three-dots menu (⋮) → Custom repositories** with category **Integration**).
3. Click **Download** and restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration** and select **Adventskranz**.

#### Option B: Manual Installation
1. Copy the `custom_components/adventskranz` folder into your Home Assistant `/config/custom_components/adventskranz` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and add **Adventskranz**.

*(Setting up the integration automatically serves the 6 PNG images and the dashboard card via `/adventskranz_static/` and registers the Lovelace dashboard resource.)*

### 🖼️ Using the Dashboard Card

Reload your browser once with **Ctrl + F5** after adding the integration.  
You can then add the card via **Add Card → Adventskranz Karte** using the visual editor, or use the following YAML configuration:

```yaml
type: custom:adventskranz-card
title: ""
show_status: true
transparent: true
use_sensor: true
test_date: ""
test_phase: auto
max_width: 100%
max_height: 100%
```

#### Using Custom Graphics
By default, the card loads the bundled graphics from `/adventskranz_static/advent_0.png` through `advent_5.png`. If you want to use your own graphics, simply place them in `/config/www/` and point the image paths (`/local/...`) to your files in the card's visual editor.

---

## 🎨 Grafiken & Lizenz / Graphics & License

- **Lizenz / License:** MIT License (see [LICENSE](LICENSE))
- **Grafiken / Graphics:** Die mitgelieferten Adventskranz-Grafiken (`advent_0.png` bis `advent_5.png` sowie die Brand-Icons) wurden KI-gestützt mit **Google Nano Banana 2** erstellt und stehen ebenfalls frei unter der MIT-Lizenz zur Verfügung. / The bundled Advent wreath graphics (`advent_0.png` to `advent_5.png` and brand icons) were AI-generated using **Google Nano Banana 2** and are freely available under the MIT License.
