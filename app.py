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
if 'num_fields' not in st.session_state:
    st.session_state.num_fields = 1
if 'team_selection' not in st.session_state:
    st.session_state.team_selection = 'JWR'

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
    # Prüfe ob team_name eine Liste ist (Round Robin) oder ein String (Feste Teams)
    if isinstance(team_name, list):
        # Für Round Robin: verwende den ersten Spieler als Team-Identifikator
        team_key = f"Team_{team_name[0]}"
    else:
        team_key = team_name
    
    color = st.session_state.team_colors.get(team_key, "gelb")
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

def load_team_players(team_name):
    """Lädt Spieler für ein spezifisches Team aus der entsprechenden JSON-Datei"""
    filename = f"{team_name}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data.get('players', [])
            else:
                # Alte Format - nur Spielerliste
                return data
    except FileNotFoundError:
        # Erstelle Standard-Spieler für das Team
        default_players = {
            "U15": ["Max Mustermann", "Anna Schmidt", "Tom Weber", "Lisa Müller", "Ben Klein", "Emma Groß"],
            "U16": ["Paul Fischer", "Sophie Bauer", "Lukas Wolf", "Mia Richter", "Noah Zimmermann", "Hannah Koch"],
            "U18": ["Felix Hoffmann", "Lena Schulz", "Jonas Wagner", "Marie Becker", "Tim Neumann", "Sarah Schwarz"],
            "JWR": ["Alex Meyer", "Julia Hoffmann", "Simon Weber", "Laura Fischer", "Daniel Klein", "Nina Wolf"]
        }
        players = default_players.get(team_name, [])
        # Speichere die Standard-Spieler in der Datei
        save_team_players(team_name, players)
        return players

def save_team_players(team_name, players):
    """Speichert Spieler für ein spezifisches Team in der entsprechenden JSON-Datei"""
    filename = f"{team_name}.json"
    data = {
        'players': players,
        'team_name': team_name,
        'last_updated': datetime.now().isoformat()
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def migrate_players_to_team_files():
    """Migriert die aktuellen Spieler aus players.json zu JWR.json"""
    try:
        # Lade aktuelle Spieler
        with open('players.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                players = data.get('players', [])
            else:
                players = data
        
        if players:
            # Speichere in JWR.json
            save_team_players("JWR", players)
            return True
    except FileNotFoundError:
        pass
    return False

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
        'players_per_team': st.session_state.players_per_team,
        'num_fields': st.session_state.num_fields
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
        'num_fields': st.session_state.num_fields,
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
        st.session_state.num_fields = data.get('num_fields', 1)
        
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
            st.session_state.num_fields = data.get('num_fields', 1)
            
            return True
    except FileNotFoundError:
        return False

def generate_round_robin_schedule(players: List[str], players_per_team: int = 2, num_fields: int = 1, games_per_player: int = 3) -> List[Dict]:
    """Generiert einen Round-Robin Spielplan - jeder Spieler hat genau games_per_player Spiele"""
    if len(players) < 4:
        return []
    
    # Berechne die Anzahl der Teams
    num_teams = len(players) // players_per_team
    if len(players) % players_per_team != 0:
        st.warning(f"Anzahl der Spieler ({len(players)}) ist nicht durch {players_per_team} teilbar. Es werden {num_teams * players_per_team} Spieler verwendet.")
        players = players[:num_teams * players_per_team]
    
    rounds = []
    import random
    
    # Zähle Spiele pro Spieler
    player_game_count = {player: 0 for player in players}
    
    # Berechne maximale Anzahl der Spiele pro Runde
    max_games_per_round = min(num_fields, num_teams // 2)
    
    # Generiere so viele Runden, bis jeder Spieler genug Spiele hat
    round_num = 0
    while any(count < games_per_player for count in player_game_count.values()):
        round_num += 1
        
        # Mische die Spieler für diese Runde
        shuffled_players = players.copy()
        random.shuffle(shuffled_players)
        
        # Erstelle Teams für diese Runde
        teams = []
        for team_num in range(num_teams):
            start_idx = team_num * players_per_team
            end_idx = start_idx + players_per_team
            team_players = shuffled_players[start_idx:end_idx]
            teams.append(team_players)
        
        # Erstelle Spiele für diese Runde
        games = []
        games_this_round = 0
        
        # Erstelle Paarungen basierend auf Spieler, die noch Spiele brauchen
        for i in range(0, len(teams) - 1, 2):
            if games_this_round >= max_games_per_round:
                break
                
            team1 = teams[i]
            team2 = teams[i + 1]
            
            # Prüfe ob beide Teams Spieler haben, die noch Spiele brauchen
            team1_needs_games = any(player_game_count[player] < games_per_player for player in team1)
            team2_needs_games = any(player_game_count[player] < games_per_player for player in team2)
            
            if team1_needs_games and team2_needs_games:
                games.append({
                    'team1': team1,
                    'team2': team2,
                    'score1': '',
                    'score2': ''
                })
                
                # Erhöhe Spielzähler nur für Spieler, die noch Spiele brauchen
                for player in team1 + team2:
                    if player_game_count[player] < games_per_player:
                        player_game_count[player] += 1
                
                games_this_round += 1
        
        # Wenn keine Spiele erstellt wurden, aber noch Spieler Spiele brauchen,
        # erstelle mindestens ein Spiel
        if games_this_round == 0 and any(count < games_per_player for count in player_game_count.values()):
            for i in range(0, len(teams) - 1, 2):
                if games_this_round >= max_games_per_round:
                    break
                    
                team1 = teams[i]
                team2 = teams[i + 1]
                
                games.append({
                    'team1': team1,
                    'team2': team2,
                    'score1': '',
                    'score2': ''
                })
                
                # Erhöhe Spielzähler nur für Spieler, die noch Spiele brauchen
                for player in team1 + team2:
                    if player_game_count[player] < games_per_player:
                        player_game_count[player] += 1
                
                games_this_round += 1
        
        rounds.append({
            'round': round_num,
            'games': games
        })
        
        # Sicherheitsabschaltung: Maximal 20 Runden
        if round_num >= 20:
            break
    
    # Verteile Runden auf Spielfelder
    if num_fields == 1:
        return rounds
    else:
        # Gruppiere Runden basierend auf Anzahl der Spielfelder
        grouped_rounds = []
        for i in range(0, len(rounds), num_fields):
            round_group = rounds[i:i + num_fields]
            grouped_rounds.append({
                'round': len(grouped_rounds) + 1,
                'sub_rounds': round_group
            })
        return grouped_rounds

def generate_fixed_teams_schedule(teams: Dict[str, List[str]], home_away: bool = False, num_fields: int = 1) -> List[Dict]:
    """Generiert einen Spielplan für feste Teams - optimiert für 5 Teams mit 4 Spielern auf 2 Spielfeldern"""
    # Nur Teams mit Spielern berücksichtigen
    teams_with_players = {name: players for name, players in teams.items() if players}
    team_names = list(teams_with_players.keys())
    
    if len(team_names) < 2:
        return []
    
    # Spezielle Optimierung für 4 Teams mit 2 Spielfeldern
    if len(team_names) == 4 and num_fields == 2:
        return generate_optimized_4_teams_schedule(teams_with_players, home_away)
    
    # Spezielle Optimierung für 5 Teams mit 2 Spielfeldern
    if len(team_names) == 5 and num_fields == 2:
        return generate_optimized_5_teams_schedule(teams_with_players, home_away)
    
    # Erstelle alle möglichen Paarungen
    hinrunde_games = []
    ruckrunde_games = []
    
    # Zuerst alle Hinrunden-Spiele
    for i in range(len(team_names)):
        for j in range(i + 1, len(team_names)):
            hinrunde_games.append({
                'team1': team_names[i],
                'team2': team_names[j],
                'players1': teams_with_players[team_names[i]],
                'players2': teams_with_players[team_names[j]],
                'score1': '',
                'score2': ''
            })
    
    # Dann alle Rückrunden-Spiele (nur wenn aktiviert)
    if home_away:
        for i in range(len(team_names)):
            for j in range(i + 1, len(team_names)):
                ruckrunde_games.append({
                    'team1': team_names[j],
                    'team2': team_names[i],
                    'players1': teams_with_players[team_names[j]],
                    'players2': teams_with_players[team_names[i]],
                    'score1': '',
                    'score2': ''
            })
    
    # Verteile Spiele auf Runden basierend auf Anzahl der Spielfelder
    if num_fields == 1:
        # Alle Spiele in einer Runde
        all_games = hinrunde_games + ruckrunde_games
        return all_games
    else:
        rounds = []
        
        # Verarbeite Hinrunde
        if hinrunde_games:
            hinrunde_rounds = distribute_games_to_rounds(hinrunde_games, num_fields, "Hinrunde", start_round=1)
            rounds.extend(hinrunde_rounds)
        
        # Verarbeite Rückrunde mit Feldwechsel - Runden-Nummerierung fortsetzen
        if ruckrunde_games:
            start_round = len(rounds) + 1
            ruckrunde_rounds = distribute_games_to_rounds(ruckrunde_games, num_fields, "Rückrunde", swap_fields=True, start_round=start_round)
            rounds.extend(ruckrunde_rounds)
        
        # Stelle sicher, dass alle Spiele die players1 und players2 Felder haben
        for round_data in rounds:
            for game in round_data['games']:
                if 'players1' not in game:
                    game['players1'] = teams_with_players.get(game['team1'], [])
                if 'players2' not in game:
                    game['players2'] = teams_with_players.get(game['team2'], [])
        
        return rounds

def generate_optimized_5_teams_schedule(teams_with_players: Dict[str, List[str]], home_away: bool = False) -> List[Dict]:
    """Generiert einen optimierten Spielplan für 5 Teams auf 2 Spielfeldern"""
    team_names = list(teams_with_players.keys())
    
    # Optimaler Spielplan für 5 Teams auf 2 Spielfeldern
    # Jede Runde hat 2 Spiele, ein Team pausiert
    # Insgesamt 5 Runden für Hinrunde (jedes Team spielt 4 mal, pausiert 1 mal)
    
    hinrunde_schedule = [
        # Runde 1: Team A vs Team B, Team C vs Team D (Team E pausiert)
        [('A', 'B'), ('C', 'D')],
        # Runde 2: Team A vs Team C, Team B vs Team E (Team D pausiert)
        [('A', 'C'), ('B', 'E')],
        # Runde 3: Team A vs Team D, Team C vs Team E (Team B pausiert)
        [('A', 'D'), ('C', 'E')],
        # Runde 4: Team A vs Team E, Team B vs Team D (Team C pausiert)
        [('A', 'E'), ('B', 'D')],
        # Runde 5: Team B vs Team C, Team D vs Team E (Team A pausiert)
        [('B', 'C'), ('D', 'E')]
    ]
    
    # Konvertiere Team-Buchstaben zu tatsächlichen Team-Namen
    team_mapping = {chr(65 + i): team_names[i] for i in range(len(team_names))}
    
    rounds = []
    
    # Erstelle Hinrunde
    for round_num, round_games in enumerate(hinrunde_schedule, 1):
        games = []
        for team1_letter, team2_letter in round_games:
            team1 = team_mapping[team1_letter]
            team2 = team_mapping[team2_letter]
            games.append({
                'team1': team1,
                'team2': team2,
                'players1': teams_with_players[team1],
                'players2': teams_with_players[team2],
                'score1': '',
                'score2': ''
            })
        
        # Finde das pausierende Team
        playing_teams = set()
        for team1_letter, team2_letter in round_games:
            playing_teams.add(team1_letter)
            playing_teams.add(team2_letter)
        resting_team_letter = [letter for letter in 'ABCDE' if letter not in playing_teams][0]
        resting_team = team_mapping[resting_team_letter]
        
        rounds.append({
            'round': f"Hinrunde {round_num}.Spieltag",
            'games': games,
            'resting_teams': [resting_team]
        })
    
    # Erstelle Rückrunde (nur wenn aktiviert)
    if home_away:
        ruckrunde_schedule = [
            # Runde 6: Team B vs Team A, Team D vs Team C (Team E pausiert)
            [('B', 'A'), ('D', 'C')],
            # Runde 7: Team C vs Team A, Team E vs Team B (Team D pausiert)
            [('C', 'A'), ('E', 'B')],
            # Runde 8: Team D vs Team A, Team E vs Team C (Team B pausiert)
            [('D', 'A'), ('E', 'C')],
            # Runde 9: Team E vs Team A, Team D vs Team B (Team C pausiert)
            [('E', 'A'), ('D', 'B')],
            # Runde 10: Team C vs Team B, Team E vs Team D (Team A pausiert)
            [('C', 'B'), ('E', 'D')]
        ]
        
        for round_num, round_games in enumerate(ruckrunde_schedule, 6):
            games = []
            for team1_letter, team2_letter in round_games:
                team1 = team_mapping[team1_letter]
                team2 = team_mapping[team2_letter]
                games.append({
                    'team1': team1,
                    'team2': team2,
                    'players1': teams_with_players[team1],
                    'players2': teams_with_players[team2],
                    'score1': '',
                    'score2': ''
                })
            
            # Finde das pausierende Team
            playing_teams = set()
            for team1_letter, team2_letter in round_games:
                playing_teams.add(team1_letter)
                playing_teams.add(team2_letter)
            resting_team_letter = [letter for letter in 'ABCDE' if letter not in playing_teams][0]
            resting_team = team_mapping[resting_team_letter]
            
            rounds.append({
                'round': f"Rückrunde {round_num-5}.Spieltag",
                'games': games,
                'resting_teams': [resting_team]
            })
    
    return rounds

def generate_optimized_4_teams_schedule(teams_with_players: Dict[str, List[str]], home_away: bool = False) -> List[Dict]:
    """Generiert einen optimierten Spielplan für 4 Teams auf 2 Spielfeldern"""
    team_names = list(teams_with_players.keys())
    
    # Optimaler Spielplan für 4 Teams auf 2 Spielfeldern
    # Jede Runde hat 2 Spiele, alle Teams spielen gleichzeitig
    # Insgesamt 3 Runden für Hinrunde (jedes Team spielt 3 mal)
    
    hinrunde_schedule = [
        # Runde 1: Team A vs Team B, Team C vs Team D
        [('A', 'B'), ('C', 'D')],
        # Runde 2: Team A vs Team C, Team B vs Team D
        [('A', 'C'), ('B', 'D')],
        # Runde 3: Team A vs Team D, Team B vs Team C
        [('A', 'D'), ('B', 'C')]
    ]
    
    # Konvertiere Team-Buchstaben zu tatsächlichen Team-Namen
    team_mapping = {chr(65 + i): team_names[i] for i in range(len(team_names))}
    
    rounds = []
    
    # Erstelle Hinrunde
    for round_num, round_games in enumerate(hinrunde_schedule, 1):
        games = []
        for team1_letter, team2_letter in round_games:
            team1 = team_mapping[team1_letter]
            team2 = team_mapping[team2_letter]
            games.append({
                'team1': team1,
                'team2': team2,
                'players1': teams_with_players[team1],
                'players2': teams_with_players[team2],
                'score1': '',
                'score2': ''
            })
        
        rounds.append({
            'round': f"Hinrunde {round_num}.Spieltag",
            'games': games,
            'resting_teams': []  # Keine pausierenden Teams bei 4 Teams
        })
    
    # Erstelle Rückrunde (nur wenn aktiviert)
    if home_away:
        ruckrunde_schedule = [
            # Runde 4: Team B vs Team A, Team D vs Team C
            [('B', 'A'), ('D', 'C')],
            # Runde 5: Team C vs Team A, Team D vs Team B
            [('C', 'A'), ('D', 'B')],
            # Runde 6: Team D vs Team A, Team C vs Team B
            [('D', 'A'), ('C', 'B')]
        ]
        
        for round_num, round_games in enumerate(ruckrunde_schedule, 4):
            games = []
            for team1_letter, team2_letter in round_games:
                team1 = team_mapping[team1_letter]
                team2 = team_mapping[team2_letter]
                games.append({
                    'team1': team1,
                    'team2': team2,
                    'players1': teams_with_players[team1],
                    'players2': teams_with_players[team2],
                    'score1': '',
                    'score2': ''
                })
            
            rounds.append({
                'round': f"Rückrunde {round_num-3}.Spieltag",
                'games': games,
                'resting_teams': []  # Keine pausierenden Teams bei 4 Teams
            })
    
    return rounds

def distribute_games_to_rounds(games, num_fields, round_type, swap_fields=False, start_round=1):
    """Verteilt Spiele auf Runden und tauscht optional die Spielfelder"""
    if not games:
        return []
    
    # Sammle alle Teams aus den Spielen
    all_teams = set()
    for game in games:
        all_teams.add(game['team1'])
        all_teams.add(game['team2'])
    all_teams = list(all_teams)
    
    rounds = []
    remaining_games = games.copy()
    round_counter = start_round
    team_pause_count = {team: 0 for team in all_teams}  # Zähle Pausen pro Team
    
    while remaining_games:
        current_round_games = []
        current_round_teams = set()
        games_to_remove = []
        
        # Fülle die aktuelle Runde mit maximal num_fields Spielen
        for game in remaining_games:
            # Prüfe ob eines der Teams bereits in dieser Runde spielt
            if game['team1'] not in current_round_teams and game['team2'] not in current_round_teams:
                # Team spielt noch nicht in dieser Runde
                if len(current_round_games) < num_fields:
                    # Noch Platz in dieser Runde
                    current_round_games.append(game)
                    current_round_teams.add(game['team1'])
                    current_round_teams.add(game['team2'])
                    games_to_remove.append(game)
        
        # Entferne die verarbeiteten Spiele
        for game in games_to_remove:
            remaining_games.remove(game)
        
        # Füge die Runde hinzu, auch wenn sie nicht voll ist
        if current_round_games:
            # Tausche Spielfelder in der Rückrunde
            if swap_fields and len(current_round_games) == num_fields:
                # Vertausche die Reihenfolge der Spiele (Feld 1 <-> Feld 2)
                current_round_games.reverse()
            
            # Zähle Pausen für Teams, die in dieser Runde nicht spielen
            playing_teams = set()
            for game in current_round_games:
                playing_teams.add(game['team1'])
                playing_teams.add(game['team2'])
            
            # Finde Teams, die in dieser Runde pausieren
            resting_teams = [team for team in all_teams if team not in playing_teams]
            for team in resting_teams:
                team_pause_count[team] += 1
            
            rounds.append({
                'round': f"{round_type} {round_counter}.Spieltag",
                'games': current_round_games,
                'resting_teams': resting_teams  # Füge pausierende Teams hinzu
            })
            round_counter += 1
        else:
            # Falls keine Spiele mehr hinzugefügt werden können, breche ab
            break
    
    return rounds

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
    """Erstellt eine Kreuztabelle der Spiele mit getrennten Hin- und Rückrunden"""
    # Sammle alle Teams - sichere Zugriffe
    teams = set()
    for game in schedule:
        team1 = game.get('team1', '')
        team2 = game.get('team2', '')
        if team1:
            teams.add(team1)
        if team2:
            teams.add(team2)
    
    teams = sorted(list(teams))
    
    # Trenne Hin- und Rückrunde
    hinrunde_games = [game for game in schedule if game.get('round') == 'Hinrunde']
    ruckrunde_games = [game for game in schedule if game.get('round') == 'Rückrunde']
    
    # Erstelle Kreuztabelle für Hinrunde
    hinrunde_data = create_round_table_data(hinrunde_games, teams, "Hinrunde")
    
    # Erstelle Kreuztabelle für Rückrunde
    ruckrunde_data = create_round_table_data(ruckrunde_games, teams, "Rückrunde")
    
    return hinrunde_data, ruckrunde_data

def create_round_table_data(games, teams, round_name):
    """Erstellt Tabellendaten für eine bestimmte Runde"""
    table_data = []
    
    # Header-Zeile
    header = [f"{round_name}"] + [f"{team}" for team in teams]
    table_data.append(header)
    
    # Daten-Zeilen
    for team1 in teams:
        row = [f"{team1}"]
        for team2 in teams:
            if team1 == team2:
                row.append("-")
            else:
                # Suche Spiele zwischen team1 und team2
                game_found = None
                for game in games:
                    game_team1 = game.get('team1', '')
                    game_team2 = game.get('team2', '')
                    if (game_team1 == team1 and game_team2 == team2) or \
                       (game_team1 == team2 and game_team2 == team1):
                        game_found = game
                        break
                
                if game_found:
                    # Bestimme Ergebnis basierend auf Team-Position
                    game_team1 = game_found.get('team1', '')
                    score1 = game_found.get('score1', '')
                    score2 = game_found.get('score2', '')
                    
                    if game_team1 == team1:
                        score = f"{score1}:{score2}"
                    else:
                        score = f"{score2}:{score1}"
                    
                    row.append(score)
                else:
                    row.append("")
        table_data.append(row)
    
    return table_data

def create_pdf_tournament_schedule(schedule, tournament_type, tournament_name, date, team_colors=None, num_fields=1):
    """Erstellt einen PDF-Turnierplan - kompakt auf einer Seite"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=18)
    
    # Extrahiere Teams aus dem Schedule für die PDF-Logik
    teams_with_players = {}
    if schedule and isinstance(schedule[0], dict) and 'games' in schedule[0]:
        for round_data in schedule:
            for game in round_data['games']:
                if 'team1' in game and 'players1' in game:
                    teams_with_players[game['team1']] = game['players1']
                if 'team2' in game and 'players2' in game:
                    teams_with_players[game['team2']] = game['players2']
    
    # Styles - kompakter für eine Seite
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        alignment=1,  # Center
        textColor=colors.darkblue
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=8,
        alignment=1,  # Center
        textColor=colors.darkgreen
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading3'],
        fontSize=10,
        spaceAfter=6,
        textColor=colors.darkblue
    )
    
    # Content
    story = []
    
    # Logo und Titel in einer Zeile
    logo = get_logo()
    
    # Erstelle Tabelle für Logo und Titel - kompakter
    header_data = [
        [logo, Paragraph(tournament_name, title_style)]
    ]
    
    header_table = Table(header_data, colWidths=[1.5*inch, 4.5*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),  # Logo links
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Titel zentriert
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 0), (1, 0), 18),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.darkblue),
    ]))
    
    story.append(header_table)
    story.append(Paragraph(f"Datum: {date} | Turniertyp: {tournament_type} | Spielfelder: {num_fields}", subtitle_style))
    
    story.append(Spacer(1, 8))
    
    if tournament_type == "Feste Teams":
        # Feste Teams Spiele
        
        # Teams unter der Überschrift auflisten
        if st.session_state.teams:
            try:
                # Prüfe ob teams ein Dictionary oder eine Liste ist
                if isinstance(st.session_state.teams, dict):
                    for team_name, team_data in st.session_state.teams.items():
                        team_color = team_colors.get(team_name, 'gelb') if team_colors else 'gelb'
                        if isinstance(team_data, dict):
                            players = team_data.get('players', [])
                            if players:
                                players_str = ", ".join(players)
                                team_text = f"{team_name} ({team_color}): {players_str}"
                            else:
                                team_text = f"{team_name} ({team_color})"
                        else:
                            # team_data ist bereits eine Liste, konvertiere zu String
                            if isinstance(team_data, list):
                                players_str = ", ".join(team_data)
                                team_text = f"{team_name} ({team_color}): {players_str}"
                            else:
                                team_text = f"{team_name} ({team_color}): {team_data}"
                        
                        story.append(Paragraph(team_text, styles['Normal']))
                else:  # Liste
                    for team in st.session_state.teams:
                        if isinstance(team, dict):
                            team_name = team.get('name', 'Unbekannt')
                            players = team.get('players', [])
                            team_color = team_colors.get(team_name, 'gelb') if team_colors else 'gelb'
                            if players:
                                players_str = ", ".join(players)
                                team_text = f"{team_name} ({team_color}): {players_str}"
                            else:
                                team_text = f"{team_name} ({team_color})"
                        else:
                            team_color = team_colors.get(team, 'gelb') if team_colors else 'gelb'
                            team_text = f"{team} ({team_color})"
                        
                        story.append(Paragraph(team_text, styles['Normal']))
                
                story.append(Spacer(1, 10))
            except Exception as e:
                # Fallback: Einfache Darstellung
                for team in st.session_state.teams:
                    team_color = team_colors.get(team, 'gelb') if team_colors else 'gelb'
                    team_text = f"{team} ({team_color})"
                    story.append(Paragraph(team_text, styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Prüfe ob Schedule in Runden strukturiert ist (mehrere Spielfelder)
        if schedule and isinstance(schedule[0], dict) and 'round' in schedule[0] and 'games' in schedule[0]:
            # Neue Struktur mit Runden (mehrere Spielfelder)
            for round_data in schedule:
                story.append(Paragraph(f"{round_data['round']}", heading_style))
                
                # Zeige pausierende Teams falls vorhanden
                if 'resting_teams' in round_data and round_data['resting_teams']:
                    resting_teams_str = ', '.join(round_data['resting_teams'])
                    story.append(Paragraph(f"⏸️ Pausierende Teams: {resting_teams_str}", styles['Normal']))
                
                # Erstelle eine Zeile für jedes Spiel dieser Runde
                for i, game in enumerate(round_data['games'], 1):
                    field_num = i
                    
                    # Team-Farben für PDF (falls verfügbar)
                    team1_color = ""
                    team2_color = ""
                    if team_colors:
                        team1_color_name = team_colors.get(game.get('team1', ''), 'gelb')
                        team2_color_name = team_colors.get(game.get('team2', ''), 'gelb')
                        team1_color = f" ({team1_color_name})"
                        team2_color = f" ({team2_color_name})"
                    
                    # Spiel-Info - sichere Zugriffe
                    team1 = game.get('team1', 'Unbekannt')
                    team2 = game.get('team2', 'Unbekannt')
                    score1 = game.get('score1', '')
                    score2 = game.get('score2', '')
                    
                    # Erstelle Spiel-Text mit ausgerichtetem Ergebnis
                    game_text = f"Feld {field_num}: {team1}{team1_color} vs {team2}{team2_color}"
                    result_text = "Ergebnis:"
                    
                    # Erstelle eine Tabelle mit fester Breite für besseren Abstand
                    table_data = [[game_text, result_text]]
                    game_table = Table(table_data, colWidths=[4*inch, 2.5*inch])
                    game_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 0, colors.white),  # Unsichtbare Linien
                        ('PADDING', (0, 0), (-1, -1), 0),
                        ('LEFTPADDING', (0, 0), (0, 0), 0),
                        ('RIGHTPADDING', (0, 0), (0, 0), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ]))
                    story.append(game_table)
                
                story.append(Spacer(1, 8))
        else:
            # Alte Struktur (ein Spielfeld)
            for i, game in enumerate(schedule, 1):
                # Runde anzeigen (falls vorhanden)
                round_info = f" ({game.get('round', '')})" if game.get('round') else ""
                
                # Team-Farben für PDF (falls verfügbar)
                team1_color = ""
                team2_color = ""
                if team_colors:
                    team1_color_name = team_colors.get(game.get('team1', ''), 'gelb')
                    team2_color_name = team_colors.get(game.get('team2', ''), 'gelb')
                    team1_color = f" ({team1_color_name})"
                    team2_color = f" ({team2_color_name})"
                
                # Spiel-Info - sichere Zugriffe
                team1 = game.get('team1', 'Unbekannt')
                team2 = game.get('team2', 'Unbekannt')
                score1 = game.get('score1', '')
                score2 = game.get('score2', '')
                
                # Erstelle Spiel-Text mit ausgerichtetem Ergebnis
                game_text = f"Spiel {i}{round_info}: {team1}{team1_color} vs {team2}{team2_color}"
                result_text = "Ergebnis:"
                
                # Erstelle eine Tabelle mit fester Breite für besseren Abstand
                table_data = [[game_text, result_text]]
                game_table = Table(table_data, colWidths=[4*inch, 2.5*inch])
                game_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0, colors.white),  # Unsichtbare Linien
                    ('PADDING', (0, 0), (-1, -1), 0),
                    ('LEFTPADDING', (0, 0), (0, 0), 0),
                    ('RIGHTPADDING', (0, 0), (0, 0), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                story.append(game_table)
                story.append(Spacer(1, 5))
    
    else:  # Round Robin - kompakter
        # Teams unter der Überschrift auflisten
        if st.session_state.teams:
            teams_text = ""
            try:
                # Prüfe ob teams ein Dictionary oder eine Liste ist
                if isinstance(st.session_state.teams, dict):
                    for team_name, team_data in st.session_state.teams.items():
                        if isinstance(team_data, dict):
                            players = team_data.get('players', [])
                            if players:
                                players_str = ", ".join(players)
                                teams_text += f"{team_name}: {players_str}\n"
                            else:
                                teams_text += f"{team_name}\n"
                        else:
                            # team_data ist bereits eine Liste, konvertiere zu String
                            if isinstance(team_data, list):
                                players_str = ", ".join(team_data)
                                teams_text += f"{team_name}: {players_str}\n"
                            else:
                                teams_text += f"{team_name}: {team_data}\n"
                else:  # Liste
                    for team in st.session_state.teams:
                        if isinstance(team, dict):
                            team_name = team.get('name', 'Unbekannt')
                            players = team.get('players', [])
                            if players:
                                players_str = ", ".join(players)
                                teams_text += f"{team_name}: {players_str}\n"
                            else:
                                teams_text += f"{team_name}\n"
                        else:
                            teams_text += f"{team}\n"
                
                # Teile den Text in separate Zeilen auf
                for line in teams_text.strip().split('\n'):
                    if line.strip():  # Nur nicht-leere Zeilen
                        story.append(Paragraph(line.strip(), styles['Normal']))
                story.append(Spacer(1, 10))
            except Exception as e:
                # Fallback: Einfache Darstellung
                teams_text = ""
                for team in st.session_state.teams:
                    teams_text += f"• {team}\n"
                # Teile den Text in separate Zeilen auf
                for line in teams_text.strip().split('\n'):
                    if line.strip():  # Nur nicht-leere Zeilen
                        story.append(Paragraph(line.strip(), styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Erstelle eine kompakte Tabelle für alle Runden
        round_data = []
        
        # Prüfe ob Schedule in Runden mit sub_rounds strukturiert ist (mehrere Spielfelder)
        if schedule and isinstance(schedule[0], dict) and 'sub_rounds' in schedule[0]:
            # Neue Struktur mit sub_rounds (mehrere Spielfelder)
            for round_info in schedule:
                round_num = round_info['round']
                for sub_round in round_info['sub_rounds']:
                    field_num = sub_round['round']
                    for i, game in enumerate(sub_round['games'], 1):
                        team1_display = ', '.join(game.get('team1', [])) if isinstance(game.get('team1', []), list) else game.get('team1', 'Unbekannt')
                        team2_display = ', '.join(game.get('team2', [])) if isinstance(game.get('team2', []), list) else game.get('team2', 'Unbekannt')
                        round_data.append([
                            f"R{round_num}",
                            f"F{field_num}S{i}",
                            team1_display,
                            team2_display,
                            f"{game.get('score1', '')}:{game.get('score2', '')}"
                        ])
        else:
            # Alte Struktur (ein Spielfeld)
            for round_info in schedule:
                round_num = round_info['round']
                for i, game in enumerate(round_info['games'], 1):
                    team1_display = ', '.join(game.get('team1', [])) if isinstance(game.get('team1', []), list) else game.get('team1', 'Unbekannt')
                    team2_display = ', '.join(game.get('team2', [])) if isinstance(game.get('team2', []), list) else game.get('team2', 'Unbekannt')
                    round_data.append([
                        f"R{round_num}",
                        f"S{i}",
                        team1_display,
                        team2_display,
                        f"{game.get('score1', '')}:{game.get('score2', '')}"
                    ])
        
        if round_data:
            # Erstelle Tabelle für Round Robin Spiele
            round_table = Table(round_data, colWidths=[0.5*inch, 0.5*inch, 2*inch, 2*inch, 0.8*inch])
            round_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header fett
                ('PADDING', (0, 0), (-1, -1), 3),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            # Header hinzufügen
            header_row = [["Runde", "Spiel", "Team 1", "Team 2", "Ergebnis"]]
            header_table = Table(header_row, colWidths=[0.5*inch, 0.5*inch, 2*inch, 2*inch, 0.8*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, -1), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            
            story.append(header_table)
            story.append(round_table)
    
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
        index=0  # Immer "Feste Teams" als Standard
    )
    
    # Wenn sich der Turniertyp ändert, lösche den aktuellen Spielplan
    if hasattr(st.session_state, 'tournament_type') and st.session_state.tournament_type != tournament_type:
        st.session_state.schedule = []
        st.session_state.teams = {}  # Auch Teams zurücksetzen bei Wechsel
        st.session_state.team_colors = {}
    
    st.session_state.tournament_type = tournament_type
    
    
    # Spieler-Management - Kompakt
    with st.expander("👥 Spieler-Management", expanded=True):
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Spieler hinzufügen - kompakt
            new_player = st.text_input("Neuer Spieler:", placeholder="Name eingeben", key="new_player_input")
            col_add1, col_add2 = st.columns([1, 1])
            with col_add1:
                if st.button("➕ Hinzufügen", key="add_player_btn"):
                    if new_player:
                        if new_player not in st.session_state.players:
                            st.session_state.players.append(new_player)
                            save_tournament_data()
                            st.success(f"'{new_player}' hinzugefügt!")
                            st.rerun()
                        else:
                            st.warning("Bereits vorhanden!")
            with col_add2:
                # Team-Auswahl für Laden
                team_options = ["U15", "U16", "U18", "JWR"]
                default_index = team_options.index(st.session_state.team_selection) if st.session_state.team_selection in team_options else 3
                selected_team = st.selectbox(
                    "Team auswählen:",
                    team_options,
                    index=default_index,
                    key="team_selection",
                    help="Wählen Sie ein Team aus, um die entsprechenden Spieler zu laden"
                )
                
                # Buttons in einer Zeile - kompakter
                if st.button("📁 Team laden", key="load_team_btn"):
                    team_players = load_team_players(selected_team)
                    if team_players:
                        # Füge nur neue Spieler hinzu (keine Duplikate)
                        new_players = [p for p in team_players if p not in st.session_state.players]
                        st.session_state.players.extend(new_players)
                        save_tournament_data()
                        st.success(f"{len(new_players)} neue Spieler von {selected_team} geladen!")
                        st.rerun()
                    else:
                        st.warning("Keine Spieler für dieses Team gefunden.")
                
                if st.button("📁 Datei laden", key="load_file_btn"):
                    loaded_players, loaded_unavailable, loaded_colors = load_players_from_file()
                    if loaded_players:
                        st.session_state.players = loaded_players
                        st.session_state.unavailable_players = loaded_unavailable
                        st.session_state.team_colors = loaded_colors
                        st.success(f"{len(loaded_players)} Spieler geladen!")
                        st.rerun()
                    else:
                        st.warning("Keine Spieler gefunden.")
                
        
        with col2:
            # Aktuelle Spieler - kompakt
            if st.session_state.players:
                # Filtere Spieler basierend auf ausgewähltem Team
                selected_team = st.session_state.team_selection
                team_players = load_team_players(selected_team)
                
                # Zeige nur Spieler des ausgewählten Teams
                filtered_players = [p for p in st.session_state.players if p in team_players]
                
                if filtered_players:
                    # Zähle verfügbare Spieler (nicht in unavailable_players)
                    available_count = len([p for p in filtered_players if p not in st.session_state.unavailable_players])
                    st.write(f"**Spieler von {selected_team} ({available_count} von {len(filtered_players)} Spieler verfügbar):**")
                    # Zeige Spieler in einer kompakten Liste
                    for i, player in enumerate(filtered_players):
                        # Finde den ursprünglichen Index
                        original_index = st.session_state.players.index(player)
                        is_unavailable = player in st.session_state.unavailable_players
                        status_icon = "🚫" if is_unavailable else "✅"
                        
                        col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
                        with col_a:
                            st.write(f"{status_icon} {player}")
                        with col_b:
                            if is_unavailable:
                                if st.button("✅", key=f"avail_{original_index}", help="Verfügbar"):
                                    st.session_state.unavailable_players.remove(player)
                                    save_tournament_data()
                                    st.rerun()
                            else:
                                if st.button("🚫", key=f"unavail_{original_index}", help="Nicht verfügbar"):
                                    st.session_state.unavailable_players.append(player)
                                    save_tournament_data()
                                    st.rerun()
                        with col_c:
                            if st.button("❌", key=f"del_{original_index}", help="Löschen"):
                                if player in st.session_state.unavailable_players:
                                    st.session_state.unavailable_players.remove(player)
                                st.session_state.players.pop(original_index)
                                save_tournament_data()
                                st.rerun()
                        with col_d:
                            # Leer für bessere Ausrichtung
                            pass
                else:
                    st.info(f"Keine Spieler von {selected_team} gefunden. Wählen Sie ein anderes Team oder laden Sie Spieler.")
            else:
                st.info("Noch keine Spieler hinzugefügt")
    
    # Daten-Management - Kompakt
    with st.expander("💾 Turnier-Management", expanded=False):
        col_save1, col_save2, col_save3, col_save4 = st.columns(4)
        with col_save1:
            if st.button("💾 Speichern", help="Daten speichern"):
                save_tournament_data()
                st.success("Gespeichert!")
        with col_save2:
            if st.button("📁 Laden", help="Daten laden"):
                load_tournament_data()
                st.success("Geladen!")
                st.rerun()
        with col_save3:
            if st.button("🗑️ Löschen", help="Alle Daten löschen"):
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
                st.session_state.num_fields = 1
                save_tournament_data()
                st.success("Gelöscht!")
                st.rerun()
        with col_save4:
            if st.button("💾 Export", help="Turnier als Datei speichern"):
                filename = save_tournament_as_file()
                if filename:
                    st.success(f"Gespeichert: {filename}")
        
        # Turnier-Datei hochladen - kompakt
        uploaded_file = st.file_uploader(
            "Turnier-Datei hochladen (.json)", 
            type=['json'],
            help="Gespeicherte Turnier-Datei auswählen"
        )
        
        if uploaded_file is not None:
            if st.button("📥 Turnier laden"):
                if load_tournament_from_file(uploaded_file):
                    st.success("Turnier geladen!")
                    st.rerun()
                else:
                    st.error("Fehler beim Laden!")
    
    # Aktuelle Turnier-Info - kompakt
    if st.session_state.tournament_name and st.session_state.tournament_name != "JWR-Turnier":
        st.info(f"**Aktuelles Turnier:** {st.session_state.tournament_name} ({st.session_state.tournament_date})")
    
    st.markdown("---")
    
    if tournament_type == "Feste Teams":
        # Feste Teams Turnier
        st.header("🏆 Feste Teams Turnier")
        
        if len(st.session_state.players) < 2:
            st.warning("Mindestens 2 Spieler erforderlich!")
            return
        
        # Team-Zuordnung - Kompakt
        with st.expander("🏆 Feste Teams Turnier", expanded=True):
            # Turnier-Einstellungen - kompakt
            col1, col2, col3 = st.columns(3)
            with col1:
                num_teams = st.number_input("Teams:", min_value=2, max_value=len(st.session_state.players), value=st.session_state.num_teams, help="Anzahl der Teams")
                st.session_state.num_teams = num_teams
            with col2:
                home_away = st.checkbox("Hin- & Rückrunde", value=st.session_state.home_away, help="Jedes Team spielt zu Hause und auswärts")
                st.session_state.home_away = home_away
            with col3:
                st.write("Spielfelder:")
                col_fields1, col_fields2, col_fields3 = st.columns([1, 1, 1])
                with col_fields1:
                    if st.button("➖", key="decrease_fields", help="Weniger Spielfelder"):
                        if st.session_state.num_fields > 1:
                            st.session_state.num_fields -= 1
                            st.rerun()
                with col_fields2:
                    st.write(f"**{st.session_state.num_fields}**")
                with col_fields3:
                    if st.button("➕", key="increase_fields", help="Mehr Spielfelder"):
                        if st.session_state.num_fields < 4:
                            st.session_state.num_fields += 1
                            st.rerun()
        
            # Teams erstellen
            team_names = [f"Team {chr(65 + i)}" for i in range(num_teams)]
            
            # Buttons für Team-Management - kompakt
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            with col_btn1:
                if st.button("🔄 Reset", help="Teams zurücksetzen"):
                    st.session_state.teams = {}
                    st.rerun()
            with col_btn2:
                if st.button("🎲 Auto-Generieren", help="Teams automatisch generieren"):
                    st.session_state.show_team_generator = True
                    st.rerun()
        
        # Team-Generierung außerhalb der verschachtelten Buttons
        if hasattr(st.session_state, 'show_team_generator') and st.session_state.show_team_generator:
            st.markdown("---")
            st.subheader("🎲 Team-Generierung")
            
            col_strategy, col_generate = st.columns([2, 1])
            with col_strategy:
                strategy = st.selectbox(
                    "Strategie:",
                    ["Zufällig", "Gleichmäßig", "Round Robin"],
                    help="Zufällig: Zufällige Aufteilung\nGleichmäßig: Gleichmäßige Verteilung\nRound Robin: Für Turnier mit wechselnden Teams"
                )
            with col_generate:
                if st.button("🎲 Generieren", type="primary"):
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
                        
                        player_index = 0
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
                    st.session_state.show_team_generator = False
                    st.rerun()
        
        with col_btn3:
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
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Statistiken
            total_assigned = sum(len(players) for players in st.session_state.teams.values())
            unassigned = len(st.session_state.players) - total_assigned
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Zugewiesene Spieler", total_assigned)
            with col2:
                st.metric("Nicht zugewiesen", unassigned)
        
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
            
            schedule = generate_fixed_teams_schedule(st.session_state.teams, home_away, st.session_state.num_fields)
            if schedule:
                st.session_state.schedule = schedule
                save_tournament_data()  # Automatisch speichern
                round_type = "Hin- und Rückrunde" if home_away else "Einfache Runde"
                st.success(f"Spielplan generiert! {len(teams_with_players)} Teams, {len(schedule)} Spiele ({round_type})")
            else:
                st.error("Kein gültiger Spielplan möglich!")
    
    else:
        # Round Robin Turnier
        st.header("🔄 Round Robin Turnier (Für 12, 16 oder 20 Spieler)")
        
        if len(st.session_state.players) < 4:
            st.warning("Mindestens 4 Spieler für Round Robin erforderlich!")
            return
        
        col1, col2, col3 = st.columns(3)
        with col1:
            players_per_team = st.number_input("Spieler pro Team:", min_value=2, max_value=len(st.session_state.players)//2, value=st.session_state.players_per_team)
            st.session_state.players_per_team = players_per_team
        with col2:
            st.write("Anzahl Spielfelder:")
            col_fields1, col_fields2, col_fields3 = st.columns([1, 1, 1])
            with col_fields1:
                if st.button("➖", key="decrease_fields_rr", help="Weniger Spielfelder"):
                    if st.session_state.num_fields > 1:
                        st.session_state.num_fields -= 1
                        st.rerun()
            with col_fields2:
                st.write(f"**{st.session_state.num_fields}**")
            with col_fields3:
                if st.button("➕", key="increase_fields_rr", help="Mehr Spielfelder"):
                    if st.session_state.num_fields < 4:
                        st.session_state.num_fields += 1
                        st.rerun()
        with col3:
            games_per_player = st.number_input(
                "Spiele pro Spieler:",
                min_value=1,
                max_value=10,
                value=st.session_state.get('games_per_player', 3),
                help="Wie viele Spiele soll jeder Spieler spielen?"
            )
            st.session_state.games_per_player = games_per_player
        
        if st.button("Round Robin Spielplan generieren"):
            # Nur verfügbare Spieler für Round Robin verwenden
            available_players = [p for p in st.session_state.players if p not in st.session_state.unavailable_players]
            if len(available_players) < 4:
                st.error("Mindestens 4 verfügbare Spieler für Round Robin erforderlich!")
                return
            
            games_per_player = st.session_state.get('games_per_player', 3)
            schedule = generate_round_robin_schedule(available_players, players_per_team, st.session_state.num_fields, games_per_player)
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
            
            # Prüfe ob Schedule in Runden strukturiert ist (mehrere Spielfelder)
            if st.session_state.schedule and isinstance(st.session_state.schedule[0], dict) and 'round' in st.session_state.schedule[0] and 'games' in st.session_state.schedule[0]:
                # Struktur mit Runden (mehrere Spielfelder)
                total_games = sum(len(round_data['games']) for round_data in st.session_state.schedule)
                st.metric("Gesamt Spiele", total_games)
                st.metric("Anzahl Runden", len(st.session_state.schedule))
                st.metric("Spielfelder", st.session_state.num_fields)
                
                # Zeige pausierende Teams pro Runde
                if any('resting_teams' in round_data and round_data['resting_teams'] for round_data in st.session_state.schedule):
                    st.info("ℹ️ **Pausierende Teams:** In jeder Runde pausiert ein Team, damit alle anderen Teams spielen können.")
            else:
                # Alte Struktur (ein Spielfeld)
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
            
            # Prüfe ob Schedule in Runden strukturiert ist (mehrere Spielfelder)
            if st.session_state.schedule and isinstance(st.session_state.schedule[0], dict) and 'round' in st.session_state.schedule[0] and 'games' in st.session_state.schedule[0]:
                # Neue Struktur mit Runden (mehrere Spielfelder)
                for round_data in st.session_state.schedule:
                    st.markdown(f"### 🏟️ {round_data['round']}")
                    
                    # Zeige pausierende Teams falls vorhanden
                    if 'resting_teams' in round_data and round_data['resting_teams']:
                        resting_teams_str = ', '.join(round_data['resting_teams'])
                        st.info(f"⏸️ **Pausierende Teams:** {resting_teams_str}")
                    
                    # Zeige Spiele in Spalten für bessere Übersicht
                    games = round_data['games']
                    if len(games) > 1:
                        cols = st.columns(min(len(games), 4))  # Max 4 Spalten
                        for i, game in enumerate(games):
                            with cols[i % len(cols)]:
                                team1_color = get_team_color_icon(game['team1'])
                                team2_color = get_team_color_icon(game['team2'])
                                field_num = (i % 2) + 1  # Immer Feld 1 oder Feld 2
                                
                                with st.expander(f"Feld {field_num}: {team1_color} {game['team1']} vs {team2_color} {game['team2']}"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        players1 = game.get('players1', [])
                                        players1_str = ', '.join(players1) if players1 else 'Keine Spieler'
                                        st.write(f"**{team1_color} {game['team1']}:** {players1_str}")
                                        score1 = st.number_input(f"Tore {game['team1']}:", min_value=0, key=f"round_{round_data['round']}_field_{field_num}_score1")
                                    with col2:
                                        players2 = game.get('players2', [])
                                        players2_str = ', '.join(players2) if players2 else 'Keine Spieler'
                                        st.write(f"**{team2_color} {game['team2']}:** {players2_str}")
                                        score2 = st.number_input(f"Tore {game['team2']}:", min_value=0, key=f"round_{round_data['round']}_field_{field_num}_score2")
                                    
                                    # Update scores
                                    if st.button(f"Ergebnis speichern - Runde {round_data['round']}, Feld {field_num}", key=f"round_{round_data['round']}_field_{field_num}_save"):
                                        game_index = round_data['games'].index(game)
                                        st.session_state.schedule[round_data['round']-1]['games'][game_index]['score1'] = str(score1)
                                        st.session_state.schedule[round_data['round']-1]['games'][game_index]['score2'] = str(score2)
                                        st.success("Ergebnis gespeichert!")
                                        st.rerun()
                    else:
                        # Einzelnes Spiel
                        game = games[0]
                        team1_color = get_team_color_icon(game['team1'])
                        team2_color = get_team_color_icon(game['team2'])
                        
                        with st.expander(f"Spiel: {team1_color} {game['team1']} vs {team2_color} {game['team2']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                players1 = game.get('players1', [])
                                players1_str = ', '.join(players1) if players1 else 'Keine Spieler'
                                st.write(f"**{team1_color} {game['team1']}:** {players1_str}")
                                score1 = st.number_input(f"Tore {game['team1']}:", min_value=0, key=f"round_{round_data['round']}_score1")
                            with col2:
                                players2 = game.get('players2', [])
                                players2_str = ', '.join(players2) if players2 else 'Keine Spieler'
                                st.write(f"**{team2_color} {game['team2']}:** {players2_str}")
                                score2 = st.number_input(f"Tore {game['team2']}:", min_value=0, key=f"round_{round_data['round']}_score2")
                            
                            # Update scores
                            if st.button(f"Ergebnis speichern - Runde {round_data['round']}", key=f"round_{round_data['round']}_save"):
                                game_index = round_data['games'].index(game)
                                st.session_state.schedule[round_data['round']-1]['games'][game_index]['score1'] = str(score1)
                                st.session_state.schedule[round_data['round']-1]['games'][game_index]['score2'] = str(score2)
                                st.success("Ergebnis gespeichert!")
                                st.rerun()
            else:
                # Alte Struktur (ein Spielfeld)
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
            # Prüfe ob Schedule in Runden mit sub_rounds strukturiert ist (mehrere Spielfelder)
            if st.session_state.schedule and isinstance(st.session_state.schedule[0], dict) and 'sub_rounds' in st.session_state.schedule[0]:
                # Neue Struktur mit sub_rounds (mehrere Spielfelder)
                for round_data in st.session_state.schedule:
                    st.subheader(f"🏟️ Runde {round_data['round']}")
                    
                    # Zeige Spiele korrekt auf Feldern verteilt
                    # Sammle alle Spiele aus allen sub_rounds
                    all_games = []
                    for sub_round in round_data['sub_rounds']:
                        for game in sub_round['games']:
                            all_games.append(game)
                    
                    # Verteile Spiele auf Felder: Spiel 1 -> Feld 1, Spiel 2 -> Feld 2, etc.
                    for i, game in enumerate(all_games, 1):
                        field_num = ((i - 1) % 2) + 1  # Feld 1, 2, 1, 2, ...
                        team1_display = ', '.join(game['team1']) if isinstance(game['team1'], list) else game['team1']
                        team2_display = ', '.join(game['team2']) if isinstance(game['team2'], list) else game['team2']
                        
                        # Zeige Feld-Überschrift nur beim ersten Spiel des Feldes
                        if i == 1 or (i > 1 and field_num != ((i - 2) % 2) + 1):
                            st.markdown(f"**Feld {field_num}:**")
                        
                        with st.expander(f"Spiel {i}: {team1_display} vs {team2_display}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Team 1:** {team1_display}")
                                    score1 = st.number_input(f"Tore Team 1:", min_value=0, key=f"rr_score1_{round_data['round']}_{field_num}_{i}")
                                with col2:
                                    st.write(f"**Team 2:** {team2_display}")
                                    score2 = st.number_input(f"Tore Team 2:", min_value=0, key=f"rr_score2_{round_data['round']}_{field_num}_{i}")
                                
                                # Update scores
                                if st.button(f"Ergebnis speichern - Runde {round_data['round']}, Feld {field_num}, Spiel {i}", key=f"rr_save_{round_data['round']}_{field_num}_{i}"):
                                    # Finde den korrekten Index
                                    round_idx = round_data['round'] - 1
                                    field_idx = field_num - 1
                                    st.session_state.schedule[round_idx]['sub_rounds'][field_idx]['games'][i-1]['score1'] = str(score1)
                                    st.session_state.schedule[round_idx]['sub_rounds'][field_idx]['games'][i-1]['score2'] = str(score2)
                                    st.success("Ergebnis gespeichert!")
                                    st.rerun()
            else:
                # Alte Struktur (ein Spielfeld) - prüfe ob Schedule die erwartete Struktur hat
                if st.session_state.schedule and isinstance(st.session_state.schedule[0], dict) and 'round' in st.session_state.schedule[0]:
                    for round_data in st.session_state.schedule:
                        st.subheader(f"Runde {round_data['round']}")
                        for i, game in enumerate(round_data['games'], 1):
                            team1_display = ', '.join(game['team1']) if isinstance(game['team1'], list) else game['team1']
                            team2_display = ', '.join(game['team2']) if isinstance(game['team2'], list) else game['team2']
                            
                            with st.expander(f"Spiel {i}: {team1_display} vs {team2_display}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Team 1:** {team1_display}")
                                    score1 = st.number_input(f"Tore Team 1:", min_value=0, key=f"rr_score1_{round_data['round']}_{i}")
                                with col2:
                                    st.write(f"**Team 2:** {team2_display}")
                                    score2 = st.number_input(f"Tore Team 2:", min_value=0, key=f"rr_score2_{round_data['round']}_{i}")
                                
                                # Update scores
                                if st.button(f"Ergebnis speichern - Runde {round_data['round']}, Spiel {i}", key=f"rr_save_{round_data['round']}_{i}"):
                                    st.session_state.schedule[round_data['round']-1]['games'][i-1]['score1'] = str(score1)
                                    st.session_state.schedule[round_data['round']-1]['games'][i-1]['score2'] = str(score2)
                                    st.success("Ergebnis gespeichert!")
                                    st.rerun()
                else:
                    st.warning("Kein gültiger Round Robin Spielplan gefunden. Bitte generieren Sie einen neuen Spielplan.")
        
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
                    st.session_state.team_colors,
                    st.session_state.num_fields
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