import streamlit as st
import json
import pandas as pd
from datetime import datetime
from itertools import combinations
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Initialize session state
if 'players' not in st.session_state:
    st.session_state.players = []
if 'unavailable_players' not in st.session_state:
    st.session_state.unavailable_players = []
if 'teams' not in st.session_state:
    st.session_state.teams = {}
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

# Team colors
TEAM_COLORS = {
    'gelb': '🟨',
    'orange': '🟧', 
    'blau': '🔵',
    'grün': '🟢',
    'weiß': '⚪',
    'rot': '🔴'
}

def get_team_color_icon(team_name):
    """Get the emoji icon for a team's color"""
    if team_name in st.session_state.team_colors:
        color = st.session_state.team_colors[team_name]
        return TEAM_COLORS.get(color, '⚪')
    return '⚪'

def load_players():
    """Load players from JSON file"""
    try:
        with open('players.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            st.session_state.players = data.get('players', [])
            st.session_state.unavailable_players = data.get('unavailable_players', [])
    except FileNotFoundError:
        st.session_state.players = []
        st.session_state.unavailable_players = []
    except Exception as e:
        st.error(f"Fehler beim Laden der Spieler: {e}")

def save_players():
    """Save players to JSON file"""
    try:
        data = {
            'players': st.session_state.players,
            'unavailable_players': st.session_state.unavailable_players
        }
        with open('players.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Fehler beim Speichern der Spieler: {e}")

def save_tournament_data():
    """Save tournament data to JSON file"""
    try:
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
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")

def load_tournament_data():
    """Load tournament data from JSON file"""
    try:
        with open('tournament_data.json', 'r', encoding='utf-8') as f:  
            data = json.load(f)
            st.session_state.players = data.get('players', [])
            st.session_state.unavailable_players = data.get('unavailable_players', [])
            st.session_state.teams = data.get('teams', {})
            st.session_state.team_colors = data.get('team_colors', {})
            st.session_state.tournament_type = data.get('tournament_type', 'fixed')
            st.session_state.schedule = data.get('schedule', [])
            st.session_state.tournament_name = data.get('tournament_name', 'JWR-Turnier')
            if 'tournament_date' in data:
                st.session_state.tournament_date = datetime.fromisoformat(data['tournament_date']).date()                                               
            st.session_state.num_teams = data.get('num_teams', 4)
            st.session_state.home_away = data.get('home_away', False)
            st.session_state.players_per_team = data.get('players_per_team', 2)
    except FileNotFoundError:
        pass
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")

def save_tournament_as_file():
    """Save tournament as named file"""
    if not st.session_state.tournament_name:
        st.error("Bitte geben Sie einen Turnier-Namen ein!")
        return None
    
    # Create filename from tournament name and date
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
    """Load tournament from uploaded file"""
    try:
        data = json.load(uploaded_file)
        
        st.session_state.players = data.get('players', [])
        st.session_state.unavailable_players = data.get('unavailable_players', [])
        st.session_state.teams = data.get('teams', {})
        st.session_state.team_colors = data.get('team_colors', {})
        st.session_state.tournament_type = data.get('tournament_type', "Feste Teams")
        st.session_state.schedule = data.get('schedule', [])
        st.session_state.tournament_name = data.get('tournament_name', "JWR-Turnier")
        
        # Convert date
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

def generate_fixed_teams_schedule(teams, home_away=False):
    """Generate schedule for fixed teams"""
    # Only include teams that have players
    teams_with_players = {team: players for team, players in teams.items() if players}
    
    if len(teams_with_players) < 2:
        return []
    
    team_names = list(teams_with_players.keys())
    schedule = []
    game_number = 1
    
    # Generate all combinations
    for team1, team2 in combinations(team_names, 2):
        if home_away:
            # Hinrunde
            schedule.append({
                'game': game_number,
                'team1': team1,
                'team2': team2,
                'players1': teams_with_players[team1],
                'players2': teams_with_players[team2],
                'score1': 0,
                'score2': 0,
                'round': 'Hinrunde'
            })
            game_number += 1
            
            # Rückrunde
            schedule.append({
                'game': game_number,
                'team1': team2,
                'team2': team1,
                'players1': teams_with_players[team2],
                'players2': teams_with_players[team1],
                'score1': 0,
                'score2': 0,
                'round': 'Rückrunde'
            })
            game_number += 1
        else:
            # Single round
            schedule.append({
                'game': game_number,
                'team1': team1,
                'team2': team2,
                'players1': teams_with_players[team1],
                'players2': teams_with_players[team2],
                'score1': 0,
                'score2': 0,
                'round': 'Einzelrunde'
            })
            game_number += 1
    
    return schedule

def generate_round_robin_schedule(players, players_per_team):
    """Generate round robin schedule where players switch teams"""
    if len(players) < players_per_team * 2:
        return []
    
    # Create all possible team combinations
    team_combinations = list(combinations(players, players_per_team))
    
    schedule = []
    game_number = 1
    
    # Generate games between different team combinations
    for i, team1 in enumerate(team_combinations):
        for j, team2 in enumerate(team_combinations[i+1:], i+1):
            schedule.append({
                'game': game_number,
                'team1': f"Team {i+1}",
                'team2': f"Team {j+1}",
                'players1': list(team1),
                'players2': list(team2),
                'score1': 0,
                'score2': 0,
                'round': 'Round Robin'
            })
            game_number += 1
    
    return schedule

def create_cross_table(schedule, team_colors=None):
    """Create a cross table for the results with Hin- and Rückrunde"""
    # Collect all teams
    teams = set()
    for game in schedule:
        teams.add(game['team1'])
        teams.add(game['team2'])
    
    teams = sorted(list(teams))
    
    # Create cross table
    table_data = []
    
    # Header row
    header = [""] + [f"{team}" for team in teams]
    table_data.append(header)
    
    # Data rows
    for team1 in teams:
        row = [f"{team1}"]
        for team2 in teams:
            if team1 == team2:
                row.append("-")
            else:
                # Find all games between team1 and team2
                games_found = []
                for game in schedule:
                    if (game['team1'] == team1 and game['team2'] == team2) or \
                       (game['team1'] == team2 and game['team2'] == team1):
                        games_found.append(game)
                
                if games_found:
                    # Sort games by round (Hinrunde first)
                    games_found.sort(key=lambda x: (x.get('round', '') == 'Rückrunde', x.get('game', 0)))
                    
                    # Create result string
                    results = []
                    for game in games_found:
                        # Determine result based on team position
                        if game['team1'] == team1:
                            score = f"{game['score1']}:{game['score2']}"
                        else:
                            score = f"{game['score2']}:{game['score1']}"
                        
                        # Add round info if available
                        round_info = ""
                        if game.get('round') == 'Hinrunde':
                            round_info = " (H)"
                        elif game.get('round') == 'Rückrunde':
                            round_info = " (R)"
                        
                        results.append(f"{score}{round_info}")
                    
                    # Join results with line break
                    row.append("\n".join(results))
                else:
                    row.append("")
        table_data.append(row)
    
    # Create table with adjusted column widths
    cross_table = Table(table_data, colWidths=[1.2*inch] + [1.2*inch] * len(teams))
    cross_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),  # First column
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # First row
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header bold
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # First column bold
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical center
    ]))
    
    return cross_table

def get_logo():
    """Load logo for PDF - specifically ried.png"""
    import os
    
    # Look specifically for ried.png
    logo_file = 'ried.png'
    
    if os.path.exists(logo_file):
        try:
            # Load the ried.png logo
            logo = Image(logo_file, width=1.5*inch, height=0.75*inch)
            return logo
        except Exception as e:
            st.warning(f"Logo konnte nicht geladen werden: {e}")
    
    # If ried.png not found, create a simple text logo
    from reportlab.graphics.shapes import Drawing, String, Circle
    from reportlab.lib.colors import green, black, white
    from reportlab.graphics.shapes import Rect
    
    logo = Drawing(100, 50)
    # Green background
    logo.add(Rect(0, 0, 100, 50, fillColor=green, strokeColor=green))
    # Black circle for the ball
    logo.add(Circle(50, 25, 20, fillColor=black, strokeColor=black))
    # White text "JWR" on the black ball
    logo.add(String(50, 25, "JWR", textAnchor="middle", fontSize=14, fillColor=white))
    
    return logo

def create_pdf_tournament_schedule(tournament_name, date, schedule, tournament_type, team_colors=None):
    """Create PDF with tournament schedule"""
    filename = f"turnier_{tournament_name}_{date.strftime('%Y%m%d')}.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
    ))
    
    # Header with logo
    logo = get_logo()
    header_data = [
        [logo, f"<b>{tournament_name}</b><br/>{date}<br/>{'Hin- und Rückrunde' if tournament_type == 'fixed' and st.session_state.home_away else 'Einzelrunde' if tournament_type == 'fixed' else 'Round Robin'}", ""]
    ]
    header_table = Table(header_data, colWidths=[2*inch, 4*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    if not schedule:
        story.append(Paragraph("Kein Spielplan verfügbar", styles['Normal']))
        doc.build(story)
        return filename
    
    # Create games table (2 columns)
    games_data = []
    for i in range(0, len(schedule), 2):
        row = []
        
        # First game
        if i < len(schedule):
            game = schedule[i]
            color1 = team_colors.get(game['team1'], 'weiß') if team_colors else 'weiß'
            color2 = team_colors.get(game['team2'], 'weiß') if team_colors else 'weiß'
            
            game_text = f"<b>Spiel {i+1}"
            if 'round' in game and game['round'] != 'Einzelrunde':
                game_text += f" ({game['round']})"
            game_text += f"</b><br/>"
            game_text += f"{game['team1']} ({color1}) vs {game['team2']} ({color2})<br/>"
            game_text += f"Spieler: {', '.join(game['players1'])}<br/>"
            game_text += f"Spieler: {', '.join(game['players2'])}<br/>"
            game_text += f"Ergebnis: {game['score1']}:{game['score2']}"
            
            row.append(Paragraph(game_text, styles['Normal']))
        else:
            row.append("")
        
        # Second game
        if i + 1 < len(schedule):
            game = schedule[i + 1]
            color1 = team_colors.get(game['team1'], 'weiß') if team_colors else 'weiß'
            color2 = team_colors.get(game['team2'], 'weiß') if team_colors else 'weiß'
            
            game_text = f"<b>Spiel {i+2}"
            if 'round' in game and game['round'] != 'Einzelrunde':
                game_text += f" ({game['round']})"
            game_text += f"</b><br/>"
            game_text += f"{game['team1']} ({color1}) vs {game['team2']} ({color2})<br/>"
            game_text += f"Spieler: {', '.join(game['players1'])}<br/>"
            game_text += f"Spieler: {', '.join(game['players2'])}<br/>"
            game_text += f"Ergebnis: {game['score1']}:{game['score2']}"
            
            row.append(Paragraph(game_text, styles['Normal']))
        else:
            row.append("")
        
        games_data.append(row)
    
    games_table = Table(games_data, colWidths=[3.5*inch, 3.5*inch])
    games_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(games_table)
    
    # Add cross table if there are results
    if any(game.get('score1', 0) > 0 or game.get('score2', 0) > 0 for game in schedule):
        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>Kreuztabelle</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        cross_table = create_cross_table(schedule, team_colors)
        story.append(cross_table)
    
    doc.build(story)
    return filename

def main():
    st.set_page_config(page_title="JWR-Turnier", page_icon="🟢", layout="wide")
    
    # Load data on startup
    load_tournament_data()
    
    st.title("🟢⚫ JWR-Turnier")
    
    # Sidebar for tournament settings
    with st.sidebar:
        st.header("Turnier-Einstellungen")
        
        tournament_type = st.selectbox(
            "Turnier-Typ",
            ["Feste Teams", "Round Robin"],
            index=0 if st.session_state.get('tournament_type', 'fixed') == 'fixed' else 1
        )
        st.session_state.tournament_type = 'fixed' if tournament_type == "Feste Teams" else 'round_robin'
        
        if st.session_state.tournament_type == 'fixed':
            st.session_state.num_teams = st.number_input("Anzahl Teams", min_value=2, max_value=8, value=st.session_state.num_teams)
            st.session_state.home_away = st.checkbox("Hin- und Rückrunde", value=st.session_state.home_away)
        else:
            st.session_state.players_per_team = st.number_input("Spieler pro Team", min_value=2, max_value=10, value=st.session_state.players_per_team)
        
        st.session_state.tournament_name = st.text_input("Turnier-Name", value=st.session_state.tournament_name)
        st.session_state.tournament_date = st.date_input("Datum", value=st.session_state.tournament_date)
    
    # Tournament Management
    st.header("Turnier-Management")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💾 Auto-Speichern"):
            save_tournament_data()
            st.success("Turnier-Daten gespeichert!")
    
    with col2:
        if st.button("📁 Auto-Laden"):
            load_tournament_data()
            st.success("Turnier-Daten geladen!")
    
    with col3:
        if st.button("🗑️ Daten löschen"):
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
            st.success("Alle Daten gelöscht!")
    
    with col4:
        if st.button("💾 Turnier speichern"):
            filename = save_tournament_as_file()
            if filename:
                st.success(f"Turnier gespeichert als: {filename}")
    
    # Load tournament
    st.header("Turnier laden")
    uploaded_file = st.file_uploader(
        "Turnier-Datei hochladen",
        type=['json'],
        help="Wählen Sie eine gespeicherte Turnier-Datei aus"
    )
    
    if uploaded_file is not None:
        if st.button("📥 Turnier laden"):
            if load_tournament_from_file(uploaded_file):
                st.success("Turnier erfolgreich geladen!")
                st.rerun()
    
    # Show current tournament info
    if st.session_state.tournament_name != "JWR-Turnier":
        st.info(f"**Aktuelles Turnier:** {st.session_state.tournament_name} ({st.session_state.tournament_date})")
    
    # Player Management
    st.header("Spieler-Verwaltung")
    
    with st.expander("Spieler hinzufügen/entfernen", expanded=True):
        new_player = st.text_input("Neuer Spieler")
        if st.button("Spieler hinzufügen"):
            if new_player and new_player not in st.session_state.players:
                st.session_state.players.append(new_player)
                save_players()
                st.success(f"Spieler '{new_player}' hinzugefügt!")
                st.rerun()
            elif new_player in st.session_state.players:
                st.error("Spieler existiert bereits!")
        
        if st.session_state.players:
            player_to_remove = st.selectbox("Spieler entfernen", st.session_state.players)
            if st.button("Spieler entfernen"):
                st.session_state.players.remove(player_to_remove)
                if player_to_remove in st.session_state.unavailable_players:
                    st.session_state.unavailable_players.remove(player_to_remove)
                # Remove from teams
                for team_name in st.session_state.teams:
                    if player_to_remove in st.session_state.teams[team_name]:
                        st.session_state.teams[team_name].remove(player_to_remove)
                save_players()
                st.success(f"Spieler '{player_to_remove}' entfernt!")
                st.rerun()
    
    # Player availability
    available_players = [p for p in st.session_state.players if p not in st.session_state.unavailable_players]
    unavailable_players = [p for p in st.session_state.players if p in st.session_state.unavailable_players]
    
    if st.session_state.players:
        st.subheader("Spieler-Liste")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Verfügbare Spieler:**")
            for i, player in enumerate(available_players):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"• {player}")
                with col_b:
                    if st.button("Nicht verfügbar", key=f"unavailable_{i}"):
                        st.session_state.unavailable_players.append(player)
                        save_players()
                        st.rerun()
        
        with col2:
            st.write("**Nicht verfügbare Spieler:**")
            for i, player in enumerate(unavailable_players):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"• {player}")
                with col_b:
                    if st.button("Verfügbar", key=f"available_{i}"):
                        st.session_state.unavailable_players.remove(player)
                        save_players()
                        st.rerun()
    
    # Team Management
    if st.session_state.tournament_type == 'fixed':
        st.header("Team-Management")
        
        # Initialize teams
        team_names = [f"Team {chr(65 + i)}" for i in range(st.session_state.num_teams)]
        for team_name in team_names:
            if team_name not in st.session_state.teams:
                st.session_state.teams[team_name] = []
            if team_name not in st.session_state.team_colors:
                st.session_state.team_colors[team_name] = 'weiß'
        
        # Show teams with players
        teams_with_players = {team: players for team, players in st.session_state.teams.items() if players}
        empty_teams = {team: players for team, players in st.session_state.teams.items() if not players}
        
        for team_name, players in teams_with_players.items():
            with st.expander(f"{get_team_color_icon(team_name)} {team_name} ({len(players)} Spieler)", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Aktuelle Spieler:**")
                    for player in players:
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.write(f"• {player}")
                        with col_b:
                            if st.button("Entfernen", key=f"remove_{team_name}_{player}"):
                                st.session_state.teams[team_name].remove(player)
                                save_tournament_data()
                                st.rerun()
                    
                    # Add player
                    available_for_team = [p for p in st.session_state.players 
                                       if p not in st.session_state.unavailable_players 
                                       and p not in players
                                       and not any(p in team_players for team_players in st.session_state.teams.values())]
                    
                    if available_for_team:
                        selected_player = st.selectbox("Spieler hinzufügen", available_for_team, key=f"add_{team_name}")
                        if st.button("Hinzufügen", key=f"add_btn_{team_name}"):
                            st.session_state.teams[team_name].append(selected_player)
                            save_tournament_data()
                            st.rerun()
                
                with col2:
                    # Team color
                    current_color = st.session_state.team_colors[team_name]
                    new_color = st.selectbox(
                        "Team-Farbe",
                        list(TEAM_COLORS.keys()),
                        key=f"color_{team_name}",
                        index=list(TEAM_COLORS.keys()).index(current_color),
                    )
                    if new_color != current_color:
                        st.session_state.team_colors[team_name] = new_color
                        save_tournament_data()
                        st.rerun()
        
        # Show one empty team for new assignments
        if empty_teams:
            empty_team_name = list(empty_teams.keys())[0]
            with st.expander(f"{get_team_color_icon(empty_team_name)} {empty_team_name} (keine Spieler)", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Keine Spieler zugewiesen**")
                    
                    # Add player
                    available_for_team = [p for p in st.session_state.players 
                                       if p not in st.session_state.unavailable_players 
                                       and not any(p in team_players for team_players in st.session_state.teams.values())]
                    
                    if available_for_team:
                        selected_player = st.selectbox("Spieler hinzufügen", available_for_team, key=f"add_{empty_team_name}")
                        if st.button("Hinzufügen", key=f"add_btn_{empty_team_name}"):
                            st.session_state.teams[empty_team_name].append(selected_player)
                            save_tournament_data()
                            st.rerun()
                
                with col2:
                    # Team color
                    current_color = st.session_state.team_colors[empty_team_name]
                    new_color = st.selectbox(
                        "Team-Farbe",
                        list(TEAM_COLORS.keys()),
                        key=f"color_{empty_team_name}",
                        index=list(TEAM_COLORS.keys()).index(current_color),
                    )
                    if new_color != current_color:
                        st.session_state.team_colors[empty_team_name] = new_color
                        save_tournament_data()
                        st.rerun()
        
        # Automatic team generation
        with st.expander("Automatische Team-Generierung", expanded=False):
            available_players = [p for p in st.session_state.players if p not in st.session_state.unavailable_players]
            
            if len(available_players) >= st.session_state.num_teams:
                strategy = st.selectbox("Strategie", ["Zufällig", "Gleichmäßig", "Round Robin"])
                
                if st.button("Teams generieren"):
                    # Clear existing teams
                    for team_name in st.session_state.teams:
                        st.session_state.teams[team_name] = []
                    
                    if strategy == "Zufällig":
                        import random
                        random.shuffle(available_players)
                        players_per_team = len(available_players) // st.session_state.num_teams
                        remainder = len(available_players) % st.session_state.num_teams
                        
                        start = 0
                        for i, team_name in enumerate(list(st.session_state.teams.keys())[:st.session_state.num_teams]):
                            end = start + players_per_team + (1 if i < remainder else 0)
                            st.session_state.teams[team_name] = available_players[start:end]
                            start = end
                    
                    elif strategy == "Gleichmäßig":
                        players_per_team = len(available_players) // st.session_state.num_teams
                        remainder = len(available_players) % st.session_state.num_teams
                        
                        start = 0
                        for i, team_name in enumerate(list(st.session_state.teams.keys())[:st.session_state.num_teams]):
                            end = start + players_per_team + (1 if i < remainder else 0)
                            st.session_state.teams[team_name] = available_players[start:end]
                            start = end
                    
                    elif strategy == "Round Robin":
                        # Distribute players in round-robin fashion
                        for i, player in enumerate(available_players):
                            team_index = i % st.session_state.num_teams
                            team_name = list(st.session_state.teams.keys())[team_index]
                            st.session_state.teams[team_name].append(player)
                    
                    # Assign random colors
                    for i, team_name in enumerate(list(st.session_state.teams.keys())[:st.session_state.num_teams]):
                        if st.session_state.teams[team_name]:  # Only assign color if team has players
                            st.session_state.team_colors[team_name] = list(TEAM_COLORS.keys())[i % len(TEAM_COLORS)]
                    
                    save_tournament_data()
                    st.success("Teams generiert!")
                    st.rerun()
            else:
                st.warning(f"Nicht genügend verfügbare Spieler. Benötigt: {st.session_state.num_teams}, Verfügbar: {len(available_players)}")
    
    # Schedule Generation
    if st.session_state.tournament_type == 'fixed':
        teams_with_players = {team: players for team, players in st.session_state.teams.items() if players}
        if len(teams_with_players) >= 2:
            if st.button("Spielplan generieren"):
                st.session_state.schedule = generate_fixed_teams_schedule(st.session_state.teams, st.session_state.home_away)
                save_tournament_data()
                st.success("Spielplan generiert!")
                st.rerun()
        else:
            st.warning("Mindestens 2 Teams mit Spielern benötigt für Spielplan-Generierung")
    else:
        available_players = [p for p in st.session_state.players if p not in st.session_state.unavailable_players]
        if len(available_players) >= st.session_state.players_per_team * 2:
            if st.button("Spielplan generieren"):
                st.session_state.schedule = generate_round_robin_schedule(available_players, st.session_state.players_per_team)
                save_tournament_data()
                st.success("Spielplan generiert!")
                st.rerun()
        else:
            st.warning(f"Mindestens {st.session_state.players_per_team * 2} verfügbare Spieler benötigt für Round Robin")
    
    # Display Schedule
    if st.session_state.schedule:
        st.header("Spielplan")
        
        # Count games by round
        hinrunde_games = [g for g in st.session_state.schedule if g.get('round') == 'Hinrunde']
        rueckrunde_games = [g for g in st.session_state.schedule if g.get('round') == 'Rückrunde']
        total_games = len(st.session_state.schedule)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        if hinrunde_games:
            st.metric("Hinrunde", len(hinrunde_games))
        if rueckrunde_games:
            st.metric("Rückrunde", len(rueckrunde_games))
        st.metric("Gesamt", total_games)
        
        # Display games grouped by round
        if hinrunde_games:
            st.subheader("Hinrunde")
            for i, game in enumerate(hinrunde_games, 1):
                with st.expander(f"Spiel {i}: {game['team1']} {get_team_color_icon(game['team1'])} vs {game['team2']} {get_team_color_icon(game['team2'])}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**{game['team1']} {get_team_color_icon(game['team1'])}**")
                        st.write(f"Spieler: {', '.join(game['players1'])}")
                        score1 = st.number_input("Tore", min_value=0, value=int(game['score1']) if game['score1'] and str(game['score1']).isdigit() else 0, key=f"hin_score1_{i}")
                        if score1 != game['score1']:
                            game['score1'] = score1
                            save_tournament_data()
                    
                    with col2:
                        st.write(f"**{game['team2']} {get_team_color_icon(game['team2'])}**")
                        st.write(f"Spieler: {', '.join(game['players2'])}")
                        score2 = st.number_input("Tore", min_value=0, value=int(game['score2']) if game['score2'] and str(game['score2']).isdigit() else 0, key=f"hin_score2_{i}")
                        if score2 != game['score2']:
                            game['score2'] = score2
                            save_tournament_data()
        
        if rueckrunde_games:
            st.subheader("Rückrunde")
            for j, game in enumerate(rueckrunde_games, 1):
                with st.expander(f"Spiel {j}: {game['team1']} {get_team_color_icon(game['team1'])} vs {game['team2']} {get_team_color_icon(game['team2'])}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**{game['team1']} {get_team_color_icon(game['team1'])}**")
                        st.write(f"Spieler: {', '.join(game['players1'])}")
                        score1 = st.number_input("Tore", min_value=0, value=int(game['score1']) if game['score1'] and str(game['score1']).isdigit() else 0, key=f"ruck_score1_{j}")
                        if score1 != game['score1']:
                            game['score1'] = score1
                            save_tournament_data()
                    
                    with col2:
                        st.write(f"**{game['team2']} {get_team_color_icon(game['team2'])}**")
                        st.write(f"Spieler: {', '.join(game['players2'])}")
                        score2 = st.number_input("Tore", min_value=0, value=int(game['score2']) if game['score2'] and str(game['score2']).isdigit() else 0, key=f"ruck_score2_{j}")
                        if score2 != game['score2']:
                            game['score2'] = score2
                            save_tournament_data()
        
        # Other games (single round or round robin)
        other_games = [g for g in st.session_state.schedule if g.get('round') not in ['Hinrunde', 'Rückrunde']]
        if other_games:
            for k, game in enumerate(other_games, 1):
                with st.expander(f"Spiel {k}: {game['team1']} {get_team_color_icon(game['team1']) if st.session_state.tournament_type == 'fixed' else ''} vs {game['team2']} {get_team_color_icon(game['team2']) if st.session_state.tournament_type == 'fixed' else ''}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**{game['team1']}**")
                        st.write(f"Spieler: {', '.join(game['players1'])}")
                        score1 = st.number_input("Tore", min_value=0, value=int(game['score1']) if game['score1'] and str(game['score1']).isdigit() else 0, key=f"other_score1_{k}")
                        if score1 != game['score1']:
                            game['score1'] = score1
                            save_tournament_data()
                    
                    with col2:
                        st.write(f"**{game['team2']}**")
                        st.write(f"Spieler: {', '.join(game['players2'])}")
                        score2 = st.number_input("Tore", min_value=0, value=int(game['score2']) if game['score2'] and str(game['score2']).isdigit() else 0, key=f"other_score2_{k}")
                        if score2 != game['score2']:
                            game['score2'] = score2
                            save_tournament_data()
        
        # PDF Export
        if st.button("📄 PDF Export"):
            filename = create_pdf_tournament_schedule(
                st.session_state.tournament_name,
                st.session_state.tournament_date,
                st.session_state.schedule,
                st.session_state.tournament_type,
                st.session_state.team_colors
            )
            st.success(f"PDF erstellt: {filename}")
            
            # Provide download link
            with open(filename, "rb") as file:
                st.download_button(
                    label="📥 PDF herunterladen",
                    data=file.read(),
                    file_name=filename,
                    mime="application/pdf"
                )

if __name__ == "__main__":
    main()

