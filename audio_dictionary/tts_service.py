from gtts import gTTS
import os
import time
import tempfile

class TextToSpeechService:
    def __init__(self):
        # No cache directory - we'll use temporary files
        pass
        
    def generate_audio(self, word, definition_data=None, language='en'):
        """Generate TTS audio for ANY word - NO STORAGE"""
        try:
            # Create speech text that ALWAYS works
            speech_text = self.create_guaranteed_speech_text(word, definition_data)
            
            # Multiple attempts to generate audio
            for attempt in range(3):
                try:
                    if attempt > 0:
                        print(f"   Attempt {attempt + 1} for '{word}'")
                        time.sleep(0.5)
                    
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                        temp_path = temp_file.name
                    
                    tts = gTTS(text=speech_text, lang=language, slow=False)
                    tts.save(temp_path)
                    
                    # Verify the file was created and has content
                    if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000:
                        print(f"✅ SUCCESS: Audio generated for '{word}'")
                        return temp_path
                    else:
                        print(f"⚠️  File too small, retrying...")
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                        continue
                        
                except Exception as e:
                    print(f"⚠️  Attempt {attempt + 1} failed: {e}")
                    if 'temp_path' in locals() and os.path.exists(temp_path):
                        os.unlink(temp_path)
                    continue
            
            return None
            
        except Exception as e:
            print(f"💥 CRITICAL TTS failure for '{word}': {e}")
            return None

    def create_guaranteed_speech_text(self, word, definition_data):
        """Create speech text that ALWAYS works"""
        word_display = word.title() if word else "Unknown"
        
        # If we have definition data, use it
        if definition_data:
            # Handle both single word data and list format
            if isinstance(definition_data, list) and len(definition_data) > 0:
                word_data = definition_data[0]
            else:
                word_data = definition_data
            
            # Try to get the phonetic pronunciation if available
            phonetic = word_data.get('phonetic', '')
            definitions = self.extract_all_definitions(word_data)
            part_of_speech = self.extract_part_of_speech(word_data)
            
            # Create a natural speech pattern
            speech_parts = []
            speech_parts.append(f"The word is {word_display}")
            
            if phonetic:
                speech_parts.append(f"pronounced as {phonetic}")
            
            if part_of_speech:
                speech_parts.append(f"It is a {part_of_speech}")
            
            # Add all definitions with numbers if there are multiple
            if definitions:
                if len(definitions) == 1:
                    speech_parts.append(f"Definition: {definitions[0]}")
                else:
                    speech_parts.append("Here are the definitions")
                    for idx, definition in enumerate(definitions, 1):
                        speech_parts.append(f"Definition {idx}: {definition}")
            
            return ". ".join(speech_parts)
        
        # Fallback texts that always work
        fallback_texts = [
            f"The word is {word_display}",
            f"Word: {word_display}",
            f"{word_display}",
            "Word not found in dictionary"
        ]
        
        # Use the first fallback that's not too long
        for text in fallback_texts:
            if len(text) <= 200:
                return text
        
        return word_display

    def extract_all_definitions(self, definition_data):
        """Extract all available definitions from the data"""
        definitions = []
        
        # Check meanings array (our app's format)
        if definition_data.get('meanings'):
            for meaning in definition_data['meanings']:
                if meaning.get('definitions'):
                    for def_item in meaning['definitions']:
                        if isinstance(def_item, dict) and def_item.get('definition'):
                            definitions.append(def_item['definition'])
        
        # Check direct definitions array
        if isinstance(definition_data.get('definitions'), list):
            for def_item in definition_data['definitions']:
                if isinstance(def_item, dict) and def_item.get('text'):
                    definitions.append(def_item['text'])
                elif isinstance(def_item, str):
                    definitions.append(def_item)
        
        # Check other possible locations
        other_sources = ['meaning', 'description', 'definition']
        for source in other_sources:
            if definition_data.get(source):
                if isinstance(definition_data[source], str):
                    definitions.append(definition_data[source])
        
        # Remove duplicates while preserving order
        unique_defs = []
        seen = set()
        for d in definitions:
            if d and isinstance(d, str):
                d = d.strip()
                if len(d) > 5 and d not in seen:
                    seen.add(d)
                    unique_defs.append(d)
                    
                    # Limit to first 3 definitions to keep audio length reasonable
                    if len(unique_defs) >= 3:
                        break
        
        return unique_defs
        
    def extract_part_of_speech(self, definition_data):
        """Extract part of speech from definition data"""
        if definition_data.get('partOfSpeech'):
            return definition_data['partOfSpeech']
            
        if definition_data.get('meanings'):
            for meaning in definition_data['meanings']:
                if meaning.get('partOfSpeech'):
                    return meaning['partOfSpeech']
                    
        return None

    def generate_definition_audio(self, word, definition_text):
        """Generate audio specifically for definition text - NO STORAGE"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_path = temp_file.name
            
            print(f"🎵 Generating definition audio for: '{word}'")
            
            # Multiple attempts to generate audio
            for attempt in range(3):
                try:
                    if attempt > 0:
                        print(f"   Definition attempt {attempt + 1} for '{word}'")
                        time.sleep(0.5)
                    
                    tts = gTTS(text=definition_text, lang='en', slow=False)
                    tts.save(temp_path)
                    
                    if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000:
                        print(f"✅ SUCCESS: Definition audio generated for '{word}'")
                        return temp_path
                        
                except Exception as e:
                    print(f"⚠️  Definition attempt {attempt + 1} failed: {e}")
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    continue
            
            return None
            
        except Exception as e:
            print(f"💥 CRITICAL TTS failure for definition '{word}': {e}")
            return None