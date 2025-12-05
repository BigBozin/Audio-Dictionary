Technical Documentation
Audio Dictionary - Technical Architecture
Overview
A Python-based desktop dictionary application with audio pronunciation capabilities, built using Pygame for the GUI and featuring both online and offline functionality.

Architecture
text
Audio Dictionary/
├── controller.py          # Main application controller (MVC)
├── model.py              # Data handling and business logic
├── view.py               # GUI rendering and user interface
├── tts_service.py        # Text-to-speech service
├── requirements.txt      # Python dependencies
└── data/
    ├── websters_english_dictionary.json  # Local dictionary database
    ├── search_history.json               # User search history
    └── settings.json                     # Application settings
Core Components
1. Controller (controller.py)
Responsibilities:

Orchestrates communication between Model and View

# Technical Documentation

Audio Dictionary — Technical Overview

This document describes the architecture, components, data flow, and operational details of the Audio Dictionary desktop application.

Table of contents
- Project structure
- Core components
- Data flow & search strategy
- Audio & TTS handling
- Threading and concurrency
- Data files and persistence
- Error handling and fallbacks
- Testing and debugging tips
- Deployment & maintenance

Project structure
--------------

Top-level layout (important files/folders):

- `main.py` — Entry point that initializes and runs the `DictionaryController`.
- `audio_dictionary/` — Main package containing source code:
  - `controller.py` — Application controller (connects Model and View).
  - `model.py` — Data access, search logic, caching, and TTS integration.
  - `view.py` — Pygame-based UI rendering and input handling.
  - `tts_service.py` — Text-to-speech generation and audio helper functions.
- `data/` — JSON files used for persistence:
  - `websters_english_dictionary.json` — Local dictionary for offline lookups.
  - `search_history.json` — Recent searches (kept to last 50 entries).
  - `settings.json` — User preferences and saved settings.

Core components
---------------

Controller (`controller.py`)
- Orchestrates user input, search flows, audio management, and settings.
- Maintains application state (running, audio flags, connectivity, etc.).
- Receives search requests from the view and delegates to the model, providing callbacks for results.

Model (`model.py`)
- Responsible for fetching and converting data from online and local sources.
- Contains enhanced local Webster JSON parsing and conversion to the app's display format.
- Caches recent lookups in memory to speed repeated queries.
- Manages search history persistence and saving online results back to the local dictionary.

View (`view.py`)
- Renders UI with Pygame and handles input events, scrolling, and interactive controls.
- Implements responsive layout, spinner loader, and audio control rendering.
- Provides settings UI and history view.

TTS Service (`tts_service.py`)
- Encapsulates text-to-speech generation (gTTS) and temporary file handling.
- Provides fallback and retry logic to improve reliability across network conditions.

Data flow & search strategy
---------------------------

Search behavior (high level):
1. When the user initiates a search the controller cancels previous audio/tts operations and shows a spinner.
2. The model attempts an online lookup first (if not in explicit offline mode):
   - A short HTTP timeout is used (e.g., 2–5s) to keep the UI responsive.
   - On success the API response is converted to the app format and optionally saved to the local dictionary.
3. If the online lookup fails (timeout, error, or not found), the model performs a local lookup in the Webster JSON.
   - If exact match found: returns formatted data.
   - If not found: a fuzzy match routine produces suggestions; the best suggestion may be returned with a `webster_suggestion` source.
4. Results are returned via a callback to the controller which updates history, triggers audio generation (if enabled), and updates the view.

Audio & TTS handling
--------------------

- Pronunciation audio sources:
  - Online API may provide an audio URL which the app downloads and plays.
  - Local words without an audio file use the app's TTS generator to produce a cached MP3.
- Playback is handled via `pygame.mixer` with separate threads monitoring playback to keep the UI responsive.
- TTS generation uses `gTTS` through `tts_service.py` and writes MP3 files to the system temp directory. Files are cleaned up after playback or kept cached (configurable).
- The controller supports canceling audio and TTS operations mid-process to quickly react to new user input.

Threading and concurrency
-------------------------

- UI (main) thread: Pygame rendering, event loop, and controller state updates.
- Worker threads:
  - Network requests (online API fetches)
  - Audio download and playback monitor
  - TTS generation
  - Background saving of local dictionary updates
- Synchronization is done with lightweight flags (e.g., `cancel_audio`, `cancel_tts`) and checks inside worker loops. Threads are started as daemons where appropriate to avoid blocking shutdown.

Data files and persistence
--------------------------

- `websters_english_dictionary.json` — primary offline dictionary. Loaded at startup and saved periodically when new online words are added.
- `search_history.json` — appended/updated on successful searches; capped to the most recent 50 entries.
- `settings.json` — saved and loaded via the controller (`_load_settings`/_`save_settings`).
- Temporary audio files created by TTS or online downloads are stored in the OS temporary directory and removed after playback (or when `stop_all_audio` is called).

Error handling and fallbacks
---------------------------

- Network failures automatically fall back to local searches and the UI displays a helpful message indicating offline/local mode.
- TTS and audio generation include retry/cancellation logic and will clean up partially created audio files on error.
- File operations (reads/writes) are guarded with try/except blocks and create directories if missing.

Testing and debugging tips
--------------------------

- Manual tests: verify search scenarios (online hit, online miss + local hit, suggestion path).
- Audio tests: verify play/pause/stop and TTS generation for local-only words.
- Connectivity tests: toggle `offline_mode` in settings and observe the behavior; run the small connectivity snippet in `README`.
- Debugging aids: add temporary logging prints or render diagnostic text in the UI (e.g., `content_height`, `scroll_offset`) to diagnose missing or clipped results.

Deployment & maintenance
------------------------

- Requirements: Python 3.8+, listed dependencies in `requirements.txt` (Pygame, requests, gTTS).
- Packaging: The app can be bundled with PyInstaller or similar tools for distribution as a native executable.
- Maintenance: periodically update `websters_english_dictionary.json` as new words are added, and ensure TTS/network dependencies are kept current.

Appendix: Important runtime knobs
--------------------------------

- `settings.json` keys worth noting:
  - `offline_mode` — force local-only behavior.
  - `auto_play_pronunciation` / `auto_speak_definition` — automation toggles for audio and TTS.
  - `audio_volume` — 0–100 integer for mixer volume.

- Cache tuning:
  - `DictionaryModel.cache_size` — in-memory cache size for search results.

If you want, I can also generate a short developer guide with typical debug commands, example words to test each code path, and a mini-checklist for release testing.
