import pygame
import sys
import os
from pygame.locals import *
import time
import datetime
import math

class SpinnerLoader:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.active = False
        self.progress_value = 0
        self.progress_max = 100
        self.message = ""
        
        # Spinner animation properties
        self.spinner_chars = ["●", "◆", "■", "▲", "▼", "◀", "▶"]
        self.colors = [
            (46, 204, 113),   # Green
            (52, 152, 219),   # Blue
            (155, 89, 182),   # Purple
            (231, 76, 60),    # Red
            (241, 196, 15),   # Yellow
            (26, 188, 156),   # Teal
            (52, 73, 94)      # Dark blue
        ]
        self.current_frame = 0
        self.last_update_time = 0
        self.frame_delay = 100  # milliseconds
        
    def start(self, message="Loading..."):
        self.active = True
        self.progress_value = 0
        self.message = message
        self.current_frame = 0
        self.last_update_time = pygame.time.get_ticks()
        
    def stop(self):
        self.active = False
        self.progress_value = 0
        self.message = ""
        
    def set_progress(self, value, max_value=100, message=None):
        self.progress_value = value
        self.progress_max = max_value
        if message:
            self.message = message
            
    def update(self):
        if not self.active:
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.spinner_chars)
            self.last_update_time = current_time
            
    def draw(self, screen, font, small_font, theme):
        if not self.active:
            return
            
        # Draw background
        pygame.draw.rect(screen, theme['SETTINGS_BG'], self.rect, border_radius=8)
        pygame.draw.rect(screen, theme['SETTINGS_BORDER'], self.rect, 2, border_radius=8)
        
        # Draw spinner
        spinner_char = self.spinner_chars[self.current_frame]
        spinner_color = self.colors[self.current_frame % len(self.colors)]
        
        # Create a surface for the spinner character
        spinner_surface = font.render(spinner_char, True, spinner_color)
        spinner_x = self.rect.x + 20
        spinner_y = self.rect.y + (self.rect.height - spinner_surface.get_height()) // 2
        screen.blit(spinner_surface, (spinner_x, spinner_y))
        
        # Draw message
        if self.message:
            message_surface = small_font.render(self.message, True, theme['TEXT_COLOR'])
            message_x = self.rect.x + 60
            message_y = self.rect.y + (self.rect.height - message_surface.get_height()) // 2
            screen.blit(message_surface, (message_x, message_y))
        
        # Draw progress bar if we have meaningful progress
        if 0 < self.progress_value < self.progress_max:
            progress_width = self.rect.width - 100
            progress_height = 8
            progress_x = self.rect.x + 60
            progress_y = self.rect.y + self.rect.height - 15
            
            # Progress bar background
            progress_bg_rect = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
            pygame.draw.rect(screen, theme['DISABLED_COLOR'], progress_bg_rect, border_radius=4)
            
            # Progress bar fill
            if self.progress_max > 0:
                fill_width = int((self.progress_value / self.progress_max) * progress_width)
                if fill_width > 0:
                    fill_rect = pygame.Rect(progress_x, progress_y, fill_width, progress_height)
                    pygame.draw.rect(screen, theme['ACCENT_COLOR'], fill_rect, border_radius=4)
            
            # Progress percentage
            percentage = f"{int((self.progress_value / self.progress_max) * 100)}%" if self.progress_max > 0 else "0%"
            percent_surface = small_font.render(percentage, True, theme['TEXT_COLOR'])
            percent_x = progress_x + progress_width + 10
            percent_y = progress_y - (percent_surface.get_height() - progress_height) // 2
            screen.blit(percent_surface, (percent_x, percent_y))


class DictionaryView:
    def __init__(self):
        pygame.init()
        
        # Set minimum window size
        self.MIN_WIDTH = 800
        self.MIN_HEIGHT = 600
        
        # Initial screen size
        self.screen_width = 1000
        self.screen_height = 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Audio Dictionary - Cellusys Edition")
        
        # Theme settings
        self.current_theme = 'light'
        self.themes = {
            'light': {
                'BG_COLOR': (240, 240, 245),
                'TEXT_COLOR': (50, 50, 80),
                'ACCENT_COLOR': (74, 144, 226),
                'OFFLINE_COLOR': (150, 150, 150),
                'LOCAL_COLOR': (106, 176, 76),
                'ERROR_COLOR': (220, 80, 80),
                'SUCCESS_COLOR': (80, 180, 80),
                'WEBSTER_COLOR': (148, 0, 211),
                'SCROLLBAR_COLOR': (180, 180, 180),
                'SCROLLBAR_ACTIVE_COLOR': (120, 120, 120),
                'AUDIO_PLAY_COLOR': (65, 105, 225),
                'AUDIO_PAUSE_COLOR': (255, 140, 0),
                'AUDIO_STOP_COLOR': (220, 80, 80),
                'AUDIO_LOADING_COLOR': (255, 165, 0),
                'SPEAK_COLOR': (75, 0, 130),
                'SPEAK_LOADING_COLOR': (186, 85, 211),
                'HISTORY_COLOR': (139, 69, 19),
                'HISTORY_HOVER_COLOR': (160, 90, 40),
                'AUTO_PLAY_COLOR': (46, 139, 87),
                'DISABLED_COLOR': (180, 180, 180),
                'SYNONYM_COLOR': (60, 179, 113),
                'ANTONYM_COLOR': (220, 20, 60),
                'SETTINGS_BG': (250, 250, 255),
                'SETTINGS_BORDER': (200, 200, 220),
                'INPUT_BG': (255, 255, 255),
                'CONTENT_BG': (255, 255, 255),
                'HISTORY_ENTRY_BG': (240, 240, 240),
                'HISTORY_ENTRY_HOVER': (220, 220, 220),
                'HEADER_BG': (230, 230, 230),
                'CURSOR_COLOR': (74, 144, 226),
                'TOP_BAR_BG': (250, 250, 250),
                'TOP_BAR_BORDER': (220, 220, 220),
                'SUGGESTION_COLOR': (255, 165, 0),
                'SUGGESTION_BG': (255, 255, 255),
                'SUGGESTION_HOVER': (240, 240, 240),
                'SUGGESTION_SELECTED': (230, 240, 255)
            },
            'dark': {
                'BG_COLOR': (30, 30, 35),
                'TEXT_COLOR': (220, 220, 220),
                'ACCENT_COLOR': (100, 160, 255),
                'OFFLINE_COLOR': (120, 120, 120),
                'LOCAL_COLOR': (86, 156, 56),
                'ERROR_COLOR': (255, 100, 100),
                'SUCCESS_COLOR': (100, 200, 100),
                'WEBSTER_COLOR': (168, 50, 231),
                'SCROLLBAR_COLOR': (80, 80, 80),
                'SCROLLBAR_ACTIVE_COLOR': (120, 120, 120),
                'AUDIO_PLAY_COLOR': (85, 125, 245),
                'AUDIO_PAUSE_COLOR': (255, 160, 40),
                'AUDIO_STOP_COLOR': (240, 100, 100),
                'AUDIO_LOADING_COLOR': (255, 185, 40),
                'SPEAK_COLOR': (95, 40, 150),
                'SPEAK_LOADING_COLOR': (206, 105, 231),
                'HISTORY_COLOR': (159, 89, 39),
                'HISTORY_HOVER_COLOR': (180, 110, 60),
                'AUTO_PLAY_COLOR': (66, 159, 107),
                'DISABLED_COLOR': (100, 100, 100),
                'SYNONYM_COLOR': (80, 199, 133),
                'ANTONYM_COLOR': (240, 40, 80),
                'SETTINGS_BG': (50, 50, 60),
                'SETTINGS_BORDER': (80, 80, 90),
                'INPUT_BG': (60, 60, 70),
                'CONTENT_BG': (40, 40, 45),
                'HISTORY_ENTRY_BG': (50, 50, 55),
                'HISTORY_ENTRY_HOVER': (70, 70, 75),
                'HEADER_BG': (60, 60, 65),
                'CURSOR_COLOR': (100, 160, 255),
                'TOP_BAR_BG': (40, 40, 45),
                'TOP_BAR_BORDER': (70, 70, 75),
                'SUGGESTION_COLOR': (255, 140, 0),
                'SUGGESTION_BG': (60, 60, 70),
                'SUGGESTION_HOVER': (80, 80, 90),
                'SUGGESTION_SELECTED': (70, 80, 100)
            },
            'blue': {
                'BG_COLOR': (230, 240, 255),
                'TEXT_COLOR': (30, 50, 90),
                'ACCENT_COLOR': (0, 100, 200),
                'OFFLINE_COLOR': (120, 140, 160),
                'LOCAL_COLOR': (80, 160, 100),
                'ERROR_COLOR': (200, 60, 60),
                'SUCCESS_COLOR': (60, 160, 60),
                'WEBSTER_COLOR': (120, 0, 180),
                'SCROLLBAR_COLOR': (150, 170, 190),
                'SCROLLBAR_ACTIVE_COLOR': (100, 120, 140),
                'AUDIO_PLAY_COLOR': (40, 80, 200),
                'AUDIO_PAUSE_COLOR': (220, 120, 0),
                'AUDIO_STOP_COLOR': (200, 60, 60),
                'AUDIO_LOADING_COLOR': (220, 140, 0),
                'SPEAK_COLOR': (60, 0, 110),
                'SPEAK_LOADING_COLOR': (160, 70, 190),
                'HISTORY_COLOR': (110, 50, 10),
                'HISTORY_HOVER_COLOR': (130, 70, 30),
                'AUTO_PLAY_COLOR': (30, 120, 70),
                'DISABLED_COLOR': (150, 170, 190),
                'SYNONYM_COLOR': (40, 160, 100),
                'ANTONYM_COLOR': (200, 10, 50),
                'SETTINGS_BG': (240, 245, 255),
                'SETTINGS_BORDER': (180, 190, 210),
                'INPUT_BG': (255, 255, 255),
                'CONTENT_BG': (245, 248, 255),
                'HISTORY_ENTRY_BG': (235, 240, 250),
                'HISTORY_ENTRY_HOVER': (220, 230, 245),
                'HEADER_BG': (225, 235, 250),
                'CURSOR_COLOR': (0, 100, 200),
                'TOP_BAR_BG': (240, 245, 255),
                'TOP_BAR_BORDER': (200, 210, 220),
                'SUGGESTION_COLOR': (220, 120, 0),
                'SUGGESTION_BG': (255, 255, 255),
                'SUGGESTION_HOVER': (240, 245, 255),
                'SUGGESTION_SELECTED': (230, 240, 255)
            }
        }
        
        # Apply current theme
        self.apply_theme()
        
        # Fonts - will be updated by _update_fonts based on settings
        self.title_font = None
        self.normal_font = None
        self.small_font = None
        self.tiny_font = None
        
        # Load icons
        self.icons = self._create_icons()
        
        # Initialize spinner loader
        self.spinner = None
        self._init_spinner()
        
        # Audio loading animation
        self.audio_loading_frames = []
        self.audio_loading_index = 0
        self.create_audio_loading_animation()
        
        # Input box with cursor movement and auto-suggestions
        self.input_box = pygame.Rect(0, 0, 400, 50)
        self.input_text = ''
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_position = 0  # Track cursor position
        
        # Auto-suggestion properties
        self.suggestions = []  # Store auto-suggestions
        self.selected_suggestion = 0  # Track selected suggestion
        self.show_suggestions = False  # Control suggestion display
        self.suggestion_boxes = []  # Store suggestion rects
        
        # Scrollbar variables
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scrollbar_rect = None
        self.scrollbar_dragging = False
        self.scrollbar_drag_offset = 0
        self.content_height = 0
        
        # Content area for scrolling
        self.content_rect = pygame.Rect(0, 0, 0, 0)
        
        # Current word data for dynamic rendering
        self.current_word_data = None
        self.current_data_source = "online"
        self.suggested_words = []  # Store suggested words when word not found
        
        # Audio state
        self.audio_playing = False
        self.audio_paused = False
        self.audio_loading = False
        self.tts_loading = False
        
        # History state
        self.showing_history = False
        self.history_data = []
        self.history_entries_rects = []
        self.selected_history_item = None
        self.history_back_rect = None
        self.history_clear_rect = None
        self.history_main_rect = None
        
        # Settings state
        self.showing_settings = False
        self.settings_options = {
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
            'auto_complete': True  # NEW: Auto-complete setting
        }
        
        # Top bar elements - MOVED TO TOP RIGHT CORNER
        self.top_bar_rect = None
        self.audio_indicator_rect = None
        self.definition_indicator_rect = None
        self.word_count_rect = None
        self.status_rect = None
        self.settings_rect = None
        
        # Settings elements
        self.settings_elements = {}
        self.settings_close_rect = None
        self.settings_scrollbar_rect = None
        self.settings_max_scroll = 0
        self.settings_content_area = None
        
        # Mouse position for hover effects
        self.mouse_pos = (0, 0)
        
        # Suggestion button rects
        self.suggestion_rects = []
        
        # Initialize UI positions
        self.update_ui_positions()
        
        # Initialize fonts based on settings
        self._update_fonts()
    
    def _init_spinner(self):
        """Initialize the spinner loader position"""
        # Position will be updated in update_ui_positions
        self.spinner = SpinnerLoader(0, 0, 400, 60)
    
    def start_spinner(self, message="Loading..."):
        """Start the spinner animation"""
        self.spinner.start(message)
    
    def stop_spinner(self):
        """Stop the spinner animation"""
        self.spinner.stop()
    
    def set_spinner_progress(self, value, max_value=100, message=None):
        """Set spinner progress values"""
        self.spinner.set_progress(value, max_value, message)
    
    def _update_fonts(self):
        """Update font sizes based on settings"""
        font_size = self.settings_options.get('font_size', 'medium')
        
        if font_size == 'small':
            self.title_font = pygame.font.SysFont('arial', 24, bold=True)
            self.normal_font = pygame.font.SysFont('arial', 14)
            self.small_font = pygame.font.SysFont('arial', 12)
            self.tiny_font = pygame.font.SysFont('arial', 10)
        elif font_size == 'large':
            self.title_font = pygame.font.SysFont('arial', 36, bold=True)
            self.normal_font = pygame.font.SysFont('arial', 20)
            self.small_font = pygame.font.SysFont('arial', 16)
            self.tiny_font = pygame.font.SysFont('arial', 14)
        else:  # medium (default)
            self.title_font = pygame.font.SysFont('arial', 30, bold=True)
            self.normal_font = pygame.font.SysFont('arial', 16)
            self.small_font = pygame.font.SysFont('arial', 14)
            self.tiny_font = pygame.font.SysFont('arial', 12)
        
        print(f"Font size updated to: {font_size}")
    
    def apply_theme(self):
        """Apply current theme colors"""
        theme = self.themes[self.current_theme]
        for attr, value in theme.items():
            setattr(self, attr, value)
    
    def apply_theme_settings(self):
        """Apply theme from settings"""
        self.current_theme = self.settings_options.get('theme', 'light')
        self.apply_theme()
    
    def set_settings(self, settings):
        """Apply settings to the view"""
        self.settings_options.update(settings)
        self.current_theme = settings.get('theme', 'light')
        self.apply_theme()
        # APPLY FONT SETTINGS
        self._update_fonts()
        print("Settings applied to view")
    
    def _create_icons(self):
        """Create icon surfaces for buttons"""
        icons = {}
        icon_size = (24, 24)
        
        # Audio icon (speaker)
        audio_icon = pygame.Surface(icon_size, pygame.SRCALPHA)
        pygame.draw.polygon(audio_icon, (255, 255, 255), [(6, 14), (6, 10), (10, 10), (10, 6), (14, 12), (10, 18), (10, 14)])
        icons['audio'] = audio_icon
        
        # Definition icon (book)
        definition_icon = pygame.Surface(icon_size, pygame.SRCALPHA)
        pygame.draw.rect(definition_icon, (255, 255, 255), (6, 6, 12, 14), 2)
        pygame.draw.line(definition_icon, (255, 255, 255), (6, 10), (18, 10), 2)
        icons['definition'] = definition_icon
        
        # Word count icon (books)
        word_count_icon = pygame.Surface(icon_size, pygame.SRCALPHA)
        pygame.draw.rect(word_count_icon, (255, 255, 255), (5, 8, 6, 10), 1)
        pygame.draw.rect(word_count_icon, (255, 255, 255), (11, 6, 6, 12), 1)
        pygame.draw.rect(word_count_icon, (255, 255, 255), (17, 4, 4, 14), 1)
        icons['word_count'] = word_count_icon
        
        # Status icons
        online_icon = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(online_icon, (0, 255, 0), (8, 8), 6)
        icons['online'] = online_icon
        
        offline_icon = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(offline_icon, (255, 0, 0), (8, 8), 6)
        icons['offline'] = offline_icon
        
        local_icon = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(local_icon, (0, 150, 255), (8, 8), 6)
        icons['local'] = local_icon
        
        # Settings icon (gear)
        settings_icon = pygame.Surface(icon_size, pygame.SRCALPHA)
        pygame.draw.circle(settings_icon, (255, 255, 255), (12, 12), 8, 2)
        for i in range(6):
            angle = i * 60
            rad_angle = angle * 3.14159 / 180
            x1 = 12 + 6 * math.cos(rad_angle)
            y1 = 12 + 6 * math.sin(rad_angle)
            x2 = 12 + 9 * math.cos(rad_angle)
            y2 = 12 + 9 * math.sin(rad_angle)
            pygame.draw.line(settings_icon, (255, 255, 255), (x1, y1), (x2, y2), 2)
        icons['settings'] = settings_icon
        
        # Search icon (magnifying glass)
        search_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(search_icon, (255, 255, 255), (12, 12), 8, 2)
        pygame.draw.line(search_icon, (255, 255, 255), (16, 16), (22, 22), 2)
        icons['search'] = search_icon
        
        # History icon (clock)
        history_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(history_icon, (255, 255, 255), (15, 15), 10, 2)
        pygame.draw.line(history_icon, (255, 255, 255), (15, 15), (15, 8), 2)
        pygame.draw.line(history_icon, (255, 255, 255), (15, 15), (20, 15), 2)
        icons['history'] = history_icon
        
        # Play icon (triangle)
        play_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.polygon(play_icon, (255, 255, 255), [(8, 6), (8, 24), (22, 15)])
        icons['play'] = play_icon
        
        # Pause icon (two bars)
        pause_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(pause_icon, (255, 255, 255), (8, 6, 5, 18))
        pygame.draw.rect(pause_icon, (255, 255, 255), (17, 6, 5, 18))
        icons['pause'] = pause_icon
        
        # Stop icon (square)
        stop_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(stop_icon, (255, 255, 255), (8, 8, 14, 14))
        icons['stop'] = stop_icon
        
        # Speak icon (sound waves)
        speak_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.arc(speak_icon, (255, 255, 255), (5, 5, 20, 20), 0.5, 2.6, 2)
        pygame.draw.arc(speak_icon, (255, 255, 255), (2, 2, 26, 26), 0.4, 2.7, 2)
        pygame.draw.polygon(speak_icon, (255, 255, 255), [(8, 12), (8, 18), (12, 15)])
        icons['speak'] = speak_icon
        
        # Home icon (for history back button)
        home_icon = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.polygon(home_icon, (255, 255, 255), [(12, 5), (5, 12), (5, 20), (19, 20), (19, 12)])
        pygame.draw.rect(home_icon, (255, 255, 255), (10, 14, 4, 6))
        icons['home'] = home_icon
        
        # Back arrow icon
        back_icon = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.polygon(back_icon, (255, 255, 255), [(18, 5), (18, 20), (5, 12.5)])
        icons['back'] = back_icon
        
        return icons
    
    def create_audio_loading_animation(self):
        """Create loading animation for audio buttons"""
        self.audio_loading_frames = []
        for i in range(8):
            frame = pygame.Surface((24, 24), pygame.SRCALPHA)
            dots = min(i + 1, 3)
            for j in range(dots):
                x_pos = 6 + j * 8
                alpha = 255 - (j * 80)
                pygame.draw.circle(frame, (255, 255, 255, alpha), (x_pos, 12), 2)
            self.audio_loading_frames.append(frame)
    
    def update_ui_positions(self):
        """Update all UI element positions based on current screen size"""
        # Ensure minimum size
        self.screen_width = max(self.MIN_WIDTH, self.screen_width)
        self.screen_height = max(self.MIN_HEIGHT, self.screen_height)
        
        # Top bar layout - MOVED TO TOP RIGHT CORNER
        top_bar_height = 60
        self.top_bar_rect = pygame.Rect(0, 0, self.screen_width, top_bar_height)
        
        # Top bar elements - positioned from right to left
        element_width = 80
        element_height = 36
        element_y = (top_bar_height - element_height) // 2 + 5  # MOVED DOWN BY 5 PIXELS
        element_spacing = 10
        
        # Calculate total width needed for all elements
        total_elements_width = 5 * element_width + 4 * element_spacing
        
        # Start from right edge and position elements leftwards
        start_x = self.screen_width - 20 - total_elements_width
        
        self.settings_rect = pygame.Rect(start_x, element_y, element_width, element_height)
        self.status_rect = pygame.Rect(start_x + element_width + element_spacing, element_y, element_width, element_height)
        self.word_count_rect = pygame.Rect(start_x + 2*(element_width + element_spacing), element_y, element_width, element_height)
        self.definition_indicator_rect = pygame.Rect(start_x + 3*(element_width + element_spacing), element_y, element_width, element_height)
        self.audio_indicator_rect = pygame.Rect(start_x + 4*(element_width + element_spacing), element_y, element_width, element_height)
        
        # Center input box - responsive
        input_width = min(500, self.screen_width - 100)
        self.input_box = pygame.Rect(
            self.screen_width // 2 - input_width // 2, 
            top_bar_height + 80, 
            input_width, 
            50
        )
        
        # Position spinner right under the input box
        spinner_width = input_width
        spinner_height = 60
        spinner_x = self.screen_width // 2 - spinner_width // 2
        spinner_y = self.input_box.bottom + 20
        
        # Update spinner position
        self.spinner.rect = pygame.Rect(spinner_x, spinner_y, spinner_width, spinner_height)
        
        # Content area - responsive (moved down to accommodate spinner)
        content_top = spinner_y + spinner_height + 40
        content_bottom_margin = 30
        content_horizontal_margin = max(40, self.screen_width * 0.05)  # 5% margin or 40px
        
        self.content_rect = pygame.Rect(
            content_horizontal_margin, 
            content_top, 
            self.screen_width - content_horizontal_margin * 2, 
            self.screen_height - content_top - content_bottom_margin
        )
        
        # Reset scroll when layout changes
        self.scroll_offset = 0
        
        # Recalculate content height if we have word data
        if self.current_word_data:
            self.content_height = self.calculate_content_height(self.current_word_data)
            self.max_scroll = max(0, self.content_height - self.content_rect.height)
    
    def handle_resize(self, event):
        """Handle window resize event with minimum size enforcement"""
        new_width = max(self.MIN_WIDTH, event.w)
        new_height = max(self.MIN_HEIGHT, event.h)
        
        if new_width != event.w or new_height != event.h:
            # Enforce minimum size
            self.screen_width = new_width
            self.screen_height = new_height
            self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
        else:
            self.screen_width, self.screen_height = event.w, event.h
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        
        self.update_ui_positions()
    
    def show_splash_screen(self, duration=3):
        """Display splash screen"""
        splash_bg = pygame.Surface((self.screen_width, self.screen_height))
        splash_bg.fill(self.WEBSTER_COLOR)
        
        title = self.title_font.render("Cellusys Audio Dictionary", True, (255, 255, 255))
        subtitle = self.normal_font.render("Powered by Webster's English Dictionary", True, (255, 255, 255))
        info_text = self.small_font.render("Works Online & Offline with 100,000+ Words", True, (255, 255, 255))
        
        self.screen.blit(splash_bg, (0, 0))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, self.screen_height//2 - 60))
        self.screen.blit(subtitle, (self.screen_width//2 - subtitle.get_width()//2, self.screen_height//2))
        self.screen.blit(info_text, (self.screen_width//2 - info_text.get_width()//2, self.screen_height//2 + 40))
        pygame.display.flip()
        
        start_time = time.time()
        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return
            time.sleep(0.1)
    
    def draw_top_bar(self, local_word_count, data_source, show_wifi_alert=False):
        """Draw the top bar with icons and status"""
        # Draw top bar background
        pygame.draw.rect(self.screen, self.TOP_BAR_BG, self.top_bar_rect)
        pygame.draw.line(self.screen, self.TOP_BAR_BORDER, (0, self.top_bar_rect.height), 
                        (self.screen_width, self.top_bar_rect.height), 2)
        
        # Audio auto-play indicator
        audio_color = self.AUTO_PLAY_COLOR if self.settings_options.get('auto_play_pronunciation', True) else self.DISABLED_COLOR
        pygame.draw.rect(self.screen, audio_color, self.audio_indicator_rect, border_radius=8)
        self.screen.blit(self.icons['audio'], (self.audio_indicator_rect.x + 10, self.audio_indicator_rect.y + 6))
        audio_text = self.tiny_font.render("Audio", True, (255, 255, 255))
        self.screen.blit(audio_text, (self.audio_indicator_rect.x + 40, self.audio_indicator_rect.y + 10))
        
        # Definition auto-speak indicator
        definition_color = self.AUTO_PLAY_COLOR if self.settings_options.get('auto_speak_definition', True) else self.DISABLED_COLOR
        pygame.draw.rect(self.screen, definition_color, self.definition_indicator_rect, border_radius=8)
        self.screen.blit(self.icons['definition'], (self.definition_indicator_rect.x + 10, self.definition_indicator_rect.y + 6))
        definition_text = self.tiny_font.render("Speak", True, (255, 255, 255))
        self.screen.blit(definition_text, (self.definition_indicator_rect.x + 40, self.definition_indicator_rect.y + 10))
        
        # Word count
        pygame.draw.rect(self.screen, self.LOCAL_COLOR, self.word_count_rect, border_radius=8)
        self.screen.blit(self.icons['word_count'], (self.word_count_rect.x + 10, self.word_count_rect.y + 6))
        count_text = self.tiny_font.render(f"{local_word_count:,}", True, (255, 255, 255))
        self.screen.blit(count_text, (self.word_count_rect.x + 40, self.word_count_rect.y + 10))
        
        # Status indicator - MOVED DOWN
        if data_source == "online":
            status_color = self.SUCCESS_COLOR
            status_icon = self.icons['online']
            status_text = "ONLINE"
        elif data_source == "webster":
            status_color = self.LOCAL_COLOR
            status_icon = self.icons['local']
            status_text = "LOCAL"
        else:
            status_color = self.OFFLINE_COLOR
            status_icon = self.icons['offline']
            status_text = "OFFLINE"
        
        pygame.draw.rect(self.screen, status_color, self.status_rect, border_radius=8)
        self.screen.blit(status_icon, (self.status_rect.x + 10, self.status_rect.y + 10))
        status_surface = self.tiny_font.render(status_text, True, (255, 255, 255))
        self.screen.blit(status_surface, (self.status_rect.x + 35, self.status_rect.y + 10))
        
        # Settings button
        settings_hover = self.settings_rect.collidepoint(self.mouse_pos)
        settings_color = self.ACCENT_COLOR if settings_hover else self.DISABLED_COLOR
        pygame.draw.rect(self.screen, settings_color, self.settings_rect, border_radius=8)
        self.screen.blit(self.icons['settings'], (self.settings_rect.x + 10, self.settings_rect.y + 6))
        settings_text = self.tiny_font.render("Settings", True, (255, 255, 255))
        self.screen.blit(settings_text, (self.settings_rect.x + 40, self.settings_rect.y + 10))
        
        # WiFi alert if needed
        if show_wifi_alert:
            alert_rect = pygame.Rect(self.screen_width - 350, self.top_bar_rect.height + 5, 330, 30)
            pygame.draw.rect(self.screen, self.ERROR_COLOR, alert_rect, border_radius=6)
            alert_text = self.small_font.render("⚠️ No internet - Using local dictionary", True, (255, 255, 255))
            self.screen.blit(alert_text, (alert_rect.x + 10, alert_rect.y + 8))
    
    def draw_wifi_alert(self, message):
        """Draw WiFi connection alert at TOP RIGHT corner"""
        # Position alert at top right corner
        alert_rect = pygame.Rect(self.screen_width - 340, 70, 330, 50)
        
        # Shadow
        shadow_rect = alert_rect.copy()
        shadow_rect.y += 2
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 30), shadow_surface.get_rect(), border_radius=10)
        self.screen.blit(shadow_surface, shadow_rect)
        
        pygame.draw.rect(self.screen, self.ERROR_COLOR, alert_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), alert_rect, 2, border_radius=10)
        
        alert_text = self.small_font.render(message, True, (255, 255, 255))
        self.screen.blit(alert_text, (alert_rect.x + 15, alert_rect.y + 12))
        
        suggestion = self.tiny_font.render("Using local dictionary", True, (255, 255, 255))
        self.screen.blit(suggestion, (alert_rect.x + 15, alert_rect.y + 28))

    def draw_audio_loading_indicator(self, rect, is_tts=False):
        """Draw audio loading animation on a button"""
        if is_tts:
            color = self.SPEAK_LOADING_COLOR
            text = "Generating..."
        else:
            color = self.AUDIO_LOADING_COLOR
            text = "Downloading..."
        
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        
        frame = self.audio_loading_frames[self.audio_loading_index]
        self.screen.blit(frame, (rect.x + rect.width//2 - 12, rect.y + rect.height//2 - 12))
        
        loading_text = self.small_font.render(text, True, (255, 255, 255))
        self.screen.blit(loading_text, (rect.x + rect.width//2 - loading_text.get_width()//2, rect.y + rect.height + 5))
        
        self.audio_loading_index = (self.audio_loading_index + 1) % len(self.audio_loading_frames)
    
    def calculate_content_height(self, word_data):
        """Calculate the total height needed for the content including synonyms/antonyms"""
        if not word_data or not word_data[0]:
            return 0
            
        try:
            height = 0
            height += 40
            height += 100
            
            for meaning in word_data[0].get('meanings', [])[:3]:
                height += 40
                
                for definition in meaning.get('definitions', [])[:2]:
                    def_text = definition.get('definition', '')
                    if def_text:
                        wrapped_def = self.wrap_text(def_text, self.content_rect.width - 40)
                        height += 25 * len(wrapped_def)
                    
                    if definition.get('example'):
                        example_text = f"Example: {definition['example']}"
                        wrapped_example = self.wrap_text(example_text, self.content_rect.width - 50)
                        height += 25 * len(wrapped_example)
                    
                    height += 15
                
                synonyms = meaning.get('synonyms', [])
                antonyms = meaning.get('antonyms', [])
                
                if synonyms:
                    height += 30
                    wrapped_synonyms = self.wrap_text(", ".join(synonyms[:5]), self.content_rect.width - 60)
                    height += 20 * len(wrapped_synonyms)
                
                if antonyms:
                    height += 30
                    wrapped_antonyms = self.wrap_text(", ".join(antonyms[:5]), self.content_rect.width - 60)
                    height += 20 * len(wrapped_antonyms)
                
                height += 20
            
            return max(height + 50, 200)
            
        except Exception as e:
            print(f"Error calculating content height: {e}")
            return 400
    
    def draw_scrollbar(self):
        """Draw scrollbar if content exceeds display area"""
        if self.content_height <= self.content_rect.height:
            self.scrollbar_rect = None
            self.scroll_offset = 0
            self.max_scroll = 0
            return
        
        visible_height = self.content_rect.height
        self.max_scroll = max(0, self.content_height - visible_height)
        
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
        
        scrollbar_width = 15
        scrollbar_x = self.content_rect.right - scrollbar_width - 5
        
        thumb_ratio = visible_height / self.content_height
        thumb_height = max(40, thumb_ratio * visible_height)
        
        if self.max_scroll > 0:
            scroll_ratio = self.scroll_offset / self.max_scroll
            track_space = visible_height - thumb_height
            thumb_position = scroll_ratio * track_space
        else:
            thumb_position = 0
        
        track_rect = pygame.Rect(scrollbar_x, self.content_rect.top, scrollbar_width, visible_height)
        pygame.draw.rect(self.screen, self.SCROLLBAR_COLOR, track_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 200, 200), track_rect, 2, border_radius=8)
        
        thumb_rect = pygame.Rect(scrollbar_x, self.content_rect.top + thumb_position, scrollbar_width, thumb_height)
        thumb_color = self.SCROLLBAR_ACTIVE_COLOR if self.scrollbar_dragging else self.SCROLLBAR_COLOR
        pygame.draw.rect(self.screen, thumb_color, thumb_rect, border_radius=8)
        pygame.draw.rect(self.screen, (150, 150, 150), thumb_rect, 1, border_radius=8)
        
        self.scrollbar_rect = thumb_rect
    
    def handle_scroll_offset(self, event):
        """Handle mouse wheel and scrollbar drag events"""
        # Handle settings scrollbar
        if self.showing_settings:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:  # Mouse wheel up
                    self.scroll_offset = max(0, self.scroll_offset - 60)
                    return True
                elif event.button == 5:  # Mouse wheel down
                    self.scroll_offset = min(self.settings_max_scroll, self.scroll_offset + 60)
                    return True
                elif event.button == 1:
                    if (hasattr(self, 'settings_scrollbar_rect') and 
                        self.settings_scrollbar_rect is not None and 
                        self.settings_scrollbar_rect.collidepoint(event.pos)):
                        self.scrollbar_dragging = True
                        self.scrollbar_drag_offset = event.pos[1] - self.settings_scrollbar_rect.y
                        return True
            
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1 and self.scrollbar_dragging:
                    self.scrollbar_dragging = False
                    return True
            
            elif event.type == MOUSEMOTION:
                if (self.scrollbar_dragging and 
                    hasattr(self, 'settings_content_area') and 
                    self.settings_content_area is not None and
                    hasattr(self, 'settings_scrollbar_rect') and
                    self.settings_scrollbar_rect is not None):
                    
                    thumb_height = self.settings_scrollbar_rect.height
                    content_height = self.settings_content_area.height
                    track_space = content_height - thumb_height
                    
                    if track_space > 0:
                        new_y = event.pos[1] - self.scrollbar_drag_offset
                        new_y = max(self.settings_content_area.top, 
                                  min(new_y, self.settings_content_area.bottom - thumb_height))
                        scroll_ratio = (new_y - self.settings_content_area.top) / track_space
                        self.scroll_offset = scroll_ratio * self.settings_max_scroll
                    return True
        
        # Handle history scrolling
        elif self.showing_history:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:  # Mouse wheel up
                    self.scroll_offset = max(0, self.scroll_offset - 60)
                    return True
                elif event.button == 5:  # Mouse wheel down
                    self.scroll_offset = min(self.max_scroll, self.scroll_offset + 60)
                    return True
                elif event.button == 1 and self.scrollbar_rect and self.scrollbar_rect.collidepoint(event.pos):
                    self.scrollbar_dragging = True
                    self.scrollbar_drag_offset = event.pos[1] - self.scrollbar_rect.y
                    return True
            
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.scrollbar_dragging = False
                    return True
            
            elif event.type == MOUSEMOTION:
                if self.scrollbar_dragging and self.scrollbar_rect:
                    thumb_height = self.scrollbar_rect.height
                    visible_height = self.content_rect.height
                    track_space = visible_height - thumb_height
                    
                    if track_space > 0:
                        new_y = event.pos[1] - self.scrollbar_drag_offset
                        new_y = max(self.content_rect.top, min(new_y, self.content_rect.bottom - thumb_height))
                        scroll_ratio = (new_y - self.content_rect.top) / track_space
                        self.scroll_offset = scroll_ratio * self.max_scroll
                    return True
        
        # Handle normal content scrolling (word definitions)
        else:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:  # Mouse wheel up
                    self.scroll_offset = max(0, self.scroll_offset - 60)
                    return True
                elif event.button == 5:  # Mouse wheel down
                    self.scroll_offset = min(self.max_scroll, self.scroll_offset + 60)
                    return True
                elif event.button == 1 and self.scrollbar_rect and self.scrollbar_rect.collidepoint(event.pos):
                    self.scrollbar_dragging = True
                    self.scrollbar_drag_offset = event.pos[1] - self.scrollbar_rect.y
                    return True
            
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.scrollbar_dragging = False
                    return True
            
            elif event.type == MOUSEMOTION:
                if self.scrollbar_dragging and self.scrollbar_rect:
                    thumb_height = self.scrollbar_rect.height
                    visible_height = self.content_rect.height
                    track_space = visible_height - thumb_height
                    
                    if track_space > 0:
                        new_y = event.pos[1] - self.scrollbar_drag_offset
                        new_y = max(self.content_rect.top, min(new_y, self.content_rect.bottom - thumb_height))
                        scroll_ratio = (new_y - self.content_rect.top) / track_space
                        self.scroll_offset = scroll_ratio * self.max_scroll
                    return True
        
        return False
    
    def set_word_data(self, word_data, data_source="online"):
        """Set the current word data and reset scroll"""
        self.current_word_data = word_data
        self.current_data_source = data_source
        self.scroll_offset = 0
        if word_data:
            self.content_height = self.calculate_content_height(word_data)
            self.max_scroll = max(0, self.content_height - self.content_rect.height)
        else:
            self.content_height = 0
            self.max_scroll = 0
    
    def set_suggested_words(self, suggested_words):
        """Set suggested words when word is not found"""
        self.suggested_words = suggested_words
    
    def set_audio_state(self, playing=False, paused=False, loading=False, tts_loading=False):
        """Set the current audio state"""
        self.audio_playing = playing
        self.audio_paused = paused
        self.audio_loading = loading
        self.tts_loading = tts_loading
    
    def set_auto_play_settings(self, pronunciation=True, definition=True):
        """Set auto-play settings"""
        self.settings_options['auto_play_pronunciation'] = pronunciation
        self.settings_options['auto_speak_definition'] = definition
    
    def set_history_data(self, history_data):
        """Set history data and switch to history view"""
        self.history_data = history_data
        self.showing_history = True
        self.selected_history_item = None
        self.scroll_offset = 0
        self.content_height = self.calculate_history_height()
        self.max_scroll = max(0, self.content_height - self.content_rect.height)
    
    def show_main_view(self):
        """Switch back to main dictionary view"""
        self.showing_history = False
        self.showing_settings = False
        self.selected_history_item = None
        self.suggested_words = []  # Clear suggestions
        self.scroll_offset = 0
        if self.current_word_data:
            self.content_height = self.calculate_content_height(self.current_word_data)
            self.max_scroll = max(0, self.content_height - self.content_rect.height)
        else:
            self.content_height = 0
            self.max_scroll = 0
    
    def show_settings(self):
        """Switch to settings view"""
        self.showing_settings = True
        self.showing_history = False
        self.selected_history_item = None
        self.scroll_offset = 0
        self.scrollbar_dragging = False
    
    def draw_settings_window(self):
        """Draw the settings window with scrolling support"""
        settings_width = min(800, self.screen_width - 100)
        settings_height = min(600, self.screen_height - 100)
        
        settings_rect = pygame.Rect(
            self.screen_width // 2 - settings_width // 2,
            (self.screen_height - settings_height) // 2,
            settings_width,
            settings_height
        )
        
        pygame.draw.rect(self.screen, self.SETTINGS_BG, settings_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.SETTINGS_BORDER, settings_rect, 2, border_radius=15)
        
        # Title bar (fixed at top)
        title_bar = pygame.Rect(settings_rect.x, settings_rect.y, settings_rect.width, 70)
        pygame.draw.rect(self.screen, self.HEADER_BG, title_bar, border_radius=15)
        
        title_text = self.title_font.render("Settings", True, self.WEBSTER_COLOR)
        self.screen.blit(title_text, (settings_rect.x + 30, settings_rect.y + 20))
        
        close_rect = pygame.Rect(settings_rect.right - 50, settings_rect.y + 20, 35, 35)
        close_hover = close_rect.collidepoint(self.mouse_pos)
        close_color = self.ERROR_COLOR if close_hover else (180, 60, 60)
        pygame.draw.rect(self.screen, close_color, close_rect, border_radius=8)
        close_text = self.normal_font.render("X", True, (255, 255, 255))
        self.screen.blit(close_text, (close_rect.x + 12, close_rect.y + 8))
        
        # Scrollable content area
        content_area = pygame.Rect(
            settings_rect.x + 20,
            settings_rect.y + 80,
            settings_rect.width - 60,
            settings_rect.height - 170
        )
        
        # Calculate total content height
        total_height = 0
        categories = [
            ("Audio & Speech", [
                ('auto_play_pronunciation', 'Auto-play pronunciation', 'toggle'),
                ('auto_speak_definition', 'Auto-speak definition', 'toggle'),
                ('play_sound_effects', 'Play sound effects', 'toggle'),
                ('audio_volume', 'Audio volume', 'slider')
            ]),
            ("History & Data", [
                ('clear_history_on_exit', 'Clear history on exit', 'toggle'),
                ('auto_export_history', 'Auto-export history', 'toggle'),
                ('search_suggestions', 'Search suggestions', 'toggle'),
                ('offline_mode', 'Offline mode only', 'toggle')
            ]),
            ("Appearance", [
                ('font_size', 'Font size', 'dropdown'),
                ('theme', 'Color theme', 'dropdown')
            ]),
            ("Input & Search", [
                ('auto_complete', 'Auto-complete suggestions', 'toggle')  # NEW: Auto-complete setting
            ])
        ]
        
        for category_name, settings in categories:
            total_height += 50  # Category header
            total_height += len(settings) * 55  # Settings items
            total_height += 20  # Spacing after category
        
        # Setup scrolling for settings
        self.settings_max_scroll = max(0, total_height - content_area.height)
        
        # Create clipping rect for scrollable content
        clip_rect = pygame.Rect(content_area.x, content_area.y, content_area.width, content_area.height)
        old_clip = self.screen.get_clip()
        self.screen.set_clip(clip_rect)
        
        y_offset = content_area.y - self.scroll_offset
        self.settings_elements = {}
        
        for category_name, settings in categories:
            # Category header
            if y_offset > content_area.y - 50 and y_offset < content_area.bottom:
                category_bg = pygame.Rect(content_area.x, y_offset, content_area.width, 40)
                pygame.draw.rect(self.screen, self.HEADER_BG, category_bg, border_radius=8)
                
                category_text = self.normal_font.render(category_name, True, self.ACCENT_COLOR)
                self.screen.blit(category_text, (content_area.x + 15, y_offset + 10))
            y_offset += 50
            
            for setting_key, setting_label, setting_type in settings:
                if y_offset > content_area.y - 60 and y_offset < content_area.bottom + 10:
                    # Setting label
                    label_text = self.small_font.render(setting_label, True, self.TEXT_COLOR)
                    self.screen.blit(label_text, (content_area.x + 20, y_offset + 12))
                    
                    # Setting control
                    control_x = content_area.x + content_area.width - 280
                    
                    if setting_type == 'toggle':
                        toggle_rect = pygame.Rect(control_x, y_offset + 8, 70, 35)
                        is_on = self.settings_options[setting_key]
                        toggle_color = self.SUCCESS_COLOR if is_on else self.DISABLED_COLOR
                        pygame.draw.rect(self.screen, toggle_color, toggle_rect, border_radius=18)
                        
                        knob_x = toggle_rect.x + 45 if is_on else toggle_rect.x + 12
                        pygame.draw.circle(self.screen, (255, 255, 255), (knob_x, toggle_rect.y + 17), 13)
                        
                        status_text = self.tiny_font.render("ON" if is_on else "OFF", True, (255, 255, 255))
                        self.screen.blit(status_text, (toggle_rect.x + 85, toggle_rect.y + 12))
                        
                        self.settings_elements[setting_key] = toggle_rect
                    
                    elif setting_type == 'slider':
                        slider_bg = pygame.Rect(control_x, y_offset + 18, 180, 14)
                        pygame.draw.rect(self.screen, self.DISABLED_COLOR, slider_bg, border_radius=7)
                        
                        fill_width = (self.settings_options[setting_key] / 100) * 180
                        fill_rect = pygame.Rect(control_x, y_offset + 18, fill_width, 14)
                        pygame.draw.rect(self.screen, self.ACCENT_COLOR, fill_rect, border_radius=7)
                        
                        handle_x = control_x + fill_width
                        handle_rect = pygame.Rect(handle_x - 10, y_offset + 10, 20, 30)
                        pygame.draw.rect(self.screen, self.TEXT_COLOR, handle_rect, border_radius=10)
                        
                        vol_text = self.small_font.render(f"{self.settings_options[setting_key]}%", True, self.TEXT_COLOR)
                        self.screen.blit(vol_text, (control_x + 195, y_offset + 12))
                        
                        self.settings_elements[setting_key] = pygame.Rect(control_x, y_offset, 220, 50)
                    
                    elif setting_type == 'dropdown':
                        dropdown_rect = pygame.Rect(control_x, y_offset + 8, 200, 40)
                        pygame.draw.rect(self.screen, self.INPUT_BG, dropdown_rect, border_radius=8)
                        pygame.draw.rect(self.screen, self.ACCENT_COLOR, dropdown_rect, 2, border_radius=8)
                        
                        current_value = self.settings_options[setting_key]
                        value_text = self.small_font.render(str(current_value).title(), True, self.TEXT_COLOR)
                        self.screen.blit(value_text, (dropdown_rect.x + 15, dropdown_rect.y + 12))
                        
                        pygame.draw.polygon(self.screen, self.ACCENT_COLOR, [
                            (dropdown_rect.right - 30, dropdown_rect.y + 15),
                            (dropdown_rect.right - 15, dropdown_rect.y + 15),
                            (dropdown_rect.right - 22, dropdown_rect.y + 25)
                        ])
                        
                        self.settings_elements[setting_key] = dropdown_rect
                
                y_offset += 55
            
            y_offset += 20
        
        self.screen.set_clip(old_clip)
        
        # Draw scrollbar for settings if needed
        if total_height > content_area.height:
            scrollbar_width = 12
            scrollbar_x = content_area.right + 5
            
            thumb_ratio = content_area.height / total_height
            thumb_height = max(40, thumb_ratio * content_area.height)
            
            if self.settings_max_scroll > 0:
                scroll_ratio = self.scroll_offset / self.settings_max_scroll
                track_space = content_area.height - thumb_height
                thumb_position = scroll_ratio * track_space
            else:
                thumb_position = 0
            
            # Track
            track_rect = pygame.Rect(scrollbar_x, content_area.top, scrollbar_width, content_area.height)
            pygame.draw.rect(self.screen, self.SCROLLBAR_COLOR, track_rect, border_radius=6)
            
            # Thumb
            thumb_rect = pygame.Rect(scrollbar_x, content_area.top + thumb_position, scrollbar_width, thumb_height)
            thumb_color = self.SCROLLBAR_ACTIVE_COLOR if self.scrollbar_dragging else self.ACCENT_COLOR
            pygame.draw.rect(self.screen, thumb_color, thumb_rect, border_radius=6)
            
            # Store for drag detection
            self.settings_scrollbar_rect = thumb_rect
            self.settings_content_area = content_area
        else:
            self.settings_scrollbar_rect = None
        
        # Action buttons (fixed at bottom)
        button_y = settings_rect.bottom - 65
        button_width = 160
        button_height = 50
        
        # Shadow for buttons
        shadow_offset = 3
        
        # Save button
        save_rect = pygame.Rect(settings_rect.x + 120, button_y, button_width, button_height)
        save_hover = save_rect.collidepoint(self.mouse_pos)
        
        shadow_rect = save_rect.copy()
        shadow_rect.y += shadow_offset
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 40), shadow_surface.get_rect(), border_radius=10)
        self.screen.blit(shadow_surface, shadow_rect)
        
        save_color = self.SUCCESS_COLOR if save_hover else (70, 160, 70)
        pygame.draw.rect(self.screen, save_color, save_rect, border_radius=10)
        save_text = self.normal_font.render("Save Settings", True, (255, 255, 255))
        self.screen.blit(save_text, (save_rect.x + 25, save_rect.y + 15))
        self.settings_elements['save'] = save_rect
        
        # Reset button
        reset_rect = pygame.Rect(settings_rect.x + 320, button_y, button_width, button_height)
        reset_hover = reset_rect.collidepoint(self.mouse_pos)
        
        shadow_rect = reset_rect.copy()
        shadow_rect.y += shadow_offset
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 40), shadow_surface.get_rect(), border_radius=10)
        self.screen.blit(shadow_surface, shadow_rect)
        
        reset_color = self.ERROR_COLOR if reset_hover else (180, 60, 60)
        pygame.draw.rect(self.screen, reset_color, reset_rect, border_radius=10)
        reset_text = self.normal_font.render("Reset Defaults", True, (255, 255, 255))
        self.screen.blit(reset_text, (reset_rect.x + 20, reset_rect.y + 15))
        self.settings_elements['reset'] = reset_rect
        
        # Cancel button
        cancel_rect = pygame.Rect(settings_rect.x + 520, button_y, button_width, button_height)
        cancel_hover = cancel_rect.collidepoint(self.mouse_pos)
        
        shadow_rect = cancel_rect.copy()
        shadow_rect.y += shadow_offset
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 40), shadow_surface.get_rect(), border_radius=10)
        self.screen.blit(shadow_surface, shadow_rect)
        
        cancel_color = self.DISABLED_COLOR if cancel_hover else (120, 120, 120)
        pygame.draw.rect(self.screen, cancel_color, cancel_rect, border_radius=10)
        cancel_text = self.normal_font.render("Cancel", True, (255, 255, 255))
        self.screen.blit(cancel_text, (cancel_rect.x + 50, cancel_rect.y + 15))
        self.settings_elements['cancel'] = cancel_rect
        
        self.settings_close_rect = close_rect
        return close_rect
    
    def handle_settings_click(self, pos):
        """Handle clicks in the settings window"""
        # Check close button first
        if hasattr(self, 'settings_close_rect') and self.settings_close_rect and self.settings_close_rect.collidepoint(pos):
            return 'cancel'
        
        for setting_key, rect in self.settings_elements.items():
            if rect.collidepoint(pos):
                if setting_key == 'save':
                    return 'save'
                elif setting_key == 'reset':
                    return 'reset'
                elif setting_key == 'cancel':
                    return 'cancel'
                elif setting_key in ['auto_play_pronunciation', 'auto_speak_definition', 
                                   'clear_history_on_exit', 'auto_export_history',
                                   'play_sound_effects', 'search_suggestions', 'offline_mode', 'auto_complete']:
                    self.settings_options[setting_key] = not self.settings_options[setting_key]
                    return 'toggle'
                elif setting_key == 'audio_volume':
                    rel_x = pos[0] - rect.x
                    volume = max(0, min(100, int((rel_x / 220) * 100)))
                    self.settings_options[setting_key] = volume
                    return 'volume'
                elif setting_key == 'font_size':
                    sizes = ['small', 'medium', 'large']
                    current_index = sizes.index(self.settings_options[setting_key])
                    self.settings_options[setting_key] = sizes[(current_index + 1) % len(sizes)]
                    # UPDATE FONTS IMMEDIATELY
                    self._update_fonts()
                    return 'font_size'
                elif setting_key == 'theme':
                    themes = ['light', 'dark', 'blue']
                    current_index = themes.index(self.settings_options[setting_key])
                    self.settings_options[setting_key] = themes[(current_index + 1) % len(themes)]
                    self.current_theme = self.settings_options[setting_key]
                    self.apply_theme()
                    return 'theme'
        return None
    
    def get_settings(self):
        """Get current settings"""
        return self.settings_options.copy()
    
    # NEW: Auto-suggestion methods
    def set_auto_suggestions(self, suggestions):
        """Set auto-suggestions for the input box"""
        self.suggestions = suggestions[:5]  # Limit to 5 suggestions
        self.show_suggestions = len(suggestions) > 0 and self.settings_options.get('auto_complete', True)
        self.selected_suggestion = 0
    
    def draw_auto_suggestions(self):
        """Draw auto-suggestion dropdown"""
        if not self.show_suggestions or not self.suggestions:
            return
        
        suggestion_height = 35
        dropdown_width = self.input_box.width
        dropdown_x = self.input_box.x
        dropdown_y = self.input_box.bottom
        
        # Draw dropdown background
        dropdown_rect = pygame.Rect(dropdown_x, dropdown_y, dropdown_width, len(self.suggestions) * suggestion_height)
        pygame.draw.rect(self.screen, self.SUGGESTION_BG, dropdown_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.SETTINGS_BORDER, dropdown_rect, 2, border_radius=8)
        
        self.suggestion_boxes = []
        
        for i, suggestion in enumerate(self.suggestions):
            suggestion_rect = pygame.Rect(dropdown_x, dropdown_y + i * suggestion_height, dropdown_width, suggestion_height)
            self.suggestion_boxes.append(suggestion_rect)
            
            # Highlight selected suggestion or hovered suggestion
            if i == self.selected_suggestion:
                pygame.draw.rect(self.screen, self.SUGGESTION_SELECTED, suggestion_rect, border_radius=6)
            elif suggestion_rect.collidepoint(self.mouse_pos):
                pygame.draw.rect(self.screen, self.SUGGESTION_HOVER, suggestion_rect, border_radius=6)
            
            # Draw suggestion text
            suggestion_text = self.small_font.render(suggestion, True, self.TEXT_COLOR)
            text_x = suggestion_rect.x + 15
            text_y = suggestion_rect.y + (suggestion_rect.height - suggestion_text.get_height()) // 2
            self.screen.blit(suggestion_text, (text_x, text_y))
    
    def handle_suggestion_click(self, pos):
        """Handle clicks on auto-suggestion items"""
        for i, rect in enumerate(self.suggestion_boxes):
            if rect.collidepoint(pos):
                return self.suggestions[i]
        return None
    
    def handle_suggestion_navigation(self, event):
        """Handle keyboard navigation for suggestions"""
        if not self.show_suggestions:
            return False
        
        if event.key == K_DOWN:
            self.selected_suggestion = (self.selected_suggestion + 1) % len(self.suggestions)
            return True
        elif event.key == K_UP:
            self.selected_suggestion = (self.selected_suggestion - 1) % len(self.suggestions)
            return True
        elif event.key == K_RETURN and self.suggestions:
            # Apply selected suggestion
            self.input_text = self.suggestions[self.selected_suggestion]
            self.cursor_position = len(self.input_text)
            self.show_suggestions = False
            return True
        elif event.key == K_ESCAPE:
            self.show_suggestions = False
            return True
        
        return False
    
    def draw_input_with_cursor(self):
        """Draw input box with cursor and text"""
        # Elegant input box with shadow
        shadow_box = self.input_box.copy()
        shadow_box.y += 3
        shadow_surface = pygame.Surface((shadow_box.width, shadow_box.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 30), shadow_surface.get_rect(), border_radius=12)
        self.screen.blit(shadow_surface, shadow_box)
        
        pygame.draw.rect(self.screen, self.INPUT_BG, self.input_box, border_radius=12)
        border_color = self.ACCENT_COLOR if self.active else (220, 220, 220)
        pygame.draw.rect(self.screen, border_color, self.input_box, 2, border_radius=12)
        
        # Calculate text position with cursor
        text_before_cursor = self.input_text[:self.cursor_position]
        text_after_cursor = self.input_text[self.cursor_position:]
        
        # Render text before cursor
        if text_before_cursor:
            before_surface = self.normal_font.render(text_before_cursor, True, self.TEXT_COLOR)
            self.screen.blit(before_surface, (self.input_box.x + 15, self.input_box.y + 15))
        
        # Calculate cursor position
        cursor_x = self.input_box.x + 15
        if text_before_cursor:
            before_width = self.normal_font.render(text_before_cursor, True, self.TEXT_COLOR).get_width()
            cursor_x += before_width
        
        # Draw cursor when active
        if self.active and self.cursor_visible:
            cursor_rect = pygame.Rect(cursor_x, self.input_box.y + 15, 2, 25)
            pygame.draw.rect(self.screen, self.CURSOR_COLOR, cursor_rect)
        
        # Render text after cursor
        if text_after_cursor:
            after_surface = self.normal_font.render(text_after_cursor, True, self.TEXT_COLOR)
            self.screen.blit(after_surface, (cursor_x, self.input_box.y + 15))
        
        # Draw placeholder if no text
        if not self.input_text and not self.active:
            placeholder = self.normal_font.render("Enter a word...", True, self.DISABLED_COLOR)
            self.screen.blit(placeholder, (self.input_box.x + 15, self.input_box.y + 15))
    
    def handle_text_input(self, event):
        """Handle text input with cursor movement"""
        if not self.active:
            return False
        
        # Handle cursor movement
        if event.key == K_LEFT:
            self.cursor_position = max(0, self.cursor_position - 1)
            return True
        elif event.key == K_RIGHT:
            self.cursor_position = min(len(self.input_text), self.cursor_position + 1)
            return True
        elif event.key == K_HOME:
            self.cursor_position = 0
            return True
        elif event.key == K_END:
            self.cursor_position = len(self.input_text)
            return True
        elif event.key == K_BACKSPACE:
            if self.cursor_position > 0:
                self.input_text = self.input_text[:self.cursor_position-1] + self.input_text[self.cursor_position:]
                self.cursor_position -= 1
                # Trigger auto-suggestions on backspace
                if self.settings_options.get('auto_complete', True) and len(self.input_text) > 0:
                    return 'update_suggestions'
            return True
        elif event.key == K_DELETE:
            if self.cursor_position < len(self.input_text):
                self.input_text = self.input_text[:self.cursor_position] + self.input_text[self.cursor_position+1:]
                # Trigger auto-suggestions on delete
                if self.settings_options.get('auto_complete', True) and len(self.input_text) > 0:
                    return 'update_suggestions'
            return True
        elif event.key == K_RETURN:
            # Don't handle return here - let controller handle search
            return False
        elif event.unicode and len(event.unicode) > 0 and ord(event.unicode) >= 32:  # Printable characters
            if len(self.input_text) < 50:
                self.input_text = (self.input_text[:self.cursor_position] + 
                                 event.unicode + 
                                 self.input_text[self.cursor_position:])
                self.cursor_position += len(event.unicode)
                # Trigger auto-suggestions on typing
                if self.settings_options.get('auto_complete', True):
                    return 'update_suggestions'
            return True
        
        return False
    
    def draw_main_interface(self, word_data=None, audio_available=False, data_source="online", local_word_count=0, dictionary_source="Unknown", show_wifi_alert=False):
        """Draw the main dictionary interface"""
        self.mouse_pos = pygame.mouse.get_pos()
        
        # Update cursor blink
        current_time = time.time()
        if current_time - self.cursor_timer > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time
        
        # Update spinner animation
        self.spinner.update()
        
        if word_data is not None and not self.showing_history and not self.showing_settings:
            self.set_word_data(word_data, data_source)
        
        self.screen.fill(self.BG_COLOR)
        
        # Draw top bar
        self.draw_top_bar(local_word_count, data_source, show_wifi_alert)
        
        # Draw elegant title with shadow
        title_text = "Cellusys Audio Dictionary"
        shadow = self.title_font.render(title_text, True, (0, 0, 0, 0))
        title = self.title_font.render(title_text, True, self.WEBSTER_COLOR)
        self.screen.blit(shadow, (self.screen_width//2 - title.get_width()//2 + 2, self.top_bar_rect.height + 22))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, self.top_bar_rect.height + 20))
        
        if self.showing_settings:
            close_rect = self.draw_settings_window()
            return None, None, None, close_rect
        elif self.showing_history:
            if self.selected_history_item is not None:
                self.display_history_item_details()
            else:
                self.display_history_list()
        elif self.current_word_data:
            self.display_word_data()
        elif self.suggested_words:
            self.display_suggestions()
        
        if not self.showing_settings and not (self.showing_history and self.selected_history_item is not None):
            self.draw_scrollbar()
        
        # Draw spinner loader
        current_theme_dict = {
            'SETTINGS_BG': self.SETTINGS_BG,
            'SETTINGS_BORDER': self.SETTINGS_BORDER,
            'TEXT_COLOR': self.TEXT_COLOR,
            'ACCENT_COLOR': self.ACCENT_COLOR,
            'DISABLED_COLOR': self.DISABLED_COLOR
        }
        self.spinner.draw(self.screen, self.normal_font, self.small_font, current_theme_dict)
        
        # Show WiFi alert if needed
        if show_wifi_alert:
            self.draw_wifi_alert("No internet connection")
        
        if not self.showing_settings and not (self.showing_history and self.selected_history_item is not None):
            # Draw input box with cursor
            self.draw_input_with_cursor()
            
            # Draw auto-suggestions
            self.draw_auto_suggestions()
            
            button_y = self.spinner.rect.bottom + 20  # Position buttons below spinner
            button_spacing = 15
            
            # Search button
            search_rect = pygame.Rect(self.screen_width//2 - 115, button_y, 110, 45)
            search_hover = search_rect.collidepoint(self.mouse_pos)
            
            shadow_rect = search_rect.copy()
            shadow_rect.y += 3
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 40), shadow_surface.get_rect(), border_radius=10)
            self.screen.blit(shadow_surface, shadow_rect)
            
            search_color = self.ACCENT_COLOR if search_hover else (100, 140, 200)
            pygame.draw.rect(self.screen, search_color, search_rect, border_radius=10)
            self.screen.blit(self.icons['search'], (search_rect.x + 15, search_rect.y + 7))
            search_text = self.normal_font.render("Search", True, (255, 255, 255))
            self.screen.blit(search_text, (search_rect.x + 50, search_rect.y + 13))
            
            # History button
            history_rect = pygame.Rect(self.screen_width//2 + 5, button_y, 110, 45)
            history_hover = history_rect.collidepoint(self.mouse_pos)
            
            shadow_rect = history_rect.copy()
            shadow_rect.y += 3
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 40), shadow_surface.get_rect(), border_radius=10)
            self.screen.blit(shadow_surface, shadow_rect)
            
            history_color = self.HISTORY_COLOR if history_hover else (120, 70, 30)
            pygame.draw.rect(self.screen, history_color, history_rect, border_radius=10)
            self.screen.blit(self.icons['history'], (history_rect.x + 15, history_rect.y + 7))
            history_text = self.normal_font.render("History", True, (255, 255, 255))
            self.screen.blit(history_text, (history_rect.x + 50, history_rect.y + 13))
            
            # Audio controls
            audio_rects = {}
            if self.current_word_data and not self.showing_history:
                control_y = button_y + 70
                
                # Show audio controls for ALL word types that have audio available
                has_audio = self.current_word_data[0].get('has_audio', False) if self.current_word_data else False
                audio_available = self.current_word_data[0].get('audio_available', False) if self.current_word_data else False
                
                if (audio_available or has_audio) and self.current_data_source in ["online", "webster", "webster_suggestion", "not_found"]:
                    # Play/Pause button - show for ALL word types with audio
                    play_rect = pygame.Rect(self.screen_width//2 - 135, control_y, 85, 45)
                    play_hover = play_rect.collidepoint(self.mouse_pos)
                    
                    shadow_rect = play_rect.copy()
                    shadow_rect.y += 2
                    shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(shadow_surface, (0, 0, 0, 40), shadow_surface.get_rect(), border_radius=10)
                    self.screen.blit(shadow_surface, shadow_rect)
                    
                    if self.audio_loading:
                        self.draw_audio_loading_indicator(play_rect, is_tts=False)
                    else:
                        play_color = self.AUDIO_PLAY_COLOR if not self.audio_playing else self.AUDIO_PAUSE_COLOR
                        if play_hover:
                            play_color = tuple(min(c + 30, 255) for c in play_color)
                        pygame.draw.rect(self.screen, play_color, play_rect, border_radius=10)
                        icon = self.icons['play'] if not self.audio_playing else self.icons['pause']
                        self.screen.blit(icon, (play_rect.x + 27, play_rect.y + 7))
                    
                    audio_rects['play'] = play_rect
                    
                    # Stop button - show for ALL word types with audio
                    stop_rect = pygame.Rect(self.screen_width//2 - 42, control_y, 85, 45)
                    stop_hover = stop_rect.collidepoint(self.mouse_pos)
                    
                    shadow_rect = stop_rect.copy()
                    shadow_rect.y += 2
                    shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(shadow_surface, (0, 0, 0, 40), shadow_surface.get_rect(), border_radius=10)
                    self.screen.blit(shadow_surface, shadow_rect)
                    
                    stop_color = self.AUDIO_STOP_COLOR if (self.audio_playing or self.audio_loading) else self.DISABLED_COLOR
                    if stop_hover and (self.audio_playing or self.audio_loading):
                        stop_color = tuple(min(c + 30, 255) for c in stop_color)
                    pygame.draw.rect(self.screen, stop_color, stop_rect, border_radius=10)
                    self.screen.blit(self.icons['stop'], (stop_rect.x + 27, stop_rect.y + 7))
                    audio_rects['stop'] = stop_rect
                    
                    # Text-to-speech button
                    speak_rect = pygame.Rect(self.screen_width//2 + 51, control_y, 85, 45)
                    speak_hover = speak_rect.collidepoint(self.mouse_pos)
                    
                    shadow_rect = speak_rect.copy()
                    shadow_rect.y += 2
                    shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(shadow_surface, (0, 0, 0, 40), shadow_surface.get_rect(), border_radius=10)
                    self.screen.blit(shadow_surface, shadow_rect)
                    
                    if self.tts_loading:
                        self.draw_audio_loading_indicator(speak_rect, is_tts=True)
                    else:
                        speak_color = self.SPEAK_COLOR if not self.tts_loading else self.DISABLED_COLOR
                        if speak_hover and not self.tts_loading:
                            speak_color = tuple(min(c + 30, 255) for c in speak_color)
                        pygame.draw.rect(self.screen, speak_color, speak_rect, border_radius=10)
                        self.screen.blit(self.icons['speak'], (speak_rect.x + 27, speak_rect.y + 7))
                    
                    audio_rects['speak'] = speak_rect
                    
                elif self.current_data_source == "webster" and self.current_word_data and not self.showing_history:
                    # Webster's indicator
                    webster_rect = pygame.Rect(self.screen_width//2 - 110, control_y, 220, 45)
                    
                    shadow_rect = webster_rect.copy()
                    shadow_rect.y += 2
                    shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(shadow_surface, (0, 0, 0, 30), shadow_surface.get_rect(), border_radius=10)
                    self.screen.blit(shadow_surface, shadow_rect)
                    
                    pygame.draw.rect(self.screen, self.LOCAL_COLOR, webster_rect, border_radius=10)
                    webster_text = self.normal_font.render("📚 Webster's Dictionary", True, (255, 255, 255))
                    self.screen.blit(webster_text, (webster_rect.x + 25, webster_rect.y + 13))
                
                return search_rect, history_rect, audio_rects, self.settings_rect
            
            return search_rect, history_rect, {}, self.settings_rect
        
        return None, None, None, None

    # ... (rest of your existing methods: display_suggestions, display_history_list, etc.)
    # These should remain exactly as they were in your original code

    def display_suggestions(self):
        """Display word suggestions when word is not found"""
        try:
            clip_rect = pygame.Rect(self.content_rect.x, self.content_rect.y, 
                                  self.content_rect.width, self.content_rect.height)
            old_clip = self.screen.get_clip()
            self.screen.set_clip(clip_rect)
            
            y_offset = self.content_rect.y - self.scroll_offset
            
            # Error message
            error_text = self.title_font.render("Word Not Found", True, self.ERROR_COLOR)
            self.screen.blit(error_text, (self.content_rect.x + 20, y_offset))
            y_offset += 60
            
            # Suggestion message
            suggestion_text = self.normal_font.render("Did you mean one of these words?", True, self.TEXT_COLOR)
            self.screen.blit(suggestion_text, (self.content_rect.x + 20, y_offset))
            y_offset += 50
            
            # Display suggested words as clickable buttons
            self.suggestion_rects = []
            button_width = 200
            button_height = 45
            button_spacing = 15
            
            for i, word in enumerate(self.suggested_words[:6]):  # Show up to 6 suggestions
                if y_offset + button_height > self.content_rect.y and y_offset < self.content_rect.bottom:
                    button_x = self.content_rect.x + 20 + (i % 2) * (button_width + button_spacing)
                    button_y_pos = y_offset + (i // 2) * (button_height + button_spacing)
                    
                    suggestion_rect = pygame.Rect(button_x, button_y_pos, button_width, button_height)
                    is_hover = suggestion_rect.collidepoint(self.mouse_pos)
                    
                    # Draw shadow
                    shadow_rect = suggestion_rect.copy()
                    shadow_rect.y += 2
                    shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(shadow_surface, (0, 0, 0, 40), shadow_surface.get_rect(), border_radius=10)
                    self.screen.blit(shadow_surface, shadow_rect)
                    
                    # Draw button
                    button_color = self.SUGGESTION_COLOR if is_hover else (200, 120, 0)
                    pygame.draw.rect(self.screen, button_color, suggestion_rect, border_radius=10)
                    
                    # Draw word text
                    word_text = self.normal_font.render(word, True, (255, 255, 255))
                    text_x = suggestion_rect.x + (suggestion_rect.width - word_text.get_width()) // 2
                    text_y = suggestion_rect.y + (suggestion_rect.height - word_text.get_height()) // 2
                    self.screen.blit(word_text, (text_x, text_y))
                    
                    self.suggestion_rects.append((word, suggestion_rect))
            
            self.screen.set_clip(old_clip)
            pygame.draw.rect(self.screen, (200, 200, 200), self.content_rect, 1, border_radius=8)
            
        except Exception as e:
            print(f"Error displaying suggestions: {e}")
            error_text = self.normal_font.render("Error displaying suggestions", True, self.ERROR_COLOR)
            self.screen.blit(error_text, (self.content_rect.x, self.content_rect.y))

    def display_history_list(self):
        """Display the history list with clickable items"""
        try:
            clip_rect = pygame.Rect(self.content_rect.x, self.content_rect.y, 
                                  self.content_rect.width, self.content_rect.height)
            old_clip = self.screen.get_clip()
            self.screen.set_clip(clip_rect)
            
            y_offset = self.content_rect.y - self.scroll_offset
            
            header_rect = pygame.Rect(self.content_rect.x, y_offset, self.content_rect.width, 60)
            pygame.draw.rect(self.screen, self.HEADER_BG, header_rect)
            
            header_text = self.title_font.render("Search History", True, self.HISTORY_COLOR)
            self.screen.blit(header_text, (self.content_rect.x + 20, y_offset + 15))
            
            # FIXED: Use the correct home icon
            main_rect = pygame.Rect(self.content_rect.right - 280, y_offset + 10, 130, 40)
            main_hover = main_rect.collidepoint(self.mouse_pos)
            main_color = self.ACCENT_COLOR if main_hover else (80, 80, 180)
            pygame.draw.rect(self.screen, main_color, main_rect, border_radius=8)
            self.screen.blit(self.icons['home'], (main_rect.x + 15, main_rect.y + 8))
            main_text = self.small_font.render("Back to Search", True, (255, 255, 255))
            self.screen.blit(main_text, (main_rect.x + 45, main_rect.y + 12))
            
            clear_rect = pygame.Rect(self.content_rect.right - 140, y_offset + 10, 120, 40)
            clear_hover = clear_rect.collidepoint(self.mouse_pos)
            clear_color = self.ERROR_COLOR if clear_hover else (180, 60, 60)
            pygame.draw.rect(self.screen, clear_color, clear_rect, border_radius=8)
            clear_text = self.small_font.render("Clear All", True, (255, 255, 255))
            self.screen.blit(clear_text, (clear_rect.x + 25, clear_rect.y + 12))
            
            self.history_main_rect = main_rect
            self.history_clear_rect = clear_rect
            
            y_offset += 70
            
            self.history_entries_rects = []
            
            if not self.history_data:
                no_history_text = self.normal_font.render("No search history yet.", True, self.TEXT_COLOR)
                if y_offset + 30 > self.content_rect.y and y_offset < self.content_rect.bottom:
                    self.screen.blit(no_history_text, (self.content_rect.x + 20, y_offset))
                y_offset += 40
            else:
                for i, entry in enumerate(self.history_data):
                    entry_rect = pygame.Rect(self.content_rect.x + 10, y_offset, self.content_rect.width - 20, 70)
                    
                    is_hover = entry_rect.collidepoint(self.mouse_pos) and y_offset + 70 > self.content_rect.y and y_offset < self.content_rect.bottom
                    
                    entry_color = self.HISTORY_ENTRY_HOVER if is_hover else self.HISTORY_ENTRY_BG
                    pygame.draw.rect(self.screen, entry_color, entry_rect, border_radius=8)
                    pygame.draw.rect(self.screen, (200, 200, 200), entry_rect, 1, border_radius=8)
                    
                    if y_offset + 70 > self.content_rect.y and y_offset < self.content_rect.bottom:
                        word = entry.get('word', 'Unknown')
                        timestamp = entry.get('timestamp', '')
                        source = entry.get('source', 'unknown')
                        
                        try:
                            dt = datetime.datetime.fromisoformat(timestamp)
                            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            time_str = timestamp
                        
                        word_color = self.ACCENT_COLOR if source == "online" else self.LOCAL_COLOR
                        word_text = self.normal_font.render(f"{word}", True, word_color)
                        self.screen.blit(word_text, (self.content_rect.x + 20, y_offset + 10))
                        
                        time_text = self.small_font.render(f"Searched: {time_str}", True, self.OFFLINE_COLOR)
                        self.screen.blit(time_text, (self.content_rect.x + 20, y_offset + 35))
                        
                        source_text = self.small_font.render(f"Source: {source.upper()}", True, self.TEXT_COLOR)
                        self.screen.blit(source_text, (self.content_rect.x + 20, y_offset + 50))
                        
                        if is_hover:
                            hover_text = self.tiny_font.render("Click to view details", True, self.ACCENT_COLOR)
                            self.screen.blit(hover_text, (self.content_rect.right - 120, y_offset + 25))
                    
                    self.history_entries_rects.append((i, entry_rect))
                    y_offset += 80
            
            self.screen.set_clip(old_clip)
            pygame.draw.rect(self.screen, (200, 200, 200), self.content_rect, 1, border_radius=8)
            
        except Exception as e:
            print(f"Error displaying history list: {e}")
            error_text = self.normal_font.render("Error displaying history", True, self.ERROR_COLOR)
            self.screen.blit(error_text, (self.content_rect.x, self.content_rect.y))

    def display_history_item_details(self):
        """Display detailed view of a selected history item"""
        try:
            if self.selected_history_item is None or self.selected_history_item >= len(self.history_data):
                return
                
            entry = self.history_data[self.selected_history_item]
            word_data = entry.get('data', None)
            
            if not word_data:
                self.display_basic_history_item(entry)
                return
            
            clip_rect = pygame.Rect(self.content_rect.x, self.content_rect.y, 
                                  self.content_rect.width, self.content_rect.height)
            old_clip = self.screen.get_clip()
            self.screen.set_clip(clip_rect)
            
            y_offset = self.content_rect.y - self.scroll_offset
            
            nav_rect = pygame.Rect(self.content_rect.x, y_offset, self.content_rect.width, 60)
            pygame.draw.rect(self.screen, self.HEADER_BG, nav_rect)
            
            back_rect = pygame.Rect(self.content_rect.x + 20, y_offset + 10, 120, 40)
            back_hover = back_rect.collidepoint(self.mouse_pos)
            back_color = self.HISTORY_COLOR if back_hover else (120, 60, 20)
            pygame.draw.rect(self.screen, back_color, back_rect, border_radius=8)
            
            self.screen.blit(self.icons['back'], (back_rect.x + 15, back_rect.y + 8))
            back_text = self.small_font.render("Back to List", True, (255, 255, 255))
            self.screen.blit(back_text, (back_rect.x + 45, back_rect.y + 12))
            
            main_rect = pygame.Rect(self.content_rect.right - 280, y_offset + 10, 130, 40)
            main_hover = main_rect.collidepoint(self.mouse_pos)
            main_color = self.ACCENT_COLOR if main_hover else (80, 80, 180)
            pygame.draw.rect(self.screen, main_color, main_rect, border_radius=8)
            self.screen.blit(self.icons['home'], (main_rect.x + 15, main_rect.y + 8))
            main_text = self.small_font.render("Back to Search", True, (255, 255, 255))
            self.screen.blit(main_text, (main_rect.x + 45, main_rect.y + 12))
            
            self.history_back_rect = back_rect
            self.history_main_rect = main_rect
            
            y_offset += 70
            
            if word_data and len(word_data) > 0:
                data_source = entry.get('source', 'unknown')
                
                source_color = self.WEBSTER_COLOR if data_source == "webster" else self.ACCENT_COLOR
                source_text = self.small_font.render(f"Source: {data_source.upper()} (From History)", True, source_color)
                if y_offset + 30 > self.content_rect.y and y_offset < self.content_rect.bottom:
                    self.screen.blit(source_text, (self.content_rect.x, y_offset))
                y_offset += 40
                
                word = word_data[0].get('word', '')
                phonetic = word_data[0].get('phonetic', '')
                
                word_text = self.title_font.render(word, True, self.TEXT_COLOR)
                if y_offset + 45 > self.content_rect.y and y_offset < self.content_rect.bottom:
                    self.screen.blit(word_text, (self.content_rect.x, y_offset))
                
                if phonetic:
                    phonetic_text = self.normal_font.render(f"/{phonetic}/", True, self.ACCENT_COLOR)
                    if y_offset + 90 > self.content_rect.y and y_offset + 45 < self.content_rect.bottom:
                        self.screen.blit(phonetic_text, (self.content_rect.x + 10, y_offset + 45))
                
                y_offset += 100
                
                for meaning in word_data[0].get('meanings', [])[:3]:
                    part_of_speech = meaning.get('partOfSpeech', '')
                    if part_of_speech:
                        pos_text = self.normal_font.render(part_of_speech, True, self.SUCCESS_COLOR)
                        if y_offset + 35 > self.content_rect.y and y_offset < self.content_rect.bottom:
                            self.screen.blit(pos_text, (self.content_rect.x, y_offset))
                    y_offset += 40
                    
                    for definition in meaning.get('definitions', [])[:2]:
                        def_text = definition.get('definition', '')
                        if def_text:
                            wrapped_def = self.wrap_text(def_text, self.content_rect.width - 40)
                            for line in wrapped_def:
                                if y_offset + 25 > self.content_rect.y and y_offset < self.content_rect.bottom:
                                    def_surface = self.small_font.render(line, True, self.TEXT_COLOR)
                                    self.screen.blit(def_surface, (self.content_rect.x + 20, y_offset))
                                y_offset += 25
                        
                        if definition.get('example'):
                            example_text = f"Example: {definition['example']}"
                            wrapped_example = self.wrap_text(example_text, self.content_rect.width - 50)
                            for line in wrapped_example:
                                if y_offset + 25 > self.content_rect.y and y_offset < self.content_rect.bottom:
                                    ex_surface = self.small_font.render(line, True, self.OFFLINE_COLOR)
                                    self.screen.blit(ex_surface, (self.content_rect.x + 30, y_offset))
                                y_offset += 25
                        
                        y_offset += 15
                    
                    synonyms = meaning.get('synonyms', [])
                    if synonyms:
                        syn_label = self.small_font.render("Synonyms:", True, self.SYNONYM_COLOR)
                        if y_offset + 25 > self.content_rect.y and y_offset < self.content_rect.bottom:
                            self.screen.blit(syn_label, (self.content_rect.x + 20, y_offset))
                        y_offset += 25
                        
                        syn_text = ", ".join(synonyms[:5])
                        wrapped_syn = self.wrap_text(syn_text, self.content_rect.width - 60)
                        for line in wrapped_syn:
                            if y_offset + 20 > self.content_rect.y and y_offset < self.content_rect.bottom:
                                syn_line = self.small_font.render(line, True, self.TEXT_COLOR)
                                self.screen.blit(syn_line, (self.content_rect.x + 40, y_offset))
                            y_offset += 20
                    
                    antonyms = meaning.get('antonyms', [])
                    if antonyms:
                        ant_label = self.small_font.render("Antonyms:", True, self.ANTONYM_COLOR)
                        if y_offset + 25 > self.content_rect.y and y_offset < self.content_rect.bottom:
                            self.screen.blit(ant_label, (self.content_rect.x + 20, y_offset))
                        y_offset += 25
                        
                        ant_text = ", ".join(antonyms[:5])
                        wrapped_ant = self.wrap_text(ant_text, self.content_rect.width - 60)
                        for line in wrapped_ant:
                            if y_offset + 20 > self.content_rect.y and y_offset < self.content_rect.bottom:
                                ant_line = self.small_font.render(line, True, self.TEXT_COLOR)
                                self.screen.blit(ant_line, (self.content_rect.x + 40, y_offset))
                            y_offset += 20
                    
                    y_offset += 20
            
            self.screen.set_clip(old_clip)
            pygame.draw.rect(self.screen, (200, 200, 200), self.content_rect, 1, border_radius=8)
            
        except Exception as e:
            print(f"Error displaying history item details: {e}")
            error_text = self.normal_font.render("Error displaying history details", True, self.ERROR_COLOR)
            self.screen.blit(error_text, (self.content_rect.x, self.content_rect.y))

    def display_basic_history_item(self, entry):
        """Display basic history item when no detailed data is available"""
        try:
            clip_rect = pygame.Rect(self.content_rect.x, self.content_rect.y, 
                                  self.content_rect.width, self.content_rect.height)
            old_clip = self.screen.get_clip()
            self.screen.set_clip(clip_rect)
            
            y_offset = self.content_rect.y - self.scroll_offset
            
            nav_rect = pygame.Rect(self.content_rect.x, y_offset, self.content_rect.width, 60)
            pygame.draw.rect(self.screen, self.HEADER_BG, nav_rect)
            
            back_rect = pygame.Rect(self.content_rect.x + 20, y_offset + 10, 120, 40)
            back_hover = back_rect.collidepoint(self.mouse_pos)
            back_color = self.HISTORY_COLOR if back_hover else (120, 60, 20)
            pygame.draw.rect(self.screen, back_color, back_rect, border_radius=8)
            
            self.screen.blit(self.icons['back'], (back_rect.x + 15, back_rect.y + 8))
            back_text = self.small_font.render("Back to List", True, (255, 255, 255))
            self.screen.blit(back_text, (back_rect.x + 45, back_rect.y + 12))
            
            main_rect = pygame.Rect(self.content_rect.right - 280, y_offset + 10, 130, 40)
            main_hover = main_rect.collidepoint(self.mouse_pos)
            main_color = self.ACCENT_COLOR if main_hover else (80, 80, 180)
            pygame.draw.rect(self.screen, main_color, main_rect, border_radius=8)
            self.screen.blit(self.icons['home'], (main_rect.x + 15, main_rect.y + 8))
            main_text = self.small_font.render("Back to Search", True, (255, 255, 255))
            self.screen.blit(main_text, (main_rect.x + 45, main_rect.y + 12))
            
            self.history_back_rect = back_rect
            self.history_main_rect = main_rect
            
            y_offset += 70
            
            word = entry.get('word', 'Unknown')
            timestamp = entry.get('timestamp', '')
            source = entry.get('source', 'unknown')
            
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_str = timestamp
            
            word_text = self.title_font.render(word, True, self.TEXT_COLOR)
            self.screen.blit(word_text, (self.content_rect.x + 20, y_offset))
            y_offset += 60
            
            source_color = self.ACCENT_COLOR if source == "online" else self.LOCAL_COLOR
            source_text = self.normal_font.render(f"Source: {source.upper()}", True, source_color)
            self.screen.blit(source_text, (self.content_rect.x + 20, y_offset))
            y_offset += 40
            
            time_text = self.normal_font.render(f"Searched on: {time_str}", True, self.OFFLINE_COLOR)
            self.screen.blit(time_text, (self.content_rect.x + 20, y_offset))
            y_offset += 40
            
            no_data_text = self.normal_font.render("No detailed definition data available for this entry.", True, self.TEXT_COLOR)
            self.screen.blit(no_data_text, (self.content_rect.x + 20, y_offset))
            
            self.screen.set_clip(old_clip)
            pygame.draw.rect(self.screen, (200, 200, 200), self.content_rect, 1, border_radius=8)
            
        except Exception as e:
            print(f"Error displaying basic history item: {e}")
            error_text = self.normal_font.render("Error displaying history item", True, self.ERROR_COLOR)
            self.screen.blit(error_text, (self.content_rect.x, self.content_rect.y))

    def calculate_history_height(self):
        """Calculate height needed for history display"""
        if not self.history_data:
            return 400
        
        # Header height
        height = 130  # Increased to account for navigation buttons
        
        # Each history entry height
        for entry in self.history_data:
            height += 80
        
        # Add some padding at the bottom
        height += 20
        
        return max(height, 400)

    def handle_history_click(self, pos):
        """Handle clicks in the history view"""
        if self.selected_history_item is not None:
            if hasattr(self, 'history_back_rect') and self.history_back_rect and self.history_back_rect.collidepoint(pos):
                return 'back'
            if hasattr(self, 'history_main_rect') and self.history_main_rect and self.history_main_rect.collidepoint(pos):
                return 'back_to_main'
        else:
            if hasattr(self, 'history_main_rect') and self.history_main_rect and self.history_main_rect.collidepoint(pos):
                return 'back_to_main'
            if hasattr(self, 'history_clear_rect') and self.history_clear_rect and self.history_clear_rect.collidepoint(pos):
                return 'clear_history'
            
            for i, rect in self.history_entries_rects:
                if rect.collidepoint(pos):
                    return f'item_{i}'
        
        return None

    def handle_suggestion_click(self, pos):
        """Handle clicks on suggestion buttons"""
        for word, rect in self.suggestion_rects:
            if rect.collidepoint(pos):
                return word
        return None

    def display_word_data(self):
        """Display the word definition and information with IMPROVED FORMATTING"""
        try:
            if not self.current_word_data:
                return
                
            word_data = self.current_word_data
            if not word_data or not word_data[0]:
                return
                
            data_source = self.current_data_source
            
            clip_rect = pygame.Rect(self.content_rect.x, self.content_rect.y, 
                                  self.content_rect.width, self.content_rect.height)
            old_clip = self.screen.get_clip()
            self.screen.set_clip(clip_rect)
            
            y_offset = self.content_rect.y - self.scroll_offset
            
            # Source indicator with better styling
            source_color = self.WEBSTER_COLOR if data_source == "webster" else self.ACCENT_COLOR
            source_text = self.small_font.render(f"Source: {data_source.upper()}", True, source_color)
            if y_offset + 30 > self.content_rect.y and y_offset < self.content_rect.bottom:
                self.screen.blit(source_text, (self.content_rect.x, y_offset))
            y_offset += 40
            
            word = word_data[0].get('word', '')
            phonetic = word_data[0].get('phonetic', '')
            
            # Word title with better styling
            word_text = self.title_font.render(word, True, self.TEXT_COLOR)
            if y_offset + 45 > self.content_rect.y and y_offset < self.content_rect.bottom:
                self.screen.blit(word_text, (self.content_rect.x, y_offset))
            
            # Phonetic with better styling
            if phonetic:
                phonetic_text = self.normal_font.render(f"/{phonetic}/", True, self.ACCENT_COLOR)
                if y_offset + 90 > self.content_rect.y and y_offset + 45 < self.content_rect.bottom:
                    self.screen.blit(phonetic_text, (self.content_rect.x + 10, y_offset + 45))
            
            y_offset += 100
            
            # Meanings with IMPROVED LAYOUT
            for meaning in word_data[0].get('meanings', [])[:4]:  # Show more meanings
                part_of_speech = meaning.get('partOfSpeech', '')
                if part_of_speech:
                    # Better part of speech styling
                    pos_bg = pygame.Rect(self.content_rect.x, y_offset, 200, 30)
                    pygame.draw.rect(self.screen, self.SUCCESS_COLOR, pos_bg, border_radius=6)
                    pos_text = self.normal_font.render(part_of_speech, True, (255, 255, 255))
                    self.screen.blit(pos_text, (self.content_rect.x + 10, y_offset + 6))
                y_offset += 40
                
                # Definitions with better spacing
                for i, definition in enumerate(meaning.get('definitions', [])[:3]):  # Show more definitions
                    def_text = definition.get('definition', '')
                    if def_text:
                        # Definition number and text
                        def_num = self.small_font.render(f"{i+1}.", True, self.ACCENT_COLOR)
                        if y_offset + 25 > self.content_rect.y and y_offset < self.content_rect.bottom:
                            self.screen.blit(def_num, (self.content_rect.x + 10, y_offset))
                        
                        wrapped_def = self.wrap_text(def_text, self.content_rect.width - 50)
                        for j, line in enumerate(wrapped_def):
                            if y_offset + 25 > self.content_rect.y and y_offset < self.content_rect.bottom:
                                def_surface = self.small_font.render(line, True, self.TEXT_COLOR)
                                self.screen.blit(def_surface, (self.content_rect.x + 35, y_offset + j * 20))
                            y_offset += 20
                        
                        y_offset += 10
                    
                    # Example with better styling
                    if definition.get('example'):
                        example_text = f"💡 Example: {definition['example']}"
                        wrapped_example = self.wrap_text(example_text, self.content_rect.width - 60)
                        for line in wrapped_example:
                            if y_offset + 25 > self.content_rect.y and y_offset < self.content_rect.bottom:
                                ex_surface = self.small_font.render(line, True, self.OFFLINE_COLOR)
                                self.screen.blit(ex_surface, (self.content_rect.x + 45, y_offset))
                            y_offset += 20
                        
                        y_offset += 10
                    
                    y_offset += 15
                
                # Synonyms with better styling - FIXED TO ALWAYS SHOW
                synonyms = meaning.get('synonyms', [])
                if synonyms:
                    syn_label = self.small_font.render("📗 Synonyms:", True, self.SYNONYM_COLOR)
                    if y_offset + 25 > self.content_rect.y and y_offset < self.content_rect.bottom:
                        self.screen.blit(syn_label, (self.content_rect.x + 20, y_offset))
                    y_offset += 25
                    
                    syn_text = ", ".join(synonyms[:8])  # Show more synonyms
                    wrapped_syn = self.wrap_text(syn_text, self.content_rect.width - 60)
                    for line in wrapped_syn:
                        if y_offset + 20 > self.content_rect.y and y_offset < self.content_rect.bottom:
                            syn_line = self.small_font.render(line, True, self.TEXT_COLOR)
                            self.screen.blit(syn_line, (self.content_rect.x + 40, y_offset))
                        y_offset += 20
                
                # Antonyms with better styling - FIXED TO ALWAYS SHOW
                antonyms = meaning.get('antonyms', [])
                if antonyms:
                    ant_label = self.small_font.render("📕 Antonyms:", True, self.ANTONYM_COLOR)
                    if y_offset + 25 > self.content_rect.y and y_offset < self.content_rect.bottom:
                        self.screen.blit(ant_label, (self.content_rect.x + 20, y_offset))
                    y_offset += 25
                    
                    ant_text = ", ".join(antonyms[:5])
                    wrapped_ant = self.wrap_text(ant_text, self.content_rect.width - 60)
                    for line in wrapped_ant:
                        if y_offset + 20 > self.content_rect.y and y_offset < self.content_rect.bottom:
                            ant_line = self.small_font.render(line, True, self.TEXT_COLOR)
                            self.screen.blit(ant_line, (self.content_rect.x + 40, y_offset))
                        y_offset += 20
                
                y_offset += 25  # More spacing between meanings
            
            self.screen.set_clip(old_clip)
            pygame.draw.rect(self.screen, (200, 200, 200), self.content_rect, 1, border_radius=8)
            
        except Exception as e:
            print(f"Error displaying word data: {e}")
            error_text = self.normal_font.render("Error displaying word data", True, self.ERROR_COLOR)
            self.screen.blit(error_text, (self.content_rect.x, self.content_rect.y))

    def wrap_text(self, text, max_width):
        """Wrap text to fit within max_width"""
        if not text:
            return []
            
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.small_font.render(test_line, True, self.TEXT_COLOR)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]

    def show_error(self, message):
        """Display error message"""
        error_text = self.normal_font.render(message, True, self.ERROR_COLOR)
        self.screen.blit(error_text, (self.screen_width//2 - error_text.get_width()//2, 320))