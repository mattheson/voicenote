import sounddevice as sd
import numpy as np
from whispercpp import Whisper
import ffmpeg
import time
import os
from datetime import datetime
from scipy.io import wavfile
import openai
import json

# List all input devices
devices = sd.query_devices()
print("Input Devices:")
for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f"{i}: {device['name']}")

# Ask user to select an input device
while True:
    try:
        device_id = int(input("Please enter the ID of the device you want to use: "))
        if devices[device_id]['max_input_channels'] > 0:
            break
        else:
            print(f"Device ID {device_id} is not an input device. Please try again.")
    except (IndexError, ValueError):
        print("Invalid device ID. Please try again.")

# Set device
sd.default.device = device_id

# Define sample rate and duration (to be overwritten later)
sample_rate = 16000  # This could change based on your device
duration = 10  # Temporary duration

# Initialize buffer and recording flag
buffer = []
recording = False

# Define callback for the stream
def callback(indata, frames, time, status):
    global buffer
    if status:
        print(status)
    if recording:
        buffer.extend(indata[:, 0])

# Create stream
stream = sd.InputStream(callback=callback, channels=1, dtype='int16', samplerate=sample_rate)
stream.start()

# Initialize whisper
w = Whisper.from_pretrained("base.en")

# Prompt user for filename
filename = input("Enter a filename to save to (without extension): ")
    
if os.path.exists(f'{filename}.json'):
    # Load messages from .json file
    with open(f'{filename}.json', 'r') as f:
        messages = json.load(f)
else:
    # Initialize messages array
    messages = [
        {
            "role": "system",
            "content": "You are a note-taking service. Your response will in Markdown. Add, remove and modify the content of the file based on the input from the user. The user is using a speech-to-text transcription. Do not refer to yourself in the first person and do not add follow-ups. Always respond with ONLY the markdown file and nothing else."
        }
    ]

print('Press Enter to start/stop recording, q to quit')
while True:
    command = input()
    if command == '':
        if recording:
            # Stop recording
            recording = False
            print('Stopped recording')

            # Convert buffer into numpy array
            buffer = np.array(buffer, dtype=np.int16)
            
            # Transcribe the audio
            arr = buffer.astype(np.float32) / 32768.0
            transcription = w.transcribe(arr)
            print(f'Transcription: {transcription}')

            # Add transcription to messages
            messages.append({
                "role": "user",
                "content": transcription
            })

            # Get response from ChatGPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0,
            )
            response_content = response["choices"][0]["message"]["content"]

            # Append response to messages
            messages.append({
                "role": "assistant",
                "content": response_content
            })

            # Write response content to .md file
            with open(f'{filename}.md', 'w') as f:
                f.write(response_content)

            # Save messages array to .json file
            with open(f'{filename}.json', 'w') as f:
                json.dump(messages, f, indent=4)

            # Clear the buffer
            buffer = []
        else:
            # Start recording
            print('Started recording')
            recording = True
    elif command.lower() == 'q':
        # Quit
        break
    else:
        print('Invalid command')
stream.stop()
stream.close()