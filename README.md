# ⚽ Fussball Turnier App

Eine Streamlit-Anwendung zur Verwaltung von Fussball-Turnieren mit PDF-Export-Funktionalität.

## 🚀 Installation und Start

1. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

2. **App starten:**
   ```bash
   streamlit run app.py
   ```

3. **Im Browser öffnen:**
   Die App öffnet sich automatisch unter `http://localhost:8501`

## 📋 Funktionen

### Spieler-Verwaltung
- Spieler hinzufügen und verwalten
- Spieler als "nicht verfügbar" markieren
- Automatisches Speichern der Daten

### Turnier-Typen
1. **Feste Teams:** Teams bleiben während des gesamten Turniers konstant
2. **Round Robin:** Spieler wechseln zwischen Teams

### Team-Features
- Manuelle und automatische Team-Generierung
- Team-Farben zuweisen (gelb, orange, blau, grün, weiß, rot)
- Verschiedene Generierungsstrategien (Zufällig, Gleichmäßig, Round Robin)

### Spielplan
- Automatische Generierung von Spielplänen
- Hin- und Rückrunde Option
- Ergebnis-Eingabe und -Speicherung
- Kreuztabelle für Ergebnisse

### PDF-Export
- Professioneller PDF-Export mit Logo
- **Logo:** Die App sucht nach `ried.png` im App-Verzeichnis
- Zwei-spaltige Spielanzeige
- Kreuztabelle mit Ergebnissen
- Team-Farben im PDF

## 🖼️ Logo-Konfiguration

Das Logo `ried.png` sollte im gleichen Verzeichnis wie die App-Datei liegen:
```
C:\Users\demmelb-ma\OneDrive - COC AG\JWR\Turnier\
├── app.py
├── ried.png          ← Logo-Datei
├── requirements.txt
└── README.md
```

**Unterstützte Logo-Formate:**
- PNG (empfohlen)
- JPG/JPEG
- SVG

**Logo-Größe im PDF:** 1.5 Zoll breit × 0.75 Zoll hoch

## 💾 Daten-Persistenz

Die App speichert automatisch:
- Spieler-Liste (`players.json`)
- Turnier-Daten (`tournament_data.json`)

Daten bleiben auch nach Seitenaktualisierung erhalten.

## 🎯 Verwendung

1. **Spieler hinzufügen:** Namen in das Textfeld eingeben und "Spieler hinzufügen" klicken
2. **Teams erstellen:** 
   - Manuell: Spieler per Dropdown auswählen
   - Automatisch: "Teams automatisch generieren" verwenden
3. **Spielplan generieren:** "Spielplan generieren" Button klicken
4. **Ergebnisse eingeben:** In den expandierbaren Spiel-Bereichen
5. **PDF exportieren:** "PDF exportieren" Button für Download

## 🔧 Technische Details

- **Framework:** Streamlit
- **PDF-Generierung:** ReportLab
- **Datenformat:** JSON
- **Logo-Integration:** ReportLab Image-Klasse

## 📁 Dateistruktur

```
Turnier/
├── app.py                 # Hauptanwendung
├── ried.png              # Logo für PDF-Export
├── requirements.txt      # Python-Abhängigkeiten
├── README.md            # Diese Datei
├── players.json         # Spieler-Daten (automatisch erstellt)
└── tournament_data.json # Turnier-Daten (automatisch erstellt)
```