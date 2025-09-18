# Synthesia Clone

A Python implementation of a piano learning application inspired by Synthesia, now featuring a **full 88-key piano** and enhanced visual feedback!

## Features

- **Full 88-key piano keyboard** (A0 to C8) with falling notes
- **Enhanced visual feedback** - hit notes reverse direction and shoot upward
- Real-time note matching and scoring
- Support for custom songs via JSON files  
- Extended keyboard controls covering 3 octave ranges
- Score tracking and progress monitoring
- Play/pause/stop controls

## Requirements

- Python 3.6+ (uses tkinter for GUI)
- No external dependencies required for basic functionality

## Installation

1. Clone the repository
2. Run the application:
   ```bash
   python main.py
   ```

## Controls

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

## Song Format

Songs are stored as JSON files with the following structure:

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

## Sample Songs

The application includes a sample song file (`sample_song.json`) with "Mary Had a Little Lamb".

## How to Play

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

## Development

The main components are:

- `MIDINote`: Represents individual notes with timing
- `PianoKey`: Represents piano keys and their state
- `SynthesiaClone`: Main application class with game logic
- Rendering system for visual feedback
- Input handling for keyboard interaction

## License

Open source - feel free to modify and distribute.