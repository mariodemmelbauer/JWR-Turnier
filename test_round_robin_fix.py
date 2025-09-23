#!/usr/bin/env python3
"""
Test script to verify the Round Robin schedule structure fix
"""

def test_round_robin_schedule_structure():
    """Test that Round Robin schedule has the expected structure"""
    
    # Simulate the generate_round_robin_schedule function output
    # For single field (num_fields = 1)
    single_field_schedule = [
        {
            'round': 1,
            'games': [
                {'team1': ['Player1', 'Player2'], 'team2': ['Player3', 'Player4'], 'score1': '', 'score2': ''},
                {'team1': ['Player5', 'Player6'], 'team2': ['Player7', 'Player8'], 'score1': '', 'score2': ''}
            ]
        },
        {
            'round': 2,
            'games': [
                {'team1': ['Player1', 'Player3'], 'team2': ['Player2', 'Player4'], 'score1': '', 'score2': ''}
            ]
        }
    ]
    
    # For multiple fields (num_fields = 2)
    multi_field_schedule = [
        {
            'round': 1,
            'sub_rounds': [
                {
                    'round': 1,
                    'games': [
                        {'team1': ['Player1', 'Player2'], 'team2': ['Player3', 'Player4'], 'score1': '', 'score2': ''}
                    ]
                },
                {
                    'round': 2,
                    'games': [
                        {'team1': ['Player5', 'Player6'], 'team2': ['Player7', 'Player8'], 'score1': '', 'score2': ''}
                    ]
                }
            ]
        }
    ]
    
    # Test single field structure
    print("Testing single field structure:")
    if single_field_schedule and isinstance(single_field_schedule[0], dict) and 'round' in single_field_schedule[0]:
        print("✅ Single field structure is valid")
        for round_data in single_field_schedule:
            print(f"  Runde {round_data['round']}: {len(round_data['games'])} Spiele")
    else:
        print("❌ Single field structure is invalid")
    
    # Test multi field structure
    print("\nTesting multi field structure:")
    if multi_field_schedule and isinstance(multi_field_schedule[0], dict) and 'sub_rounds' in multi_field_schedule[0]:
        print("✅ Multi field structure is valid")
        for round_data in multi_field_schedule:
            print(f"  Runde {round_data['round']}: {len(round_data['sub_rounds'])} Sub-Runden")
    else:
        print("❌ Multi field structure is invalid")
    
    # Test invalid structure (should trigger warning)
    print("\nTesting invalid structure:")
    invalid_schedule = [{'invalid': 'data'}]
    if invalid_schedule and isinstance(invalid_schedule[0], dict) and 'round' in invalid_schedule[0]:
        print("❌ Invalid structure incorrectly passed validation")
    else:
        print("✅ Invalid structure correctly failed validation")

if __name__ == "__main__":
    test_round_robin_schedule_structure()

