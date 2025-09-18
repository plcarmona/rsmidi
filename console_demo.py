#!/usr/bin/env python3
"""
Console Demo of Synthesia Clone
A text-based demonstration of the piano learning application
"""

import json
import time
import threading
import os
import sys

class MIDINote:
    """Represents a MIDI note with timing information"""
    def __init__(self, note, velocity, start_time, duration=0.5):
        self.note = note
        self.velocity = velocity
        self.start_time = start_time
        self.duration = duration
        self.hit = False

class ConsoleSynthesiaDemo:
    """Console-based demonstration of the Synthesia clone"""
    
    def __init__(self):
        self.notes = []
        self.current_time = 0.0
        self.is_playing = False
        self.score = 0
        self.notes_hit = 0
        self.notes_missed = 0
        
        # Note names for display
        self.note_names = {
            60: 'C4', 61: 'C#4', 62: 'D4', 63: 'D#4', 64: 'E4', 65: 'F4',
            66: 'F#4', 67: 'G4', 68: 'G#4', 69: 'A4', 70: 'A#4', 71: 'B4', 72: 'C5'
        }
        
        self.load_sample_song()
    
    def load_sample_song(self):
        """Load the sample song"""
        self.notes = [
            MIDINote(64, 80, 0.0, 0.5),   # E4
            MIDINote(62, 80, 0.5, 0.5),   # D4  
            MIDINote(60, 80, 1.0, 0.5),   # C4
            MIDINote(62, 80, 1.5, 0.5),   # D4
            MIDINote(64, 80, 2.0, 0.5),   # E4
            MIDINote(64, 80, 2.5, 0.5),   # E4
            MIDINote(64, 80, 3.0, 1.0),   # E4
            MIDINote(62, 80, 4.5, 0.5),   # D4
            MIDINote(62, 80, 5.0, 0.5),   # D4
            MIDINote(62, 80, 5.5, 1.0),   # D4
            MIDINote(64, 80, 7.0, 0.5),   # E4
            MIDINote(67, 80, 7.5, 0.5),   # G4
            MIDINote(67, 80, 8.0, 1.0),   # G4
        ]
    
    def display_instructions(self):
        """Display game instructions"""
        print("=" * 60)
        print("SYNTHESIA CLONE - CONSOLE DEMO")
        print("=" * 60)
        print("Song: Mary Had a Little Lamb")
        print("")
        print("Instructions:")
        print("- Notes will appear with their timing")
        print("- Type the note name when prompted (e.g., 'C4', 'E4')")
        print("- Try to hit notes at the right time!")
        print("")
        print("Available notes in this song:")
        used_notes = set(note.note for note in self.notes)
        for note_num in sorted(used_notes):
            print(f"  {self.note_names.get(note_num, f'Note{note_num}')}")
        print("")
        print("Press Enter to start...")
        input()
    
    def run_demo(self):
        """Run the console demonstration"""
        self.display_instructions()
        
        print("\nStarting song in 3 seconds...")
        time.sleep(1)
        print("3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        print("GO!\n")
        
        start_time = time.time()
        last_update = start_time
        
        while True:
            current_real_time = time.time()
            self.current_time = current_real_time - start_time
            
            # Check for active notes
            active_notes = []
            for note in self.notes:
                if (note.start_time <= self.current_time <= note.start_time + note.duration 
                    and not note.hit):
                    active_notes.append(note)
            
            # Display active notes and get input
            if active_notes and current_real_time - last_update > 0.1:
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print(f"Time: {self.current_time:.1f}s | Score: {self.score} | "
                      f"Hit: {self.notes_hit} | Missed: {self.notes_missed}")
                print("-" * 50)
                
                print("ACTIVE NOTES:")
                for note in active_notes:
                    note_name = self.note_names.get(note.note, f'Note{note.note}')
                    time_left = note.start_time + note.duration - self.current_time
                    print(f"  -> {note_name} (time left: {time_left:.1f}s)")
                
                print("\nUpcoming notes:")
                upcoming = [n for n in self.notes 
                           if n.start_time > self.current_time and n.start_time < self.current_time + 2]
                for note in upcoming[:3]:
                    note_name = self.note_names.get(note.note, f'Note{note.note}')
                    time_until = note.start_time - self.current_time
                    print(f"  {note_name} in {time_until:.1f}s")
                
                if active_notes:
                    print(f"\nType note name to play (e.g., '{self.note_names.get(active_notes[0].note, 'C4')}'): ")
                
                last_update = current_real_time
            
            # Check for missed notes
            for note in self.notes:
                if (note.start_time + note.duration < self.current_time 
                    and not note.hit and note not in active_notes):
                    # Mark as missed
                    note.hit = True  # Prevent counting again
                    self.notes_missed += 1
            
            # Check if song is over
            if self.current_time > max(n.start_time + n.duration for n in self.notes) + 1:
                break
            
            # Simple input handling (non-blocking would be better but this works for demo)
            if active_notes:
                try:
                    # Use a timeout for input (Python 3.3+)
                    import select
                    import sys
                    
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        user_input = input().strip().upper()
                        
                        # Check if input matches any active note
                        for note in active_notes:
                            expected_name = self.note_names.get(note.note, '').upper()
                            if user_input == expected_name and not note.hit:
                                note.hit = True
                                self.score += 100
                                self.notes_hit += 1
                                print(f"HIT! +100 points ({expected_name})")
                                time.sleep(0.5)
                                break
                        else:
                            if user_input:
                                print(f"Wrong note: {user_input}")
                                time.sleep(0.3)
                
                except (ImportError, OSError):
                    # Fallback for systems without select
                    time.sleep(0.1)
            else:
                time.sleep(0.1)
        
        # Final score
        os.system('clear' if os.name == 'posix' else 'cls')
        print("=" * 60)
        print("SONG COMPLETE!")
        print("=" * 60)
        print(f"Final Score: {self.score}")
        print(f"Notes Hit: {self.notes_hit}/{len(self.notes)}")
        print(f"Notes Missed: {self.notes_missed}")
        accuracy = (self.notes_hit / len(self.notes)) * 100 if self.notes else 0
        print(f"Accuracy: {accuracy:.1f}%")
        
        if accuracy >= 90:
            print("\n🌟 EXCELLENT! Perfect performance!")
        elif accuracy >= 70:
            print("\n👍 GOOD JOB! Well done!")
        elif accuracy >= 50:
            print("\n👌 NOT BAD! Keep practicing!")
        else:
            print("\n💪 KEEP TRYING! Practice makes perfect!")
        
        print("\nThank you for trying the Synthesia Clone demo!")

def run_simple_demo():
    """Run a simpler demo that works on all systems"""
    print("=" * 60)
    print("SYNTHESIA CLONE - SIMPLE DEMO")
    print("=" * 60)
    print("This demonstrates the core functionality of our Synthesia clone.")
    print("")
    
    # Create sample notes
    notes = [
        MIDINote(60, 80, 0.0, 0.5),   # C4
        MIDINote(64, 80, 0.5, 0.5),   # E4  
        MIDINote(67, 80, 1.0, 0.5),   # G4
        MIDINote(72, 80, 1.5, 0.5),   # C5
    ]
    
    note_names = {60: 'C4', 64: 'E4', 67: 'G4', 72: 'C5'}
    
    print("Song preview: C4 -> E4 -> G4 -> C5")
    print("")
    
    score = 0
    for i, note in enumerate(notes, 1):
        note_name = note_names[note.note]
        print(f"Note {i}/4: Play {note_name}")
        print("Type the note name and press Enter:")
        
        user_input = input("> ").strip().upper()
        
        if user_input == note_name:
            print("✅ CORRECT! +100 points")
            score += 100
        else:
            print(f"❌ Wrong. Expected {note_name}, got {user_input}")
        
        print("-" * 30)
        time.sleep(0.5)
    
    print(f"\nFinal Score: {score}/400")
    accuracy = (score / 400) * 100
    print(f"Accuracy: {accuracy:.1f}%")
    print("\nThis demonstrates the basic note-matching gameplay!")

if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Simple Demo (works everywhere)")
    print("2. Advanced Demo (requires select module)")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "2":
            demo = ConsoleSynthesiaDemo()
            demo.run_demo()
        else:
            run_simple_demo()
            
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Thanks for trying!")
    except Exception as e:
        print(f"\nError: {e}")
        print("Running simple demo instead...")
        run_simple_demo()