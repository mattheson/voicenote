# voicenote
Voice-powered note taking with whispercpp/ChatGPT API.

This script couples well with a Markdown renderer that supports auto-refresh, [here's what I use.](https://chrome.google.com/webstore/detail/markdown-viewer/ckkdlimhmcjmikdlpkmbgfkaikojcbjk?hl=en)

## Usage
- Install the following libraries (`pip install ...`):
  - sounddevice, numpy, whispercpp, ffmpeg, scipy, openai
- You will need an OpenAI API key (https://platform.openai.com/account/api-keys).
- Setup the API key enviornmental variable: `export OPENAI_API_KEY='sk-...'`
- Just run `python3 main.py`.

## Todo
- Handle context better
  - Right now the request is in this format: `[system prompt, latest file version, transcription]`
  - There is probably a way better way of handling context
- Add GUI
- This might be a nice Obsidian plugin 
- Audio recording and handling of messages could be done better