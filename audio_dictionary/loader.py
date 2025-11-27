'''import customtkinter as ctk
import threading
import time

class CircularLoader(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Loader Demo")
        self.geometry("400x300")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title
        self.title_label = ctk.CTkLabel(self.main_frame, text="Loader Examples", 
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=10)
        
        # Circular progress loader
        self.progress = ctk.CTkProgressBar(self.main_frame)
        self.progress.pack(pady=20, padx=20, fill="x")
        self.progress.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.main_frame, text="Ready", 
                                        font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=5)
        
        # Buttons
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=20)
        
        self.start_btn = ctk.CTkButton(self.button_frame, text="Start Loader", 
                                      command=self.start_loading)
        self.start_btn.pack(side="left", padx=10)
        
        self.reset_btn = ctk.CTkButton(self.button_frame, text="Reset", 
                                      command=self.reset_loader)
        self.reset_btn.pack(side="left", padx=10)
        
        self.loading = False
    
    def start_loading(self):
        if not self.loading:
            self.loading = True
            self.start_btn.configure(state="disabled")
            thread = threading.Thread(target=self.simulate_loading)
            thread.daemon = True
            thread.start()
    
    def simulate_loading(self):
        for i in range(101):
            if not self.loading:
                break
            progress = i / 100
            self.progress.set(progress)
            self.status_label.configure(text=f"Loading... {i}%")
            time.sleep(0.05)
        
        if self.loading:
            self.status_label.configure(text="Completed!")
            self.start_btn.configure(state="normal")
            self.loading = False
    
    def reset_loader(self):
        self.loading = False
        self.progress.set(0)
        self.status_label.configure(text="Ready")
        self.start_btn.configure(state="normal")

if __name__ == "__main__":
    app = CircularLoader()
    app.mainloop()'''
    
    
'''import customtkinter as ctk
import threading
import time

class SpinnerLoader(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Animated Spinner Loader")
        self.geometry("500x400")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Spinner display
        self.spinner_frame = ctk.CTkFrame(self.main_frame, height=150)
        self.spinner_frame.pack(pady=20, padx=20, fill="x")
        self.spinner_frame.pack_propagate(False)
        
        self.spinner_label = ctk.CTkLabel(self.spinner_frame, text="●", 
                                         font=ctk.CTkFont(size=40),
                                         text_color="#2Ecc71")
        self.spinner_label.pack(expand=True)
        
        # Status
        self.status_label = ctk.CTkLabel(self.main_frame, text="Click Start to begin", 
                                        font=ctk.CTkFont(size=16))
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self.main_frame)
        self.progress.pack(pady=10, padx=20, fill="x")
        self.progress.set(0)
        
        # Buttons
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=20)
        
        self.start_btn = ctk.CTkButton(self.button_frame, text="Start Spinner", 
                                      command=self.start_spinner)
        self.start_btn.pack(side="left", padx=10)
        
        self.stop_btn = ctk.CTkButton(self.button_frame, text="Stop", 
                                     command=self.stop_spinner, state="disabled")
        self.stop_btn.pack(side="left", padx=10)
        
        self.spinner_active = False
        self.spinner_chars = ["●", "◆", "■", "▲", "▼", "◀", "▶"]
        self.colors = ["#2Ecc71", "#3498db", "#9b59b6", "#e74c3c", "#f39c12", "#1abc9c", "#34495e"]
    
    def start_spinner(self):
        if not self.spinner_active:
            self.spinner_active = True
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.progress.set(0)
            
            # Start spinner animation
            spinner_thread = threading.Thread(target=self.animate_spinner)
            spinner_thread.daemon = True
            spinner_thread.start()
            
            # Start progress
            progress_thread = threading.Thread(target=self.update_progress)
            progress_thread.daemon = True
            progress_thread.start()
    
    def stop_spinner(self):
        self.spinner_active = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Stopped")
    
    def animate_spinner(self):
        index = 0
        while self.spinner_active and index < 100:
            char_index = index % len(self.spinner_chars)
            color_index = index % len(self.colors)
            
            self.spinner_label.configure(
                text=self.spinner_chars[char_index],
                text_color=self.colors[color_index]
            )
            
            index += 1
            time.sleep(0.1)
    
    def update_progress(self):
        for i in range(101):
            if not self.spinner_active:
                break
            self.progress.set(i / 100)
            self.status_label.configure(text=f"Processing... {i}%")
            time.sleep(0.1)
        
        if self.spinner_active:
            self.status_label.configure(text="Completed!")
            self.spinner_active = False
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

if __name__ == "__main__":
    app = SpinnerLoader()
    app.mainloop()'''
    


import customtkinter as ctk
import threading
import time

class SpinnerLoader(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.configure(fg_color="transparent")
        
        # Spinner display frame
        self.spinner_frame = ctk.CTkFrame(self, height=80)
        self.spinner_frame.pack(pady=5, padx=20, fill="x")
        self.spinner_frame.pack_propagate(False)
        
        self.spinner_label = ctk.CTkLabel(self.spinner_frame, text="●", 
                                         font=ctk.CTkFont(size=30),
                                         text_color="#2Ecc71")
        self.spinner_label.pack(expand=True)
        
        # Status label
        self.status_label = ctk.CTkLabel(self, text="Ready", 
                                        font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=2)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self, height=8)
        self.progress.pack(pady=5, padx=20, fill="x")
        self.progress.set(0)
        
        # Initially hide the spinner
        self.pack_forget()
        
        self.spinner_active = False
        self.spinner_chars = ["●", "◆", "■", "▲", "▼", "◀", "▶"]
        self.colors = ["#2Ecc71", "#3498db", "#9b59b6", "#e74c3c", "#f39c12", "#1abc9c", "#34495e"]
    
    def start_spinner(self):
        if not self.spinner_active:
            self.spinner_active = True
            self.progress.set(0)
            self.pack(pady=5, padx=20, fill="x")
            
            # Start spinner animation
            spinner_thread = threading.Thread(target=self.animate_spinner)
            spinner_thread.daemon = True
            spinner_thread.start()
            
            # Start progress
            progress_thread = threading.Thread(target=self.update_progress)
            progress_thread.daemon = True
            progress_thread.start()
    
    def stop_spinner(self):
        self.spinner_active = False
        self.status_label.configure(text="Completed!")
        # Hide the spinner after completion
        self.after(1000, self.pack_forget)
    
    def animate_spinner(self):
        index = 0
        while self.spinner_active and index < 100:
            char_index = index % len(self.spinner_chars)
            color_index = index % len(self.colors)
            
            self.spinner_label.configure(
                text=self.spinner_chars[char_index],
                text_color=self.colors[color_index]
            )
            
            index += 1
            time.sleep(0.1)
    
    def update_progress(self):
        for i in range(101):
            if not self.spinner_active:
                break
            self.progress.set(i / 100)
            self.status_label.configure(text=f"Searching... {i}%")
            time.sleep(0.05)
        
        if self.spinner_active:
            self.stop_spinner()

# Example usage in your main dictionary app:
class DictionaryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Dictionary App")
        self.geometry("600x500")
        
        # Main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Entry box
        self.entry_label = ctk.CTkLabel(self.main_container, text="Enter word:")
        self.entry_label.pack(anchor="w", pady=(0, 5))
        
        self.entry_frame = ctk.CTkFrame(self.main_container)
        self.entry_frame.pack(fill="x", pady=(0, 10))
        
        self.entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Type a word...")
        self.entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        self.search_btn = ctk.CTkButton(self.entry_frame, text="Search", width=80)
        self.search_btn.pack(side="left", padx=(5, 5), pady=10)
        
        self.history_btn = ctk.CTkButton(self.entry_frame, text="History", width=80)
        self.history_btn.pack(side="left", padx=(5, 10), pady=10)
        
        # Spinner loader - placed right under entry frame
        self.spinner_loader = SpinnerLoader(self.main_container)
        
        # Results area
        self.results_frame = ctk.CTkFrame(self.main_container)
        self.results_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # Bind search button to show spinner
        self.search_btn.configure(command=self.perform_search)
    
    def perform_search(self):
        # Show the spinner
        self.spinner_loader.start_spinner()
        
        # Simulate search completion after 3 seconds
        self.after(3000, self.spinner_loader.stop_spinner)

if __name__ == "__main__":
    app = DictionaryApp()
    app.mainloop()