# RSMIDI - MIDI Editor & Piano Learning Suite

A comprehensive MIDI editing and piano learning application, evolved from a Synthesia clone into a full-featured **MIDI Editor** with advanced editing capabilities!

## 🎹 Applications Included

### 1. **MIDI Editor** (`midi_editor.py`) - NEW!
A professional MIDI editor with both GUI and command-line interfaces:

**Features:**
- ✨ **Multi-track MIDI editing** - Create and edit multiple instrument tracks
- ✨ **Piano roll editor** - Visual note editing with drag & drop (GUI mode)
- ✨ **Import/Export MIDI files** - Full .mid/.midi file support
- ✨ **Advanced editing tools** - Quantization, transposition, velocity editing
- ✨ **Timeline-based editing** - Precise timing control with grid snapping
- ✨ **Track management** - Individual track properties (instrument, volume, pan)
- ✨ **Tempo & time signature** - Full project tempo and timing control
- ✨ **Command-line interface** - Complete editing functionality without GUI
- ✨ **JSON project format** - Human-readable project files

### 2. **Piano Learning Game** (`main.py`)
The original Synthesia-inspired piano learning application:

**Features:**
- ✨ **Full 88-key piano keyboard** (A0 to C8) with falling notes
- ✨ **Enhanced visual feedback** - hit notes reverse direction and shoot upward
- ✨ Real-time note matching and scoring
- ✨ Support for custom songs via JSON files  
- ✨ Extended keyboard controls covering 3 octave ranges
- ✨ Score tracking and progress monitoring
- ✨ Play/pause/stop controls

### 3. **Enhanced Song Creator** (`enhanced_song_creator.py`) - NEW!
Advanced song creation tool with multi-track support:

**Features:**
- ✨ **Multi-track composition** - Create complex arrangements
- ✨ **Template songs** - Scales, chord progressions, melodies
- ✨ **Batch note creation** - Generate scales, chords, and arpeggios
- ✨ **Advanced note editing** - Quantization, transposition
- ✨ **Extended note mapping** - Full note name support (C-1 to G9)

## 🚀 Quick Start

### MIDI Editor (Recommended)
```bash
# GUI mode (if tkinter available)
python launcher.py

# Command-line mode
python launcher.py --cli
# or
python midi_editor.py --cli

# Help
python launcher.py --help
```

### Piano Learning Game
```bash
python main.py
```

### Enhanced Song Creator
```bash
python enhanced_song_creator.py
```

## 📋 Requirements

### Basic Requirements
- **Python 3.6+** (uses tkinter for GUI)
- **No external dependencies** required for piano learning game

### Enhanced MIDI Editor Requirements
- **mido** - MIDI file import/export
- **numpy** - Audio processing utilities  
- **pygame** - Enhanced audio features (optional)

```bash
pip install mido numpy pygame
```

## 📁 Project Structure

```
rsmidi/
├── midi_editor.py           # Main MIDI editor application
├── launcher.py              # Application launcher
├── main.py                  # Piano learning game
├── enhanced_song_creator.py # Advanced song creation
├── song_creator.py          # Basic song creation (legacy)
├── utils.py                 # Utility functions
├── console_demo.py          # Console demonstration
├── interface_preview.py     # Interface preview
├── README.md                # This file
├── requirements.txt         # Python dependencies
└── *.json                   # Sample songs and projects
```

## 🎮 MIDI Editor Usage

### GUI Mode Commands
- **File Management**: New, Open, Save, Import MIDI, Export MIDI
- **Editing**: Select All (Ctrl+A), Delete (Del), Quantize, Transpose
- **View**: Zoom In/Out, Fit to Window
- **Playback**: Play/Pause (Space), Stop, Tempo control
- **Tracks**: Add/Delete tracks, Track properties

### CLI Mode Commands
1. **Project Management** - View info, set tempo, time signature
2. **Track Management** - Add, delete, select tracks
3. **Note Editing** - Add, delete, list notes
4. **Advanced Editing** - Quantize, transpose tracks
5. **File Operations** - Load/Save JSON, Import/Export MIDI
6. **Templates** - Create scales, chords, progressions

### Keyboard Shortcuts (GUI)
- `Ctrl+N` - New Project
- `Ctrl+O` - Open Project  
- `Ctrl+S` - Save Project
- `Ctrl+A` - Select All Notes
- `Delete` - Delete Selected Notes
- `Space` - Play/Pause
- Mouse drag - Move/resize notes
- Double-click - Create/edit notes

## 🎹 Piano Learning Game Controls

### Piano Keys
**Full 88-Key Piano Support** - Now supports the complete piano range from A0 to C8!

#### Lower Octave (C3-B3)
- **White keys**: `z x c v b n m` (C3, D3, E3, F3, G3, A3, B3)
- **Black keys**: `s d g h j` (C#3, D#3, F#3, G#3, A#3)

#### Middle Octave (C4-B4) - Primary Range
- **White keys**: `a q w e r t y` (C4, D4, E4, F4, G4, A4, B4)
- **Black keys**: `2 3 5 6 7` (C#4, D#4, F#4, G#4, A#4)

#### Upper Octave (C5-B5)
- **White keys**: `u i o p [ ] \` (C5, D5, E5, F5, G5, A5, B5)
- **Black keys**: `9 0 = l ;` (C#5, D#5, F#5, G#5, A#5)

### Game Controls
- **Play/Pause**: Click the Play button or spacebar
- **Stop**: Click the Stop button
- **Load Song**: Click 'Load Song' to load a JSON song file

## 🎵 Song/Project Format

### Enhanced Multi-Track Format (MIDI Editor)
```json
{
  "title": "My Project",
  "tempo": 120,
  "time_signature": [4, 4],
  "tracks": [
    {
      "name": "Piano",
      "instrument": 0,
      "volume": 100,
      "pan": 64,
      "notes": [
        {
          "note": 60,        // MIDI note number (60 = C4)
          "start_time": 0.0, // When the note starts (seconds)
          "duration": 0.5,   // How long the note lasts (seconds)
          "velocity": 80,    // Note velocity (1-127)
          "channel": 0       // MIDI channel (0-15)
        }
      ]
    }
  ]
}
```

### Legacy Single-Track Format (Piano Game)
```json
{
  "title": "Song Title",
  "notes": [
    {
      "note": 60,        // MIDI note number (60 = C4)
      "start_time": 0.0, // When the note starts (seconds)
      "duration": 0.5,   // How long the note lasts (seconds)
      "velocity": 80     // Note velocity (0-127, optional)
    }
  ]
}
```

## 📄 Sample Files

The application includes several sample files:

- **sample_song.json** - "Mary Had a Little Lamb" (piano game format)
- **twinkle_twinkle.json** - "Twinkle Twinkle Little Star"
- **c_major_scale.json** - C major scale example
- **chord_progression.json** - C-Am-F-G chord progression

## 🎮 How to Use the MIDI Editor

### Getting Started
1. Launch with `python launcher.py` (GUI) or `python launcher.py --cli` (CLI)
2. Create a new project or load existing MIDI/JSON files
3. Add tracks for different instruments
4. Add notes using the interface or import from MIDI
5. Edit notes: move, resize, change velocity
6. Use advanced tools: quantize, transpose
7. Export as MIDI file for use in other applications

### Piano Learning Game Usage

1. Start the application
2. Press Play to begin the song
3. Watch the blue notes fall from the top of the screen toward the piano
4. Press the corresponding piano keys when the notes reach the red line (piano)
5. **NEW**: Successfully hit notes turn green and shoot upward!
6. Missed notes turn red and continue falling
7. Try to get the highest score possible across the full 88-key range!

## MIDI Note Numbers

The application now supports the **full 88-key piano range**:

### Piano Range
- **Lowest note**: A0 (MIDI 21)
- **Highest note**: C8 (MIDI 108)
- **Total keys**: 88 (52 white keys + 36 black keys)

### Common Reference Notes
- A0: 21 (lowest piano key)
- C4 (Middle C): 60
- D4: 62
- E4: 64
- F4: 65
- G4: 67
- A4: 69 (concert pitch reference)
- B4: 71
- C5: 72
- C8: 108 (highest piano key)

## 💡 Advanced Features

### MIDI Editor Advanced Features
- **Multi-track editing** - Create complex arrangements with different instruments
- **Piano roll visualization** - See notes on a timeline with precise editing
- **MIDI file compatibility** - Import/export standard MIDI files
- **Professional editing tools** - Quantize timing, transpose pitch, adjust velocity
- **Track properties** - Set instrument, volume, pan for each track
- **Grid-based editing** - Snap notes to musical beats (1/4, 1/8, 1/16, 1/32)
- **Command-line automation** - Script-friendly CLI for batch operations
- **Template creation** - Generate scales, chords, and progressions automatically

### Development Architecture
- **MIDINote** - Individual note representation with full MIDI properties
- **MIDITrack** - Track container with instrument and mixing properties  
- **MIDIProject** - Complete project with tempo, time signature, multiple tracks
- **MIDIEditor** - Main editor class with both GUI and CLI interfaces
- **Modular design** - Easy to extend with new features and formats

## License

Open source - feel free to modify and distribute.