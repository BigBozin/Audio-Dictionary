import pygame
import os
from pygame.locals import *
import requests
import threading
import time
import tempfile
import json
from audio_dictionary.tts_service import TextToSpeechService
from audio_dictionary.model import DictionaryModel
from audio_dictionary.view import DictionaryView

class DictionaryController:
    def __init__(self):
        self.model = DictionaryModel()
        self.view = DictionaryView()
        
        # Initialize pygame mixer for audio with proper settings
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Load settings
        self.settings_file = "data/settings.json"
        self.settings = self._load_settings()
        
        # Apply ALL settings from the loaded file
        self._apply_all_settings()

        # If settings requested offline mode but we have internet, temporarily prefer online
        try:
            if self.offline_mode:
                has_conn = self.model.check_internet_connection()
                if has_conn:
                    print("ℹ️ Settings specify offline mode, but internet is available — using online for this session")
                    # Temporarily override for this session (do not change saved settings)
                    self.offline_mode = False
                    self.model.set_offline_mode(False)
                    # Show wifi alert false so UI doesn't show offline banner
                    self.show_wifi_alert = False
        except Exception as e:
            print(f"⚠️ Connectivity check at startup failed: {e}")
        
        self.running = True
        self.audio_available = False
        self.current_audio_url = None
        self.data_source = "online"
        self.show_wifi_alert = False
        self.current_word_data = None
        
        # Enhanced audio states
        self.audio_playing = False
        self.audio_paused = False
        self.audio_loading = False
        self.audio_downloaded = False
        self.audio_file_path = None
        
        # TTS states
        self.tts_speaking = False
        self.tts_loading = False
        
        # Audio cancellation flags and thread tracking
        self.cancel_audio = False
        self.cancel_tts = False
        self.current_audio_thread = None
        self.current_tts_thread = None
        
        # Store button rects for click detection
        self.search_rect = None
        self.history_rect = None
        self.audio_rects = {}
        self.settings_rect = None
        self.settings_close_rect = None
        
        # Progress tracking
        self.progress_value = 0
        self.progress_max = 100
        self.progress_message = ""
        # Track internet connectivity state
        self.has_connection = True
        
        # Apply volume setting
        self._apply_volume_setting()
    
    def _load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        # Default settings
        return {
            'auto_play_pronunciation': True,
            'auto_speak_definition': True,
            'clear_history_on_exit': False,
            'auto_export_history': False,
            'play_sound_effects': True,
            'font_size': 'medium',
            'theme': 'light',
            'audio_volume': 80,
            'search_suggestions': True,
            'offline_mode': False,
            'auto_complete': True
        }
    
    def _apply_all_settings(self):
        """Apply all settings to both view and controller"""
        # Apply to view first
        self.view.set_settings(self.settings)
        
        # Apply to controller
        self.auto_play_pronunciation = self.settings.get('auto_play_pronunciation', True)
        self.auto_speak_definition = self.settings.get('auto_speak_definition', True)
        self.clear_history_on_exit = self.settings.get('clear_history_on_exit', False)
        self.auto_export_history = self.settings.get('auto_export_history', False)
        self.play_sound_effects = self.settings.get('play_sound_effects', True)
        self.search_suggestions = self.settings.get('search_suggestions', True)
        self.offline_mode = self.settings.get('offline_mode', False)
        
        # Apply to model
        self.model.set_offline_mode(self.offline_mode)
        self.model.set_search_suggestions(self.search_suggestions)
        
        print("All settings applied:")
        print(f"  Auto-play pronunciation: {self.auto_play_pronunciation}")
        print(f"  Auto-speak definition: {self.auto_speak_definition}")
        print(f"  Play sound effects: {self.play_sound_effects}")
        print(f"  Audio volume: {self.settings.get('audio_volume', 80)}%")
        print(f"  Auto-export history: {self.auto_export_history}")
        print(f"  Search suggestions: {self.search_suggestions}")
        print(f"  Offline mode: {self.offline_mode}")
        print(f"  Auto-complete: {self.settings.get('auto_complete', True)}")
    
    def _save_settings(self):
        """Save settings to file"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print("Settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _apply_volume_setting(self):
        """Apply audio volume setting"""
        volume = self.settings.get('audio_volume', 80) / 100.0
        pygame.mixer.music.set_volume(volume)
        print(f"Audio volume set to: {volume * 100}%")
    
    def _play_sound_effect(self, sound_type):
        """Play sound effects if enabled"""
        if self.play_sound_effects:
            try:
                # You can add actual sound files here
                if sound_type == "click":
                    # Play a simple beep for click
                    print("Click sound effect played")
                elif sound_type == "success":
                    # Play success sound
                    print("Success sound effect played")
                elif sound_type == "error":
                    # Play error sound
                    print("Error sound effect played")
            except Exception as e:
                print(f"Error playing sound effect: {e}")
    
    def run(self):
        """Main application loop"""
        # Show splash screen
        self.view.show_splash_screen(2)
        
        # Apply initial settings to view
        self.view.set_auto_play_settings(
            self.auto_play_pronunciation,
            self.auto_speak_definition
        )
        
        # Main game loop
        clock = pygame.time.Clock()
        last_connection_check = 0
        
        while self.running:
            current_time = time.time()
            
            # Check internet connection every 10 seconds (unless in offline mode)
            # Check internet connection every 10 seconds
            if current_time - last_connection_check > 10:
                has_connection = False
                try:
                    has_connection = self.model.check_internet_connection()
                except Exception:
                    has_connection = False
                last_connection_check = current_time

                # Show offline/notification when explicitly in offline mode or when connection missing
                if self.offline_mode:
                    self.show_wifi_alert = True
                else:
                    self.show_wifi_alert = not has_connection
                # Save current connectivity state for view usage
                self.has_connection = has_connection
        
            
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    self._handle_exit()
                    self.running = False
                    self.stop_all_audio()
                
                elif event.type == VIDEORESIZE:
                    self.view.handle_resize(event)
                
                elif event.type == MOUSEBUTTONDOWN:
                    if self.view.showing_settings:
                        # Handle settings window clicks
                        result = self.view.handle_settings_click(event.pos)
                        self._handle_settings_action(result)
                    elif self.view.showing_history:
                        # Handle history view clicks
                        result = self.view.handle_history_click(event.pos)
                        self._handle_history_action(result)
                    else:
                        self.handle_mouse_click(event.pos)
                    # Handle scroll events for all views
                    self.view.handle_scroll_offset(event)
                
                elif event.type == MOUSEBUTTONUP:
                    self.view.handle_scroll_offset(event)
                
                elif event.type == MOUSEMOTION:
                    self.view.handle_scroll_offset(event)
                    # Update mouse position for hover effects
                    self.view.mouse_pos = event.pos
                
                elif event.type == KEYDOWN:
                    self.handle_keydown(event)
            
            # Update audio state in view
            self.view.set_audio_state(
                playing=self.audio_playing,
                paused=self.audio_paused,
                loading=self.audio_loading,
                tts_loading=self.tts_loading
            )
            
            # Update progress bar - USE SPINNER METHODS
            self.update_progress(self.progress_value, self.progress_max, self.progress_message)
            
            # Prepare offline/connection message to show (string or False)
            wifi_message = False
            if self.show_wifi_alert:
                if self.offline_mode:
                    wifi_message = "📴 Offline mode enabled — using local dictionary"
                else:
                    wifi_message = "⚠️ No internet connection — using local dictionary"

            # Draw interface (pass wifi_message to allow custom alert text)
            search_rect, history_rect, audio_rects, settings_close_rect = self.view.draw_main_interface(
                None,
                self.audio_available,
                self.data_source,
                self.model.get_local_word_count(),
                self.model.get_dictionary_source(),
                wifi_message,
                self.has_connection
            )
            
            # Store button rects for click detection
            self.search_rect = search_rect
            self.history_rect = history_rect
            self.audio_rects = audio_rects
            self.settings_rect = self.view.settings_rect  # Get from view
            self.settings_close_rect = settings_close_rect
            
            # (Notification drawing is handled by the view via the `show_wifi_alert` / message passed above)
            
            pygame.display.flip()
            clock.tick(60)
        
        # Clean up
        self.stop_all_audio()
        pygame.quit()
    
    def _handle_exit(self):
        """Handle application exit"""
        if self.clear_history_on_exit:
            self.model.clear_history()
            print("History cleared on exit")
        
        if self.auto_export_history:
            success = self.export_history()
            if success:
                print("History auto-exported on exit")
            else:
                print("Failed to auto-export history on exit")
    
    def _handle_settings_action(self, action):
        """Handle settings window actions"""
        if action == 'save':
            # Save settings
            new_settings = self.view.get_settings()
            self.settings.update(new_settings)
            self._save_settings()
            
            # Apply ALL settings
            self._apply_all_settings()
            
            self.view.show_main_view()
            print("Settings saved and applied")
            
        elif action == 'reset':
            # Reset to default settings
            default_settings = {
                'auto_play_pronunciation': True,
                'auto_speak_definition': True,
                'clear_history_on_exit': False,
                'auto_export_history': False,
                'play_sound_effects': True,
                'font_size': 'medium',
                'theme': 'light',
                'audio_volume': 80,
                'search_suggestions': True,
                'offline_mode': False,
                'auto_complete': True
            }
            self.view.set_settings(default_settings)
            print("Settings reset to defaults")     
        elif action == 'cancel':
            # Cancel without saving - reload original settings
            self.view.set_settings(self.settings)
            self.view.show_main_view()
            print("Settings changes cancelled")
            
        elif action in ['toggle', 'volume', 'font_size', 'theme']:
            # Settings were updated in the view, play sound effect
            self._play_sound_effect("click")
            
            # If volume was changed, apply it immediately
            if action == 'volume':
                self._apply_volume_setting()
    
    def _handle_history_action(self, action):
        """Handle history view actions"""
        if action == 'back':
            # Go back to history list from details view
            self.view.selected_history_item = None
            self.view.scroll_offset = 0
            self._play_sound_effect("click")
        elif action == 'clear_history':
            # Clear history from history view
            self.clear_search_history()
            self._play_sound_effect("click")
        elif action == 'back_to_main':
            # Go back to main view from history
            self.view.show_main_view()
            self._play_sound_effect("click")
        elif action and action.startswith('item_'):
            # Show history item details
            item_index = int(action.split('_')[1])
            self.view.selected_history_item = item_index
            self.view.scroll_offset = 0
            self._play_sound_effect("click")
    
    def handle_mouse_click(self, pos):
        """Handle mouse click events"""
        # Play sound effect for click
        self._play_sound_effect("click")
        
        # Check settings button click
        if hasattr(self, 'settings_rect') and self.settings_rect and self.settings_rect.collidepoint(pos):
            self.view.show_settings()
            print("Settings button clicked")
            return
        
        # Check settings close button
        if hasattr(self, 'settings_close_rect') and self.settings_close_rect and self.settings_close_rect.collidepoint(pos):
            self.view.show_main_view()
            print("Settings close button clicked")
            return
        
        # Check if input box was clicked
        if self.view.input_box.collidepoint(pos):
            self.view.active = True
            self.view.cursor_visible = True
            self.view.cursor_timer = time.time()
        else:
            self.view.active = False
            self.view.show_suggestions = False
        
        # Check auto-suggestion clicks
        if self.view.show_suggestions:
            suggestion = self.view.handle_suggestion_click(pos)
            if suggestion:
                self.view.input_text = suggestion
                self.view.cursor_position = len(suggestion)
                self.view.show_suggestions = False
                self._play_sound_effect("click")
                return
        
        # Check search button click
        if hasattr(self, 'search_rect') and self.search_rect and self.search_rect.collidepoint(pos):
            self.search_word()
        
        # Check history button click
        if hasattr(self, 'history_rect') and self.history_rect and self.history_rect.collidepoint(pos):
            self.show_history()
        
        # Check audio button clicks
        if hasattr(self, 'audio_rects') and self.audio_rects and self.current_word_data and not self.view.showing_history:
            if 'play' in self.audio_rects and self.audio_rects['play'].collidepoint(pos):
                if not self.audio_playing and not self.audio_loading:
                    self.play_pronunciation()
                elif self.audio_playing:
                    self.pause_pronunciation()
            
            if 'stop' in self.audio_rects and self.audio_rects['stop'].collidepoint(pos):
                self.stop_pronunciation()
            
            if 'speak' in self.audio_rects and self.audio_rects['speak'].collidepoint(pos):
                if not self.tts_speaking and not self.tts_loading:
                    self.speak_definition()
        
        # Check suggestion button clicks
        if self.view.suggested_words and not self.view.showing_history and not self.view.showing_settings:
            suggested_word = self.view.handle_suggestion_click(pos)
            if suggested_word:
                self.view.input_text = suggested_word
                self.view.cursor_position = len(suggested_word)
                self.search_word()
                self._play_sound_effect("click")
    
    def handle_keydown(self, event):
        """Handle keyboard events"""
        if self.view.active:
            # First handle auto-suggestion navigation
            if self.view.handle_suggestion_navigation(event):
                self._play_sound_effect("click")
                return
            
            # Then handle text input and cursor movement
            result = self.view.handle_text_input(event)
            if result == 'update_suggestions':
                # Trigger auto-suggestions update
                self.update_auto_suggestions()
            elif result:
                return  # Text was handled
            elif event.key == K_RETURN:
                self.search_word()
                self._play_sound_effect("click")
            elif event.key == K_ESCAPE:
                if self.view.showing_history:
                    if self.view.selected_history_item is not None:
                        # Go back to history list from details
                        self.view.selected_history_item = None
                        self.view.scroll_offset = 0
                    else:
                        # Go back to main view from history list
                        self.view.show_main_view()
                elif self.view.showing_settings:
                    self.view.show_main_view()
    
    def update_auto_suggestions(self):
        """Update auto-suggestions based on current input"""
        if (self.view.settings_options.get('auto_complete', True) and 
            len(self.view.input_text) > 1):
            # Get suggestions from the model
            word = self.view.input_text.lower()
            suggestions = self.model.get_auto_suggestions(word)
            self.view.set_auto_suggestions(suggestions)
        else:
            self.view.show_suggestions = False
    
    def search_word(self):
        """Search for a word in the dictionary - IMPROVED: Properly cancels previous audio"""
        word = self.view.input_text.strip()
        if word:
            print(f"🔍 Searching for: '{word}'")
            
            # CANCEL ALL PREVIOUS AUDIO OPERATIONS FIRST
            self.cancel_all_audio_operations()
            
            # Reset progress and start new search
            self.start_progress("Searching...")
            self.audio_available = False
            self.current_word_data = None
            self.stop_all_audio()
            self.view.show_main_view()
            self.view.show_suggestions = False  # Hide suggestions during search
            
            # Reset audio states
            self.audio_loading = False
            self.audio_downloaded = False
            self.audio_file_path = None
            self.current_audio_url = None
            
            # Use search suggestions if enabled
            use_suggestions = self.search_suggestions
            print(f"Searching with suggestions: {use_suggestions}")
            
            # Start the search
            self.model.fetch_word_data(word, self.on_word_data_received, use_suggestions=use_suggestions)
    
    def cancel_all_audio_operations(self):
        """Cancel all ongoing audio operations and threads"""
        print("🛑 Cancelling all audio operations...")
        
        # Set cancellation flags
        self.cancel_audio = True
        self.cancel_tts = True
        
        # Stop any playing audio immediately
        self.stop_all_audio()
        
        # Wait a brief moment for threads to respond to cancellation
        time.sleep(0.1)
        
        # Reset cancellation flags
        self.cancel_audio = False
        self.cancel_tts = False
        
        # Reset audio states
        self.audio_loading = False
        self.tts_loading = False
        self.audio_playing = False
        self.tts_speaking = False
        self.audio_paused = False
        
        print("✅ Audio operations cancelled")
    
    def start_progress(self, message="Loading..."):
        """Start progress bar animation"""
        self.progress_value = 0
        self.progress_max = 100
        self.progress_message = message
        self.view.start_spinner(message)
    
    def update_progress(self, value, max_value=100, message=None):
        """Update progress bar"""
        self.progress_value = value
        self.progress_max = max_value
        if message:
            self.progress_message = message
        self.view.set_spinner_progress(value, max_value, message)
    
    def stop_progress(self):
        """Stop progress bar animation"""
        self.progress_value = 100
        # Small delay to show completion
        time.sleep(0.2)
        self.view.stop_spinner()
    
    def show_history(self):
        """Show search history"""
        history_data = self.model.get_search_history()
        self.view.set_history_data(history_data)
        self.view.scroll_offset = 0
    
    def on_word_data_received(self, success, data, audio_url, source):
        """Callback when word data is received - MODIFIED FOR ONLINE-FIRST PRIORITY"""
        self.stop_progress()
        self.data_source = source
        
        if success:
            self.current_word_data = data
            self.current_audio_url = audio_url
            
            # Set audio available based on the data
            if data and len(data) > 0:
                has_audio = data[0].get('has_audio', False)
                audio_available = data[0].get('audio_available', False)
                self.audio_available = has_audio or audio_available or (audio_url is not None)
            else:
                self.audio_available = audio_url is not None
                
            self.view.set_word_data(data, source)
            print(f"✅ Word data loaded successfully from {source}")
            
            # ADD WORD TO HISTORY WITH ACTUAL DATA
            word = self.view.input_text.strip()
            if word and data:
                try:
                    self.model.add_to_history(word, source, data)
                    print(f"📝 Added '{word}' to search history with data")
                except Exception as e:
                    print(f"⚠️ Error adding to history: {e}")
            
            # AUTO-GENERATE AUDIO AFTER SUCCESSFUL SEARCH
            self.auto_generate_audio()
            
            # Play success sound effect
            self._play_sound_effect("success")
            
        else:
            # Check if we have suggestions in the data
            if isinstance(data, str) and "Did you mean" in data:
                # Extract suggested words from the error message
                import re
                suggestions = re.findall(r"'([^']*)'", data)
                if suggestions:
                    self.view.set_suggested_words(suggestions)
                    print(f"💡 Showing suggestions: {suggestions}")
                else:
                    self.view.show_error(data)
            else:
                # If no internet and offline search also failed
                if self.data_source == "offline" and not self.model.check_internet_connection():
                    error_msg = "No internet connection and word not found in local dictionary"
                    self.view.show_error(error_msg)
                else:
                    self.view.show_error(data)
                    
            self.audio_available = False
            self.current_word_data = None
            self.view.set_word_data(None)
            # Play error sound effect
            self._play_sound_effect("error")
    
    def auto_generate_audio(self):
        """Automatically generate audio when word is successfully searched"""
        if not self.current_word_data:
            return
            
        print("🎵 Auto-generating audio for searched word...")
        
        # Auto-play pronunciation if available and enabled
        if self.auto_play_pronunciation and self.audio_available:
            print("🔊 Auto-playing pronunciation...")
            # Small delay to ensure UI is updated
            threading.Timer(0.5, self.play_pronunciation).start()
        
        # Auto-speak definition if enabled
        if self.auto_speak_definition:
            delay = 3 if self.audio_available else 1
            print(f"🗣️ Auto-speaking definition in {delay} seconds...")
            threading.Timer(delay, self.speak_definition).start()

    def play_pronunciation(self):
        """Play pronunciation audio for ANY word (online or local)"""
        if self.current_word_data and not self.audio_loading:
            try:
                # Check if we have cached TTS audio (works for both online and local words)
                audio_path = None
                if self.current_word_data and len(self.current_word_data) > 0:
                    audio_path = self.current_word_data[0].get('audio_path')
                
                # Check if audio is available (either from online API or TTS)
                has_audio = self.current_word_data[0].get('has_audio', False) if self.current_word_data else False
                audio_available = self.current_word_data[0].get('audio_available', False) if self.current_word_data else False
                
                if audio_path and os.path.exists(audio_path):
                    # Play cached TTS audio (works for both online and local words)
                    print(f"🔊 Playing cached TTS audio: {audio_path}")
                    self.audio_loading = False
                    self.audio_playing = True
                    self.audio_paused = False
                    
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    
                    # Start playback monitoring in a separate thread
                    self.current_audio_thread = threading.Thread(target=self._wait_for_playback, daemon=True)
                    self.current_audio_thread.start()
                    
                elif (has_audio or audio_available) and self.data_source in ["webster", "webster_suggestion", "not_found"]:
                    # For locally found words without cached audio, generate it on the fly
                    print("🎵 Generating TTS audio for local word...")
                    self.audio_loading = True
                    self.audio_playing = False
                    self.audio_paused = False
                    
                    # Generate audio in a separate thread
                    self.current_audio_thread = threading.Thread(target=self._generate_and_play_audio, daemon=True)
                    self.current_audio_thread.start()
                    
                elif self.current_audio_url and self.audio_available and self.data_source == "online":
                    # Download and play from online API (original behavior)
                    self.audio_loading = True
                    self.audio_playing = False
                    self.audio_paused = False
                    print(f"📥 Downloading pronunciation from: {self.current_audio_url}")
                    self.current_audio_thread = threading.Thread(target=self._download_and_play_pronunciation, daemon=True)
                    self.current_audio_thread.start()
                else:
                    print("❌ No pronunciation audio available")
                    
            except Exception as e:
                print(f"❌ Error playing pronunciation audio: {e}")
                self.audio_loading = False
        elif self.audio_paused:
            pygame.mixer.music.unpause()
            self.audio_playing = True
            self.audio_paused = False
            print("⏯️ Resumed pronunciation audio")

    def _generate_and_play_audio(self):
        """Generate TTS audio for local words and play it"""
        try:
            if not self.current_word_data or self.cancel_audio:
                return
                
            word = self.current_word_data[0].get('word', '')
            print(f"🎵 Generating TTS audio for: {word}")
            
            # Use the model's TTS service to generate audio
            audio_path = self.model._generate_word_audio(word, self.current_word_data[0])
            
            # Check if audio was cancelled
            if self.cancel_audio:
                print(f"🛑 Audio generation cancelled for: {word}")
                if audio_path and os.path.exists(audio_path):
                    try:
                        os.unlink(audio_path)
                    except:
                        pass
                return
            
            if audio_path and os.path.exists(audio_path):
                # Update the current word data with the new audio path
                for entry in self.current_word_data:
                    entry['audio_path'] = audio_path
                
                print("✅ TTS audio generated, now playing...")
                self.audio_file_path = audio_path
                self.audio_downloaded = True
                self.audio_loading = False
                
                # Check again for cancellation before playing
                if self.cancel_audio:
                    print("🛑 Audio playback cancelled before starting")
                    return
                
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                self.audio_playing = True
                
                # Monitor playback with cancellation check
                while (pygame.mixer.music.get_busy() and 
                       self.audio_playing and 
                       not self.cancel_audio):
                    pygame.time.wait(100)
                
                if not self.cancel_audio:
                    self.audio_playing = False
                    self.audio_paused = False
                    print("✅ TTS audio finished")
                else:
                    print("🛑 TTS audio playback cancelled")
            else:
                print("❌ Failed to generate TTS audio")
                self.audio_loading = False
                
        except Exception as e:
            print(f"❌ Error generating and playing TTS audio: {e}")
            self.audio_playing = False
            self.audio_paused = False
            self.audio_loading = False
    
    def pause_pronunciation(self):
        """Pause currently playing pronunciation audio"""
        if self.audio_playing and not self.audio_paused:
            pygame.mixer.music.pause()
            self.audio_paused = True
            self.audio_playing = False
            print("⏸️ Pronunciation audio paused")
    
    def stop_pronunciation(self):
        """Stop currently playing pronunciation audio"""
        if self.audio_playing or self.audio_paused or self.audio_loading:
            pygame.mixer.music.stop()
            self.audio_playing = False
            self.audio_paused = False
            self.audio_loading = False
            print("⏹️ Pronunciation audio stopped")
    
    def speak_definition(self):
        """Speak ONLY what is displayed on the interface - no extra content"""
        if self.current_word_data and not self.tts_speaking and not self.tts_loading:
            try:
                # Stop any ongoing pronunciation first
                self.stop_pronunciation()
                
                word = self.current_word_data[0].get('word', '')
                phonetic = self.current_word_data[0].get('phonetic', '')
                
                # Build speech text to match EXACTLY what's shown on screen
                speech_parts = []
                
                # Add word and phonetic (exactly as displayed)
                speech_parts.append(f"The word is {word}")
                if phonetic:
                    speech_parts.append(f"pronounced {phonetic}")
                
                # Add meanings and definitions (only what's displayed)
                for i, meaning in enumerate(self.current_word_data[0].get('meanings', [])[:3]):  # Only first 3 meanings like display
                    part_of_speech = meaning.get('partOfSpeech', '')
                    
                    if part_of_speech:
                        speech_parts.append(f"As a {part_of_speech}")
                    
                    # Add definitions (only first 2 per meaning like display)
                    for j, definition in enumerate(meaning.get('definitions', [])[:2]):
                        def_text = definition.get('definition', '')
                        if def_text:
                            speech_parts.append(f"Definition {j+1}: {def_text}")
                        
                        # Add examples (only if displayed)
                        example_text = definition.get('example', '')
                        if example_text:
                            speech_parts.append(f"Example: {example_text}")
                    
                    # Add synonyms (only if displayed and limited to 5 like display)
                    synonyms = meaning.get('synonyms', [])
                    if synonyms:
                        syn_text = ", ".join(synonyms[:5])
                        speech_parts.append(f"Synonyms: {syn_text}")
                    
                    # Add antonyms (only if displayed and limited to 5 like display)
                    antonyms = meaning.get('antonyms', [])
                    if antonyms:
                        ant_text = ", ".join(antonyms[:5])
                        speech_parts.append(f"Antonyms: {ant_text}")
                
                # Combine all parts
                speech_text = ". ".join(speech_parts)
                
                print(f"🗣️ Speaking EXACTLY what's displayed for: {word}")
                print(f"📝 Speech text: {speech_text[:100]}...")  # Log first 100 chars
                
                self.tts_loading = True
                self.tts_speaking = False
                
                # Start TTS in a separate thread
                self.current_tts_thread = threading.Thread(target=self._speak_text_with_gtts, args=(speech_text,), daemon=True)
                self.current_tts_thread.start()
                
            except Exception as e:
                print(f"❌ Error in text-to-speech: {e}")
                self.tts_loading = False
    
    def _speak_text_with_gtts(self, text):
        """Speak text using Google TTS with multiple attempts"""
        try:
            # Check for cancellation before starting
            if self.cancel_tts:
                print("🛑 TTS generation cancelled before starting")
                return
                
            # Use the model's TTS service for reliable generation
            audio_path = self.model.tts_service.generate_definition_audio("definition", text)
            
            # Check if TTS was cancelled
            if self.cancel_tts:
                print("🛑 TTS generation cancelled")
                if audio_path and os.path.exists(audio_path):
                    try:
                        os.unlink(audio_path)
                    except:
                        pass
                return
            
            if audio_path and os.path.exists(audio_path):
                # Check again for cancellation before playing
                if self.cancel_tts:
                    print("🛑 TTS playback cancelled before starting")
                    return
                    
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                self.tts_speaking = True
                
                # Monitor playback with cancellation check
                while (pygame.mixer.music.get_busy() and 
                       self.tts_speaking and 
                       not self.cancel_tts):
                    pygame.time.wait(100)
                    
                if not self.cancel_tts:
                    print("✅ TTS finished playing")
                else:
                    print("🛑 TTS playback cancelled")
                    
        except Exception as e:
            print(f"❌ Google TTS error: {e}")
        finally:
            self.tts_speaking = False
            self.tts_loading = False
    
    def _wait_for_playback(self):
        """Wait for audio playback to finish with cancellation support"""
        try:
            while (pygame.mixer.music.get_busy() and 
                   self.audio_playing and 
                   not self.cancel_audio):
                pygame.time.wait(100)
            
            if not self.cancel_audio:
                self.audio_playing = False
                self.audio_paused = False
                print("✅ Audio playback finished")
            else:
                print("🛑 Audio playback cancelled")
        except Exception as e:
            print(f"❌ Error waiting for playback: {e}")
            self.audio_playing = False
            self.audio_paused = False
    
    def _download_and_play_pronunciation(self):
        """Download and play pronunciation audio file"""
        try:
            print(f"📥 Downloading audio from: {self.current_audio_url}")
            response = requests.get(self.current_audio_url, timeout=30)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                    temp_file.write(response.content)
                    temp_path = temp_file.name
                
                print("✅ Audio downloaded, now playing...")
                self.audio_file_path = temp_path
                self.audio_downloaded = True
                self.audio_loading = False
                
                # Check for cancellation before playing
                if self.cancel_audio:
                    print("🛑 Audio playback cancelled before starting")
                    return
                
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                self.audio_playing = True
                
                # Monitor playback with cancellation check
                while (pygame.mixer.music.get_busy() and 
                       self.audio_playing and 
                       not self.cancel_audio):
                    pygame.time.wait(100)
                
                if not self.cancel_audio:
                    self.audio_playing = False
                    self.audio_paused = False
                    print("✅ Pronunciation audio finished")
                else:
                    print("🛑 Pronunciation audio cancelled")
                    
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
            self.audio_playing = False
            self.audio_paused = False
            self.audio_loading = False
    
    def _cleanup_audio_file(self):
        """Clean up downloaded audio file"""
        if self.audio_file_path and os.path.exists(self.audio_file_path):
            try:
                os.unlink(self.audio_file_path)
                self.audio_file_path = None
                self.audio_downloaded = False
                print("🧹 Cleaned up audio file")
            except:
                pass
    
    def cancel_all_audio(self):
        """Cancel all ongoing audio operations"""
        print("🛑 Cancelling all audio operations...")
        
        # Set cancellation flags
        self.cancel_audio = True
        self.cancel_tts = True
        
        # Stop any playing audio
        self.stop_all_audio()
        
        # Reset cancellation flags after a short delay
        def reset_cancel_flags():
            time.sleep(0.2)  # Small delay to ensure cancellation is processed
            self.cancel_audio = False
            self.cancel_tts = False
            print("✅ Audio cancellation flags reset")
        
        threading.Thread(target=reset_cancel_flags, daemon=True).start()
    
    def stop_all_audio(self):
        """Stop all audio playback"""
        self.stop_pronunciation()
        if self.tts_speaking or self.tts_loading:
            pygame.mixer.music.stop()
            self.tts_speaking = False
            self.tts_loading = False
        self._cleanup_audio_file()

    def clear_search_history(self):
        """Clear all search history"""
        self.model.clear_history()
        if self.view.showing_history:
            self.show_history()
        print("🗑️ Search history cleared")

    def export_history(self):
        """Export search history to file"""
        try:
            history_dir = os.path.join(os.path.expanduser("~"), "DictionaryHistory")
            os.makedirs(history_dir, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(history_dir, f"dictionary_history_{timestamp}.txt")
            
            history = self.model.get_search_history()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Dictionary Search History\n")
                f.write("=" * 30 + "\n\n")
                
                for i, entry in enumerate(reversed(history), 1):
                    f.write(f"{i}. {entry['word']} ({entry['timestamp']})\n")
                    if 'definition' in entry:
                        f.write(f"   Definition: {entry['definition'][:100]}...\n")
                    f.write("\n")
            
            print(f"💾 History exported to: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error exporting history: {e}")
            return False

    def get_audio_settings(self):
        """Get current audio settings"""
        return {
            'auto_play_pronunciation': self.auto_play_pronunciation,
            'auto_speak_definition': self.auto_speak_definition,
            'audio_available': self.audio_available,
            'audio_playing': self.audio_playing,
            'audio_paused': self.audio_paused
        }

    def get_application_info(self):
        """Get application information"""
        return {
            'data_source': self.data_source,
            'local_word_count': self.model.get_local_word_count(),
            'history_count': len(self.model.get_search_history()),
            'dictionary_source': self.model.get_dictionary_source(),
            'offline_mode': self.offline_mode,
            'search_suggestions': self.search_suggestions
        }

    def shutdown(self):
        """Clean shutdown of the controller"""
        self.stop_all_audio()
        self.running = False
        if hasattr(self.model, 'close'):
            self.model.close()


def main():
    """Main function to run the dictionary application"""
    try:
        controller = DictionaryController()
        controller.run()
    except Exception as e:
        print(f"❌ Error running dictionary application: {e}")
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()