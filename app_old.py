import streamlit as st
import pandas as pd
from datetime import datetime
import itertools
from typing import List, Dict, Tuple
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

# Page configuration
st.set_page_config(
    page_title="JWR-Turnier",
    page_icon="🟢",
    layout="wide"
)

# Initialize session state
if 'players' not in st.session_state:
    st.session_state.players = []
if 'teams' not in st.session_state:
    st.session_state.teams = {}
if 'tournament_type' not in st.session_state:
    st.session_state.tournament_type = "Feste Teams"
if 'unavailable_players' not in st.session_state:
    st.session_state.unavailable_players = []
if 'team_colors' not in st.session_state:
    st.session_state.team_colors = {}
if 'schedule' not in st.session_state:
    st.session_state.schedule = []
if 'tournament_name' not in st.session_state:
    st.session_state.tournament_name = "JWR-Turnier"
if 'tournament_date' not in st.session_state:
    st.session_state.tournament_date = datetime.now().date()
if 'num_teams' not in st.session_state:
    st.session_state.num_teams = 4
if 'home_away' not in st.session_state:
    st.session_state.home_away = False
if 'players_per_team' not in st.session_state:
    st.session_state.players_per_team = 2

# Verfügbare Team-Farben
TEAM_COLORS = {
    "gelb": "🟡",
    "orange": "🟠", 
    "blau": "🔵",
    "grün": "🟢",
    "weiß": "⚪",
    "rot": "🔴"
}

def get_team_color_icon(team_name):
    """Gibt das Farb-Icon für ein Team zurück"""
    color = st.session_state.team_colors.get(team_name, "gelb")
    return TEAM_COLORS.get(color, "⚪")

def load_players_from_file():
    """Lädt Spieler aus einer JSON-Datei"""
    try:
        with open('players.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data.get('players', []), data.get('unavailable_players', []), data.get('team_colors', {})
            else:
                # Alte Format - nur Spielerliste
                return data, [], {}
    except FileNotFoundError:
        return [], [], {}

def save_players_to_file(players, unavailable_players, team_colors):
    """Speichert Spieler in einer JSON-Datei"""
    data = {
        'players': players,
        'unavailable_players': unavailable_players,
        'team_colors': team_colors
    }
    with open('players.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_tournament_data():
    """Speichert alle Turnierdaten"""
    data = {
        'players': st.session_state.players,
        'unavailable_players': st.session_state.unavailable_players,
        'teams': st.session_state.teams,
        'team_colors': st.session_state.team_colors,
        'tournament_type': st.session_state.tournament_type,
        'schedule': st.session_state.schedule,
        'tournament_name': st.session_state.tournament_name,
        'tournament_date': st.session_state.tournament_date.isoformat(),
        'num_teams': st.session_state.num_teams,
        'home_away': st.session_state.home_away,
        'players_per_team': st.session_state.players_per_team
    }
    with open('tournament_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_tournament_as_file():
    """Speichert das Turnier als benannte Datei"""
    if not st.session_state.tournament_name:
        st.error("Bitte geben Sie einen Turnier-Namen ein!")
        return None
    
    # Erstelle Dateiname aus Turnier-Name und Datum
    safe_name = "".join(c for c in st.session_state.tournament_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_')
    date_str = st.session_state.tournament_date.strftime('%Y%m%d')
    filename = f"turnier_{safe_name}_{date_str}.json"
    
    data = {
        'players': st.session_state.players,
        'unavailable_players': st.session_state.unavailable_players,
        'teams': st.session_state.teams,
        'team_colors': st.session_state.team_colors,
        'tournament_type': st.session_state.tournament_type,
        'schedule': st.session_state.schedule,
        'tournament_name': st.session_state.tournament_name,
        'tournament_date': st.session_state.tournament_date.isoformat(),
        'num_teams': st.session_state.num_teams,
        'home_away': st.session_state.home_away,
        'players_per_team': st.session_state.players_per_team,
        'saved_at': datetime.now().isoformat()
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
        return None

def load_tournament_from_file(uploaded_file):
    """Lädt ein Turnier aus einer hochgeladenen Datei"""
    try:
        data = json.load(uploaded_file)
        
        st.session_state.players = data.get('players', [])
        st.session_state.unavailable_players = data.get('unavailable_players', [])
        st.session_state.teams = data.get('teams', {})
        st.session_state.team_colors = data.get('team_colors', {})
        st.session_state.tournament_type = data.get('tournament_type', "Feste Teams")
        st.session_state.schedule = data.get('schedule', [])
        st.session_state.tournament_name = data.get('tournament_name', "JWR-Turnier")
        
        # Datum konvertieren
        date_str = data.get('tournament_date', datetime.now().date().isoformat())
        if isinstance(date_str, str):
            st.session_state.tournament_date = datetime.fromisoformat(date_str).date()
        else:
            st.session_state.tournament_date = datetime.now().date()
            
        st.session_state.num_teams = data.get('num_teams', 4)
        st.session_state.home_away = data.get('home_away', False)
        st.session_state.players_per_team = data.get('players_per_team', 2)
        
        return True
    except Exception as e:
        st.error(f"Fehler beim Laden der Datei: {e}")
        return False

def load_tournament_data():
    """Lädt alle Turnierdaten"""
    try:
        with open('tournament_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            st.session_state.players = data.get('players', [])
            st.session_state.unavailable_players = data.get('unavailable_players', [])
            st.session_state.teams = data.get('teams', {})
            st.session_state.team_colors = data.get('team_colors', {})
            st.session_state.tournament_type = data.get('tournament_type', "Feste Teams")
            st.session_state.schedule = data.get('schedule', [])
            st.session_state.tournament_name = data.get('tournament_name', "JWR-Turnier")
            
            # Datum konvertieren
            date_str = data.get('tournament_date', datetime.now().date().isoformat())
            if isinstance(date_str, str):
                st.session_state.tournament_date = datetime.fromisoformat(date_str).date()
            else:
                st.session_state.tournament_date = datetime.now().date()
                
            st.session_state.num_teams = data.get('num_teams', 4)
            st.session_state.home_away = data.get('home_away', False)
            st.session_state.players_per_team = data.get('players_per_team', 2)
            
            return True
    except FileNotFoundError:
        return False

def generate_round_robin_schedule(players: List[str], players_per_team: int = 2) -> List[Dict]:
    """Generiert einen Round-Robin Spielplan"""
    if len(players) < 4:
        return []
    
    num_teams = len(players) // players_per_team
    if len(players) % players_per_team != 0:
        st.warning(f"Anzahl der Spieler ({len(players)}) ist nicht durch {players_per_team} teilbar. Es werden {num_teams * players_per_team} Spieler verwendet.")
        players = players[:num_teams * players_per_team]
    
    # Erstelle Teams für jede Runde
    rounds = []
    for round_num in range(num_teams):
        teams = []
        for team_num in range(num_teams):
            team_players = []
            for player_pos in range(players_per_team):
                player_index = (round_num + team_num * players_per_team + player_pos) % len(players)
                team_players.append(players[player_index])
            teams.append(team_players)
        
        # Erstelle Spiele für diese Runde
        games = []
        for i in range(0, num_teams, 2):
            if i + 1 < num_teams:
                games.append({
                    'team1': teams[i],
                    'team2': teams[i + 1],
                    'score1': '',
                    'score2': ''
                })
        
        rounds.append({
            'round': round_num + 1,
            'games': games
        })
    
    return rounds

def generate_fixed_teams_schedule(teams: Dict[str, List[str]], home_away: bool = False) -> List[Dict]:
    """Generiert einen Spielplan für feste Teams"""
    # Nur Teams mit Spielern berücksichtigen
    teams_with_players = {name: players for name, players in teams.items() if players}
    team_names = list(teams_with_players.keys())
    
    if len(team_names) < 2:
        return []
    
    # Erstelle alle möglichen Paarungen
    games = []
    
    # Zuerst alle Hinrunden-Spiele
    for i in range(len(team_names)):
        for j in range(i + 1, len(team_names)):
            games.append({
                'team1': team_names[i],
                'team2': team_names[j],
                'players1': teams_with_players[team_names[i]],
                'players2': teams_with_players[team_names[j]],
                'score1': '',
                'score2': '',
                'round': 'Hinrunde'
            })
    
    # Dann alle Rückrunden-Spiele (nur wenn aktiviert)
    if home_away:
        for i in range(len(team_names)):
            for j in range(i + 1, len(team_names)):
                games.append({
                    'team1': team_names[j],
                    'team2': team_names[i],
                    'players1': teams_with_players[team_names[j]],
                    'players2': teams_with_players[team_names[i]],
                    'score1': '',
                    'score2': '',
                    'round': 'Rückrunde'
            })
    
    return games

def get_logo():
    """Lädt das Logo für das PDF - spezifisch ried.png"""
    import os
    
    # Suche spezifisch nach ried.png
    logo_file = 'ried.png'
    
    if os.path.exists(logo_file):
        try:
            # Lade das ried.png Logo
            logo = Image(logo_file, width=1.5*inch, height=0.75*inch)
            return logo
        except Exception as e:
            st.warning(f"Logo konnte nicht geladen werden: {e}")
    
    # Falls ried.png nicht gefunden wird, erstelle ein einfaches Text-Logo
    from reportlab.graphics.shapes import Drawing, String, Circle
    from reportlab.lib.colors import green, black, white
    from reportlab.graphics.shapes import Rect
    
    logo = Drawing(100, 50)
    # Grüner Hintergrund
    logo.add(Rect(0, 0, 100, 50, fillColor=green, strokeColor=green))
    # Schwarzer Kreis für den Ball
    logo.add(Circle(50, 25, 20, fillColor=black, strokeColor=black))
    # Weißer Text "JWR" auf dem schwarzen Ball
    logo.add(String(50, 25, "JWR", textAnchor="middle", fontSize=14, fillColor=white))
    
    return logo

def create_cross_table(schedule, team_colors=None):
    """Erstellt eine Kreuztabelle der Spiele mit Hin- und Rückrunde"""
    # Sammle alle Teams
    teams = set()
    for game in schedule:
        teams.add(game['team1'])
        teams.add(game['team2'])
    
    teams = sorted(list(teams))
    
    # Erstelle Kreuztabelle
    table_data = []
    
    # Header-Zeile
    header = [""] + [f"{team}" for team in teams]
    table_data.append(header)
    
    # Daten-Zeilen
    for team1 in teams:
        row = [f"{team1}"]
        for team2 in teams:
            if team1 == team2:
                row.append("-")
            else:
                # Suche alle Spiele zwischen team1 und team2
                games_found = []
                for game in schedule:
                    if (game['team1'] == team1 and game['team2'] == team2) or \
                       (game['team1'] == team2 and game['team2'] == team1):
                        games_found.append(game)
                
                if games_found:
                    # Sortiere Spiele nach Runde (Hinrunde zuerst)
                    games_found.sort(key=lambda x: (x.get('round', '') == 'Rückrunde', x.get('game', 0)))
                    
                    # Erstelle Ergebnis-String
                    results = []
                    for game in games_found:
                        # Bestimme Ergebnis basierend auf Team-Position
                        if game['team1'] == team1:
                            score = f"{game['score1']}:{game['score2']}"
                        else:
                            score = f"{game['score2']}:{game['score1']}"
                        
                        # Füge Runden-Info hinzu falls vorhanden
                        round_info = ""
                        if game.get('round') == 'Hinrunde':
                            round_info = " (H)"
                        elif game.get('round') == 'Rückrunde':
                            round_info = " (R)"
                        
                        results.append(f"{score}{round_info}")
                    
                    # Verbinde Ergebnisse mit Zeilenumbruch
                    row.append("\n".join(results))
                else:
                    row.append("")
        table_data.append(row)
    
    # Erstelle Tabelle mit angepassten Spaltenbreiten
    cross_table = Table(table_data, colWidths=[1.2*inch] + [1.2*inch] * len(teams))
    cross_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),  # Erste Spalte
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Erste Zeile
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header fett
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Erste Spalte fett
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertikal zentrieren
    ]))
    
    return cross_table

def create_pdf_tournament_schedule(schedule, tournament_type, tournament_name, date, team_colors=None):
    """Erstellt einen PDF-Turnierplan"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center
        textColor=colors.darkblue
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=1,  # Center
        textColor=colors.darkgreen
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Content
    story = []
    
    # Logo und Titel in einer Zeile
    logo = get_logo()
    
    # Erstelle Tabelle für Logo und Titel
    header_data = [
        [logo, Paragraph(tournament_name, title_style)]
    ]
    
    header_table = Table(header_data, colWidths=[2*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),  # Logo links
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Titel zentriert
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 0), (1, 0), 24),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.darkblue),
    ]))
    
    story.append(header_table)
    story.append(Paragraph(f"Datum: {date} | Turniertyp: {tournament_type}", subtitle_style))
    story.append(Spacer(1, 15))
    
    if tournament_type == "Feste Teams":
        # Feste Teams Spiele in 2 Spalten
        story.append(Paragraph("Spiele", heading_style))
        
        # Erstelle Tabelle für Spiele (2 Spalten)
        game_data = []
        for i, game in enumerate(schedule, 1):
            # Runde anzeigen (falls vorhanden)
            round_info = f" ({game.get('round', '')})" if game.get('round') else ""
            
            # Team-Farben für PDF (falls verfügbar)
            team1_color = ""
            team2_color = ""
            if team_colors:
                team1_color_name = team_colors.get(game['team1'], 'gelb')
                team2_color_name = team_colors.get(game['team2'], 'gelb')
                team1_color = f" ({team1_color_name})"
                team2_color = f" ({team2_color_name})"
            
            # Spiel-Info - ohne HTML-Tags, stattdessen separate Paragraphen
            game_info = {
                'spiel': f"Spiel {i}{round_info}",
                'teams': f"{game['team1']}{team1_color} vs {game['team2']}{team2_color}",
                'spieler1': f"Spieler: {', '.join(game['players1'])}",
                'spieler2': f"Spieler: {', '.join(game['players2'])}",
                'ergebnis': f"Ergebnis: {game['score1']} : {game['score2']}"
            }
            
            game_data.append([game_info])
        
        # Erstelle Tabelle mit 2 Spalten
        if game_data:
            # Paare von Spielen für 2 Spalten
            table_data = []
            for i in range(0, len(game_data), 2):
                row = []
                
                # Erstes Spiel - als formatierten Text
                game1 = game_data[i][0]
                cell1_text = f"<b>{game1['spiel']}</b><br/>"
                cell1_text += f"{game1['teams']}<br/>"
                cell1_text += f"{game1['spieler1']}<br/>"
                cell1_text += f"{game1['spieler2']}<br/>"
                cell1_text += f"{game1['ergebnis']}"
                row.append(Paragraph(cell1_text, styles['Normal']))
                
                # Zweites Spiel (falls vorhanden)
                if i + 1 < len(game_data):
                    game2 = game_data[i + 1][0]
                    cell2_text = f"<b>{game2['spiel']}</b><br/>"
                    cell2_text += f"{game2['teams']}<br/>"
                    cell2_text += f"{game2['spieler1']}<br/>"
                    cell2_text += f"{game2['spieler2']}<br/>"
                    cell2_text += f"{game2['ergebnis']}"
                    row.append(Paragraph(cell2_text, styles['Normal']))
                else:
                    row.append("")  # Leere Zelle für ungerade Anzahl
                
                table_data.append(row)
            
            # Erstelle Tabelle
            game_table = Table(table_data, colWidths=[3*inch, 3*inch])
            game_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(game_table)
            story.append(Spacer(1, 20))
            
            # Kreuztabelle hinzufügen
            story.append(Paragraph("Kreuztabelle", heading_style))
            story.append(create_cross_table(schedule, team_colors))
    
    else:  # Round Robin
        for round_data in schedule:
            story.append(Paragraph(f"Runde {round_data['round']}", heading_style))
            
            for i, game in enumerate(round_data['games'], 1):
                team1_text = f"<b>Team 1:</b> {', '.join(game['team1'])}"
                team2_text = f"<b>Team 2:</b> {', '.join(game['team2'])}"
                score_text = f"Ergebnis: {game['score1']} : {game['score2']}"
                
                story.append(Paragraph(f"Spiel {i}:", styles['Normal']))
                story.append(Paragraph(team1_text, styles['Normal']))
                story.append(Paragraph(team2_text, styles['Normal']))
                story.append(Paragraph(score_text, styles['Normal']))
                story.append(Spacer(1, 10))
            
            story.append(Spacer(1, 15))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def main():
    st.title("🟢⚫ JWR-Turnier")
    
    # Lade gespeicherte Daten beim Start
    if not hasattr(st.session_state, 'data_loaded'):
        load_tournament_data()
        st.session_state.data_loaded = True
    
    # Sidebar für Navigation
    st.sidebar.title("Navigation")
    tournament_type = st.sidebar.selectbox(
        "Turniertyp auswählen:",
        ["Feste Teams", "Round Robin (jeder mit jedem)"],
        index=0 if st.session_state.tournament_type == "Feste Teams" else 1
    )
    st.session_state.tournament_type = tournament_type
    
    # Spieler-Management
    st.header("👥 Spieler-Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Spieler hinzufügen")
        
        # Manuell eingeben
        new_player = st.text_input("Neuer Spieler:", placeholder="Spielername eingeben")
        if st.button("Spieler hinzufügen") and new_player:
            if new_player not in st.session_state.players:
                st.session_state.players.append(new_player)
                save_tournament_data()  # Automatisch speichern
                st.success(f"Spieler '{new_player}' hinzugefügt!")
            else:
                st.warning("Spieler bereits vorhanden!")
        
        # Aus Datei laden
        if st.button("Spieler aus Datei laden"):
            loaded_players, loaded_unavailable, loaded_colors = load_players_from_file()
            if loaded_players:
                st.session_state.players = loaded_players
                st.session_state.unavailable_players = loaded_unavailable
                st.session_state.team_colors = loaded_colors
                st.success(f"{len(loaded_players)} Spieler geladen! ({len(loaded_unavailable)} nicht verfügbar)")
            else:
                st.warning("Keine Spieler in der Datei gefunden.")
    
    with col2:
        st.subheader("Aktuelle Spieler")
        if st.session_state.players:
            for i, player in enumerate(st.session_state.players):
                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    is_unavailable = player in st.session_state.unavailable_players
                    status_icon = "🚫" if is_unavailable else "✅"
                    st.write(f"{i+1}. {status_icon} {player}")
                with col_b:
                    if is_unavailable:
                        if st.button("✅", key=f"avail_{i}", help="Verfügbar machen"):
                            st.session_state.unavailable_players.remove(player)
                            save_tournament_data()  # Automatisch speichern
                            st.rerun()
                    else:
                        if st.button("🚫", key=f"unavail_{i}", help="Nicht verfügbar"):
                            st.session_state.unavailable_players.append(player)
                            save_tournament_data()  # Automatisch speichern
                            st.rerun()
                with col_c:
                    if st.button("❌", key=f"del_{i}", help="Spieler löschen"):
                        if player in st.session_state.unavailable_players:
                            st.session_state.unavailable_players.remove(player)
                        st.session_state.players.pop(i)
                        save_tournament_data()  # Automatisch speichern
                        st.rerun()
        else:
            st.info("Noch keine Spieler hinzugefügt")
    
    # Daten-Management
    st.subheader("💾 Turnier-Management")
    
    col_save1, col_save2, col_save3, col_save4 = st.columns(4)
    with col_save1:
        if st.button("💾 Auto-Speichern"):
            save_tournament_data()
            st.success("Daten automatisch gespeichert!")
    with col_save2:
        if st.button("📁 Auto-Laden"):
            load_tournament_data()
            st.success("Daten geladen!")
            st.rerun()
    with col_save3:
        if st.button("🗑️ Daten löschen"):
            # Lösche alle Daten
            st.session_state.players = []
            st.session_state.unavailable_players = []
            st.session_state.teams = {}
            st.session_state.team_colors = {}
            st.session_state.schedule = []
            st.session_state.tournament_name = "JWR-Turnier"
            st.session_state.tournament_date = datetime.now().date()
            st.session_state.num_teams = 4
            st.session_state.home_away = False
            st.session_state.players_per_team = 2
            save_tournament_data()
            st.success("Alle Daten gelöscht!")
            st.rerun()
    with col_save4:
        if st.button("💾 Turnier speichern"):
            filename = save_tournament_as_file()
            if filename:
                st.success(f"Turnier gespeichert als: {filename}")
    
    # Turnier-Datei hochladen
    st.markdown("---")
    st.subheader("📤 Turnier laden")
    
    uploaded_file = st.file_uploader(
        "Turnier-Datei hochladen (.json)", 
        type=['json'],
        help="Wählen Sie eine gespeicherte Turnier-Datei aus"
    )
    
    if uploaded_file is not None:
        if st.button("📥 Turnier laden"):
            if load_tournament_from_file(uploaded_file):
                st.success("Turnier erfolgreich geladen!")
                st.rerun()
            else:
                st.error("Fehler beim Laden des Turniers!")
    
    # Aktuelle Turnier-Info anzeigen
    if st.session_state.tournament_name and st.session_state.tournament_name != "JWR-Turnier":
        st.info(f"**Aktuelles Turnier:** {st.session_state.tournament_name} ({st.session_state.tournament_date})")
    
    st.markdown("---")
    
    if tournament_type == "Feste Teams":
        # Feste Teams Turnier
        st.header("🏆 Feste Teams Turnier")
        
        if len(st.session_state.players) < 2:
            st.warning("Mindestens 2 Spieler erforderlich!")
            return
        
        # Team-Zuordnung
        st.subheader("Team-Zuordnung")
        
        # Turnier-Einstellungen
        col1, col2 = st.columns(2)
        with col1:
            num_teams = st.number_input("Anzahl Teams:", min_value=2, max_value=len(st.session_state.players), value=st.session_state.num_teams)
            st.session_state.num_teams = num_teams
        with col2:
            home_away = st.checkbox("Hin- und Rückrunde", value=st.session_state.home_away, help="Jedes Team spielt sowohl zu Hause als auch auswärts gegen jedes andere Team")
            st.session_state.home_away = home_away
        
        # Teams erstellen
        team_names = [f"Team {chr(65 + i)}" for i in range(num_teams)]
        
        # Buttons für Team-Management
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🔄 Teams zurücksetzen"):
                st.session_state.teams = {}
                st.rerun()
        with col2:
            # Erweiterte Team-Generierung
            with st.expander("🎲 Teams automatisch generieren", expanded=False):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    strategy = st.selectbox(
                        "Generierungsstrategie:",
                        ["Zufällig", "Gleichmäßig", "Round Robin"],
                        help="Zufällig: Zufällige Aufteilung\nGleichmäßig: Gleichmäßige Verteilung\nRound Robin: Für Turnier mit wechselnden Teams"
                    )
                
                with col_b:
                    if st.button("🎲 Teams generieren", type="primary"):
                        import random
                        
                        if strategy == "Zufällig":
                            # Zufällige Aufteilung - nur verfügbare Spieler
                            available_players = [p for p in st.session_state.players if p not in st.session_state.unavailable_players]
                            if len(available_players) < 2:
                                st.error("Nicht genügend verfügbare Spieler für Teams!")
                                st.stop()
                            
                            random.shuffle(available_players)
                            players_per_team = len(available_players) // num_teams
                            remainder = len(available_players) % num_teams
                            
                            st.session_state.teams = {}
                            available_colors = list(TEAM_COLORS.keys())
                            random.shuffle(available_colors)
                            
                            for i, team_name in enumerate(team_names):
                                team_size = players_per_team + (1 if i < remainder else 0)
                                team_players = available_players[player_index:player_index + team_size]
                                st.session_state.teams[team_name] = team_players
                                # Weise zufällige Farbe zu
                                st.session_state.team_colors[team_name] = available_colors[i % len(available_colors)]
                                player_index += team_size
                        
                        elif strategy == "Gleichmäßig":
                            # Gleichmäßige Verteilung (Round Robin Stil) - nur verfügbare Spieler
                            available_players = [p for p in st.session_state.players if p not in st.session_state.unavailable_players]
                            if len(available_players) < 2:
                                st.error("Nicht genügend verfügbare Spieler für Teams!")
                                st.stop()
                            
                            st.session_state.teams = {}
                            available_colors = list(TEAM_COLORS.keys())
                            
                            for i, team_name in enumerate(team_names):
                                st.session_state.teams[team_name] = []
                                # Weise Farbe zu
                                st.session_state.team_colors[team_name] = available_colors[i % len(available_colors)]
                            
                            # Verteile Spieler gleichmäßig
                            for i, player in enumerate(available_players):
                                team_index = i % num_teams
                                team_name = team_names[team_index]
                                st.session_state.teams[team_name].append(player)
                        
                        elif strategy == "Round Robin":
                            # Für Round Robin Turnier - erstelle Teams für erste Runde - nur verfügbare Spieler
                            available_players = [p for p in st.session_state.players if p not in st.session_state.unavailable_players]
                            if len(available_players) < 2:
                                st.error("Nicht genügend verfügbare Spieler für Teams!")
                                st.stop()
                            
                            players_per_team = len(available_players) // num_teams
                            if len(available_players) % players_per_team != 0:
                                st.warning(f"Für Round Robin werden {num_teams * players_per_team} Spieler verwendet.")
                                players = available_players[:num_teams * players_per_team]
                            else:
                                players = available_players
                            
                            st.session_state.teams = {}
                            available_colors = list(TEAM_COLORS.keys())
                            
                            for i, team_name in enumerate(team_names):
                                start_idx = i * players_per_team
                                end_idx = start_idx + players_per_team
                                st.session_state.teams[team_name] = players[start_idx:end_idx]
                                # Weise Farbe zu
                                st.session_state.team_colors[team_name] = available_colors[i % len(available_colors)]
                        
                        st.success(f"Teams mit '{strategy}' Strategie generiert!")
                        st.rerun()
        with col3:
            # Zeige nicht verfügbare Spieler
            if st.session_state.unavailable_players:
                st.markdown("**🚫 Nicht verfügbare Spieler:**")
                for player in st.session_state.unavailable_players:
                    st.write(f"• {player}")
        
        # Team-Übersicht anzeigen
        if st.session_state.teams and any(st.session_state.teams.values()):
            st.markdown("---")
            st.subheader("📊 Team-Übersicht")
            
            # Erstelle Übersichtstabelle
            team_data = []
            for team_name, players in st.session_state.teams.items():
                team_color_icon = get_team_color_icon(team_name)
                team_data.append({
                    "Team": f"{team_color_icon} {team_name}",
                    "Spieler": ", ".join(players) if players else "Keine Spieler",
                    "Anzahl": len(players)
                })
            
            df = pd.DataFrame(team_data)
            st.dataframe(df, use_container_width=True)
            
            # Statistiken
            total_assigned = sum(len(players) for players in st.session_state.teams.values())
            unassigned = len(st.session_state.players) - total_assigned
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Zugewiesene Spieler", total_assigned)
            with col2:
                st.metric("Nicht zugewiesen", unassigned)
            with col3:
                avg_team_size = total_assigned / len(team_names) if team_names else 0
                st.metric("Ø Team-Größe", f"{avg_team_size:.1f}")
        
        # Zeige nur Teams mit Spielern + ein leeres Team für neue Zuweisungen
        teams_with_players = [name for name, players in st.session_state.teams.items() if players]
        teams_to_show = teams_with_players.copy()
        
        # Füge ein leeres Team hinzu, wenn noch nicht alle Teams besetzt sind
        if len(teams_with_players) < num_teams:
        for team_name in team_names:
                if team_name not in teams_to_show:
                    teams_to_show.append(team_name)
                    break
        
        for team_name in teams_to_show:
            current_team_players = st.session_state.teams.get(team_name, [])
            team_status = "✅" if current_team_players else "⚠️"
            team_color_icon = get_team_color_icon(team_name)
            st.write(f"**{team_status} {team_color_icon} {team_name}:**")
            
            # Team-Farbe auswählen
            col_color1, col_color2 = st.columns([1, 3])
            with col_color1:
                current_color = st.session_state.team_colors.get(team_name, "gelb")
                selected_color = st.selectbox(
                    "Farbe:",
                    list(TEAM_COLORS.keys()),
                    index=list(TEAM_COLORS.keys()).index(current_color),
                    key=f"color_{team_name}",
                    help="Wähle eine Farbe für das Team"
                )
                st.session_state.team_colors[team_name] = selected_color
            
            with col_color2:
                # Berechne verfügbare Spieler (alle verfügbaren Spieler minus bereits zugewiesene)
                assigned_players = []
                for other_team in team_names:
                    if other_team != team_name:
                        assigned_players.extend(st.session_state.teams.get(other_team, []))
                
                # Nur verfügbare Spieler (nicht als "nicht verfügbar" markiert)
                available_for_teams = [p for p in st.session_state.players if p not in st.session_state.unavailable_players]
                available_players = [p for p in available_for_teams if p not in assigned_players]
                
                # Füge bereits zugewiesene Spieler dieses Teams hinzu
                available_players.extend(current_team_players)
                available_players = list(dict.fromkeys(available_players))  # Entferne Duplikate
                
                # Zeige bereits zugewiesene Spieler an
                if assigned_players:
                    st.info(f"Bereits zugewiesen: {', '.join(assigned_players)}")
                
            selected_players = st.multiselect(
                f"Spieler für {team_name} auswählen:",
                    available_players,
                key=f"team_{team_name}",
                    default=current_team_players
            )
            st.session_state.teams[team_name] = selected_players
        
        # Spielplan generieren
        if st.button("Spielplan generieren"):
            # Prüfe, ob mindestens 2 Teams mit Spielern existieren
            teams_with_players = {name: players for name, players in st.session_state.teams.items() if players}
            if len(teams_with_players) < 2:
                st.error(f"Mindestens 2 Teams mit Spielern erforderlich! Aktuell: {len(teams_with_players)} Teams")
                return
            
            schedule = generate_fixed_teams_schedule(st.session_state.teams, home_away)
            if schedule:
                st.session_state.schedule = schedule
                save_tournament_data()  # Automatisch speichern
                round_type = "Hin- und Rückrunde" if home_away else "Einfache Runde"
                st.success(f"Spielplan generiert! {len(teams_with_players)} Teams, {len(schedule)} Spiele ({round_type})")
            else:
                st.error("Kein gültiger Spielplan möglich!")
    
    else:
        # Round Robin Turnier
        st.header("🔄 Round Robin Turnier")
        
        if len(st.session_state.players) < 4:
            st.warning("Mindestens 4 Spieler für Round Robin erforderlich!")
            return
        
        players_per_team = st.number_input("Spieler pro Team:", min_value=2, max_value=len(st.session_state.players)//2, value=st.session_state.players_per_team)
        st.session_state.players_per_team = players_per_team
        
        if st.button("Round Robin Spielplan generieren"):
            # Nur verfügbare Spieler für Round Robin verwenden
            available_players = [p for p in st.session_state.players if p not in st.session_state.unavailable_players]
            if len(available_players) < 4:
                st.error("Mindestens 4 verfügbare Spieler für Round Robin erforderlich!")
                return
            
            schedule = generate_round_robin_schedule(available_players, players_per_team)
            if schedule:
                st.session_state.schedule = schedule
                save_tournament_data()  # Automatisch speichern
                st.success("Round Robin Spielplan generiert!")
            else:
                st.error("Kein gültiger Spielplan möglich!")
    
    # Spielplan anzeigen
    if 'schedule' in st.session_state:
        st.markdown("---")
        st.header("📋 Spielplan")
        
        col1, col2 = st.columns(2)
        with col1:
            tournament_name = st.text_input("Turniername:", value=st.session_state.tournament_name)
            st.session_state.tournament_name = tournament_name
        with col2:
            tournament_date = st.date_input("Datum:", value=st.session_state.tournament_date)
            st.session_state.tournament_date = tournament_date
        
        if st.session_state.tournament_type == "Feste Teams":
            st.subheader("Spiele")
            
            # Runden-Übersicht
            if any(game.get('round') for game in st.session_state.schedule):
                hinrunde_games = [g for g in st.session_state.schedule if g.get('round') == 'Hinrunde']
                ruckrunde_games = [g for g in st.session_state.schedule if g.get('round') == 'Rückrunde']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Hinrunde", len(hinrunde_games))
                with col2:
                    st.metric("Rückrunde", len(ruckrunde_games))
                with col3:
                    st.metric("Gesamt", len(st.session_state.schedule))
            
            # Spiele nach Runden gruppiert anzeigen
            hinrunde_games = [g for g in st.session_state.schedule if g.get('round') == 'Hinrunde']
            ruckrunde_games = [g for g in st.session_state.schedule if g.get('round') == 'Rückrunde']
            other_games = [g for g in st.session_state.schedule if not g.get('round')]
            
            # Hinrunde
            if hinrunde_games:
                st.markdown("### 🏠 Hinrunde")
                for i, game in enumerate(hinrunde_games, 1):
                    team1_color = get_team_color_icon(game['team1'])
                    team2_color = get_team_color_icon(game['team2'])
                    with st.expander(f"Spiel {i}: {team1_color} {game['team1']} vs {team2_color} {game['team2']} (Hinrunde)"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**{team1_color} {game['team1']}:** {', '.join(game['players1'])}")
                            score1 = st.number_input(f"Tore {game['team1']}:", min_value=0, key=f"hin_score1_{i}")
                        with col2:
                            st.write(f"**{team2_color} {game['team2']}:** {', '.join(game['players2'])}")
                            score2 = st.number_input(f"Tore {game['team2']}:", min_value=0, key=f"hin_score2_{i}")
                        
                        # Update scores
                        if st.button(f"Ergebnis speichern - Hinrunde Spiel {i}", key=f"hin_save_{i}"):
                            game_index = st.session_state.schedule.index(game)
                            st.session_state.schedule[game_index]['score1'] = str(score1)
                            st.session_state.schedule[game_index]['score2'] = str(score2)
                            st.success("Ergebnis gespeichert!")
                            st.rerun()
            
            # Rückrunde
            if ruckrunde_games:
                st.markdown("### 🚌 Rückrunde")
                for i, game in enumerate(ruckrunde_games, 1):
                    team1_color = get_team_color_icon(game['team1'])
                    team2_color = get_team_color_icon(game['team2'])
                    with st.expander(f"Spiel {len(hinrunde_games) + i}: {team1_color} {game['team1']} vs {team2_color} {game['team2']} (Rückrunde)"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**{team1_color} {game['team1']}:** {', '.join(game['players1'])}")
                            score1 = st.number_input(f"Tore {game['team1']}:", min_value=0, key=f"ruck_score1_{i}")
                        with col2:
                            st.write(f"**{team2_color} {game['team2']}:** {', '.join(game['players2'])}")
                            score2 = st.number_input(f"Tore {game['team2']}:", min_value=0, key=f"ruck_score2_{i}")
                        
                        # Update scores
                        if st.button(f"Ergebnis speichern - Rückrunde Spiel {i}", key=f"ruck_save_{i}"):
                            game_index = st.session_state.schedule.index(game)
                            st.session_state.schedule[game_index]['score1'] = str(score1)
                            st.session_state.schedule[game_index]['score2'] = str(score2)
                            st.success("Ergebnis gespeichert!")
                            st.rerun()
            
            # Andere Spiele (falls vorhanden)
            if other_games:
                st.markdown("### ⚽ Weitere Spiele")
                for i, game in enumerate(other_games, 1):
                    with st.expander(f"Spiel {i}: {game['team1']} vs {game['team2']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**{game['team1']}:** {', '.join(game['players1'])}")
                            score1 = st.number_input(f"Tore {game['team1']}:", min_value=0, key=f"other_score1_{i}")
                        with col2:
                            st.write(f"**{game['team2']}:** {', '.join(game['players2'])}")
                            score2 = st.number_input(f"Tore {game['team2']}:", min_value=0, key=f"other_score2_{i}")
                        
                        # Update scores
                        if st.button(f"Ergebnis speichern - Spiel {i}", key=f"other_save_{i}"):
                            game_index = st.session_state.schedule.index(game)
                            st.session_state.schedule[game_index]['score1'] = str(score1)
                            st.session_state.schedule[game_index]['score2'] = str(score2)
                            st.success("Ergebnis gespeichert!")
                            st.rerun()
        
        else:  # Round Robin
            for round_data in st.session_state.schedule:
                st.subheader(f"Runde {round_data['round']}")
                for i, game in enumerate(round_data['games'], 1):
                    with st.expander(f"Spiel {i}: {', '.join(game['team1'])} vs {', '.join(game['team2'])}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Team 1:** {', '.join(game['team1'])}")
                            score1 = st.number_input(f"Tore Team 1:", min_value=0, key=f"rr_score1_{round_data['round']}_{i}")
                        with col2:
                            st.write(f"**Team 2:** {', '.join(game['team2'])}")
                            score2 = st.number_input(f"Tore Team 2:", min_value=0, key=f"rr_score2_{round_data['round']}_{i}")
                        
                        # Update scores
                        if st.button(f"Ergebnis speichern - Runde {round_data['round']}, Spiel {i}", key=f"rr_save_{round_data['round']}_{i}"):
                            st.session_state.schedule[round_data['round']-1]['games'][i-1]['score1'] = str(score1)
                            st.session_state.schedule[round_data['round']-1]['games'][i-1]['score2'] = str(score2)
                            st.success("Ergebnis gespeichert!")
                            st.rerun()
        
        # PDF Export
        st.markdown("---")
        st.markdown("## 📄 PDF Export")
        
        if st.button("📥 Turnierplan als PDF exportieren"):
            try:
                pdf_buffer = create_pdf_tournament_schedule(
            st.session_state.schedule, 
            st.session_state.tournament_type,
            tournament_name,
                    tournament_date.strftime("%d.%m.%Y"),
                    st.session_state.team_colors
                )
                
                st.download_button(
                    label="📥 PDF herunterladen",
                    data=pdf_buffer.getvalue(),
                    file_name=f"{tournament_name}_{tournament_date.strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
                st.success("PDF erfolgreich generiert!")
                
            except Exception as e:
                st.error(f"Fehler beim Erstellen der PDF: {str(e)}")

if __name__ == "__main__":
    main()