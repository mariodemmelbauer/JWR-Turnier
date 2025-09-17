#!/usr/bin/env python3
"""
Test-Script für die optimierte Spielplan-Generierung
Demonstriert die Funktionalität für 5 Teams mit 4 Spielern auf 2 Spielfeldern
"""

def generate_optimized_5_teams_schedule(teams_with_players, home_away=False):
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

def test_schedule():
    """Testet die Spielplan-Generierung mit Beispiel-Daten"""
    
    # Beispiel-Teams mit je 4 Spielern
    teams = {
        "Team A": ["Spieler A1", "Spieler A2", "Spieler A3", "Spieler A4"],
        "Team B": ["Spieler B1", "Spieler B2", "Spieler B3", "Spieler B4"],
        "Team C": ["Spieler C1", "Spieler C2", "Spieler C3", "Spieler C4"],
        "Team D": ["Spieler D1", "Spieler D2", "Spieler D3", "Spieler D4"],
        "Team E": ["Spieler E1", "Spieler E2", "Spieler E3", "Spieler E4"]
    }
    
    print("🏆 SPIELPLAN FÜR 5 TEAMS MIT 4 SPIELERN AUF 2 SPIELFELDERN")
    print("=" * 60)
    print()
    
    # Teste Hinrunde
    print("📅 HINRUNDE (nur Hinrunde):")
    print("-" * 30)
    schedule_hinrunde = generate_optimized_5_teams_schedule(teams, home_away=False)
    
    for round_data in schedule_hinrunde:
        print(f"\n🏟️ {round_data['round']}")
        if 'resting_teams' in round_data:
            print(f"⏸️ Pausierende Teams: {', '.join(round_data['resting_teams'])}")
        
        for i, game in enumerate(round_data['games'], 1):
            print(f"   Feld {i}: {game['team1']} vs {game['team2']}")
            print(f"           {', '.join(game['players1'])}")
            print(f"           vs")
            print(f"           {', '.join(game['players2'])}")
    
    print("\n" + "=" * 60)
    print("📊 STATISTIKEN HINRUNDE:")
    print(f"   • Anzahl Runden: {len(schedule_hinrunde)}")
    print(f"   • Spiele pro Runde: 2")
    print(f"   • Gesamt Spiele: {sum(len(round_data['games']) for round_data in schedule_hinrunde)}")
    print(f"   • Jedes Team spielt: 4 Spiele")
    print(f"   • Jedes Team pausiert: 1 Runde")
    
    # Teste Hin- und Rückrunde
    print("\n" + "=" * 60)
    print("📅 HIN- UND RÜCKRUNDE:")
    print("-" * 30)
    schedule_beide = generate_optimized_5_teams_schedule(teams, home_away=True)
    
    for round_data in schedule_beide:
        print(f"\n🏟️ {round_data['round']}")
        if 'resting_teams' in round_data:
            print(f"⏸️ Pausierende Teams: {', '.join(round_data['resting_teams'])}")
        
        for i, game in enumerate(round_data['games'], 1):
            print(f"   Feld {i}: {game['team1']} vs {game['team2']}")
    
    print("\n" + "=" * 60)
    print("📊 STATISTIKEN HIN- UND RÜCKRUNDE:")
    print(f"   • Anzahl Runden: {len(schedule_beide)}")
    print(f"   • Spiele pro Runde: 2")
    print(f"   • Gesamt Spiele: {sum(len(round_data['games']) for round_data in schedule_beide)}")
    print(f"   • Jedes Team spielt: 8 Spiele")
    print(f"   • Jedes Team pausiert: 2 Runden")
    
    # Überprüfe, ob alle Paarungen vorkommen
    print("\n" + "=" * 60)
    print("✅ ÜBERPRÜFUNG DER PAARUNGEN:")
    print("-" * 30)
    
    all_games = []
    for round_data in schedule_beide:
        for game in round_data['games']:
            # Normalisiere Paarung (alphabetisch sortiert)
            pair = tuple(sorted([game['team1'], game['team2']]))
            all_games.append(pair)
    
    # Erwartete Paarungen für 5 Teams
    expected_pairs = set()
    team_names = list(teams.keys())
    for i in range(len(team_names)):
        for j in range(i + 1, len(team_names)):
            expected_pairs.add(tuple(sorted([team_names[i], team_names[j]])))
    
    actual_pairs = set(all_games)
    
    print(f"   • Erwartete Paarungen: {len(expected_pairs)}")
    print(f"   • Tatsächliche Paarungen: {len(actual_pairs)}")
    print(f"   • Fehlende Paarungen: {expected_pairs - actual_pairs}")
    print(f"   • Zusätzliche Paarungen: {actual_pairs - expected_pairs}")
    
    if expected_pairs == actual_pairs:
        print("   ✅ Alle Paarungen sind korrekt!")
    else:
        print("   ❌ Es fehlen oder gibt zu viele Paarungen!")
    
    print("\n" + "=" * 60)
    print("🎯 OPTIMIERUNGEN:")
    print("   • Jede Runde nutzt beide Spielfelder optimal")
    print("   • Nur ein Team pausiert pro Runde")
    print("   • Gleichmäßige Verteilung der Pausen")
    print("   • Minimale Gesamtspielzeit")
    print("   • Fairer Spielplan für alle Teams")

if __name__ == "__main__":
    test_schedule()
