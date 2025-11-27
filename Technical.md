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

Handles user input and application flow

Manages audio playback and TTS operations

Implements application settings

Key Features:

Threaded audio operations to prevent UI blocking

Progress tracking for long operations

Audio cancellation system

Settings management with persistence

2. Model (model.py)
Responsibilities:

Data retrieval from multiple sources

Search history management

Local dictionary caching

TTS audio generation

Data Sources:

Online API: Free Dictionary API (https://api.dictionaryapi.dev)

Local Dictionary: Webster's English Dictionary (100,000+ words)

Cache System: In-memory caching for performance

Key Algorithms:

Parallel search (online + local)

Fuzzy matching for suggestions

Search result caching

Audio file management

3. View (view.py)
Responsibilities:

GUI rendering using Pygame

User interaction handling

Theme management

Responsive layout

UI Components:

Search interface with suggestions

Word definition display with scrolling

History view with detailed entries

Settings panel with multiple options

Audio controls with visual feedback

4. TTS Service (tts_service.py)
Responsibilities:

Text-to-speech audio generation

Temporary file management

Multiple fallback attempts

Audio content creation

Technical Specifications
Audio System
Format: MP3

Library: pygame.mixer + gTTS

Features: Play, pause, stop, cancellation

Volume Control: 0-100% with persistence

Data Management
Local Storage: JSON files

Cache Size: 100 entries (configurable)

History Limit: 50 entries (FIFO)

File Encoding: UTF-8

Performance Optimizations
Parallel search execution

In-memory caching

Lazy loading of audio files

Progressive UI updates

Dependencies
python
# Core Dependencies (from requirements.txt)
pygame==2.5.0          # GUI framework
requests==2.31.0       # HTTP client for API calls
gTTS==2.3.2           # Google Text-to-Speech

# Python Standard Library
json, os, threading, time, tempfile, datetime, math
Installation & Setup
Quick Start
bash
# Install dependencies from requirements.txt
pip install -r requirements.txt

# Run the application
python controller.py
Development Setup
bash
# Create virtual environment (recommended)
python -m venv dictionary_env

# Activate virtual environment
# On Windows:
dictionary_env\Scripts\activate
# On macOS/Linux:
source dictionary_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python controller.py
Configuration
Settings File (settings.json)
json
{
  "auto_play_pronunciation": true,
  "auto_speak_definition": true,
  "clear_history_on_exit": false,
  "auto_export_history": false,
  "play_sound_effects": true,
  "font_size": "medium",
  "theme": "light",
  "audio_volume": 80,
  "search_suggestions": true,
  "offline_mode": false
}
File Structure Details
Data Files
websters_english_dictionary.json: Local word database

search_history.json: User search history with timestamps

settings.json: Application configuration

Temporary Files
Audio files are stored in system temp directory

Automatic cleanup after playback

No persistent audio storage

Threading Model
Main Thread
UI rendering and user input

Application state management

Worker Threads
Audio download and playback

TTS generation

Network requests

File operations

Error Handling
Network Errors
Automatic fallback to local dictionary

Connection timeout detection

Graceful degradation

Audio Errors
Multiple TTS generation attempts

Audio file validation

Cleanup on failure

File System Errors
Directory creation fallbacks

File corruption detection

Default value provisioning

Security Considerations
No sensitive data storage

Local file operations only

HTTPS for API calls

Input validation and sanitization

Performance Metrics
Search Response: < 2 seconds (cached), < 5 seconds (uncached)

Audio Generation: < 3 seconds

Memory Usage: ~50-100 MB

Startup Time: < 3 seconds

Browser Compatibility
N/A - Desktop application using Pygame

API Documentation
External APIs
Free Dictionary API: https://api.dictionaryapi.dev/api/v2/entries/en/{word}

Google TTS: Through gTTS library

Internal API (Controller Methods)
search_word(): Initiate word search

play_pronunciation(): Play word audio

speak_definition(): TTS for definitions

show_history(): Display search history

export_history(): Export to text file

Testing Strategy
Manual UI testing

Audio playback verification

Network connectivity testing

Error scenario testing

Performance benchmarking

Deployment
Requirements
Python 3.8+

Dependencies from requirements.txt

Internet connection (for online features)

Installation
bash
pip install -r requirements.txt
python controller.py
Maintenance
Regular Tasks
Clear temporary files

Monitor disk space for audio cache

Update local dictionary periodically

Backup search history

Troubleshooting
Audio issues: Check volume settings and file permissions

Search failures: Verify internet connection and API status

Performance: Clear cache and restart application
