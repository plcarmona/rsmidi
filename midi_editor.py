#!/usr/bin/env python3
"""
MIDI Editor - A comprehensive MIDI editing application
Transforms the Synthesia clone into a full-featured MIDI editor
"""

import json
import os
import sys
import time
import threading
from typing import List, Dict, Tuple, Optional
import mido
import numpy as np

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("GUI not available - running in command-line mode")

class MIDINote:
    """Enhanced MIDI note class for editing"""
    def __init__(self, note: int, velocity: int, start_time: float, duration: float = 0.5, channel: int = 0):
        self.note = note  # MIDI note number (0-127)
        self.velocity = velocity  # Note velocity (0-127)
        self.start_time = start_time  # When the note starts (in seconds)
        self.duration = duration  # How long the note lasts
        self.channel = channel  # MIDI channel (0-15)
        self.selected = False  # For GUI selection
        self.end_time = start_time + duration
        
    def __repr__(self):
        return f"MIDINote(note={self.note}, vel={self.velocity}, start={self.start_time:.2f}, dur={self.duration:.2f})"
    
    def overlaps_with(self, other: 'MIDINote') -> bool:
        """Check if this note overlaps with another note"""
        return (self.start_time < other.end_time and 
                other.start_time < self.end_time and
                self.note == other.note)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "note": self.note,
            "velocity": self.velocity, 
            "start_time": self.start_time,
            "duration": self.duration,
            "channel": self.channel
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MIDINote':
        """Create from dictionary"""
        return cls(
            note=data["note"],
            velocity=data.get("velocity", 80),
            start_time=data["start_time"],
            duration=data.get("duration", 0.5),
            channel=data.get("channel", 0)
        )

class MIDITrack:
    """Represents a MIDI track with multiple notes"""
    def __init__(self, name: str = "Untitled Track"):
        self.name = name
        self.notes: List[MIDINote] = []
        self.instrument = 0  # General MIDI instrument (0-127)
        self.volume = 100   # Track volume (0-127)
        self.pan = 64       # Pan position (0-127, 64=center)
        self.muted = False
        self.solo = False
    
    def add_note(self, note: MIDINote) -> None:
        """Add a note to the track"""
        self.notes.append(note)
        self.sort_notes()
    
    def remove_note(self, note: MIDINote) -> None:
        """Remove a note from the track"""
        if note in self.notes:
            self.notes.remove(note)
    
    def sort_notes(self) -> None:
        """Sort notes by start time"""
        self.notes.sort(key=lambda n: n.start_time)
    
    def get_duration(self) -> float:
        """Get total duration of the track"""
        if not self.notes:
            return 0.0
        return max(note.end_time for note in self.notes)
    
    def quantize_notes(self, grid_size: float = 0.25) -> None:
        """Quantize note timings to grid"""
        for note in self.notes:
            note.start_time = round(note.start_time / grid_size) * grid_size
            note.end_time = note.start_time + note.duration

class MIDIProject:
    """Represents a complete MIDI project with multiple tracks"""
    def __init__(self, title: str = "Untitled Project"):
        self.title = title
        self.tracks: List[MIDITrack] = []
        self.tempo = 120  # BPM
        self.time_signature = (4, 4)  # (numerator, denominator)
        self.key_signature = 0  # Number of sharps/flats (-7 to 7)
        self.ticks_per_beat = 480
    
    def add_track(self, track: MIDITrack) -> None:
        """Add a track to the project"""
        self.tracks.append(track)
    
    def remove_track(self, track: MIDITrack) -> None:
        """Remove a track from the project"""
        if track in self.tracks:
            self.tracks.remove(track)
    
    def get_duration(self) -> float:
        """Get total duration of the project"""
        if not self.tracks:
            return 0.0
        return max(track.get_duration() for track in self.tracks)
    
    def get_all_notes(self) -> List[MIDINote]:
        """Get all notes from all tracks"""
        all_notes = []
        for track in self.tracks:
            all_notes.extend(track.notes)
        return sorted(all_notes, key=lambda n: n.start_time)

class MIDIEditor:
    """Main MIDI Editor class"""
    
    def __init__(self, use_gui: bool = GUI_AVAILABLE):
        self.project = MIDIProject()
        self.use_gui = use_gui and GUI_AVAILABLE
        self.current_track_index = 0
        self.is_playing = False
        self.current_time = 0.0
        self.selected_notes: List[MIDINote] = []
        
        # Grid settings for editing
        self.grid_size = 0.25  # 16th notes at 120 BPM
        self.snap_to_grid = True
        
        # View settings
        self.zoom_level = 1.0
        self.view_start_time = 0.0
        self.view_duration = 16.0  # Show 16 seconds by default
        
        # Initialize with a default track
        default_track = MIDITrack("Track 1")
        self.project.add_track(default_track)
        
        if self.use_gui:
            self.init_gui()
        
    def init_gui(self):
        """Initialize GUI components"""
        self.root = tk.Tk()
        self.root.title("MIDI Editor")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2a2a2a')
        
        self.setup_menu()
        self.setup_toolbar()
        self.setup_main_area()
        self.setup_piano_roll()
        self.setup_status_bar()
        
        # Bind events
        self.root.bind('<Control-n>', lambda e: self.new_project())
        self.root.bind('<Control-o>', lambda e: self.open_project())
        self.root.bind('<Control-s>', lambda e: self.save_project())
        self.root.bind('<space>', lambda e: self.toggle_playback())
        self.root.bind('<Delete>', lambda e: self.delete_selected_notes())
        
    def setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Project...", command=self.open_project, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Import MIDI...", command=self.import_midi)
        file_menu.add_command(label="Export MIDI...", command=self.export_midi)
        file_menu.add_separator()
        file_menu.add_command(label="Save Project", command=self.save_project, accelerator="Ctrl+S")
        file_menu.add_command(label="Save Project As...", command=self.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Select All", command=self.select_all_notes, accelerator="Ctrl+A")
        edit_menu.add_command(label="Delete Selected", command=self.delete_selected_notes, accelerator="Del")
        edit_menu.add_separator()
        edit_menu.add_command(label="Quantize", command=self.quantize_selected)
        edit_menu.add_command(label="Transpose...", command=self.transpose_selected)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        view_menu.add_command(label="Fit to Window", command=self.zoom_fit)
        
        # Track menu
        track_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Track", menu=track_menu)
        track_menu.add_command(label="Add Track", command=self.add_track)
        track_menu.add_command(label="Delete Track", command=self.delete_track)
        track_menu.add_command(label="Track Properties...", command=self.track_properties)
    
    def setup_toolbar(self):
        """Setup toolbar with common controls"""
        toolbar = tk.Frame(self.root, bg='#3a3a3a')
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # Transport controls
        self.play_button = tk.Button(toolbar, text="Play", command=self.toggle_playback,
                                   bg='#4CAF50', fg='white')
        self.play_button.pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="Stop", command=self.stop_playback,
                 bg='#f44336', fg='white').pack(side=tk.LEFT, padx=2)
        
        # Tempo control
        tk.Label(toolbar, text="Tempo:", bg='#3a3a3a', fg='white').pack(side=tk.LEFT, padx=(10, 2))
        self.tempo_var = tk.StringVar(value=str(self.project.tempo))
        tempo_spin = tk.Spinbox(toolbar, from_=60, to=200, width=6, textvariable=self.tempo_var,
                              command=self.update_tempo)
        tempo_spin.pack(side=tk.LEFT, padx=2)
        
        # Grid size control
        tk.Label(toolbar, text="Grid:", bg='#3a3a3a', fg='white').pack(side=tk.LEFT, padx=(10, 2))
        self.grid_var = tk.StringVar(value="1/16")
        grid_combo = ttk.Combobox(toolbar, width=6, textvariable=self.grid_var,
                                values=["1/4", "1/8", "1/16", "1/32"], state="readonly")
        grid_combo.pack(side=tk.LEFT, padx=2)
        grid_combo.bind("<<ComboboxSelected>>", self.update_grid_size)
        
        # Snap to grid
        self.snap_var = tk.BooleanVar(value=self.snap_to_grid)
        tk.Checkbutton(toolbar, text="Snap", variable=self.snap_var,
                      bg='#3a3a3a', fg='white', selectcolor='#3a3a3a',
                      command=self.toggle_snap).pack(side=tk.LEFT, padx=(10, 2))
    
    def setup_main_area(self):
        """Setup main editing area with tracks and piano roll"""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Create paned window for resizable sections
        paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, bg='#2a2a2a')
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Track list
        track_frame = tk.Frame(paned, bg='#333333', width=200)
        paned.add(track_frame)
        
        tk.Label(track_frame, text="Tracks", bg='#333333', fg='white', font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Track listbox
        self.track_listbox = tk.Listbox(track_frame, bg='#444444', fg='white', selectbackground='#555555')
        self.track_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.track_listbox.bind('<<ListboxSelect>>', self.on_track_select)
        
        # Track controls
        track_controls = tk.Frame(track_frame, bg='#333333')
        track_controls.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(track_controls, text="Add", command=self.add_track,
                 bg='#4CAF50', fg='white', width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(track_controls, text="Delete", command=self.delete_track,
                 bg='#f44336', fg='white', width=8).pack(side=tk.LEFT, padx=2)
        
        # Piano roll area
        self.piano_roll_frame = tk.Frame(paned, bg='#2a2a2a')
        paned.add(self.piano_roll_frame)
        
        self.update_track_list()
    
    def setup_piano_roll(self):
        """Setup piano roll editor"""
        # Create canvas with scrollbars
        canvas_frame = tk.Frame(self.piano_roll_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        
        self.piano_canvas = tk.Canvas(canvas_frame, 
                                    bg='#2a2a2a',
                                    xscrollcommand=h_scrollbar.set,
                                    yscrollcommand=v_scrollbar.set)
        
        h_scrollbar.config(command=self.piano_canvas.xview)
        v_scrollbar.config(command=self.piano_canvas.yview)
        
        # Pack scrollbars and canvas
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.piano_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse events for editing
        self.piano_canvas.bind("<Button-1>", self.on_canvas_click)
        self.piano_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.piano_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.piano_canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        
        # Update piano roll
        self.update_piano_roll()
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = tk.Frame(self.root, bg='#3a3a3a', relief=tk.SUNKEN, bd=1)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(self.status_bar, text="Ready", bg='#3a3a3a', fg='white')
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Time display
        self.time_label = tk.Label(self.status_bar, text="00:00.000", bg='#3a3a3a', fg='white')
        self.time_label.pack(side=tk.RIGHT, padx=5)
    
    # File operations
    def new_project(self):
        """Create new project"""
        if messagebox.askokcancel("New Project", "Create new project? Unsaved changes will be lost."):
            self.project = MIDIProject()
            default_track = MIDITrack("Track 1")
            self.project.add_track(default_track)
            self.current_track_index = 0
            self.selected_notes = []
            self.update_track_list()
            self.update_piano_roll()
    
    def open_project(self):
        """Open project from file"""
        file_path = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("JSON files", "*.json"), ("MIDI files", "*.mid *.midi"), ("All files", "*.*")]
        )
        if file_path:
            try:
                if file_path.lower().endswith(('.mid', '.midi')):
                    self.import_midi_file(file_path)
                else:
                    self.load_json_project(file_path)
                self.update_track_list()
                self.update_piano_roll()
                self.status_label.config(text=f"Opened: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def save_project(self):
        """Save current project"""
        file_path = filedialog.asksaveasfilename(
            title="Save Project",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.save_json_project(file_path)
                self.status_label.config(text=f"Saved: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def save_project_as(self):
        """Save project as new file"""
        self.save_project()
    
    def import_midi(self):
        """Import MIDI file"""
        file_path = filedialog.askopenfilename(
            title="Import MIDI",
            filetypes=[("MIDI files", "*.mid *.midi"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.import_midi_file(file_path)
                self.update_track_list()
                self.update_piano_roll()
                self.status_label.config(text=f"Imported: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import MIDI: {str(e)}")
    
    def export_midi(self):
        """Export to MIDI file"""
        file_path = filedialog.asksaveasfilename(
            title="Export MIDI",
            defaultextension=".mid",
            filetypes=[("MIDI files", "*.mid"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.export_midi_file(file_path)
                self.status_label.config(text=f"Exported: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export MIDI: {str(e)}")
    
    # Core editing functions (available for both GUI and CLI)
    def load_json_project(self, file_path: str):
        """Load project from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Handle both old format (single track) and new format (multiple tracks)
        if 'notes' in data:
            # Old single-track format
            self.project = MIDIProject(data.get('title', 'Imported Song'))
            track = MIDITrack("Main Track")
            for note_data in data['notes']:
                note = MIDINote.from_dict(note_data)
                track.add_note(note)
            self.project.add_track(track)
        else:
            # New multi-track format
            self.project = MIDIProject(data.get('title', 'Untitled Project'))
            self.project.tempo = data.get('tempo', 120)
            self.project.time_signature = tuple(data.get('time_signature', [4, 4]))
            
            for track_data in data.get('tracks', []):
                track = MIDITrack(track_data.get('name', 'Untitled Track'))
                track.instrument = track_data.get('instrument', 0)
                track.volume = track_data.get('volume', 100)
                for note_data in track_data.get('notes', []):
                    note = MIDINote.from_dict(note_data)
                    track.add_note(note)
                self.project.add_track(track)
    
    def save_json_project(self, file_path: str):
        """Save project to JSON file"""
        data = {
            'title': self.project.title,
            'tempo': self.project.tempo,
            'time_signature': list(self.project.time_signature),
            'tracks': []
        }
        
        for track in self.project.tracks:
            track_data = {
                'name': track.name,
                'instrument': track.instrument,
                'volume': track.volume,
                'notes': [note.to_dict() for note in track.notes]
            }
            data['tracks'].append(track_data)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_midi_file(self, file_path: str):
        """Import MIDI file"""
        mid = mido.MidiFile(file_path)
        self.project = MIDIProject(os.path.splitext(os.path.basename(file_path))[0])
        
        # Get tempo from first tempo message
        for msg in mid:
            if msg.type == 'set_tempo':
                self.project.tempo = int(60000000 / msg.tempo)
                break
        
        # Process each track
        for i, midi_track in enumerate(mid.tracks):
            track = MIDITrack(f"Track {i+1}")
            current_time = 0.0
            active_notes = {}  # note_number -> (start_time, velocity)
            
            for msg in midi_track:
                current_time += mido.tick2second(msg.time, mid.ticks_per_beat, 
                                                mido.bpm2tempo(self.project.tempo))
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = (current_time, msg.velocity)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in active_notes:
                        start_time, velocity = active_notes.pop(msg.note)
                        duration = current_time - start_time
                        note = MIDINote(msg.note, velocity, start_time, duration, msg.channel)
                        track.add_note(note)
            
            if track.notes:  # Only add tracks that have notes
                self.project.add_track(track)
    
    def export_midi_file(self, file_path: str):
        """Export to MIDI file"""
        mid = mido.MidiFile()
        
        for track in self.project.tracks:
            midi_track = mido.MidiTrack()
            mid.tracks.append(midi_track)
            
            # Add track name
            midi_track.append(mido.MetaMessage('track_name', name=track.name))
            
            # Sort notes by start time
            sorted_notes = sorted(track.notes, key=lambda n: n.start_time)
            
            # Convert notes to MIDI messages
            events = []
            for note in sorted_notes:
                # Note on event
                events.append((note.start_time, 'note_on', note.note, note.velocity, note.channel))
                # Note off event
                events.append((note.start_time + note.duration, 'note_off', note.note, 0, note.channel))
            
            # Sort events by time
            events.sort(key=lambda x: x[0])
            
            # Convert to MIDI messages with delta times
            current_time = 0.0
            for event_time, msg_type, note, velocity, channel in events:
                delta_time = event_time - current_time
                delta_ticks = int(mido.second2tick(delta_time, mid.ticks_per_beat, 
                                                 mido.bpm2tempo(self.project.tempo)))
                
                if msg_type == 'note_on':
                    midi_track.append(mido.Message('note_on', channel=channel, note=note, 
                                                  velocity=velocity, time=delta_ticks))
                else:
                    midi_track.append(mido.Message('note_off', channel=channel, note=note, 
                                                  velocity=velocity, time=delta_ticks))
                current_time = event_time
        
        mid.save(file_path)
    
    # Command line interface methods
    def run_cli(self):
        """Run command-line interface"""
        print("🎹 MIDI Editor - Command Line Interface 🎹")
        print("=" * 50)
        
        while True:
            print("\nCommands:")
            print("1. View project info")
            print("2. List tracks")
            print("3. Add track")
            print("4. Select track")
            print("5. Add note to current track")
            print("6. List notes in current track")
            print("7. Delete note")
            print("8. Load project (JSON/MIDI)")
            print("9. Save project (JSON)")
            print("10. Export MIDI")
            print("11. Play project")
            print("12. Set tempo")
            print("13. Quantize current track")
            print("14. Transpose current track")
            print("0. Exit")
            
            choice = input("\nEnter choice (0-14): ").strip()
            
            try:
                if choice == "0":
                    break
                elif choice == "1":
                    self.cli_project_info()
                elif choice == "2":
                    self.cli_list_tracks()
                elif choice == "3":
                    self.cli_add_track()
                elif choice == "4":
                    self.cli_select_track()
                elif choice == "5":
                    self.cli_add_note()
                elif choice == "6":
                    self.cli_list_notes()
                elif choice == "7":
                    self.cli_delete_note()
                elif choice == "8":
                    self.cli_load_project()
                elif choice == "9":
                    self.cli_save_project()
                elif choice == "10":
                    self.cli_export_midi()
                elif choice == "11":
                    self.cli_play_project()
                elif choice == "12":
                    self.cli_set_tempo()
                elif choice == "13":
                    self.cli_quantize_track()
                elif choice == "14":
                    self.cli_transpose_track()
                else:
                    print("Invalid choice")
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def cli_project_info(self):
        """Show project information"""
        print(f"\nProject: {self.project.title}")
        print(f"Tempo: {self.project.tempo} BPM")
        print(f"Time Signature: {self.project.time_signature[0]}/{self.project.time_signature[1]}")
        print(f"Duration: {self.project.get_duration():.2f} seconds")
        print(f"Total Tracks: {len(self.project.tracks)}")
        print(f"Total Notes: {len(self.project.get_all_notes())}")
    
    def cli_list_tracks(self):
        """List all tracks"""
        print("\nTracks:")
        for i, track in enumerate(self.project.tracks):
            marker = "* " if i == self.current_track_index else "  "
            print(f"{marker}{i+1}. {track.name} ({len(track.notes)} notes)")
    
    def cli_add_track(self):
        """Add new track"""
        name = input("Track name: ").strip() or f"Track {len(self.project.tracks) + 1}"
        track = MIDITrack(name)
        self.project.add_track(track)
        print(f"Added track: {name}")
    
    def cli_select_track(self):
        """Select current track"""
        self.cli_list_tracks()
        try:
            index = int(input("Select track number: ")) - 1
            if 0 <= index < len(self.project.tracks):
                self.current_track_index = index
                print(f"Selected: {self.project.tracks[index].name}")
            else:
                print("Invalid track number")
        except ValueError:
            print("Please enter a valid number")
    
    def cli_add_note(self):
        """Add note to current track"""
        if not self.project.tracks:
            print("No tracks available. Create a track first.")
            return
        
        track = self.project.tracks[self.current_track_index]
        print(f"Adding note to: {track.name}")
        
        # Get note number
        note_input = input("Note (C4, 60, etc.): ").strip().upper()
        if note_input.isdigit():
            note_num = int(note_input)
        else:
            # Convert note name to MIDI number
            note_map = {
                'C': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3, 'E': 4,
                'F': 5, 'F#': 6, 'GB': 6, 'G': 7, 'G#': 8, 'AB': 8, 'A': 9,
                'A#': 10, 'BB': 10, 'B': 11
            }
            try:
                octave = int(note_input[-1])
                note_name = note_input[:-1]
                note_num = note_map[note_name] + (octave + 1) * 12
            except (KeyError, ValueError, IndexError):
                print("Invalid note format. Use C4, D#5, or MIDI number 0-127")
                return
        
        if not (0 <= note_num <= 127):
            print("Note must be between 0 and 127")
            return
        
        # Get timing
        start_time = float(input("Start time (seconds): ") or "0")
        duration = float(input("Duration (seconds): ") or "0.5")
        velocity = int(input("Velocity (1-127): ") or "80")
        
        note = MIDINote(note_num, velocity, start_time, duration)
        track.add_note(note)
        print(f"Added note: {note}")
    
    def cli_list_notes(self):
        """List notes in current track"""
        if not self.project.tracks:
            print("No tracks available")
            return
        
        track = self.project.tracks[self.current_track_index]
        print(f"\nNotes in {track.name}:")
        for i, note in enumerate(track.notes):
            print(f"  {i+1}. MIDI {note.note:3d} | {note.start_time:6.2f}s | "
                  f"{note.duration:5.2f}s | vel {note.velocity:3d}")
    
    def cli_delete_note(self):
        """Delete note from current track"""
        if not self.project.tracks:
            print("No tracks available")
            return
        
        track = self.project.tracks[self.current_track_index]
        if not track.notes:
            print("No notes in current track")
            return
        
        self.cli_list_notes()
        try:
            index = int(input("Note number to delete: ")) - 1
            if 0 <= index < len(track.notes):
                deleted = track.notes.pop(index)
                print(f"Deleted: {deleted}")
            else:
                print("Invalid note number")
        except ValueError:
            print("Please enter a valid number")
    
    def cli_load_project(self):
        """Load project from file"""
        file_path = input("File path: ").strip()
        if not file_path:
            return
        
        try:
            if file_path.lower().endswith(('.mid', '.midi')):
                self.import_midi_file(file_path)
            else:
                self.load_json_project(file_path)
            print(f"Loaded: {file_path}")
        except Exception as e:
            print(f"Error loading file: {str(e)}")
    
    def cli_save_project(self):
        """Save project to JSON file"""
        file_path = input("Save as (JSON file): ").strip()
        if not file_path:
            return
        
        if not file_path.endswith('.json'):
            file_path += '.json'
        
        try:
            self.save_json_project(file_path)
            print(f"Saved: {file_path}")
        except Exception as e:
            print(f"Error saving file: {str(e)}")
    
    def cli_export_midi(self):
        """Export to MIDI file"""
        file_path = input("Export as (MIDI file): ").strip()
        if not file_path:
            return
        
        if not file_path.lower().endswith(('.mid', '.midi')):
            file_path += '.mid'
        
        try:
            self.export_midi_file(file_path)
            print(f"Exported: {file_path}")
        except Exception as e:
            print(f"Error exporting MIDI: {str(e)}")
    
    def cli_play_project(self):
        """Simple playback simulation"""
        print("Playing project (simulation)...")
        all_notes = self.project.get_all_notes()
        if not all_notes:
            print("No notes to play")
            return
        
        print(f"Duration: {self.project.get_duration():.2f} seconds")
        print("Notes will be listed in order:")
        
        for note in all_notes:
            note_name = self.midi_to_note_name(note.note)
            print(f"  {note.start_time:6.2f}s: {note_name} (vel {note.velocity})")
    
    def cli_set_tempo(self):
        """Set project tempo"""
        try:
            tempo = int(input(f"Current tempo: {self.project.tempo} BPM\nNew tempo: ") or str(self.project.tempo))
            if 60 <= tempo <= 200:
                self.project.tempo = tempo
                print(f"Tempo set to {tempo} BPM")
            else:
                print("Tempo must be between 60 and 200 BPM")
        except ValueError:
            print("Please enter a valid number")
    
    def cli_quantize_track(self):
        """Quantize current track"""
        if not self.project.tracks:
            print("No tracks available")
            return
        
        track = self.project.tracks[self.current_track_index]
        if not track.notes:
            print("No notes to quantize")
            return
        
        print("Grid sizes: 1=quarter, 0.5=eighth, 0.25=sixteenth, 0.125=32nd")
        try:
            grid = float(input("Grid size: ") or "0.25")
            track.quantize_notes(grid)
            print(f"Quantized {len(track.notes)} notes to {grid} beat grid")
        except ValueError:
            print("Please enter a valid number")
    
    def cli_transpose_track(self):
        """Transpose current track"""
        if not self.project.tracks:
            print("No tracks available")
            return
        
        track = self.project.tracks[self.current_track_index]
        if not track.notes:
            print("No notes to transpose")
            return
        
        try:
            semitones = int(input("Transpose by semitones (+/-): ") or "0")
            transposed = 0
            for note in track.notes:
                new_note = note.note + semitones
                if 0 <= new_note <= 127:
                    note.note = new_note
                    transposed += 1
            print(f"Transposed {transposed} notes by {semitones} semitones")
        except ValueError:
            print("Please enter a valid number")
    
    def midi_to_note_name(self, midi_num: int) -> str:
        """Convert MIDI number to note name"""
        if not (0 <= midi_num <= 127):
            return f"MIDI{midi_num}"
        
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_num // 12) - 1
        note = notes[midi_num % 12]
        return f"{note}{octave}"
    
    # GUI-specific methods (only used when GUI is available)
    def update_track_list(self):
        """Update track list in GUI"""
        if not self.use_gui:
            return
        
        self.track_listbox.delete(0, tk.END)
        for i, track in enumerate(self.project.tracks):
            self.track_listbox.insert(tk.END, f"{track.name} ({len(track.notes)} notes)")
        
        if self.project.tracks and self.current_track_index < len(self.project.tracks):
            self.track_listbox.selection_set(self.current_track_index)
    
    def update_piano_roll(self):
        """Update piano roll display"""
        if not self.use_gui:
            return
        
        self.piano_canvas.delete("all")
        
        canvas_width = self.piano_canvas.winfo_width()
        canvas_height = self.piano_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, self.update_piano_roll)
            return
        
        # Draw grid
        self.draw_grid(canvas_width, canvas_height)
        
        # Draw piano keys (vertical)
        self.draw_piano_keys(canvas_width, canvas_height)
        
        # Draw notes
        if self.project.tracks and self.current_track_index < len(self.project.tracks):
            self.draw_notes(canvas_width, canvas_height)
    
    def draw_grid(self, width: int, height: int):
        """Draw time grid"""
        # Time grid lines
        pixels_per_second = (width - 100) / self.view_duration
        for i in range(int(self.view_duration) + 1):
            x = 100 + i * pixels_per_second
            self.piano_canvas.create_line(x, 0, x, height, fill='#444444', width=1)
        
        # Beat grid lines
        pixels_per_beat = pixels_per_second * (60.0 / self.project.tempo)
        for i in range(int(self.view_duration * self.project.tempo / 60) + 1):
            x = 100 + i * pixels_per_beat
            self.piano_canvas.create_line(x, 0, x, height, fill='#666666', width=1)
    
    def draw_piano_keys(self, width: int, height: int):
        """Draw piano keyboard on the left"""
        key_height = height // 88  # 88 piano keys
        
        for i in range(88):
            midi_note = 108 - i  # Start from C8 (108) at top
            y = i * key_height
            
            # Determine if black key
            note_in_octave = midi_note % 12
            is_black = note_in_octave in [1, 3, 6, 8, 10]
            
            # Draw key
            color = '#333333' if is_black else '#ffffff'
            text_color = '#ffffff' if is_black else '#000000'
            
            self.piano_canvas.create_rectangle(0, y, 100, y + key_height,
                                             fill=color, outline='#666666')
            
            # Draw note name for C notes
            if midi_note % 12 == 0:  # C notes
                octave = (midi_note // 12) - 1
                self.piano_canvas.create_text(50, y + key_height//2,
                                            text=f"C{octave}", fill=text_color, font=('Arial', 8))
    
    def draw_notes(self, width: int, height: int):
        """Draw notes on piano roll"""
        track = self.project.tracks[self.current_track_index]
        pixels_per_second = (width - 100) / self.view_duration
        key_height = height // 88
        
        for note in track.notes:
            # Calculate position
            x1 = 100 + note.start_time * pixels_per_second
            x2 = 100 + (note.start_time + note.duration) * pixels_per_second
            y = (108 - note.note) * key_height
            
            # Skip notes outside view
            if x2 < 100 or x1 > width:
                continue
            
            # Note color based on velocity
            intensity = note.velocity / 127.0
            color = f"#{int(100 + 155 * intensity):02x}{int(150 + 105 * intensity):02x}50"
            
            if note.selected:
                color = "#ff6666"
            
            # Draw note rectangle
            self.piano_canvas.create_rectangle(x1, y, x2, y + key_height,
                                             fill=color, outline='#ffffff', width=1,
                                             tags=f"note_{id(note)}")
    
    def on_canvas_click(self, event):
        """Handle canvas click for note selection/creation"""
        # Implement note selection and creation logic
        pass
    
    def on_canvas_drag(self, event):
        """Handle canvas drag for note editing"""
        # Implement note dragging logic
        pass
    
    def on_canvas_release(self, event):
        """Handle canvas release"""
        # Finalize note editing
        pass
    
    def on_canvas_double_click(self, event):
        """Handle double-click for note creation/editing"""
        # Create new note or edit existing
        pass
    
    def on_track_select(self, event):
        """Handle track selection"""
        selection = self.track_listbox.curselection()
        if selection:
            self.current_track_index = selection[0]
            self.update_piano_roll()
    
    def add_track(self):
        """Add new track (GUI)"""
        name = tk.simpledialog.askstring("Add Track", "Track name:")
        if name:
            track = MIDITrack(name)
            self.project.add_track(track)
            self.update_track_list()
    
    def delete_track(self):
        """Delete current track (GUI)"""
        if self.project.tracks and messagebox.askokcancel("Delete Track", "Delete current track?"):
            self.project.tracks.pop(self.current_track_index)
            if self.current_track_index >= len(self.project.tracks):
                self.current_track_index = max(0, len(self.project.tracks) - 1)
            self.update_track_list()
            self.update_piano_roll()
    
    def toggle_playback(self):
        """Toggle playback"""
        # Implement playback logic
        self.is_playing = not self.is_playing
        self.play_button.config(text="Pause" if self.is_playing else "Play")
    
    def stop_playback(self):
        """Stop playback"""
        self.is_playing = False
        self.current_time = 0.0
        self.play_button.config(text="Play")
    
    def update_tempo(self):
        """Update tempo from GUI"""
        try:
            self.project.tempo = int(self.tempo_var.get())
        except ValueError:
            pass
    
    def update_grid_size(self, event=None):
        """Update grid size from GUI"""
        grid_map = {"1/4": 1.0, "1/8": 0.5, "1/16": 0.25, "1/32": 0.125}
        self.grid_size = grid_map.get(self.grid_var.get(), 0.25)
        self.update_piano_roll()
    
    def toggle_snap(self):
        """Toggle snap to grid"""
        self.snap_to_grid = self.snap_var.get()
    
    def zoom_in(self):
        """Zoom in timeline"""
        self.zoom_level *= 1.5
        self.view_duration /= 1.5
        self.update_piano_roll()
    
    def zoom_out(self):
        """Zoom out timeline"""
        self.zoom_level /= 1.5
        self.view_duration *= 1.5
        self.update_piano_roll()
    
    def zoom_fit(self):
        """Fit entire project in view"""
        duration = self.project.get_duration()
        if duration > 0:
            self.view_duration = max(duration + 2, 4)
            self.update_piano_roll()
    
    def select_all_notes(self):
        """Select all notes in current track"""
        if self.project.tracks and self.current_track_index < len(self.project.tracks):
            track = self.project.tracks[self.current_track_index]
            self.selected_notes = track.notes[:]
            for note in track.notes:
                note.selected = True
            self.update_piano_roll()
    
    def delete_selected_notes(self):
        """Delete selected notes"""
        if self.project.tracks and self.current_track_index < len(self.project.tracks):
            track = self.project.tracks[self.current_track_index]
            for note in self.selected_notes:
                if note in track.notes:
                    track.remove_note(note)
            self.selected_notes = []
            self.update_piano_roll()
    
    def quantize_selected(self):
        """Quantize selected notes"""
        for note in self.selected_notes:
            note.start_time = round(note.start_time / self.grid_size) * self.grid_size
            note.end_time = note.start_time + note.duration
        self.update_piano_roll()
    
    def transpose_selected(self):
        """Transpose selected notes"""
        semitones = tk.simpledialog.askinteger("Transpose", "Transpose by semitones:", initialvalue=0)
        if semitones is not None:
            for note in self.selected_notes:
                new_note = note.note + semitones
                if 0 <= new_note <= 127:
                    note.note = new_note
            self.update_piano_roll()
    
    def track_properties(self):
        """Show track properties dialog"""
        # Implement track properties dialog
        pass
    
    def run(self):
        """Run the MIDI editor"""
        if self.use_gui:
            self.root.mainloop()
        else:
            self.run_cli()

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # Force CLI mode
        editor = MIDIEditor(use_gui=False)
    else:
        # Use GUI if available, CLI otherwise
        editor = MIDIEditor()
    
    editor.run()

if __name__ == "__main__":
    main()