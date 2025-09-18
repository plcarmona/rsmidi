#!/usr/bin/env python3
"""
Visual representation of the Synthesia clone interface
Generate ASCII art showing what the GUI would look like
"""

def show_synthesia_interface():
    """Generate ASCII representation of the Synthesia clone interface"""
    
    interface = """
╔══════════════════════════════════════════════════════════════════════════╗
║                           SYNTHESIA CLONE                                ║
║                        Piano Learning Application                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║  [Play] [Stop] [Load Song]              Score: 2500  Notes: 15/20 (3)   ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║                              🟦 E4                                       ║
║                                                                          ║
║                        🟦 C4    🟦 G4                                    ║
║                                                                          ║
║                  🟨 A4 (active)                                          ║
║                                                                          ║
║            🟩 F4 (hit)    🟥 D4 (missed)                                 ║
║                                                                          ║
║  ═══════════════════════════════════════════════════════════════════════ ║ ← Timeline
║  ┌─┐   ┌─┐   ┌─┐   ┌─┐   ┌─┐   ┌─┐   ┌─┐   ┌─┐                        ║
║  │C│ █ │D│ █ │E│   │F│ █ │G│ █ │A│ █ │B│   │C│                        ║
║  │4│ ■ │4│ ■ │4│   │4│ ■ │4│ ■ │4│ ■ │4│   │5│                        ║
║  └─┘   └─┘   └─┘   └─┘   └─┘   └─┘   └─┘   └─┘                        ║
║   a  w  s  e  d    f  t  g  y  h  u  j    k                            ║
╚══════════════════════════════════════════════════════════════════════════╝

LEGEND:
🟦 Blue notes = Upcoming notes falling down
🟨 Yellow notes = Active notes (play now!)  
🟩 Green notes = Successfully hit notes
🟥 Red notes = Missed notes
█ Black keys, ■ Black key labels
Timeline (red line) = Where notes should be played

KEYBOARD CONTROLS:
White keys: a s d f g h j k (C4 to C5)
Black keys: w e t y u (sharps/flats)

GAMEPLAY:
1. Notes fall from top to bottom
2. Press the corresponding key when note reaches the red timeline
3. Get points for hitting notes at the right time
4. Try to achieve the highest score possible!

FEATURES:
- Real-time score tracking
- Visual feedback for hits and misses
- Support for custom JSON song files
- Play/pause/stop controls
- Multiple sample songs included
"""
    
    print(interface)

def show_song_format():
    """Show the JSON song format"""
    print("\nSONG FILE FORMAT (JSON):")
    print("=" * 50)
    
    example = """{
  "title": "Mary Had a Little Lamb",
  "notes": [
    {"note": 64, "start_time": 0.0, "duration": 0.5, "velocity": 80},
    {"note": 62, "start_time": 0.5, "duration": 0.5, "velocity": 80},
    {"note": 60, "start_time": 1.0, "duration": 0.5, "velocity": 80}
  ]
}"""
    
    print(example)
    print("\nFIELD DESCRIPTIONS:")
    print("- note: MIDI note number (60=C4, 61=C#4, 62=D4, etc.)")
    print("- start_time: When the note should be played (in seconds)")
    print("- duration: How long the note lasts (optional, default 0.5)")
    print("- velocity: Note intensity 0-127 (optional, default 80)")

if __name__ == "__main__":
    print("SYNTHESIA CLONE - Visual Interface Preview")
    print("=" * 80)
    show_synthesia_interface()
    show_song_format()
    print("\nTo run the actual application:")
    print("python main.py          # GUI version (requires tkinter)")
    print("python console_demo.py  # Console version (text-based)")