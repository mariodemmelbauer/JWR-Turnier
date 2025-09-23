#!/usr/bin/env python3
"""
Test-Script für die optimierte Spielplan-Generierung für 4 Teams
Demonstriert die Funktionalität für 4 Teams mit 5 Spielern auf 2 Spielfeldern
"""

def generate_optimized_4_teams_schedule(teams_with_players, home_away=False):
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

def test_4_teams_schedule():
    """Testet die Spielplan-Generierung für 4 Teams mit Beispiel-Daten"""
    
    # Beispiel-Teams mit je 5 Spielern
    teams = {
        "Team A": ["Spieler A1", "Spieler A2", "Spieler A3", "Spieler A4", "Spieler A5"],
        "Team B": ["Spieler B1", "Spieler B2", "Spieler B3", "Spieler B4", "Spieler B5"],
        "Team C": ["Spieler C1", "Spieler C2", "Spieler C3", "Spieler C4", "Spieler C5"],
        "Team D": ["Spieler D1", "Spieler D2", "Spieler D3", "Spieler D4", "Spieler D5"]
    }
    
    print("🏆 SPIELPLAN FÜR 4 TEAMS MIT 5 SPIELERN AUF 2 SPIELFELDERN")
    print("=" * 60)
    print()
    
    # Teste Hinrunde
    print("📅 HINRUNDE (nur Hinrunde):")
    print("-" * 30)
    schedule_hinrunde = generate_optimized_4_teams_schedule(teams, home_away=False)
    
    for round_data in schedule_hinrunde:
        print(f"\n🏟️ {round_data['round']}")
        if 'resting_teams' in round_data and round_data['resting_teams']:
            print(f"⏸️ Pausierende Teams: {', '.join(round_data['resting_teams'])}")
        else:
            print("✅ Alle Teams spielen gleichzeitig - optimale Feldnutzung!")
        
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
    print(f"   • Jedes Team spielt: 3 Spiele")
    print(f"   • Pausierende Teams: 0 (alle spielen gleichzeitig)")
    
    # Teste Hin- und Rückrunde
    print("\n" + "=" * 60)
    print("📅 HIN- UND RÜCKRUNDE:")
    print("-" * 30)
    schedule_beide = generate_optimized_4_teams_schedule(teams, home_away=True)
    
    for round_data in schedule_beide:
        print(f"\n🏟️ {round_data['round']}")
        if 'resting_teams' in round_data and round_data['resting_teams']:
            print(f"⏸️ Pausierende Teams: {', '.join(round_data['resting_teams'])}")
        else:
            print("✅ Alle Teams spielen gleichzeitig - optimale Feldnutzung!")
        
        for i, game in enumerate(round_data['games'], 1):
            print(f"   Feld {i}: {game['team1']} vs {game['team2']}")
    
    print("\n" + "=" * 60)
    print("📊 STATISTIKEN HIN- UND RÜCKRUNDE:")
    print(f"   • Anzahl Runden: {len(schedule_beide)}")
    print(f"   • Spiele pro Runde: 2")
    print(f"   • Gesamt Spiele: {sum(len(round_data['games']) for round_data in schedule_beide)}")
    print(f"   • Jedes Team spielt: 6 Spiele")
    print(f"   • Pausierende Teams: 0 (alle spielen gleichzeitig)")
    
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
    
    # Erwartete Paarungen für 4 Teams
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
    print("🎯 OPTIMIERUNGEN FÜR 4 TEAMS:")
    print("   • Alle Teams spielen gleichzeitig - keine Pausen nötig")
    print("   • Beide Spielfelder werden optimal genutzt")
    print("   • Minimale Gesamtspielzeit (nur 3 Runden für Hinrunde)")
    print("   • Perfekte Balance - jedes Team spielt gleich oft")
    print("   • Einfache Organisation - keine Wartezeiten")
    
    print("\n" + "=" * 60)
    print("📈 VERGLEICH 4 vs 5 TEAMS:")
    print("   • 4 Teams: 3 Runden, 6 Spiele (Hinrunde)")
    print("   • 5 Teams: 5 Runden, 10 Spiele (Hinrunde)")
    print("   • 4 Teams: Keine Pausen nötig")
    print("   • 5 Teams: Ein Team pausiert pro Runde")
    print("   • 4 Teams: Optimale Feldnutzung (100%)")
    print("   • 5 Teams: Gute Feldnutzung (80%)")

if __name__ == "__main__":
    test_4_teams_schedule()

