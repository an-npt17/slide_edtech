from flask import send_static_file, render_template
import sounddevice as sd
import soundfile as sf

# Define the constants for the audio recording parameters
SAMPLERATE = 44100  # Hertz
DURATION = 10  # seconds

# Create a class to encapsulate the audio recording functions and attributes
class AudioRecorder:
    def __init__(self):
        # Initialize the samplerate and duration attributes
        self.samplerate = SAMPLERATE
        self.duration = DURATION
    
    def start_recording(self):
        # Start recording using sounddevice library
        self.recording = sd.rec(int(self.duration * self.samplerate),
                                samplerate=self.samplerate,
                                channels=2)
    
    def stop_recording(self):
        # Stop recording using sounddevice library
        sd.stop()
    
    def play_recording(self):
        # Play the recording using sounddevice library
        sd.play(self.recording, self.samplerate)
    
    def save_recording(self, filename):
        # Save the recording to a wav file using soundfile library
        sf.write(filename, self.recording, self.samplerate)
    
    def display_recording_page(self):
        # Display the recording page using Flask app object
        return send_static_file('audio_rec.html')

    # Add any other methods for audio recording as needed

