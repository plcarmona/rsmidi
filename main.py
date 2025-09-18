#!/usr/bin/env python3
"""
Synthesia Clone - A simple piano learning application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import time
import threading
import math
import os

class MIDINote:
    """Represents a MIDI note with timing information"""
    def __init__(self, note, velocity, start_time, duration=0.5):
        self.note = note  # MIDI note number (0-127)
        self.velocity = velocity  # Note velocity (0-127)
        self.start_time = start_time  # When the note starts (in seconds)
        self.duration = duration  # How long the note lasts
        self.y_pos = 0  # Y position for rendering
        self.active = False  # Whether the note is currently being played
        self.hit = False  # Whether the note has been hit by the player

class PianoKey:
    """Represents a piano key"""
    def __init__(self, note_number, is_black=False):
        self.note_number = note_number
        self.is_black = is_black
        self.pressed = False
        self.x_pos = 0
        self.width = 0

class SynthesiaClone:
    """Main application class for the Synthesia clone"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Synthesia Clone - Piano Learning")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2a2a2a')
        
        # Game state
        self.is_playing = False
        self.current_time = 0.0
        self.notes = []
        self.score = 0
        self.notes_hit = 0
        self.notes_missed = 0
        
        # Piano configuration
        self.octave_start = 3  # Starting octave (C3)
        self.octave_count = 3  # Number of octaves to display
        self.keys = self.create_piano_keys()
        
        # Visual settings
        self.note_speed = 200  # pixels per second
        self.note_height = 20
        self.piano_height = 150
        
        self.setup_ui()
        self.create_sample_song()
        
    def create_piano_keys(self):
        """Create the piano key configuration"""
        keys = []
        white_keys = [0, 2, 4, 5, 7, 9, 11]  # C, D, E, F, G, A, B
        black_keys = [1, 3, 6, 8, 10]  # C#, D#, F#, G#, A#
        
        for octave in range(self.octave_count):
            base_note = (self.octave_start + octave) * 12
            
            # Add white keys
            for key in white_keys:
                keys.append(PianoKey(base_note + key, False))
            
            # Add black keys
            for key in black_keys:
                keys.append(PianoKey(base_note + key, True))
        
        return sorted(keys, key=lambda k: k.note_number)
    
    def setup_ui(self):
        """Initialize the user interface"""
        # Control frame
        control_frame = tk.Frame(self.root, bg='#2a2a2a')
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Play/Pause button
        self.play_button = tk.Button(
            control_frame, 
            text="Play", 
            command=self.toggle_play,
            bg='#4CAF50', 
            fg='white',
            font=('Arial', 12, 'bold')
        )
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        tk.Button(
            control_frame, 
            text="Stop", 
            command=self.stop_song,
            bg='#f44336', 
            fg='white',
            font=('Arial', 12, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        # Load song button
        tk.Button(
            control_frame, 
            text="Load Song", 
            command=self.load_song,
            bg='#2196F3', 
            fg='white',
            font=('Arial', 12, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        # Score display
        self.score_label = tk.Label(
            control_frame, 
            text="Score: 0", 
            fg='white', 
            bg='#2a2a2a',
            font=('Arial', 12, 'bold')
        )
        self.score_label.pack(side=tk.RIGHT, padx=10)
        
        # Progress display
        self.progress_label = tk.Label(
            control_frame, 
            text="Notes: 0/0", 
            fg='white', 
            bg='#2a2a2a',
            font=('Arial', 12)
        )
        self.progress_label.pack(side=tk.RIGHT, padx=10)
        
        # Main game canvas
        self.canvas = tk.Canvas(
            self.root, 
            bg='#1a1a1a', 
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Bind keyboard events
        self.root.bind('<KeyPress>', self.key_press)
        self.root.bind('<KeyRelease>', self.key_release)
        self.root.focus_set()
        
        # Start the game loop
        self.update_game()
        
    def create_sample_song(self):
        """Create a sample song for demonstration"""
        # Simple melody: C-D-E-F-G-A-B-C
        base_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C4 to C5
        
        self.notes = []
        for i, note in enumerate(base_notes):
            start_time = i * 0.8  # 0.8 seconds apart
            self.notes.append(MIDINote(note, 80, start_time, 0.5))
        
        # Add some chords
        chord_notes = [60, 64, 67]  # C major chord
        for note in chord_notes:
            self.notes.append(MIDINote(note, 60, 8.0, 1.0))
    
    def load_song(self):
        """Load a song from a JSON file"""
        file_path = filedialog.askopenfilename(
            title="Select Song File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    song_data = json.load(f)
                
                self.notes = []
                for note_data in song_data.get('notes', []):
                    note = MIDINote(
                        note_data['note'],
                        note_data.get('velocity', 80),
                        note_data['start_time'],
                        note_data.get('duration', 0.5)
                    )
                    self.notes.append(note)
                
                messagebox.showinfo("Success", f"Loaded {len(self.notes)} notes")
                self.stop_song()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load song: {str(e)}")
    
    def toggle_play(self):
        """Toggle play/pause state"""
        self.is_playing = not self.is_playing
        self.play_button.config(text="Pause" if self.is_playing else "Play")
        
        if self.is_playing:
            self.play_button.config(bg='#FF9800')  # Orange for pause
        else:
            self.play_button.config(bg='#4CAF50')  # Green for play
    
    def stop_song(self):
        """Stop the song and reset"""
        self.is_playing = False
        self.current_time = 0.0
        self.score = 0
        self.notes_hit = 0
        self.notes_missed = 0
        
        # Reset all notes
        for note in self.notes:
            note.hit = False
            note.active = False
        
        self.play_button.config(text="Play", bg='#4CAF50')
        self.update_score_display()
    
    def key_press(self, event):
        """Handle key press events"""
        key_map = {
            'a': 60,  # C4
            's': 62,  # D4
            'd': 64,  # E4
            'f': 65,  # F4
            'g': 67,  # G4
            'h': 69,  # A4
            'j': 71,  # B4
            'k': 72,  # C5
            'w': 61,  # C#4
            'e': 63,  # D#4
            't': 66,  # F#4
            'y': 68,  # G#4
            'u': 70,  # A#4
        }
        
        note_num = key_map.get(event.char)
        if note_num:
            self.play_note(note_num)
    
    def key_release(self, event):
        """Handle key release events"""
        # Reset key visual state
        for key in self.keys:
            key.pressed = False
    
    def play_note(self, note_number):
        """Play a note and check if it matches current notes"""
        # Mark key as pressed
        for key in self.keys:
            if key.note_number == note_number:
                key.pressed = True
                break
        
        # Check if this note matches any active notes
        current_notes = [n for n in self.notes 
                        if n.start_time <= self.current_time <= n.start_time + n.duration + 0.5]
        
        for note in current_notes:
            if note.note_number == note_number and not note.hit:
                note.hit = True
                self.score += 100
                self.notes_hit += 1
                self.update_score_display()
                break
    
    def update_game(self):
        """Main game update loop"""
        if self.is_playing:
            self.current_time += 0.02  # 50 FPS
            
            # Check for missed notes
            for note in self.notes:
                if (note.start_time + note.duration + 0.5 < self.current_time 
                    and not note.hit and not note.active):
                    note.active = True  # Mark as processed
                    self.notes_missed += 1
        
        self.render()
        self.update_score_display()
        
        # Schedule next update
        self.root.after(20, self.update_game)  # ~50 FPS
    
    def render(self):
        """Render the game"""
        self.canvas.delete("all")
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Draw falling notes
        self.draw_falling_notes(canvas_width, canvas_height)
        
        # Draw piano
        self.draw_piano(canvas_width, canvas_height)
        
        # Draw current time line
        self.draw_time_line(canvas_width, canvas_height)
    
    def draw_falling_notes(self, canvas_width, canvas_height):
        """Draw the falling notes"""
        piano_y = canvas_height - self.piano_height
        
        for note in self.notes:
            # Calculate note position
            time_diff = note.start_time - self.current_time
            note_y = piano_y + time_diff * self.note_speed
            
            # Only draw notes that are visible
            if -self.note_height <= note_y <= canvas_height:
                # Calculate note X position based on note number
                note_x = self.get_note_x_position(note.note_number, canvas_width)
                
                # Choose color based on note state
                if note.hit:
                    color = '#4CAF50'  # Green for hit notes
                elif note.active:
                    color = '#f44336'  # Red for missed notes
                elif note.start_time <= self.current_time <= note.start_time + note.duration:
                    color = '#FFC107'  # Yellow for active notes
                else:
                    color = '#2196F3'  # Blue for upcoming notes
                
                # Draw note
                self.canvas.create_rectangle(
                    note_x - 15, note_y,
                    note_x + 15, note_y + self.note_height,
                    fill=color, outline='white'
                )
    
    def draw_piano(self, canvas_width, canvas_height):
        """Draw the piano keyboard"""
        piano_y = canvas_height - self.piano_height
        
        # Calculate key dimensions
        white_key_count = sum(1 for k in self.keys if not k.is_black)
        if white_key_count == 0:
            return
            
        white_key_width = canvas_width / white_key_count
        black_key_width = white_key_width * 0.6
        
        # Draw white keys first
        white_key_index = 0
        for key in self.keys:
            if not key.is_black:
                x = white_key_index * white_key_width
                key.x_pos = x + white_key_width / 2
                key.width = white_key_width
                
                color = '#333333' if key.pressed else '#ffffff'
                self.canvas.create_rectangle(
                    x, piano_y,
                    x + white_key_width, canvas_height,
                    fill=color, outline='black'
                )
                
                white_key_index += 1
        
        # Draw black keys
        black_key_pattern = [1, 3, 6, 8, 10]  # Positions of black keys in octave
        for key in self.keys:
            if key.is_black:
                # Find corresponding white key position
                note_in_octave = key.note_number % 12
                if note_in_octave in black_key_pattern:
                    # Calculate position relative to white keys
                    octave_start = (key.note_number // 12 - self.octave_start) * 7
                    
                    if note_in_octave == 1:  # C#
                        x = (octave_start + 0.7) * white_key_width
                    elif note_in_octave == 3:  # D#
                        x = (octave_start + 1.7) * white_key_width
                    elif note_in_octave == 6:  # F#
                        x = (octave_start + 3.7) * white_key_width
                    elif note_in_octave == 8:  # G#
                        x = (octave_start + 4.7) * white_key_width
                    elif note_in_octave == 10:  # A#
                        x = (octave_start + 5.7) * white_key_width
                    else:
                        continue
                    
                    if 0 <= x <= canvas_width - black_key_width:
                        key.x_pos = x + black_key_width / 2
                        key.width = black_key_width
                        
                        color = '#666666' if key.pressed else '#000000'
                        self.canvas.create_rectangle(
                            x, piano_y,
                            x + black_key_width, canvas_height - 30,
                            fill=color, outline='gray'
                        )
    
    def draw_time_line(self, canvas_width, canvas_height):
        """Draw the current time indicator line"""
        piano_y = canvas_height - self.piano_height
        self.canvas.create_line(
            0, piano_y, canvas_width, piano_y,
            fill='red', width=2
        )
    
    def get_note_x_position(self, note_number, canvas_width):
        """Calculate the X position for a note on the canvas"""
        for key in self.keys:
            if key.note_number == note_number:
                return key.x_pos
        
        # Fallback calculation if key not found
        white_key_count = sum(1 for k in self.keys if not k.is_black)
        if white_key_count == 0:
            return canvas_width / 2
            
        white_key_width = canvas_width / white_key_count
        relative_note = note_number - (self.octave_start * 12)
        octave = relative_note // 12
        note_in_octave = relative_note % 12
        
        white_key_positions = {0: 0, 2: 1, 4: 2, 5: 3, 7: 4, 9: 5, 11: 6}
        if note_in_octave in white_key_positions:
            white_key_index = octave * 7 + white_key_positions[note_in_octave]
            return white_key_index * white_key_width + white_key_width / 2
        
        return canvas_width / 2
    
    def update_score_display(self):
        """Update the score and progress displays"""
        self.score_label.config(text=f"Score: {self.score}")
        total_notes = len(self.notes)
        self.progress_label.config(
            text=f"Notes: {self.notes_hit}/{total_notes} "
                 f"(Missed: {self.notes_missed})"
        )
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def create_sample_song_file():
    """Create a sample song file for demonstration"""
    sample_song = {
        "title": "Sample Song - Mary Had a Little Lamb",
        "notes": [
            {"note": 64, "start_time": 0.0, "duration": 0.5, "velocity": 80},  # E
            {"note": 62, "start_time": 0.5, "duration": 0.5, "velocity": 80},  # D
            {"note": 60, "start_time": 1.0, "duration": 0.5, "velocity": 80},  # C
            {"note": 62, "start_time": 1.5, "duration": 0.5, "velocity": 80},  # D
            {"note": 64, "start_time": 2.0, "duration": 0.5, "velocity": 80},  # E
            {"note": 64, "start_time": 2.5, "duration": 0.5, "velocity": 80},  # E
            {"note": 64, "start_time": 3.0, "duration": 1.0, "velocity": 80},  # E
            {"note": 62, "start_time": 4.5, "duration": 0.5, "velocity": 80},  # D
            {"note": 62, "start_time": 5.0, "duration": 0.5, "velocity": 80},  # D
            {"note": 62, "start_time": 5.5, "duration": 1.0, "velocity": 80},  # D
            {"note": 64, "start_time": 7.0, "duration": 0.5, "velocity": 80},  # E
            {"note": 67, "start_time": 7.5, "duration": 0.5, "velocity": 80},  # G
            {"note": 67, "start_time": 8.0, "duration": 1.0, "velocity": 80},  # G
        ]
    }
    
    with open('sample_song.json', 'w') as f:
        json.dump(sample_song, f, indent=2)
    
    print("Created sample_song.json")

if __name__ == "__main__":
    # Create sample song file
    create_sample_song_file()
    
    # Start the application
    app = SynthesiaClone()
    print("Synthesia Clone - Piano Learning Application")
    print("=" * 50)
    print("Controls:")
    print("  Piano Keys (White): a s d f g h j k")
    print("  Piano Keys (Black): w e t y u")
    print("  Play/Pause: Click the Play button")
    print("  Stop: Click the Stop button")
    print("  Load Song: Click 'Load Song' to load a JSON file")
    print("=" * 50)
    app.run()
