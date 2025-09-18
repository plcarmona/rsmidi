# Synthesia Clone

A Python implementation of a piano learning application inspired by Synthesia.

## Features

- Visual piano keyboard with falling notes
- Real-time note matching and scoring
- Support for custom songs via JSON files  
- Keyboard controls for playing piano
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
- **White keys**: `a s d f g h j k` (C4-C5)
- **Black keys**: `w e t y u` (C#4, D#4, F#4, G#4, A#4)

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
3. Watch the blue notes fall from the top of the screen
4. Press the corresponding piano keys when the notes reach the red line (piano)
5. Hit notes turn green, missed notes turn red
6. Try to get the highest score possible!

## MIDI Note Numbers

Common MIDI note numbers for reference:
- C4 (Middle C): 60
- D4: 62
- E4: 64
- F4: 65
- G4: 67
- A4: 69
- B4: 71
- C5: 72

## Development

The main components are:

- `MIDINote`: Represents individual notes with timing
- `PianoKey`: Represents piano keys and their state
- `SynthesiaClone`: Main application class with game logic
- Rendering system for visual feedback
- Input handling for keyboard interaction

## License

Open source - feel free to modify and distribute.