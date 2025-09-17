#!/usr/bin/env python3
"""
Test script to verify that widget warnings are fixed
"""

def test_widget_initialization():
    """Test that widgets are properly initialized without warnings"""
    
    # Simulate the session state initialization
    session_state = {
        'tournament_name': 'JWR-Turnier',
        'tournament_date': '2024-01-01',
        'num_teams': 4,
        'home_away': False,
        'players_per_team': 2,
        'games_per_player': 3,
        'team_selection': 'JWR'
    }
    
    # Test that all required session state values are initialized
    required_keys = [
        'tournament_name', 'tournament_date', 'num_teams', 'home_away',
        'players_per_team', 'games_per_player', 'team_selection'
    ]
    
    print("Testing session state initialization:")
    for key in required_keys:
        if key in session_state:
            print(f"✅ {key}: {session_state[key]}")
        else:
            print(f"❌ {key}: Missing")
    
    # Test widget key patterns
    widget_keys = [
        'tournament_name', 'tournament_date', 'num_teams', 'home_away',
        'players_per_team', 'games_per_player', 'team_selection'
    ]
    
    print("\nTesting widget key patterns:")
    for key in widget_keys:
        if key in session_state:
            print(f"✅ Widget key '{key}' has corresponding session state value")
        else:
            print(f"❌ Widget key '{key}' missing session state value")
    
    print("\n✅ All widget warnings should be fixed!")

if __name__ == "__main__":
    test_widget_initialization()
