import json
import numpy as np
import sounddevice as sd
from whispercpp import Whisper
import openai
import os

def choose_device():
    devices = sd.query_devices()
    print("Input Devices:")
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"{i}: {device['name']}")

    while True:
        try:
            device_id = int(input("Please enter the ID of the device you want to use: "))
            if devices[device_id]['max_input_channels'] > 0:
                return device_id
            else:
                print(f"Device ID {device_id} is not an input device. Please try again.")
        except (IndexError, ValueError):
            print("Invalid device ID. Please try again.")

def create_stream(callback, device_id, sample_rate=16000):
    sd.default.device = device_id
    stream = sd.InputStream(callback=callback, channels=1, dtype='int16', samplerate=sample_rate)
    stream.start()
    return stream

def load_messages(filename):
    if os.path.exists(f'{filename}.json'):
        with open(f'{filename}.json', 'r') as f:
            return json.load(f)
    else:
        return [
            {
                "role": "system",
                "content": "You are a note-taking program. Only respond in Markdown. The user is using a speech-to-text transcription. Do not communicate like a person. Notes can be added at the bottom if information is needed."
            }
        ]

def save_messages(filename, messages):
    with open(f'{filename}.json', 'w') as f:
        json.dump(messages, f, indent=4)

def transcribe_audio(buffer, whisper):
    arr = np.array(buffer, dtype=np.int16).astype(np.float32) / 32768.0
    return whisper.transcribe(arr)

def get_chat_gpt_response(messages):
    api_messages = [messages[0], messages[-2], messages[-1]] if len(messages) > 2 else messages
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=api_messages,
        temperature=0,
    )
    return response["choices"][0]["message"]["content"]

def write_markdown(filename, content):
    with open(f'{filename}.md', 'w') as f:
        f.write(content)

def run_recording_session():
    device_id = choose_device()
    whisper = Whisper.from_pretrained("base.en")
    filename = input("Enter a filename to save to (without extension): ")
    messages = load_messages(filename)

    buffer = []
    recording = False

    def callback(indata, frames, time, status):
        nonlocal buffer
        if status:
            print(status)
        if recording:
            buffer.extend(indata[:, 0])

    stream = create_stream(callback, device_id)

    print('Press Enter to start/stop recording, q to quit')
    while True:
        command = input()
        if command == '':
            if recording:
                recording = False
                print('Stopped recording')

                transcription = transcribe_audio(buffer, whisper)
                print(f'Transcription: {transcription}')
                messages.append({"role": "user", "content": transcription})

                response_content = get_chat_gpt_response(messages)
                messages.append({"role": "assistant", "content": response_content})

                write_markdown(filename, response_content)
                save_messages(filename, messages)

                buffer = []
            else:
                print('Started recording')
                recording = True
        elif command.lower() == 'q':
            break
        else:
            print('Invalid command')
    stream.stop()
    stream.close()

if __name__ == "__main__":
    run_recording_session()