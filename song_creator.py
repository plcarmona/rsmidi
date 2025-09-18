#!/usr/bin/env python3
"""
Song Creator Utility for Synthesia Clone
Create custom songs in JSON format
"""

import json
import os

class SongCreator:
    """Utility to create songs for the Synthesia clone"""
    
    def __init__(self):
        self.notes = []
        self.note_map = {
            'C4': 60, 'C#4': 61, 'D4': 62, 'D#4': 63, 'E4': 64, 'F4': 65,
            'F#4': 66, 'G4': 67, 'G#4': 68, 'A4': 69, 'A#4': 70, 'B4': 71, 'C5': 72
        }
    
    def show_available_notes(self):
        """Display available notes"""
        print("Available notes:")
        for note_name, note_num in self.note_map.items():
            print(f"  {note_name} = {note_num}")
        print("")
    
    def add_note_interactive(self):
        """Add a note interactively"""
        print("Add a note:")
        
        # Get note
        while True:
            note_input = input("Note name (e.g., C4, E4, G4): ").strip().upper()
            if note_input in self.note_map:
                note_number = self.note_map[note_input]
                break
            elif note_input.isdigit() and 0 <= int(note_input) <= 127:
                note_number = int(note_input)
                break
            else:
                print("Invalid note. Use note names like C4, E4 or MIDI numbers 0-127")
        
        # Get start time
        while True:
            try:
                start_time = float(input("Start time (seconds): "))
                if start_time >= 0:
                    break
                else:
                    print("Start time must be non-negative")
            except ValueError:
                print("Please enter a valid number")
        
        # Get duration
        while True:
            try:
                duration = float(input("Duration (seconds, default 0.5): ") or "0.5")
                if duration > 0:
                    break
                else:
                    print("Duration must be positive")
            except ValueError:
                print("Please enter a valid number")
        
        # Get velocity (optional)
        while True:
            try:
                velocity_input = input("Velocity (0-127, default 80): ") or "80"
                velocity = int(velocity_input)
                if 0 <= velocity <= 127:
                    break
                else:
                    print("Velocity must be between 0 and 127")
            except ValueError:
                print("Please enter a valid number")
        
        # Add the note
        note_data = {
            'note': note_number,
            'start_time': start_time,
            'duration': duration,
            'velocity': velocity
        }
        self.notes.append(note_data)
        
        note_name = next((name for name, num in self.note_map.items() 
                         if num == note_number), f"Note{note_number}")
        print(f"Added: {note_name} at {start_time}s for {duration}s")
        print("")
    
    def show_current_song(self):
        """Display the current song"""
        if not self.notes:
            print("No notes added yet.")
            return
        
        print(f"Current song ({len(self.notes)} notes):")
        print("-" * 40)
        for i, note in enumerate(sorted(self.notes, key=lambda x: x['start_time']), 1):
            note_name = next((name for name, num in self.note_map.items() 
                             if num == note['note']), f"Note{note['note']}")
            print(f"{i:2d}. {note_name:<4} at {note['start_time']:5.1f}s "
                  f"for {note['duration']:4.1f}s (vel: {note['velocity']:3d})")
        print("")
    
    def remove_note(self):
        """Remove a note from the song"""
        if not self.notes:
            print("No notes to remove.")
            return
        
        self.show_current_song()
        try:
            index = int(input("Enter note number to remove (1-based): ")) - 1
            if 0 <= index < len(self.notes):
                removed = self.notes.pop(index)
                note_name = next((name for name, num in self.note_map.items() 
                                 if num == removed['note']), f"Note{removed['note']}")
                print(f"Removed: {note_name} at {removed['start_time']}s")
            else:
                print("Invalid note number.")
        except ValueError:
            print("Please enter a valid number.")
        print("")
    
    def save_song(self):
        """Save the song to a JSON file"""
        if not self.notes:
            print("No notes to save.")
            return
        
        title = input("Song title: ").strip() or "Untitled Song"
        filename = input("Filename (without .json): ").strip() or "custom_song"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        song_data = {
            'title': title,
            'notes': sorted(self.notes, key=lambda x: x['start_time'])
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(song_data, f, indent=2)
            print(f"Song saved as '{filename}'")
        except Exception as e:
            print(f"Error saving file: {e}")
        print("")
    
    def load_song(self):
        """Load a song from a JSON file"""
        filename = input("Filename to load: ").strip()
        
        try:
            with open(filename, 'r') as f:
                song_data = json.load(f)
            
            self.notes = song_data.get('notes', [])
            title = song_data.get('title', 'Unknown')
            print(f"Loaded '{title}' with {len(self.notes)} notes")
            
        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print(f"Error loading file: {e}")
        print("")
    
    def create_preset_songs(self):
        """Create some preset songs"""
        print("Choose a preset song:")
        print("1. Twinkle Twinkle Little Star")
        print("2. Happy Birthday (simplified)")
        print("3. Simple Scale (C-D-E-F-G-A-B-C)")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            # Twinkle Twinkle Little Star
            self.notes = [
                {"note": 60, "start_time": 0.0, "duration": 0.5, "velocity": 80},  # C
                {"note": 60, "start_time": 0.5, "duration": 0.5, "velocity": 80},  # C
                {"note": 67, "start_time": 1.0, "duration": 0.5, "velocity": 80},  # G
                {"note": 67, "start_time": 1.5, "duration": 0.5, "velocity": 80},  # G
                {"note": 69, "start_time": 2.0, "duration": 0.5, "velocity": 80},  # A
                {"note": 69, "start_time": 2.5, "duration": 0.5, "velocity": 80},  # A
                {"note": 67, "start_time": 3.0, "duration": 1.0, "velocity": 80},  # G
                {"note": 65, "start_time": 4.0, "duration": 0.5, "velocity": 80},  # F
                {"note": 65, "start_time": 4.5, "duration": 0.5, "velocity": 80},  # F
                {"note": 64, "start_time": 5.0, "duration": 0.5, "velocity": 80},  # E
                {"note": 64, "start_time": 5.5, "duration": 0.5, "velocity": 80},  # E
                {"note": 62, "start_time": 6.0, "duration": 0.5, "velocity": 80},  # D
                {"note": 62, "start_time": 6.5, "duration": 0.5, "velocity": 80},  # D
                {"note": 60, "start_time": 7.0, "duration": 1.0, "velocity": 80},  # C
            ]
            print("Loaded Twinkle Twinkle Little Star")
        
        elif choice == "2":
            # Happy Birthday (simplified)
            self.notes = [
                {"note": 60, "start_time": 0.0, "duration": 0.3, "velocity": 80},  # C
                {"note": 60, "start_time": 0.3, "duration": 0.3, "velocity": 80},  # C
                {"note": 62, "start_time": 0.6, "duration": 0.6, "velocity": 80},  # D
                {"note": 60, "start_time": 1.2, "duration": 0.6, "velocity": 80},  # C
                {"note": 65, "start_time": 1.8, "duration": 0.6, "velocity": 80},  # F
                {"note": 64, "start_time": 2.4, "duration": 1.2, "velocity": 80},  # E
            ]
            print("Loaded Happy Birthday (simplified)")
        
        elif choice == "3":
            # Simple scale
            notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C D E F G A B C
            self.notes = []
            for i, note in enumerate(notes):
                self.notes.append({
                    "note": note,
                    "start_time": i * 0.5,
                    "duration": 0.4,
                    "velocity": 80
                })
            print("Loaded Simple Scale")
        
        else:
            print("Invalid choice.")
        print("")
    
    def run(self):
        """Run the song creator"""
        print("=" * 50)
        print("SYNTHESIA CLONE - SONG CREATOR")
        print("=" * 50)
        print("Create custom songs for the piano learning game")
        print("")
        
        while True:
            print("Options:")
            print("1. Show available notes")
            print("2. Add note")
            print("3. Show current song")
            print("4. Remove note")
            print("5. Save song")
            print("6. Load song")
            print("7. Create preset song")
            print("8. Clear all notes")
            print("9. Exit")
            print("")
            
            choice = input("Enter choice (1-9): ").strip()
            
            if choice == "1":
                self.show_available_notes()
            elif choice == "2":
                self.add_note_interactive()
            elif choice == "3":
                self.show_current_song()
            elif choice == "4":
                self.remove_note()
            elif choice == "5":
                self.save_song()
            elif choice == "6":
                self.load_song()
            elif choice == "7":
                self.create_preset_songs()
            elif choice == "8":
                self.notes = []
                print("All notes cleared.")
                print("")
            elif choice == "9":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
                print("")

if __name__ == "__main__":
    creator = SongCreator()
    creator.run()