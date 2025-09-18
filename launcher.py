#!/usr/bin/env python3
"""
MIDI Editor Launcher
Launch either the GUI or CLI version of the MIDI editor
"""

import sys
import os

def main():
    print("🎹 MIDI Editor Launcher 🎹")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--cli" or sys.argv[1] == "-c":
            print("Starting CLI mode...")
            from midi_editor import MIDIEditor
            editor = MIDIEditor(use_gui=False)
            editor.run()
            return
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print_help()
            return
    
    # Try GUI first
    try:
        import tkinter
        print("Starting GUI mode...")
        from midi_editor import MIDIEditor
        editor = MIDIEditor(use_gui=True)
        editor.run()
    except ImportError:
        print("GUI not available. Starting CLI mode...")
        from midi_editor import MIDIEditor
        editor = MIDIEditor(use_gui=False)
        editor.run()

def print_help():
    print("""
MIDI Editor - A comprehensive MIDI editing application

Usage: python launcher.py [options]

Options:
  --cli, -c     Force command-line interface mode
  --help, -h    Show this help message

Features:
  ✨ Multi-track MIDI editing
  ✨ Piano roll editor (GUI mode)
  ✨ Import/Export MIDI files
  ✨ JSON project format
  ✨ Note editing (create, modify, delete)
  ✨ Quantization and transposition
  ✨ Tempo and time signature control
  ✨ Full 88-key piano support

GUI Mode:
  - Visual piano roll editing
  - Drag and drop note editing
  - Timeline view with grid
  - Track management panel
  - Menu-driven interface

CLI Mode:
  - Text-based interface
  - All core editing features
  - Keyboard-friendly operation
  - Script-friendly automation

Examples:
  python launcher.py                  # Start with GUI if available
  python launcher.py --cli            # Force CLI mode
  python midi_editor.py --cli         # Direct CLI access
""")

if __name__ == "__main__":
    main()