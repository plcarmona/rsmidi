#!/usr/bin/env python3
"""
Enhanced Song Creator for MIDI Editor
Create songs with multiple tracks and advanced features
"""

import json
import os
import sys
from typing import List, Dict

class EnhancedSongCreator:
    """Enhanced song creator with multi-track support"""
    
    def __init__(self):
        self.project = {
            'title': 'Untitled Project',
            'tempo': 120,
            'time_signature': [4, 4],
            'tracks': []
        }
        self.current_track_index = 0
        
        # Extended note mapping
        self.note_map = self.create_note_map()
    
    def create_note_map(self) -> Dict[str, int]:
        """Create comprehensive note name to MIDI number mapping"""
        note_map = {}
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        for octave in range(-1, 10):  # C-1 to G9 (MIDI range)
            for i, note in enumerate(notes):
                midi_num = (octave + 1) * 12 + i
                if 0 <= midi_num <= 127:
                    note_map[f"{note}{octave}"] = midi_num
                    # Add flat equivalents
                    if '#' in note:
                        flat_note = notes[(i + 1) % 12] + 'b'
                        note_map[f"{flat_note}{octave}"] = midi_num
        
        return note_map
    
    def run(self):
        """Run the enhanced song creator"""
        print("🎵 Enhanced MIDI Song Creator 🎵")
        print("=" * 50)
        print("Create multi-track MIDI projects")
        print()
        
        while True:
            self.show_menu()
            choice = input("Enter choice: ").strip()
            
            try:
                if choice == "0":
                    break
                elif choice == "1":
                    self.project_info()
                elif choice == "2":
                    self.edit_project_settings()
                elif choice == "3":
                    self.list_tracks()
                elif choice == "4":
                    self.add_track()
                elif choice == "5":
                    self.select_track()
                elif choice == "6":
                    self.edit_track()
                elif choice == "7":
                    self.delete_track()
                elif choice == "8":
                    self.add_note()
                elif choice == "9":
                    self.list_notes()
                elif choice == "10":
                    self.delete_note()
                elif choice == "11":
                    self.quantize_track()
                elif choice == "12":
                    self.transpose_track()
                elif choice == "13":
                    self.load_project()
                elif choice == "14":
                    self.save_project()
                elif choice == "15":
                    self.export_midi()
                elif choice == "16":
                    self.create_templates()
                elif choice == "17":
                    self.batch_add_notes()
                else:
                    print("Invalid choice")
            except Exception as e:
                print(f"Error: {str(e)}")
                print()
    
    def show_menu(self):
        """Display main menu"""
        print("Menu:")
        print("1.  Project info")
        print("2.  Edit project settings")
        print("3.  List tracks")
        print("4.  Add track")
        print("5.  Select track")
        print("6.  Edit track properties")
        print("7.  Delete track")
        print("8.  Add note to current track")
        print("9.  List notes in current track")
        print("10. Delete note")
        print("11. Quantize current track")
        print("12. Transpose current track")
        print("13. Load project")
        print("14. Save project")
        print("15. Export MIDI")
        print("16. Create template songs")
        print("17. Batch add notes (scale/chord)")
        print("0.  Exit")
        print()
    
    def project_info(self):
        """Show project information"""
        print(f"\nProject: {self.project['title']}")
        print(f"Tempo: {self.project['tempo']} BPM")
        print(f"Time Signature: {self.project['time_signature'][0]}/{self.project['time_signature'][1]}")
        print(f"Tracks: {len(self.project['tracks'])}")
        
        total_notes = sum(len(track['notes']) for track in self.project['tracks'])
        print(f"Total Notes: {total_notes}")
        
        if self.project['tracks']:
            print(f"Current Track: {self.project['tracks'][self.current_track_index]['name']}")
        print()
    
    def edit_project_settings(self):
        """Edit project settings"""
        print("Edit Project Settings:")
        
        # Title
        title = input(f"Title [{self.project['title']}]: ").strip()
        if title:
            self.project['title'] = title
        
        # Tempo
        tempo_str = input(f"Tempo [{self.project['tempo']}]: ").strip()
        if tempo_str:
            try:
                tempo = int(tempo_str)
                if 60 <= tempo <= 200:
                    self.project['tempo'] = tempo
                else:
                    print("Tempo must be between 60 and 200")
            except ValueError:
                print("Invalid tempo")
        
        # Time signature
        ts_str = input(f"Time Signature [{self.project['time_signature'][0]}/{self.project['time_signature'][1]}]: ").strip()
        if ts_str and '/' in ts_str:
            try:
                parts = ts_str.split('/')
                num, den = int(parts[0]), int(parts[1])
                if num > 0 and den in [2, 4, 8, 16]:
                    self.project['time_signature'] = [num, den]
                else:
                    print("Invalid time signature")
            except ValueError:
                print("Invalid time signature format")
        print()
    
    def list_tracks(self):
        """List all tracks"""
        print("Tracks:")
        if not self.project['tracks']:
            print("  No tracks")
        else:
            for i, track in enumerate(self.project['tracks']):
                marker = "* " if i == self.current_track_index else "  "
                print(f"{marker}{i+1}. {track['name']} ({len(track['notes'])} notes, "
                      f"inst: {track['instrument']}, vol: {track['volume']})")
        print()
    
    def add_track(self):
        """Add new track"""
        name = input("Track name: ").strip() or f"Track {len(self.project['tracks']) + 1}"
        
        # Get instrument
        print("Common instruments: 0=Piano, 24=Guitar, 32=Bass, 40=Violin, 56=Trumpet")
        inst_str = input("Instrument (0-127) [0]: ").strip()
        instrument = 0
        if inst_str:
            try:
                instrument = max(0, min(127, int(inst_str)))
            except ValueError:
                pass
        
        track = {
            'name': name,
            'instrument': instrument,
            'volume': 100,
            'pan': 64,
            'notes': []
        }
        
        self.project['tracks'].append(track)
        self.current_track_index = len(self.project['tracks']) - 1
        print(f"Added track: {name}")
        print()
    
    def select_track(self):
        """Select current track"""
        if not self.project['tracks']:
            print("No tracks available")
            return
        
        self.list_tracks()
        try:
            index = int(input("Select track number: ")) - 1
            if 0 <= index < len(self.project['tracks']):
                self.current_track_index = index
                track = self.project['tracks'][index]
                print(f"Selected: {track['name']}")
            else:
                print("Invalid track number")
        except ValueError:
            print("Please enter a valid number")
        print()
    
    def edit_track(self):
        """Edit track properties"""
        if not self.project['tracks']:
            print("No tracks available")
            return
        
        track = self.project['tracks'][self.current_track_index]
        print(f"Editing track: {track['name']}")
        
        # Name
        name = input(f"Name [{track['name']}]: ").strip()
        if name:
            track['name'] = name
        
        # Instrument
        inst_str = input(f"Instrument [{track['instrument']}]: ").strip()
        if inst_str:
            try:
                track['instrument'] = max(0, min(127, int(inst_str)))
            except ValueError:
                print("Invalid instrument number")
        
        # Volume
        vol_str = input(f"Volume [{track['volume']}]: ").strip()
        if vol_str:
            try:
                track['volume'] = max(0, min(127, int(vol_str)))
            except ValueError:
                print("Invalid volume")
        print()
    
    def delete_track(self):
        """Delete track"""
        if not self.project['tracks']:
            print("No tracks available")
            return
        
        track = self.project['tracks'][self.current_track_index]
        confirm = input(f"Delete track '{track['name']}'? (y/n): ").lower()
        if confirm == 'y':
            self.project['tracks'].pop(self.current_track_index)
            if self.current_track_index >= len(self.project['tracks']):
                self.current_track_index = max(0, len(self.project['tracks']) - 1)
            print("Track deleted")
        print()
    
    def add_note(self):
        """Add note to current track"""
        if not self.project['tracks']:
            print("No tracks available. Create a track first.")
            return
        
        track = self.project['tracks'][self.current_track_index]
        print(f"Adding note to: {track['name']}")
        
        # Note
        note_input = input("Note (C4, 60, etc.): ").strip().upper()
        if note_input.isdigit():
            note_num = int(note_input)
        elif note_input in self.note_map:
            note_num = self.note_map[note_input]
        else:
            print("Invalid note format")
            return
        
        if not (0 <= note_num <= 127):
            print("Note must be between 0 and 127")
            return
        
        # Timing
        start_time = float(input("Start time (seconds): ") or "0")
        duration = float(input("Duration (seconds): ") or "0.5")
        velocity = int(input("Velocity (1-127): ") or "80")
        
        note = {
            'note': note_num,
            'start_time': start_time,
            'duration': duration,
            'velocity': max(1, min(127, velocity)),
            'channel': 0
        }
        
        track['notes'].append(note)
        track['notes'].sort(key=lambda n: n['start_time'])
        
        note_name = self.midi_to_note_name(note_num)
        print(f"Added: {note_name} at {start_time}s for {duration}s")
        print()
    
    def list_notes(self):
        """List notes in current track"""
        if not self.project['tracks']:
            print("No tracks available")
            return
        
        track = self.project['tracks'][self.current_track_index]
        print(f"\nNotes in {track['name']}:")
        
        if not track['notes']:
            print("  No notes")
        else:
            for i, note in enumerate(track['notes']):
                note_name = self.midi_to_note_name(note['note'])
                print(f"  {i+1:2d}. {note_name:4s} | {note['start_time']:6.2f}s | "
                      f"{note['duration']:5.2f}s | vel {note['velocity']:3d}")
        print()
    
    def delete_note(self):
        """Delete note from current track"""
        if not self.project['tracks']:
            print("No tracks available")
            return
        
        track = self.project['tracks'][self.current_track_index]
        if not track['notes']:
            print("No notes in current track")
            return
        
        self.list_notes()
        try:
            index = int(input("Note number to delete: ")) - 1
            if 0 <= index < len(track['notes']):
                deleted = track['notes'].pop(index)
                note_name = self.midi_to_note_name(deleted['note'])
                print(f"Deleted: {note_name}")
            else:
                print("Invalid note number")
        except ValueError:
            print("Please enter a valid number")
        print()
    
    def quantize_track(self):
        """Quantize current track"""
        if not self.project['tracks']:
            print("No tracks available")
            return
        
        track = self.project['tracks'][self.current_track_index]
        if not track['notes']:
            print("No notes to quantize")
            return
        
        print("Grid sizes: 1.0=quarter, 0.5=eighth, 0.25=sixteenth, 0.125=32nd")
        try:
            grid = float(input("Grid size: ") or "0.25")
            for note in track['notes']:
                note['start_time'] = round(note['start_time'] / grid) * grid
            print(f"Quantized {len(track['notes'])} notes to {grid} beat grid")
        except ValueError:
            print("Please enter a valid number")
        print()
    
    def transpose_track(self):
        """Transpose current track"""
        if not self.project['tracks']:
            print("No tracks available")
            return
        
        track = self.project['tracks'][self.current_track_index]
        if not track['notes']:
            print("No notes to transpose")
            return
        
        try:
            semitones = int(input("Transpose by semitones (+/-): ") or "0")
            transposed = 0
            for note in track['notes']:
                new_note = note['note'] + semitones
                if 0 <= new_note <= 127:
                    note['note'] = new_note
                    transposed += 1
            print(f"Transposed {transposed} notes by {semitones} semitones")
        except ValueError:
            print("Please enter a valid number")
        print()
    
    def load_project(self):
        """Load project from file"""
        file_path = input("File path: ").strip()
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle both old and new formats
            if 'notes' in data:
                # Convert old format
                self.project = {
                    'title': data.get('title', 'Imported Song'),
                    'tempo': 120,
                    'time_signature': [4, 4],
                    'tracks': [{
                        'name': 'Main Track',
                        'instrument': 0,
                        'volume': 100,
                        'pan': 64,
                        'notes': data['notes']
                    }]
                }
            else:
                self.project = data
            
            self.current_track_index = 0
            print(f"Loaded: {file_path}")
        except Exception as e:
            print(f"Error loading file: {str(e)}")
        print()
    
    def save_project(self):
        """Save project to file"""
        file_path = input("Save as (JSON file): ").strip()
        if not file_path:
            return
        
        if not file_path.endswith('.json'):
            file_path += '.json'
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.project, f, indent=2)
            print(f"Saved: {file_path}")
        except Exception as e:
            print(f"Error saving file: {str(e)}")
        print()
    
    def export_midi(self):
        """Export to MIDI file (placeholder)"""
        print("MIDI export requires the full MIDI editor.")
        print("Save as JSON and open in the MIDI editor, then export to MIDI.")
        print()
    
    def create_templates(self):
        """Create template songs"""
        print("Template Songs:")
        print("1. C Major Scale")
        print("2. Chord Progression (C-Am-F-G)")
        print("3. Chromatic Scale")
        print("4. Blues Scale")
        print("5. Simple Melody")
        
        choice = input("Select template (1-5): ").strip()
        
        if choice == "1":
            self.create_c_major_scale()
        elif choice == "2":
            self.create_chord_progression()
        elif choice == "3":
            self.create_chromatic_scale()
        elif choice == "4":
            self.create_blues_scale()
        elif choice == "5":
            self.create_simple_melody()
        else:
            print("Invalid choice")
        print()
    
    def create_c_major_scale(self):
        """Create C major scale"""
        if not self.project['tracks']:
            self.add_track_simple("C Major Scale")
        
        track = self.project['tracks'][self.current_track_index]
        notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C4 to C5
        
        for i, note in enumerate(notes):
            track['notes'].append({
                'note': note,
                'start_time': i * 0.5,
                'duration': 0.4,
                'velocity': 80,
                'channel': 0
            })
        
        print("Added C major scale")
    
    def create_chord_progression(self):
        """Create chord progression"""
        if not self.project['tracks']:
            self.add_track_simple("Chord Progression")
        
        track = self.project['tracks'][self.current_track_index]
        
        # C major chord
        for note in [60, 64, 67]:  # C-E-G
            track['notes'].append({
                'note': note,
                'start_time': 0.0,
                'duration': 1.0,
                'velocity': 80,
                'channel': 0
            })
        
        # A minor chord
        for note in [57, 60, 64]:  # A-C-E
            track['notes'].append({
                'note': note,
                'start_time': 1.0,
                'duration': 1.0,
                'velocity': 80,
                'channel': 0
            })
        
        # F major chord
        for note in [53, 57, 60]:  # F-A-C
            track['notes'].append({
                'note': note,
                'start_time': 2.0,
                'duration': 1.0,
                'velocity': 80,
                'channel': 0
            })
        
        # G major chord
        for note in [55, 59, 62]:  # G-B-D
            track['notes'].append({
                'note': note,
                'start_time': 3.0,
                'duration': 1.0,
                'velocity': 80,
                'channel': 0
            })
        
        print("Added chord progression (C-Am-F-G)")
    
    def create_chromatic_scale(self):
        """Create chromatic scale"""
        if not self.project['tracks']:
            self.add_track_simple("Chromatic Scale")
        
        track = self.project['tracks'][self.current_track_index]
        
        for i in range(13):  # C4 to C5 chromatically
            track['notes'].append({
                'note': 60 + i,
                'start_time': i * 0.25,
                'duration': 0.2,
                'velocity': 80,
                'channel': 0
            })
        
        print("Added chromatic scale")
    
    def create_blues_scale(self):
        """Create blues scale"""
        if not self.project['tracks']:
            self.add_track_simple("Blues Scale")
        
        track = self.project['tracks'][self.current_track_index]
        notes = [60, 63, 65, 66, 67, 70, 72]  # C blues scale
        
        for i, note in enumerate(notes):
            track['notes'].append({
                'note': note,
                'start_time': i * 0.5,
                'duration': 0.4,
                'velocity': 85,
                'channel': 0
            })
        
        print("Added blues scale")
    
    def create_simple_melody(self):
        """Create simple melody"""
        if not self.project['tracks']:
            self.add_track_simple("Simple Melody")
        
        track = self.project['tracks'][self.current_track_index]
        
        # Twinkle Twinkle Little Star
        notes_and_times = [
            (60, 0.0), (60, 0.5), (67, 1.0), (67, 1.5),
            (69, 2.0), (69, 2.5), (67, 3.0),
            (65, 4.0), (65, 4.5), (64, 5.0), (64, 5.5),
            (62, 6.0), (62, 6.5), (60, 7.0)
        ]
        
        for note, time in notes_and_times:
            track['notes'].append({
                'note': note,
                'start_time': time,
                'duration': 0.4,
                'velocity': 80,
                'channel': 0
            })
        
        print("Added simple melody (Twinkle Twinkle)")
    
    def batch_add_notes(self):
        """Batch add notes (scales, chords, etc.)"""
        print("Batch Add:")
        print("1. Scale from root note")
        print("2. Chord from root note")
        print("3. Arpeggio from root note")
        
        choice = input("Select type (1-3): ").strip()
        
        if choice == "1":
            self.batch_add_scale()
        elif choice == "2":
            self.batch_add_chord()
        elif choice == "3":
            self.batch_add_arpeggio()
        else:
            print("Invalid choice")
        print()
    
    def batch_add_scale(self):
        """Add scale starting from root note"""
        if not self.project['tracks']:
            print("No tracks available")
            return
        
        root_input = input("Root note (C4, 60, etc.): ").strip().upper()
        if root_input.isdigit():
            root = int(root_input)
        elif root_input in self.note_map:
            root = self.note_map[root_input]
        else:
            print("Invalid note")
            return
        
        scale_type = input("Scale type (major/minor/blues): ").strip().lower()
        start_time = float(input("Start time: ") or "0")
        note_duration = float(input("Note duration: ") or "0.5")
        
        if scale_type == "major":
            intervals = [0, 2, 4, 5, 7, 9, 11, 12]
        elif scale_type == "minor":
            intervals = [0, 2, 3, 5, 7, 8, 10, 12]
        elif scale_type == "blues":
            intervals = [0, 3, 5, 6, 7, 10, 12]
        else:
            print("Unknown scale type")
            return
        
        track = self.project['tracks'][self.current_track_index]
        
        for i, interval in enumerate(intervals):
            note_num = root + interval
            if 0 <= note_num <= 127:
                track['notes'].append({
                    'note': note_num,
                    'start_time': start_time + i * note_duration,
                    'duration': note_duration * 0.8,
                    'velocity': 80,
                    'channel': 0
                })
        
        track['notes'].sort(key=lambda n: n['start_time'])
        print(f"Added {scale_type} scale starting from {self.midi_to_note_name(root)}")
    
    def batch_add_chord(self):
        """Add chord"""
        if not self.project['tracks']:
            print("No tracks available")
            return
        
        root_input = input("Root note (C4, 60, etc.): ").strip().upper()
        if root_input.isdigit():
            root = int(root_input)
        elif root_input in self.note_map:
            root = self.note_map[root_input]
        else:
            print("Invalid note")
            return
        
        chord_type = input("Chord type (major/minor/dim/aug): ").strip().lower()
        start_time = float(input("Start time: ") or "0")
        duration = float(input("Duration: ") or "1.0")
        
        if chord_type == "major":
            intervals = [0, 4, 7]
        elif chord_type == "minor":
            intervals = [0, 3, 7]
        elif chord_type == "dim":
            intervals = [0, 3, 6]
        elif chord_type == "aug":
            intervals = [0, 4, 8]
        else:
            print("Unknown chord type")
            return
        
        track = self.project['tracks'][self.current_track_index]
        
        for interval in intervals:
            note_num = root + interval
            if 0 <= note_num <= 127:
                track['notes'].append({
                    'note': note_num,
                    'start_time': start_time,
                    'duration': duration,
                    'velocity': 80,
                    'channel': 0
                })
        
        track['notes'].sort(key=lambda n: n['start_time'])
        print(f"Added {chord_type} chord starting from {self.midi_to_note_name(root)}")
    
    def batch_add_arpeggio(self):
        """Add arpeggio"""
        if not self.project['tracks']:
            print("No tracks available")
            return
        
        root_input = input("Root note (C4, 60, etc.): ").strip().upper()
        if root_input.isdigit():
            root = int(root_input)
        elif root_input in self.note_map:
            root = self.note_map[root_input]
        else:
            print("Invalid note")
            return
        
        chord_type = input("Chord type (major/minor): ").strip().lower()
        start_time = float(input("Start time: ") or "0")
        note_duration = float(input("Note duration: ") or "0.25")
        
        if chord_type == "major":
            intervals = [0, 4, 7, 12]
        elif chord_type == "minor":
            intervals = [0, 3, 7, 12]
        else:
            print("Unknown chord type")
            return
        
        track = self.project['tracks'][self.current_track_index]
        
        for i, interval in enumerate(intervals):
            note_num = root + interval
            if 0 <= note_num <= 127:
                track['notes'].append({
                    'note': note_num,
                    'start_time': start_time + i * note_duration,
                    'duration': note_duration * 0.8,
                    'velocity': 80,
                    'channel': 0
                })
        
        track['notes'].sort(key=lambda n: n['start_time'])
        print(f"Added {chord_type} arpeggio starting from {self.midi_to_note_name(root)}")
    
    def add_track_simple(self, name: str):
        """Add track without prompts"""
        track = {
            'name': name,
            'instrument': 0,
            'volume': 100,
            'pan': 64,
            'notes': []
        }
        self.project['tracks'].append(track)
        self.current_track_index = len(self.project['tracks']) - 1
    
    def midi_to_note_name(self, midi_num: int) -> str:
        """Convert MIDI number to note name"""
        if not (0 <= midi_num <= 127):
            return f"MIDI{midi_num}"
        
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_num // 12) - 1
        note = notes[midi_num % 12]
        return f"{note}{octave}"

def main():
    """Main entry point"""
    creator = EnhancedSongCreator()
    creator.run()

if __name__ == "__main__":
    main()