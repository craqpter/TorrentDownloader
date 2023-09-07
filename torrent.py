import libtorrent as lt
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import PhotoImage, Menu, Text, Scrollbar
import os
import time
import threading


class TorrentDownloader:
    def __init__(self, root):
        self.root = root
        icon = PhotoImage(file="res/123.png")
        self.root.iconphoto(True, icon)        
        self.root.title("Torrent Downloader")
        self.root.resizable(width=False, height=False)
        self.root.geometry("550x450")
        self.root.config(bg="#26242f")        
        self.session = lt.session()
        self.torrent_info = None
        self.torrent_handle = None
        self.download_path = "./downloads"  # Default download path
        self.status_label = tk.Label(root, text="Status: AFK", bg="#26242f", fg="white")  # Style the status label
        self.status_label.pack()
        self.select_torrent_button = tk.Button(root, text="Select .torrent file", command=self.select_torrent, bg="#26242f", fg="white", borderwidth=5)  # Style the select torrent button
        self.select_torrent_button.pack()
        self.select_path_button = tk.Button(root, text="Select Download Path/Folder", command=self.select_download_path, bg="#26242f", fg="white", borderwidth=5)  # Style the select path button
        self.select_path_button.pack()
        self.start_button = tk.Button(root, text="Start Download", command=self.start_download, state=tk.DISABLED, bg="#007FFF", fg="white", borderwidth=5, padx=10)  # Style the start button
        self.start_button.pack()
        # Listbox to display downloaded torrents
        self.listbox_label = tk.Label(root, text="List of downloaded torrents:", bg="#26242f", fg="white")
        self.listbox_label.pack(anchor=tk.W, padx=1, pady=1)  # Adjust padx and pady as needed
        self.torrent_listbox = tk.Listbox(root, selectmode=tk.SINGLE)
        self.torrent_listbox.pack(fill=tk.BOTH, expand=True)
        self.torrent_listbox_scrollbar = tk.Scrollbar(self.torrent_listbox, orient=tk.VERTICAL)
        self.torrent_listbox.configure(yscrollcommand=self.torrent_listbox_scrollbar.set)
        self.torrent_listbox_scrollbar.config(command=self.torrent_listbox.yview)
        self.torrent_listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)        
        # Load and display downloaded torrents
        self.load_downloaded_torrents()
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Create the menu bar
        menubar = Menu(root)
        root.config(menu=menubar)

        # Create the File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        # Create the Edit menu
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Reset", command=self.update_torrent_list)

        # Create the Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About App", command=self.about_app)
        help_menu.add_command(label="Contribute Link", command=self.contribute_link)
        
    def about_app(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About App")
        about_window.geometry("300x300")
        about_window.resizable(False, False)  # Disable resizing

        # Create a frame to center the labels vertically
        center_frame = tk.Frame(about_window)
        center_frame.pack(expand=True, fill="both")

        # Load and display the icon
        icon = PhotoImage(file="123.png")
        icon_label = tk.Label(center_frame, image=icon)
        
        
        # Display the app name (centered)
        app_name_label = tk.Label(center_frame, text="Torrent Downloader", font=("Helvetica", 14, "bold"))
        app_name_label.pack(side="top", padx=10, pady=10)
        
        # Display the build time (centered)
        build_time_label = tk.Label(center_frame, text=f"Build time: {time.strftime('%m.%Y')}", font=("Helvetica", 12))
        build_time_label.pack(side="top", padx=10, pady=10)

        # Display the GNU General Public License (centered)
        license_label = tk.Label(center_frame, text="GNU General Public License", font=("Helvetica", 12))
        license_label.pack(side="top", padx=10, pady=10)
        license_frame = tk.Frame(center_frame)
        license_frame.pack(side="top", padx=10, pady=10)

        # Create a Text widget for the license text
        license_text = (
            "This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or at your option any later version.\n"
            "\n"
            "This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n"
            "\n"
            "You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/."
        )
        license_text_widget = Text(license_frame, wrap="word", height=10, width=30)
        license_text_widget.insert("1.0", license_text)
        license_text_widget.config(state="disabled")
        license_text_widget.pack(side="left")

        # Create a Scrollbar for the license text
        scrollbar = Scrollbar(license_frame, command=license_text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        license_text_widget.config(yscrollcommand=scrollbar.set)
      
      
    def contribute_link(self):
        messagebox.showinfo("Contribute", "Buy Me a Coffee!!!")
        webbrowser.open_new("https://www.google.com/")
        
    def select_torrent(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Torrent Files", "*.torrent")])
        if self.file_path:
            self.torrent_info = lt.torrent_info(self.file_path)
            self.start_button.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Torrent selected")
            
    def select_download_path(self):
        self.download_path = filedialog.askdirectory()
        self.status_label.config(text=f"Download Path: {self.download_path}")

    def start_download(self):
        if self.torrent_info:
            params = {
                'ti': self.torrent_info,
                'save_path': self.download_path  # Change the path to your desired download location
            }
            # Check if the file already exists in the download path
            download_file_path = os.path.join(self.download_path, self.torrent_info.name() + ".torrent")
            if os.path.exists(download_file_path):
                response = tk.messagebox.askquestion("File Exists", "The file already exists in the download path. Do you want to re-download it?", icon="warning")
                if response != "yes":
                    return
                    
            self.torrent_handle = self.session.add_torrent(params)          
            self.status_label.config(text="Status: Downloading...")
            self.start_button.config(state=tk.DISABLED)
            
            # Start downloading in a separate thread
            self.download_thread = threading.Thread(target=self.download_thread_function)
            self.download_thread.start()

    def download_thread_function(self):
        if self.torrent_info:
            params = {
                'ti': self.torrent_info,
                'save_path': self.download_path
            }
            self.torrent_handle = self.session.add_torrent(params)
            saved = False
            while not self.torrent_handle.is_seed():
                s = self.torrent_handle.status()
                file_size_mb = s.total_done / (1024 * 1024)  # Convert to megabytes (MB)
                self.status_label.config(text=f"Status: Downloading ({s.progress * 100:.2f}%) - Size: {file_size_mb:.2f} MB - D: {s.download_rate / 1_000_000:.2f} MB/s - U: {s.upload_rate / 1_000_000:.2f} MB/s - Peers: {s.num_peers}")
                if not saved:
                    self.save_downloaded_torrent(self.torrent_info.name(), time.strftime('%Y-%m-%d %H:%M:%S'))
                    saved = True  # Set the flag to True after saving once
                self.root.update_idletasks()
                time.sleep(1)  # Use time.sleep() for the sleep function   
            self.status_label.config(text="Status: Download Complete")
            self.root.after(2000, self.reset_status)  # Reset status after 2 seconds           
            self.update_torrent_list()
            
 
    def reset_status(self):
        self.status_label.config(text="Status: AFK")
        self.start_button.config(state=tk.NORMAL)
        
    def on_close(self):
        # Handle window close event
        if hasattr(self, 'download_thread') and self.download_thread.is_alive():
            self.torrent_handle.pause()
        self.root.destroy()
        
    def save_downloaded_torrent(self, name, date):
        with open("res/downloaded_torrents.txt", "a") as f:
            f.write(f"\nName: {name}, Date: {date}")
        
    def load_downloaded_torrents(self):
        try:
            with open("res/downloaded_torrents.txt", "r") as f:
                for line in f:
                    self.torrent_listbox.insert(tk.END, line)
        except FileNotFoundError:
            pass
                       
    def update_torrent_list(self):
        # Clear the existing list
        self.torrent_listbox.delete(0, tk.END)

        try:
            # Reload the list from the file
            with open("res/downloaded_torrents.txt", "r") as f:
                for line in f:
                    self.torrent_listbox.insert(tk.END, line)
        except FileNotFoundError:
            pass
        
if __name__ == "__main__":
    root = tk.Tk()
    app = TorrentDownloader(root)
    root.mainloop()
