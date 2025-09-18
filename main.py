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
        
        # Piano configuration - Full 88-key piano (A0 to C8)
        # Standard 88-key piano starts at A0 (note 21) and ends at C8 (note 108)
        self.piano_start_note = 21  # A0
        self.piano_end_note = 108   # C8
        self.keys = self.create_piano_keys()
        
        # Visual settings
        self.note_speed = 200  # pixels per second
        self.note_height = 20
        self.piano_height = 150
        
        self.setup_ui()
        self.create_sample_song()
        
    def create_piano_keys(self):
        """Create the full 88-key piano configuration (A0 to C8)"""
        keys = []
        
        # Standard 88-key piano layout
        # MIDI notes 21 (A0) to 108 (C8)
        for note_number in range(self.piano_start_note, self.piano_end_note + 1):
            # Determine if it's a black key based on note position within octave
            note_in_octave = note_number % 12
            is_black = note_in_octave in [1, 3, 6, 8, 10]  # C#, D#, F#, G#, A#
            keys.append(PianoKey(note_number, is_black))
        
        return keys
    
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
        """Create a sample song for demonstration using the full piano range"""
        # Sample melody that demonstrates the wider range of the 88-key piano
        melody_notes = [
            # Lower register
            48, 50, 52, 53,  # C3-F3
            # Middle register  
            60, 62, 64, 65, 67, 69, 71, 72,  # C4-C5
            # Higher register
            72, 74, 76, 77, 79, 81  # C5-A5
        ]
        
        self.notes = []
        for i, note in enumerate(melody_notes):
            start_time = i * 0.6  # 0.6 seconds apart
            self.notes.append(MIDINote(note, 80, start_time, 0.4))
        
        # Add some bass notes (lower piano range)
        bass_notes = [36, 41, 43]  # C2, F2, G2
        for i, note in enumerate(bass_notes):
            start_time = i * 2.0 + 1.0
            self.notes.append(MIDINote(note, 70, start_time, 1.5))
        
        # Add some treble notes (higher piano range)
        treble_notes = [84, 88, 91]  # C6, E6, G6
        for i, note in enumerate(treble_notes):
            start_time = i * 1.5 + 10.0
            self.notes.append(MIDINote(note, 65, start_time, 0.8))
    
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
        # Extended key mapping for more keys on the full 88-key piano
        # Focus on the middle register (around C4) for main gameplay
        key_map = {
            # Lower octave (C3-B3)
            'z': 48,  # C3
            'x': 50,  # D3
            'c': 52,  # E3
            'v': 53,  # F3
            'b': 55,  # G3
            'n': 57,  # A3
            'm': 59,  # B3
            # Black keys for lower octave
            's': 49,  # C#3
            'd': 51,  # D#3
            'g': 54,  # F#3
            'h': 56,  # G#3
            'j': 58,  # A#3
            
            # Middle octave (C4-B4) - primary playing range
            'a': 60,  # C4
            'q': 62,  # D4
            'w': 64,  # E4
            'e': 65,  # F4
            'r': 67,  # G4
            't': 69,  # A4
            'y': 71,  # B4
            # Black keys for middle octave
            '2': 61,  # C#4
            '3': 63,  # D#4
            '5': 66,  # F#4
            '6': 68,  # G#4
            '7': 70,  # A#4
            
            # Upper octave (C5-B5)
            'u': 72,  # C5
            'i': 74,  # D5
            'o': 76,  # E5
            'p': 77,  # F5
            '[': 79,  # G5
            ']': 81,  # A5
            '\\': 83, # B5
            # Black keys for upper octave
            '9': 73,  # C#5
            '0': 75,  # D#5
            '=': 78,  # F#5
            'l': 80,  # G#5
            ';': 82,  # A#5
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
            if note.note == note_number and not note.hit:
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
        """Draw the falling notes with reversed behavior for hit notes"""
        piano_y = canvas_height - self.piano_height
        
        for note in self.notes:
            # Calculate note position
            time_diff = note.start_time - self.current_time
            
            if note.hit:
                # Hit notes move upward from piano to top of screen
                hit_time = self.current_time - note.start_time
                note_y = piano_y - hit_time * self.note_speed
                # Only show hit notes for a short time as they move up
                if note_y < -self.note_height:
                    continue
            else:
                # Regular falling notes (move down toward piano)
                note_y = piano_y + time_diff * self.note_speed
            
            # Only draw notes that are visible
            if -self.note_height <= note_y <= canvas_height:
                # Calculate note X position based on note number
                note_x = self.get_note_x_position(note.note, canvas_width)
                
                # Choose color based on note state
                if note.hit:
                    color = '#4CAF50'  # Green for hit notes moving up
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
        """Draw the full 88-key piano keyboard"""
        piano_y = canvas_height - self.piano_height
        
        # Calculate key dimensions for 88 keys
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
                    # Count white keys before this black key
                    white_keys_before = 0
                    for check_note in range(self.piano_start_note, key.note_number):
                        if check_note % 12 not in [1, 3, 6, 8, 10]:  # if it's a white key
                            white_keys_before += 1
                    
                    # Position black key relative to white keys
                    if note_in_octave == 1:  # C#
                        x = (white_keys_before - 0.3) * white_key_width
                    elif note_in_octave == 3:  # D#
                        x = (white_keys_before - 0.3) * white_key_width
                    elif note_in_octave == 6:  # F#
                        x = (white_keys_before - 0.3) * white_key_width
                    elif note_in_octave == 8:  # G#
                        x = (white_keys_before - 0.3) * white_key_width
                    elif note_in_octave == 10:  # A#
                        x = (white_keys_before - 0.3) * white_key_width
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
        
        # Fallback calculation for notes outside the piano range
        # This handles any edge cases where notes might be outside 88-key range
        white_key_count = sum(1 for k in self.keys if not k.is_black)
        if white_key_count == 0:
            return canvas_width / 2
            
        # If note is outside piano range, place it proportionally
        if note_number < self.piano_start_note:
            return 0
        elif note_number > self.piano_end_note:
            return canvas_width
        
        # Calculate relative position for any MIDI note
        white_keys_before = 0
        for check_note in range(self.piano_start_note, min(note_number + 1, self.piano_end_note + 1)):
            if check_note % 12 not in [1, 3, 6, 8, 10]:  # if it's a white key
                white_keys_before += 1
        
        white_key_width = canvas_width / white_key_count
        return white_keys_before * white_key_width
    
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
    print("🎹 Synthesia Clone - Full 88-Key Piano Learning Application 🎹")
    print("=" * 65)
    print("Features:")
    print("  ✨ Full 88-key piano (A0 to C8)")
    print("  ✨ Enhanced visual feedback - hit notes shoot upward!")
    print("  ✨ Extended keyboard mapping across 3 octave ranges")
    print()
    print("Controls:")
    print("  Lower Octave:  z x c v b n m  (white)  |  s d g h j  (black)")
    print("  Middle Octave: a q w e r t y  (white)  |  2 3 5 6 7  (black)")
    print("  Upper Octave:  u i o p [ ] \\  (white)  |  9 0 = l ;  (black)")
    print()
    print("Game Controls:")
    print("  Play/Pause: Click the Play button")
    print("  Stop: Click the Stop button")
    print("  Load Song: Click 'Load Song' to load a JSON file")
    print("=" * 65)
    app.run()
