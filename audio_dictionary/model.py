import requests
import json
import os
import threading
import datetime
from typing import Dict, Optional, List, Any, Callable
import time
from audio_dictionary.tts_service import TextToSpeechService

class DictionaryModel:
    def __init__(self):
        self.api_url = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        self.current_word_data = None
        self.audio_url = None
        self.webster_file = "data/websters_english_dictionary.json"
        self.history_file = "data/search_history.json"
        self.webster_dictionary = self._load_webster_dictionary()
        self.search_history = self._load_search_history()
        
        # Initialize enhanced TTS service
        self.tts_service = TextToSpeechService()
        
        # Settings
        self.offline_mode = False
        self.search_suggestions = True
        
        # Cache for faster searches
        self.search_cache = {}
        self.cache_size = 100
        
        # Performance tracking
        self.last_search_time = 0
        
    def _load_webster_dictionary(self) -> Dict:
        """Load Webster's English Dictionary JSON file - OPTIMIZED"""
        try:
            if os.path.exists(self.webster_file):
                start_time = time.time()
                with open(self.webster_file, 'r', encoding='utf-8') as f:
                    webster_data = json.load(f)
                load_time = time.time() - start_time
                print(f"✅ Loaded Webster's dictionary with {len(webster_data)} words in {load_time:.2f}s")
                return webster_data
            else:
                print(f"⚠️ Webster's dictionary file not found: {self.webster_file}")
                # Create directory and return empty dict
                os.makedirs(os.path.dirname(self.webster_file), exist_ok=True)
                return {}
        except Exception as e:
            print(f"❌ Error loading Webster's dictionary: {e}")
            return {}

    def _load_search_history(self) -> List:
        """Load search history from JSON file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading search history: {e}")
            return []

    def _save_search_history(self):
        """Save search history to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.search_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving search history: {e}")

    def add_to_history(self, word: str, source: str, data: Dict = None):
        """Add a search to history"""
        history_entry = {
            "word": word,
            "timestamp": datetime.datetime.now().isoformat(),
            "source": source,
            "data": data
        }
        
        # Remove existing entry for the same word to avoid duplicates
        self.search_history = [entry for entry in self.search_history if entry["word"].lower() != word.lower()]
        
        # Add new entry at the beginning
        self.search_history.insert(0, history_entry)
        
        # Keep only last 50 entries
        self.search_history = self.search_history[:50]
        
        # Save to file
        self._save_search_history()

    def get_search_history(self) -> List:
        """Get search history sorted by timestamp (newest first)"""
        return sorted(self.search_history, key=lambda x: x["timestamp"], reverse=True)

    def clear_history(self):
        """Clear all search history"""
        self.search_history = []
        self._save_search_history()

    def _generate_word_audio(self, word: str, definition_data: Dict = None) -> str:
        """Generate audio for word using enhanced TTS service - ASYNC"""
        try:
            # Run TTS in background thread to not block UI
            def tts_thread():
                return self.tts_service.generate_audio(word, definition_data)
            
            # For now, we'll run it synchronously but quickly
            return self.tts_service.generate_audio(word, definition_data)
        except Exception as e:
            print(f"Error generating word audio: {e}")
            return None
    
    def fetch_word_data(self, word: str, callback: Callable, use_suggestions: bool = True) -> None:
        """Fetch word definition - ALWAYS TRY ONLINE FIRST, THEN OFFLINE"""
        def fetch_thread():
            start_time = time.time()
            word_lower = word.lower().strip()
            print(f"🔍 Searching for: '{word_lower}'")
            
            # Check cache first (FASTEST)
            cache_key = f"{word_lower}_{use_suggestions}"
            if cache_key in self.search_cache:
                cached_data = self.search_cache[cache_key]
                print(f"✅ Found in cache: '{word_lower}'")
                callback(True, cached_data['data'], cached_data['audio_url'], cached_data['source'])
                return
            
            # STEP 1: ALWAYS TRY ONLINE FIRST (unless offline mode is explicitly enabled)
            if not self.offline_mode:
                print("🌐 Attempting online search first...")
                self._try_online_then_local(word_lower, callback, use_suggestions, start_time)
            else:
                # Offline mode explicitly enabled - use local only
                print("📴 Offline mode enabled - using local dictionary only")
                self._fetch_from_local_dict_fast(word_lower, callback, use_suggestions, start_time)
        
        threading.Thread(target=fetch_thread, daemon=True).start()

    def _try_online_then_local(self, word: str, callback: Callable, use_suggestions: bool, start_time: float):
        """Try online first, then fall back to local if online fails"""
        # First check if we have internet connection
        if not self.check_internet_connection():
            print("🌐 No internet connection, switching to offline mode")
            # If no internet, go straight to local dictionary
            self._fetch_from_local_dict_fast(word, callback, use_suggestions, start_time)
            return
        
        # Try online search with timeout
        try:
            api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            print(f"🌐 Online search: {api_url}")
            
            # Use timeout for online request
            response = requests.get(api_url, timeout=5)  # 5 second timeout
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Online success for '{word}'")
                
                converted_data = self._convert_free_api_format(data)
                if converted_data:
                    audio_url = self._extract_audio_url_free_api(data)
                    
                    # Save to local dictionary for future offline use
                    self._save_online_word_to_local(word, converted_data)
                    
                    total_time = time.time() - start_time
                    print(f"⏱️ Online search completed in {total_time:.2f}s")
                    
                    # Cache the result
                    self._cache_result(word, use_suggestions, converted_data, audio_url, "online")
                    callback(True, converted_data, audio_url, "online")
                    return
            else:
                print(f"❌ Online API returned status {response.status_code} for '{word}'")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Online timeout for '{word}' - switching to offline")
        except requests.exceptions.ConnectionError:
            print(f"🔌 Connection error for '{word}' - switching to offline")
        except Exception as e:
            print(f"❌ Online error for '{word}': {e}")
        
        # If we reach here, online search failed - try local
        print(f"🔄 Online search failed, trying local dictionary for '{word}'")
        self._fetch_from_local_dict_fast(word, callback, use_suggestions, start_time)
    
    def _fetch_from_local_dict_fast(self, word: str, callback: Callable, use_suggestions: bool, start_time: float):
        """Fast local-only search"""
        try:
            exact_data = self._get_webster_word_data_enhanced(word)
            if exact_data:
                total_time = time.time() - start_time
                print(f"✅ Local found '{word}' in {total_time:.2f}s")
                # Cache the result
                self._cache_result(word, use_suggestions, exact_data, None, "webster")
                callback(True, exact_data, None, "webster")
                return
            
            if use_suggestions:
                self._try_fuzzy_match_fast(word, callback, start_time)
            else:
                callback(False, f"Word '{word}' not found in dictionary.", None, "offline")
                
        except Exception as e:
            print(f"❌ Local error for '{word}': {e}")
            callback(False, f"Error: {str(e)}", None, "error")
    
    def _get_webster_word_data_enhanced(self, word: str) -> Optional[List]:
        """Get word data from Webster's dictionary with BETTER FORMATTING"""
        word_lower = word.lower().strip()
        
        # Direct match
        if word_lower in self.webster_dictionary:
            word_data = self.webster_dictionary[word_lower]
            return [self._convert_webster_format_enhanced(word, word_data)]
        
        # Common plural forms
        if word_lower.endswith('s'):
            singular = word_lower[:-1]
            if singular in self.webster_dictionary:
                word_data = self.webster_dictionary[singular]
                return [self._convert_webster_format_enhanced(word, word_data)]
        
        # Common verb forms
        if word_lower.endswith('ing'):
            base = word_lower[:-3]
            if base in self.webster_dictionary:
                word_data = self.webster_dictionary[base]
                return [self._convert_webster_format_enhanced(word, word_data)]
        
        if word_lower.endswith('ed'):
            base = word_lower[:-2]
            if base in self.webster_dictionary:
                word_data = self.webster_dictionary[base]
                return [self._convert_webster_format_enhanced(word, word_data)]
        
        return None
    
    def _convert_webster_format_enhanced(self, word: str, webster_data: Any) -> Dict:
        """Convert Webster's format to our app format with CLEAN, READABLE STRUCTURE"""
        try:
            # Initialize with clean structure
            converted = {
                "word": word.capitalize(),
                "phonetic": "",
                "meanings": [],
                "has_audio": True,
                "audio_available": True
            }
            
            # Handle different data types in Webster's dictionary
            if isinstance(webster_data, dict):
                pronunciation = webster_data.get('pronunciation', '')
                definitions_data = webster_data.get('definitions', [])
                part_of_speech = webster_data.get('part_of_speech', '')
                synonyms = webster_data.get('synonyms', [])
                antonyms = webster_data.get('antonyms', [])
                
                # Set phonetic if available
                if pronunciation:
                    converted["phonetic"] = f"/{pronunciation}/" if not pronunciation.startswith('/') else pronunciation
                
                # Create main meaning entry
                meaning = {
                    "partOfSpeech": self._clean_part_of_speech(part_of_speech),
                    "definitions": [],
                    "synonyms": synonyms[:8] if isinstance(synonyms, list) else [],  # Limit synonyms
                    "antonyms": antonyms[:5] if isinstance(antonyms, list) else []   # Limit antonyms
                }
                
                # Process definitions with clean formatting
                if isinstance(definitions_data, list):
                    for i, def_item in enumerate(definitions_data[:5]):  # Limit to 5 definitions
                        if isinstance(def_item, dict):
                            definition_text = def_item.get('definition', '')
                            example_text = def_item.get('example', '')
                        else:
                            definition_text = str(def_item)
                            example_text = ""
                        
                        if definition_text:
                            # Clean up definition text
                            definition_text = self._clean_definition_text(definition_text)
                            
                            definition_entry = {
                                "definition": definition_text,
                                "example": self._clean_example_text(example_text)
                            }
                            meaning["definitions"].append(definition_entry)
                
                elif isinstance(definitions_data, str):
                    # Single string definition
                    definition_text = self._clean_definition_text(definitions_data)
                    meaning["definitions"].append({
                        "definition": definition_text,
                        "example": ""
                    })
                
                if meaning["definitions"]:
                    converted["meanings"].append(meaning)
                    
            elif isinstance(webster_data, str):
                # Simple string definition
                definition_text = self._clean_definition_text(webster_data)
                meaning = {
                    "partOfSpeech": "",
                    "definitions": [{
                        "definition": definition_text,
                        "example": ""
                    }],
                    "synonyms": [],
                    "antonyms": []
                }
                converted["meanings"].append(meaning)
            
            # If no meanings were created, create a basic one
            if not converted["meanings"]:
                meaning = {
                    "partOfSpeech": "",
                    "definitions": [{
                        "definition": f"Definition for {word.capitalize()}",
                        "example": ""
                    }],
                    "synonyms": [],
                    "antonyms": []
                }
                converted["meanings"].append(meaning)
            
            return converted
            
        except Exception as e:
            print(f"Error converting Webster's format: {e}")
            # Return basic structure on error
            return {
                "word": word.capitalize(),
                "phonetic": "",
                "meanings": [{
                    "partOfSpeech": "",
                    "definitions": [{
                        "definition": f"Definition for {word.capitalize()}",
                        "example": ""
                    }],
                    "synonyms": [],
                    "antonyms": []
                }],
                "has_audio": True,
                "audio_available": True
            }
    
    def _clean_part_of_speech(self, pos: str) -> str:
        """Clean and format part of speech"""
        if not pos:
            return ""
        
        pos = pos.strip().lower()
        
        # Common abbreviations to full forms
        pos_map = {
            'n': 'noun',
            'v': 'verb', 
            'adj': 'adjective',
            'adv': 'adverb',
            'prep': 'preposition',
            'conj': 'conjunction',
            'interj': 'interjection',
            'pron': 'pronoun',
            'art': 'article'
        }
        
        return pos_map.get(pos, pos.capitalize())
    
    def _clean_definition_text(self, text: str) -> str:
        """Clean definition text for better readability"""
        if not text:
            return ""
        
        text = text.strip()
        
        # Remove excessive punctuation
        if text.endswith('..'):
            text = text[:-1]
        
        # Ensure proper capitalization
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Ensure it ends with a period
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text
    
    def _clean_example_text(self, text: str) -> str:
        """Clean example text for better readability"""
        if not text:
            return ""
        
        text = text.strip()
        
        # Ensure proper formatting
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Ensure it ends with proper punctuation
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text
    
    def _try_fuzzy_match_fast(self, word: str, callback: Callable, start_time: float):
        """Fast fuzzy matching with better suggestions"""
        try:
            word_lower = word.lower()
            suggestions = []
            
            # Simple and fast matching
            for dict_word in self.webster_dictionary.keys():
                if (word_lower in dict_word or 
                    dict_word in word_lower or 
                    self._simple_similarity(word_lower, dict_word) > 0.7):
                    suggestions.append(dict_word)
                    if len(suggestions) >= 8:  # More suggestions
                        break
            
            if suggestions:
                # Use the closest match
                suggested_word = self._find_best_match(word_lower, suggestions)
                exact_data = self._get_webster_word_data_enhanced(suggested_word)
                
                if exact_data:
                    total_time = time.time() - start_time
                    print(f"💡 Using suggestion: '{suggested_word}' for '{word}' in {total_time:.2f}s")
                    
                    # Cache the result
                    self._cache_result(word, True, exact_data, None, "webster_suggestion")
                    # Add to history with original word but suggested data
                    self.add_to_history(word, exact_data, "webster_suggestion")
                    callback(True, exact_data, None, "webster_suggestion")
                else:
                    callback(False, f"Word not found. Did you mean: {', '.join(suggestions[:3])}?", None, "suggestions")
            else:
                callback(False, f"Word '{word}' not found in dictionary.", None, "not_found")
                
        except Exception as e:
            print(f"Error finding suggestions: {e}")
            callback(False, f"Word '{word}' not found in dictionary.", None, "error")
    
    def _simple_similarity(self, word1: str, word2: str) -> float:
        """Simple similarity calculation for fast matching"""
        if word1 == word2:
            return 1.0
        
        # Simple substring matching
        if word1 in word2 or word2 in word1:
            return 0.8
        
        # Length-based similarity
        len_similarity = 1 - abs(len(word1) - len(word2)) / max(len(word1), len(word2))
        
        # Character overlap
        set1, set2 = set(word1), set(word2)
        overlap = len(set1.intersection(set2))
        char_similarity = overlap / max(len(set1), len(set2))
        
        return (len_similarity + char_similarity) / 2
    
    def _find_best_match(self, target: str, suggestions: List[str]) -> str:
        """Find the best match from suggestions"""
        if not suggestions:
            return target
        
        # Simple: prefer exact matches, then shortest
        exact_matches = [s for s in suggestions if target in s]
        if exact_matches:
            return min(exact_matches, key=len)  # Shortest exact match
        
        return suggestions[0]  # First suggestion
    
    def _cache_result(self, word: str, use_suggestions: bool, data: Any, audio_url: str, source: str):
        """Cache search results for faster future searches"""
        cache_key = f"{word.lower()}_{use_suggestions}"
        
        # Add to cache
        self.search_cache[cache_key] = {
            'data': data,
            'audio_url': audio_url,
            'source': source,
            'timestamp': time.time()
        }
        
        # Limit cache size
        if len(self.search_cache) > self.cache_size:
            # Remove oldest entry
            oldest_key = min(self.search_cache.keys(), 
                           key=lambda k: self.search_cache[k]['timestamp'])
            del self.search_cache[oldest_key]
    
    def _save_online_word_to_local(self, word: str, word_data: List[Dict]):
        """Save online word data to Webster's local dictionary"""
        try:
            word_lower = word.lower().strip()
            
            # Check if word already exists in local dictionary
            if word_lower in self.webster_dictionary:
                return
            
            # Convert our app format back to Webster's format for storage
            webster_format_data = self._convert_to_webster_format(word_data[0] if word_data else {})
            
            if webster_format_data:
                # Add to Webster's dictionary
                self.webster_dictionary[word_lower] = webster_format_data
                
                # Save the updated dictionary to file (in background)
                threading.Thread(target=self._save_webster_dictionary, daemon=True).start()
                
                print(f"💾 Saved '{word}' to local dictionary")
                
        except Exception as e:
            print(f"Error saving online word to local dictionary: {e}")

    def _convert_to_webster_format(self, word_data: Dict) -> Dict:
        """Convert our app format to Webster's dictionary format for storage"""
        try:
            webster_data = {
                'pronunciation': word_data.get('phonetic', '').replace('/', ''),
                'part_of_speech': '',
                'definitions': [],
                'synonyms': [],
                'antonyms': []
            }
            
            # Extract definitions from meanings
            for meaning in word_data.get('meanings', []):
                part_of_speech = meaning.get('partOfSpeech', '')
                if part_of_speech and not webster_data['part_of_speech']:
                    webster_data['part_of_speech'] = part_of_speech
                
                for definition in meaning.get('definitions', []):
                    def_entry = {
                        'definition': definition.get('definition', ''),
                        'example': definition.get('example', '')
                    }
                    webster_data['definitions'].append(def_entry)
                
                # Add synonyms and antonyms
                webster_data['synonyms'].extend(meaning.get('synonyms', []))
                webster_data['antonyms'].extend(meaning.get('antonyms', []))
            
            # Limit the number of definitions to save space
            webster_data['definitions'] = webster_data['definitions'][:3]
            webster_data['synonyms'] = webster_data['synonyms'][:5]
            webster_data['antonyms'] = webster_data['antonyms'][:5]
            
            return webster_data
            
        except Exception as e:
            print(f"Error converting to Webster's format: {e}")
            return None

    def _save_webster_dictionary(self):
        """Save Webster's dictionary to file"""
        try:
            os.makedirs(os.path.dirname(self.webster_file), exist_ok=True)
            with open(self.webster_file, 'w', encoding='utf-8') as f:
                json.dump(self.webster_dictionary, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving Webster's dictionary: {e}")

    def set_offline_mode(self, enabled: bool):
        """Set offline mode"""
        self.offline_mode = enabled
        print(f"Offline mode: {'enabled' if enabled else 'disabled'}")

    def set_search_suggestions(self, enabled: bool):
        """Set search suggestions"""
        self.search_suggestions = enabled
        print(f"Search suggestions: {'enabled' if enabled else 'disabled'}")

    def _extract_audio_url_free_api(self, data: dict) -> Optional[str]:
        """Extract audio pronunciation URL from free API response"""
        try:
            if isinstance(data, list) and len(data) > 0:
                first_entry = data[0]
                # Free dictionary API structure
                if 'phonetics' in first_entry:
                    for phonetic in first_entry['phonetics']:
                        if 'audio' in phonetic and phonetic['audio']:
                            audio_url = phonetic['audio']
                            # Ensure the URL is valid
                            if audio_url.startswith('http'):
                                return audio_url
            return None
        except Exception as e:
            print(f"Error extracting audio URL: {e}")
            return None
    
    def _convert_free_api_format(self, api_data: dict) -> Optional[List]:
        """Convert free dictionary API format to our app format"""
        try:
            if not isinstance(api_data, list) or len(api_data) == 0:
                return None
                
            converted_entries = []
            
            for entry in api_data:
                converted_entry = {
                    "word": entry.get('word', ''),
                    "phonetic": entry.get('phonetic', ''),
                    "phonetics": entry.get('phonetics', []),
                    "meanings": [],
                    "has_audio": True,
                    "audio_available": True
                }
                
                # Convert meanings
                for meaning in entry.get('meanings', []):
                    converted_meaning = {
                        "partOfSpeech": meaning.get('partOfSpeech', ''),
                        "definitions": [],
                        "synonyms": meaning.get('synonyms', []),
                        "antonyms": meaning.get('antonyms', [])
                    }
                    
                    for definition in meaning.get('definitions', []):
                        def_entry = {
                            "definition": definition.get('definition', ''),
                            "example": definition.get('example', '')
                        }
                        converted_meaning["definitions"].append(def_entry)
                    
                    converted_entry["meanings"].append(converted_meaning)
                
                converted_entries.append(converted_entry)
            
            return converted_entries
            
        except Exception as e:
            print(f"Error converting free API format: {e}")
            return None
    
    def check_internet_connection(self) -> bool:
        """Check if internet connection is available - OPTIMIZED"""
        try:
            # Faster check with shorter timeout
            response = requests.get("https://www.google.com", timeout=2)
            return True
        except:
            return False
    
    def get_local_word_count(self) -> int:
        """Get number of words in Webster's dictionary"""
        return len(self.webster_dictionary)
    
    def get_dictionary_source(self) -> str:
        """Get the source of the current dictionary"""
        return "Webster's English Dictionary"
    
    def get_auto_suggestions(self, partial_word):
        """Get auto-suggestions for partial word input"""
        suggestions = []
        partial_lower = partial_word.lower()
        
        # Search through Webster's dictionary for matching words
        for word in self.webster_dictionary.keys():
            if word.startswith(partial_lower) and word != partial_lower:
                suggestions.append(word)
                if len(suggestions) >= 10:  # Limit to 10 suggestions
                    break
        
        return suggestions