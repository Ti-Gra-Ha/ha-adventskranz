/**
 * Adventskranz Custom Lovelace Card for Home Assistant
 * Displays one of 6 PNG images based on the current Advent date or sensor state.
 */

const DEFAULT_IMAGES = [
  "/local/adventskranz/advent_0.png",
  "/local/adventskranz/advent_1.png",
  "/local/adventskranz/advent_2.png",
  "/local/adventskranz/advent_3.png",
  "/local/adventskranz/advent_4.png",
  "/local/adventskranz/advent_5.png",
];

const PHASE_META = [
  {
    phase: 0,
    shortLabel: "Vor dem 1. Advent",
    fullLabel: "4 neue Kerzen (ab 01.01.)",
    candlesLit: 0,
    burnedDown: false,
  },
  {
    phase: 1,
    shortLabel: "1. Advent",
    fullLabel: "1. Advent (1 brennende Kerze)",
    candlesLit: 1,
    burnedDown: false,
  },
  {
    phase: 2,
    shortLabel: "2. Advent",
    fullLabel: "2. Advent (2 brennende Kerzen)",
    candlesLit: 2,
    burnedDown: false,
  },
  {
    phase: 3,
    shortLabel: "3. Advent",
    fullLabel: "3. Advent (3 brennende Kerzen)",
    candlesLit: 3,
    burnedDown: false,
  },
  {
    phase: 4,
    shortLabel: "4. Advent",
    fullLabel: "4. Advent (4 brennende Kerzen)",
    candlesLit: 4,
    burnedDown: false,
  },
  {
    phase: 5,
    shortLabel: "Nach dem 4. Advent",
    fullLabel: "4 abgebrannte Kerzen (bis 31.12.)",
    candlesLit: 0,
    burnedDown: true,
  },
];

/**
 * Parse a YYYY-MM-DD string into a local Date at midnight (or null if invalid).
 */
function parseLocalDateString(dateStr) {
  if (!dateStr || typeof dateStr !== "string") return null;
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateStr.trim());
  if (!match) return null;
  const year = Number(match[1]);
  const month = Number(match[2]) - 1;
  const day = Number(match[3]);
  const d = new Date(year, month, day, 0, 0, 0, 0);
  if (Number.isNaN(d.getTime())) return null;
  return d;
}

/**
 * Format a Date object as DD.MM.YYYY
 */
function formatGermanDate(d) {
  if (!d) return "";
  const dd = String(d.getDate()).padStart(2, "0");
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const yyyy = d.getFullYear();
  return `${dd}.${mm}.${yyyy}`;
}

/**
 * Calculate the 4 Advent Sundays and the Sunday after 4th Advent for a given year.
 * 4th Advent is the Sunday on or before December 24.
 */
function calculateAdventDates(year) {
  const dec24 = new Date(year, 11, 24, 0, 0, 0, 0);
  const daysSinceSunday = dec24.getDay(); // 0 = Sunday .. 6 = Saturday
  const advent4 = new Date(year, 11, 24 - daysSinceSunday, 0, 0, 0, 0);
  const advent3 = new Date(advent4.getFullYear(), advent4.getMonth(), advent4.getDate() - 7);
  const advent2 = new Date(advent4.getFullYear(), advent4.getMonth(), advent4.getDate() - 14);
  const advent1 = new Date(advent4.getFullYear(), advent4.getMonth(), advent4.getDate() - 21);
  const sundayAfterAdvent4 = new Date(advent4.getFullYear(), advent4.getMonth(), advent4.getDate() + 7);

  return {
    advent1,
    advent2,
    advent3,
    advent4,
    sundayAfterAdvent4,
  };
}

/**
 * Determine the phase (0..5) for a given Date object.
 */
function getPhaseForDate(now = new Date()) {
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
  const dates = calculateAdventDates(today.getFullYear());

  if (today >= dates.sundayAfterAdvent4) return 5;
  if (today >= dates.advent4) return 4;
  if (today >= dates.advent3) return 3;
  if (today >= dates.advent2) return 2;
  if (today >= dates.advent1) return 1;
  return 0;
}

/**
 * Generate an inline SVG fallback illustration when the PNG file is not yet placed in /local/adventskranz/
 */
function renderFallbackSvg(phaseIndex, expectedPath) {
  const meta = PHASE_META[phaseIndex] || PHASE_META[0];
  const candleHeight = meta.burnedDown ? 28 : 68;
  const candleY = meta.burnedDown ? 92 : 52;
  const candleXPositions = [75, 130, 185, 240];

  const candlesSvg = candleXPositions
    .map((x, idx) => {
      const isLit = idx < meta.candlesLit;
      const wickY = candleY - 7;
      const flameSvg = isLit
        ? `
          <ellipse cx="${x + 12}" cy="${candleY - 18}" rx="8" ry="13" fill="url(#flameOuter)" />
          <ellipse cx="${x + 12}" cy="${candleY - 15}" rx="4" ry="7" fill="#fff6a9" />
          <circle cx="${x + 12}" cy="${candleY - 18}" r="18" fill="rgba(255, 180, 40, 0.22)" />
        `
        : "";
      return `
        <g>
          ${flameSvg}
          <line x1="${x + 12}" y1="${candleY}" x2="${x + 12}" y2="${wickY}" stroke="#2b2b2b" stroke-width="2" stroke-linecap="round" />
          <rect x="${x}" y="${candleY}" width="24" height="${candleHeight}" rx="4" fill="url(#candleRed)" stroke="#7a1515" stroke-width="1.5" />
        </g>
      `;
    })
    .join("");

  return `
    <div class="fallback-container">
      <svg viewBox="0 0 340 190" class="fallback-svg" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="candleRed" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#b71c1c" />
            <stop offset="45%" stop-color="#e53935" />
            <stop offset="100%" stop-color="#8e1414" />
          </linearGradient>
          <radialGradient id="flameOuter" cx="50%" cy="60%" r="50%">
            <stop offset="0%" stop-color="#ffee58" />
            <stop offset="65%" stop-color="#fb8c00" />
            <stop offset="100%" stop-color="#e65100" stop-opacity="0" />
          </radialGradient>
          <linearGradient id="wreathGreen" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#2e7d32" />
            <stop offset="100%" stop-color="#1b5e20" />
          </linearGradient>
        </defs>
        <ellipse cx="170" cy="132" rx="135" ry="28" fill="url(#wreathGreen)" stroke="#144517" stroke-width="3" />
        <ellipse cx="170" cy="126" rx="122" ry="18" fill="#388e3c" opacity="0.55" />
        <circle cx="65" cy="132" r="5" fill="#d32f2f" />
        <circle cx="115" cy="142" r="5" fill="#d32f2f" />
        <circle cx="170" cy="145" r="5" fill="#d32f2f" />
        <circle cx="225" cy="142" r="5" fill="#d32f2f" />
        <circle cx="275" cy="132" r="5" fill="#d32f2f" />
        ${candlesSvg}
      </svg>
      <div class="fallback-hint">
        Vorschau-Grafik (${meta.fullLabel})<br/>
        <small>Erwartete PNG-Datei: <code>${expectedPath}</code></small>
      </div>
    </div>
  `;
}

class AdventskranzCard extends HTMLElement {
  static getConfigElement() {
    return document.createElement("adventskranz-card-editor");
  }

  static getStubConfig() {
    return {
      title: "",
      show_status: true,
      transparent: false,
      use_sensor: true,
      entity: "sensor.adventskranz_status",
      test_date: "",
      test_phase: "auto",
      max_width: "100%",
      max_height: "100%",
      image_0: DEFAULT_IMAGES[0],
      image_1: DEFAULT_IMAGES[1],
      image_2: DEFAULT_IMAGES[2],
      image_3: DEFAULT_IMAGES[3],
      image_4: DEFAULT_IMAGES[4],
      image_5: DEFAULT_IMAGES[5],
    };
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._failedImages = new Set();
    this._lastRenderSignature = "";
  }

  setConfig(config) {
    if (!config) {
      throw new Error("Ungültige Konfiguration");
    }
    this._config = {
      title: "",
      show_status: true,
      transparent: false,
      use_sensor: true,
      entity: "sensor.adventskranz_status",
      test_date: "",
      test_phase: "auto",
      max_width: "100%",
      max_height: "100%",
      image_0: DEFAULT_IMAGES[0],
      image_1: DEFAULT_IMAGES[1],
      image_2: DEFAULT_IMAGES[2],
      image_3: DEFAULT_IMAGES[3],
      image_4: DEFAULT_IMAGES[4],
      image_5: DEFAULT_IMAGES[5],
      ...config,
    };
    this._failedImages.clear();
    this._lastRenderSignature = "";
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _resolveState() {
    // 1. Card-level simulated test_date (calculates phase from entered date)
    const parsedTestDate = parseLocalDateString(this._config.test_date);
    if (parsedTestDate) {
      return {
        phaseIndex: getPhaseForDate(parsedTestDate),
        isTestMode: true,
        testLabel: `Test-Datum: ${formatGermanDate(parsedTestDate)}`,
      };
    }

    // 2. Card-level manual phase override
    const testPhase = this._config.test_phase;
    if (
      testPhase !== undefined &&
      testPhase !== null &&
      testPhase !== "auto" &&
      testPhase !== ""
    ) {
      const parsed = Number(testPhase);
      if (!Number.isNaN(parsed) && parsed >= 0 && parsed <= 5) {
        return {
          phaseIndex: parsed,
          isTestMode: true,
          testLabel: "Testmodus",
        };
      }
    }

    // 3. Home Assistant sensor (if enabled and available)
    if (this._config.use_sensor !== false && this._hass) {
      const entityId = this._config.entity || "sensor.adventskranz_status";
      const stateObj = this._hass.states[entityId];
      if (stateObj && stateObj.attributes && typeof stateObj.attributes.phase === "number") {
        const sensorPhase = stateObj.attributes.phase;
        if (sensorPhase >= 0 && sensorPhase <= 5) {
          const isSensorOverride = Boolean(stateObj.attributes.is_test_override);
          const effDate = parseLocalDateString(stateObj.attributes.effective_date);
          const testLabel =
            stateObj.attributes.use_test_date && effDate
              ? `Test-Datum: ${formatGermanDate(effDate)}`
              : "Testmodus";
          return {
            phaseIndex: sensorPhase,
            isTestMode: isSensorOverride,
            testLabel,
          };
        }
      }
    }

    // 4. Local date calculation
    return {
      phaseIndex: getPhaseForDate(new Date()),
      isTestMode: false,
      testLabel: "",
    };
  }

  _getImageForPhase(phaseIndex) {
    const key = `image_${phaseIndex}`;
    return this._config[key] || DEFAULT_IMAGES[phaseIndex] || DEFAULT_IMAGES[0];
  }

  _render() {
    if (!this.shadowRoot || !this._config) return;

    const { phaseIndex, isTestMode, testLabel } = this._resolveState();
    const meta = PHASE_META[phaseIndex] || PHASE_META[0];
    const imageUrl = this._getImageForPhase(phaseIndex);
    const isFailed = this._failedImages.has(imageUrl);

    const signature = JSON.stringify({
      phaseIndex,
      imageUrl,
      isFailed,
      title: this._config.title,
      show_status: this._config.show_status,
      transparent: this._config.transparent,
      max_width: this._config.max_width,
      max_height: this._config.max_height,
      isTestMode,
      testLabel,
    });

    if (signature === this._lastRenderSignature) {
      return;
    }
    this._lastRenderSignature = signature;

    const transparentClass = this._config.transparent ? "transparent" : "";
    const maxWidth = this._config.max_width || "100%";
    const maxHeight = this._config.max_height || "100%";

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          height: 100%;
          box-sizing: border-box;
        }
        ha-card {
          height: 100%;
          width: 100%;
          overflow: hidden;
          transition: all 0.25s ease-in-out;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 12px;
          box-sizing: border-box;
        }
        ha-card.transparent {
          background: transparent !important;
          box-shadow: none !important;
          border: none !important;
          padding: 0;
        }
        .card-title {
          flex: 0 0 auto;
          width: 100%;
          font-size: 1.15rem;
          font-weight: 500;
          color: var(--primary-text-color);
          margin-bottom: 8px;
          text-align: center;
        }
        .image-wrapper {
          flex: 1 1 auto;
          min-height: 0;
          min-width: 0;
          width: 100%;
          height: 100%;
          max-width: ${maxWidth};
          max-height: ${maxHeight};
          display: flex;
          justify-content: center;
          align-items: center;
          position: relative;
          overflow: hidden;
        }
        .wreath-image {
          width: 100%;
          height: 100%;
          max-width: 100%;
          max-height: 100%;
          display: block;
          object-fit: contain;
          border-radius: var(--ha-card-border-radius, 12px);
        }
        ha-card.transparent .wreath-image {
          border-radius: 0;
        }
        .status-badge {
          flex: 0 0 auto;
          margin-top: 8px;
          font-size: 0.95rem;
          font-weight: 500;
          color: var(--secondary-text-color);
          text-align: center;
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          justify-content: center;
          gap: 6px;
        }
        .test-pill {
          font-size: 0.72rem;
          background: var(--warning-color, #ff9800);
          color: #fff;
          padding: 2px 7px;
          border-radius: 999px;
          font-weight: 600;
        }
        .fallback-container {
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          text-align: center;
          padding: 8px 4px;
          box-sizing: border-box;
        }
        .fallback-svg {
          width: 100%;
          height: 100%;
          max-width: 320px;
          max-height: 100%;
          margin: 0 auto;
          display: block;
        }
        .fallback-hint {
          flex: 0 0 auto;
          margin-top: 6px;
          font-size: 0.8rem;
          color: var(--secondary-text-color);
          line-height: 1.35;
        }
        .fallback-hint code {
          background: rgba(127, 127, 127, 0.15);
          padding: 2px 5px;
          border-radius: 4px;
        }
      </style>
      <ha-card class="${transparentClass}">
        ${this._config.title ? `<div class="card-title">${this._config.title}</div>` : ""}
        <div class="image-wrapper">
          ${
            isFailed
              ? renderFallbackSvg(phaseIndex, imageUrl)
              : `<img class="wreath-image" src="${imageUrl}" alt="${meta.fullLabel}" />`
          }
        </div>
        ${
          this._config.show_status
            ? `<div class="status-badge">
                <span>${meta.shortLabel}</span>
                ${isTestMode ? `<span class="test-pill">${testLabel}</span>` : ""}
              </div>`
            : ""
        }
      </ha-card>
    `;

    const imgEl = this.shadowRoot.querySelector(".wreath-image");
    if (imgEl) {
      imgEl.addEventListener("error", () => {
        this._failedImages.add(imageUrl);
        this._lastRenderSignature = "";
        this._render();
      });
    }
  }

  getCardSize() {
    return 4;
  }

  /**
   * Support Home Assistant Sections view resizing (both columns/width and rows/height).
   */
  getGridOptions() {
    return {
      columns: 6,
      rows: 4,
      min_columns: 1,
      max_columns: 12,
      min_rows: 1,
      max_rows: 12,
    };
  }
}

/**
 * Visual Editor for the Adventskranz Card
 */
class AdventskranzCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._initialized = false;
  }

  setConfig(config) {
    this._config = {
      ...AdventskranzCard.getStubConfig(),
      ...config,
    };
    if (!this._initialized) {
      this._render();
      this._initialized = true;
    } else {
      this._updateValues();
    }
  }

  set hass(hass) {
    this._hass = hass;
  }

  _updateValues() {
    if (!this.shadowRoot) return;
    const fields = [
      "title",
      "max_width",
      "max_height",
      "test_date",
      "test_phase",
      "image_0",
      "image_1",
      "image_2",
      "image_3",
      "image_4",
      "image_5",
    ];
    for (const key of fields) {
      const el = this.shadowRoot.querySelector(`[data-field="${key}"]`);
      if (el && document.activeElement !== el) {
        el.value = this._config[key] ?? "";
      }
    }
    const checkboxes = ["show_status", "transparent", "use_sensor"];
    for (const key of checkboxes) {
      const el = this.shadowRoot.querySelector(`[data-field="${key}"]`);
      if (el) {
        el.checked = Boolean(this._config[key]);
      }
    }
    this._updateDatePreviewInfo();
  }

  _updateDatePreviewInfo() {
    if (!this.shadowRoot) return;
    const infoEl = this.shadowRoot.querySelector("#date-preview-info");
    if (!infoEl) return;

    const refDate = parseLocalDateString(this._config.test_date) || new Date();
    const dates = calculateAdventDates(refDate.getFullYear());
    const calcPhase = getPhaseForDate(refDate);
    const meta = PHASE_META[calcPhase];
    const isSimulated = Boolean(parseLocalDateString(this._config.test_date));

    infoEl.innerHTML = `
      <div><strong>${isSimulated ? "Simuliertes Datum" : "Heutiges Datum"} (${formatGermanDate(refDate)}):</strong> → <strong>${meta.shortLabel}</strong> (Bild ${calcPhase + 1})</div>
      <div style="margin-top:4px; font-size: 0.78rem; opacity: 0.9;">
        Berechnete Termine ${refDate.getFullYear()}:
        1. Adv: ${formatGermanDate(dates.advent1)} |
        2. Adv: ${formatGermanDate(dates.advent2)} |
        3. Adv: ${formatGermanDate(dates.advent3)} |
        4. Adv: ${formatGermanDate(dates.advent4)} |
        Abgebrannt ab: ${formatGermanDate(dates.sundayAfterAdvent4)}
      </div>
    `;
  }

  _render() {
    if (!this.shadowRoot) return;

    this.shadowRoot.innerHTML = `
      <style>
        .editor-container {
          display: flex;
          flex-direction: column;
          gap: 14px;
          padding: 8px 0;
          color: var(--primary-text-color);
          font-family: var(--paper-font-body1_-_font-family, inherit);
        }
        .section-title {
          font-weight: 600;
          font-size: 0.95rem;
          margin-top: 8px;
          padding-bottom: 4px;
          border-bottom: 1px solid var(--divider-color, rgba(127,127,127,0.3));
        }
        .row {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .two-col {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 10px;
        }
        .date-input-row {
          display: flex;
          gap: 8px;
          align-items: center;
        }
        .clear-btn {
          padding: 8px 12px;
          border-radius: 6px;
          border: 1px solid var(--divider-color, #ccc);
          background: var(--secondary-background-color, #f0f0f0);
          color: var(--primary-text-color);
          cursor: pointer;
          font-size: 0.85rem;
          white-space: nowrap;
        }
        .info-box {
          background: rgba(127, 127, 127, 0.1);
          border-radius: 6px;
          padding: 8px 10px;
          font-size: 0.83rem;
          line-height: 1.4;
        }
        .checkbox-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 4px 0;
        }
        label {
          font-size: 0.85rem;
          color: var(--secondary-text-color);
        }
        input[type="text"],
        input[type="date"],
        select {
          width: 100%;
          padding: 8px 10px;
          border-radius: 6px;
          border: 1px solid var(--divider-color, #ccc);
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color);
          font-size: 0.9rem;
          box-sizing: border-box;
        }
        input[type="checkbox"] {
          width: 18px;
          height: 18px;
          cursor: pointer;
        }
      </style>
      <div class="editor-container">
        <div class="section-title">Allgemeine Darstellung</div>

        <div class="row">
          <label>Titel (optional)</label>
          <input type="text" data-field="title" placeholder="z. B. Adventskranz" />
        </div>

        <div class="two-col">
          <div class="row">
            <label>Max. Bildbreite (z. B. 100% oder 350px)</label>
            <input type="text" data-field="max_width" placeholder="100%" />
          </div>
          <div class="row">
            <label>Max. Bildhöhe (z. B. 100% oder 250px)</label>
            <input type="text" data-field="max_height" placeholder="100%" />
          </div>
        </div>

        <div class="checkbox-row">
          <label>Aktuellen Status als Text anzeigen (z. B. "Vor dem 1. Advent")</label>
          <input type="checkbox" data-field="show_status" />
        </div>

        <div class="checkbox-row">
          <label>Transparenter Modus (ohne Karten-Rahmen & Hintergrund)</label>
          <input type="checkbox" data-field="transparent" />
        </div>

        <div class="checkbox-row">
          <label>Mit Home Assistant Sensor koppeln (sensor.adventskranz_status)</label>
          <input type="checkbox" data-field="use_sensor" />
        </div>

        <div class="section-title">Test- & Simulationsmodus</div>

        <div class="row">
          <label>Test-Datum wählen (prüft die echte Datumsberechnung für ein beliebiges Datum)</label>
          <div class="date-input-row">
            <input type="date" data-field="test_date" />
            <button type="button" class="clear-btn" id="clear-test-date">Heute (Echtzeit)</button>
          </div>
        </div>

        <div class="info-box" id="date-preview-info"></div>

        <div class="row">
          <label>Oder Zustand direkt erzwingen (unabhängig vom Datum)</label>
          <select data-field="test_phase">
            <option value="auto">Automatisch (nach Datum / Sensor)</option>
            <option value="0">Bild 1: Vor dem 1. Advent (4 neue Kerzen)</option>
            <option value="1">Bild 2: 1. Advent (1 brennende Kerze)</option>
            <option value="2">Bild 3: 2. Advent (2 brennende Kerzen)</option>
            <option value="3">Bild 4: 3. Advent (3 brennende Kerzen)</option>
            <option value="4">Bild 5: 4. Advent (4 brennende Kerzen)</option>
            <option value="5">Bild 6: Nach dem 4. Advent (4 abgebrannte Kerzen)</option>
          </select>
        </div>

        <div class="section-title">Bild-Pfade (6 PNG-Grafiken)</div>

        <div class="row">
          <label>1. Bild (ab 01.01. – Vor dem 1. Advent)</label>
          <input type="text" data-field="image_0" />
        </div>
        <div class="row">
          <label>2. Bild (ab 1. Advent – 1 brennende Kerze)</label>
          <input type="text" data-field="image_1" />
        </div>
        <div class="row">
          <label>3. Bild (ab 2. Advent – 2 brennende Kerzen)</label>
          <input type="text" data-field="image_2" />
        </div>
        <div class="row">
          <label>4. Bild (ab 3. Advent – 3 brennende Kerzen)</label>
          <input type="text" data-field="image_3" />
        </div>
        <div class="row">
          <label>5. Bild (ab 4. Advent – 4 brennende Kerzen)</label>
          <input type="text" data-field="image_4" />
        </div>
        <div class="row">
          <label>6. Bild (ab Sonntag nach 4. Advent bis 31.12. – 4 abgebrannte Kerzen)</label>
          <input type="text" data-field="image_5" />
        </div>
      </div>
    `;

    this._updateValues();

    const clearBtn = this.shadowRoot.querySelector("#clear-test-date");
    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        this._config = {
          ...this._config,
          test_date: "",
        };
        this._updateValues();
        this.dispatchEvent(
          new CustomEvent("config-changed", {
            detail: { config: this._config },
            bubbles: true,
            composed: true,
          })
        );
      });
    }

    this.shadowRoot.querySelectorAll("input, select").forEach((el) => {
      const eventName =
        el.type === "checkbox" || el.type === "date" || el.tagName === "SELECT"
          ? "change"
          : "input";
      el.addEventListener(eventName, (e) => {
        const field = e.target.getAttribute("data-field");
        if (!field) return;
        const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
        this._config = {
          ...this._config,
          [field]: value,
        };
        this._updateDatePreviewInfo();
        this.dispatchEvent(
          new CustomEvent("config-changed", {
            detail: { config: this._config },
            bubbles: true,
            composed: true,
          })
        );
      });
    });
  }
}

if (!customElements.get("adventskranz-card")) {
  customElements.define("adventskranz-card", AdventskranzCard);
}
if (!customElements.get("adventskranz-card-editor")) {
  customElements.define("adventskranz-card-editor", AdventskranzCardEditor);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "adventskranz-card")) {
  window.customCards.push({
    type: "adventskranz-card",
    name: "Adventskranz Karte",
    description: "Zeigt abhängig vom Adventsdatum eine von 6 PNG-Grafiken eines Adventskranzes an.",
    preview: true,
  });
}
