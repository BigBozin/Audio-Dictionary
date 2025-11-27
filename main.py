import pygame
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from audio_dictionary.controller import DictionaryController

def main():
    """Main function to run the dictionary application"""
    try:
        print("Starting Cellusys Audio Dictionary...")
        controller = DictionaryController()
        controller.run()
    except Exception as e:
        print(f"Error running dictionary application: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()