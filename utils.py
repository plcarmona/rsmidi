#!/usr/bin/env python3
"""
Utilities for Synthesia Clone
Various helper scripts and tools
"""

import json
import os
import sys

def create_twinkle_twinkle():
    """Create Twinkle Twinkle Little Star song"""
    song_data = {
        "title": "Twinkle Twinkle Little Star",
        "notes": [
            {"note": 60, "start_time": 0.0, "duration": 0.5, "velocity": 80},  # C-C
            {"note": 60, "start_time": 0.5, "duration": 0.5, "velocity": 80},
            {"note": 67, "start_time": 1.0, "duration": 0.5, "velocity": 80},  # G-G
            {"note": 67, "start_time": 1.5, "duration": 0.5, "velocity": 80},
            {"note": 69, "start_time": 2.0, "duration": 0.5, "velocity": 80},  # A-A
            {"note": 69, "start_time": 2.5, "duration": 0.5, "velocity": 80},
            {"note": 67, "start_time": 3.0, "duration": 1.0, "velocity": 80},  # G
            {"note": 65, "start_time": 4.0, "duration": 0.5, "velocity": 80},  # F-F
            {"note": 65, "start_time": 4.5, "duration": 0.5, "velocity": 80},
            {"note": 64, "start_time": 5.0, "duration": 0.5, "velocity": 80},  # E-E
            {"note": 64, "start_time": 5.5, "duration": 0.5, "velocity": 80},
            {"note": 62, "start_time": 6.0, "duration": 0.5, "velocity": 80},  # D-D
            {"note": 62, "start_time": 6.5, "duration": 0.5, "velocity": 80},
            {"note": 60, "start_time": 7.0, "duration": 1.0, "velocity": 80},  # C
        ]
    }
    
    with open('twinkle_twinkle.json', 'w') as f:
        json.dump(song_data, f, indent=2)
    print("Created twinkle_twinkle.json")

def create_scale_song():
    """Create a simple C major scale song"""
    notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C D E F G A B C
    song_data = {
        "title": "C Major Scale",
        "notes": []
    }
    
    for i, note in enumerate(notes):
        song_data["notes"].append({
            "note": note,
            "start_time": i * 0.5,
            "duration": 0.4,
            "velocity": 80
        })
    
    with open('c_major_scale.json', 'w') as f:
        json.dump(song_data, f, indent=2)
    print("Created c_major_scale.json")

def create_chord_progression():
    """Create a simple chord progression"""
    song_data = {
        "title": "Simple Chord Progression (C-Am-F-G)",
        "notes": [
            # C major chord (C-E-G)
            {"note": 60, "start_time": 0.0, "duration": 2.0, "velocity": 80},
            {"note": 64, "start_time": 0.0, "duration": 2.0, "velocity": 80},
            {"note": 67, "start_time": 0.0, "duration": 2.0, "velocity": 80},
            
            # A minor chord (A-C-E)
            {"note": 57, "start_time": 2.0, "duration": 2.0, "velocity": 80},
            {"note": 60, "start_time": 2.0, "duration": 2.0, "velocity": 80},
            {"note": 64, "start_time": 2.0, "duration": 2.0, "velocity": 80},
            
            # F major chord (F-A-C)
            {"note": 53, "start_time": 4.0, "duration": 2.0, "velocity": 80},
            {"note": 57, "start_time": 4.0, "duration": 2.0, "velocity": 80},
            {"note": 60, "start_time": 4.0, "duration": 2.0, "velocity": 80},
            
            # G major chord (G-B-D)
            {"note": 55, "start_time": 6.0, "duration": 2.0, "velocity": 80},
            {"note": 59, "start_time": 6.0, "duration": 2.0, "velocity": 80},
            {"note": 62, "start_time": 6.0, "duration": 2.0, "velocity": 80},
        ]
    }
    
    with open('chord_progression.json', 'w') as f:
        json.dump(song_data, f, indent=2)
    print("Created chord_progression.json")

def validate_song(filename):
    """Validate a song file"""
    try:
        with open(filename, 'r') as f:
            song_data = json.load(f)
        
        print(f"Validating {filename}...")
        
        # Check structure
        if 'notes' not in song_data:
            print("❌ Error: Missing 'notes' field")
            return False
        
        if not isinstance(song_data['notes'], list):
            print("❌ Error: 'notes' must be a list")
            return False
        
        # Check each note
        for i, note in enumerate(song_data['notes']):
            if not isinstance(note, dict):
                print(f"❌ Error: Note {i+1} must be a dictionary")
                return False
            
            required_fields = ['note', 'start_time']
            for field in required_fields:
                if field not in note:
                    print(f"❌ Error: Note {i+1} missing '{field}' field")
                    return False
            
            # Validate ranges
            if not (0 <= note['note'] <= 127):
                print(f"❌ Error: Note {i+1} has invalid MIDI note: {note['note']}")
                return False
            
            if note['start_time'] < 0:
                print(f"❌ Error: Note {i+1} has negative start_time: {note['start_time']}")
                return False
        
        title = song_data.get('title', 'Unknown')
        note_count = len(song_data['notes'])
        duration = max(n['start_time'] + n.get('duration', 0.5) for n in song_data['notes']) if song_data['notes'] else 0
        
        print("✅ Song is valid!")
        print(f"   Title: {title}")
        print(f"   Notes: {note_count}")
        print(f"   Duration: {duration:.1f} seconds")
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in '{filename}': {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def list_songs():
    """List all song files in current directory"""
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    if not json_files:
        print("No song files (.json) found in current directory")
        return
    
    print("Available song files:")
    for filename in sorted(json_files):
        try:
            with open(filename, 'r') as f:
                song_data = json.load(f)
            title = song_data.get('title', 'Unknown')
            note_count = len(song_data.get('notes', []))
            print(f"  {filename:<25} - {title} ({note_count} notes)")
        except:
            print(f"  {filename:<25} - (Invalid or corrupted)")

def show_help():
    """Show help information"""
    print("Synthesia Clone Utilities")
    print("=" * 50)
    print("Usage: python utils.py <command>")
    print("")
    print("Commands:")
    print("  create-samples    Create sample song files")
    print("  validate <file>   Validate a song file")
    print("  list-songs       List all song files")
    print("  help             Show this help")
    print("")
    print("Song File Format:")
    print("  JSON files with 'title' and 'notes' fields")
    print("  Each note needs: 'note' (MIDI), 'start_time' (seconds)")
    print("  Optional: 'duration' (seconds), 'velocity' (0-127)")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'create-samples':
        create_twinkle_twinkle()
        create_scale_song()
        create_chord_progression()
        print("\nSample songs created! Try:")
        print("- twinkle_twinkle.json")
        print("- c_major_scale.json") 
        print("- chord_progression.json")
        
    elif command == 'validate':
        if len(sys.argv) < 3:
            print("Usage: python utils.py validate <filename>")
            return
        validate_song(sys.argv[2])
        
    elif command == 'list-songs':
        list_songs()
        
    elif command == 'help':
        show_help()
        
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()