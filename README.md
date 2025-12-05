
# Audio Dictionary

Audio Dictionary is a desktop Python application that provides word definitions, pronunciations, and audio playback. It works both online (using the Free Dictionary API) and offline (using a local Webster JSON dictionary). The app includes text-to-speech (TTS), search suggestions, history, and a responsive Pygame-based UI.

Core features
- Online-first search with local fallback (offline mode)
- Clean, readable definitions formatted for display
- Pronunciation audio from online sources or generated via TTS
- Text-to-speech for definitions (gTTS-based service)
- Search suggestions and fuzzy matching
- Search history with export capability
- Configurable settings (audio, theme, font size, suggestions)

Quick start
1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the application:

```powershell
python main.py
```

Project layout
- `main.py` — entry point that launches the application
- `audio_dictionary/` — application package
	- `controller.py` — main controller (MVC pattern)
	- `model.py` — data access, caching, and TTS integration
	- `view.py` — Pygame-based UI and rendering
	- `tts_service.py` — TTS helper and audio generation
- `data/` — JSON data files (local dictionary, history, settings)

Configuration & settings
- `data/settings.json` contains user preferences. Defaults include audio volume, theme, auto-play, and offline mode. The app reads and writes this file automatically.

Using the app
- Type a word into the input box and press the `Search` button or Enter.
- If the app is online it will try the free dictionary API first and fall back to the local Webster dictionary if needed.
- Use the Play/Pause/Stop audio controls to hear pronunciations or use the Speak button to have the definition read aloud.
- Open `Settings` to adjust preferences (themes, font size, offline mode).

Troubleshooting
- If the app reports offline but you have a working internet connection, try running a connectivity check:

```python
from audio_dictionary.model import DictionaryModel
m = DictionaryModel()
print(m.check_internet_connection())
```

- If audio fails to play, verify your system audio and that `pygame` can initialize the mixer.

Contributing
- Bug reports, feature requests, and pull requests are welcome. Please run the app locally and include logs or screenshots when filing issues.

License
- This repository does not include a license file by default. Add a license if you plan to publish or share this project widely.

Acknowledgements
- Uses the Free Dictionary API (https://dictionaryapi.dev) and gTTS for text-to-speech.
- 
