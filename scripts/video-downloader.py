import os
import threading
import yt_dlp
import customtkinter as ctk

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader")
        self.root.geometry("500x400")

        # URL Entry
        self.url_label = ctk.CTkLabel(root, text="Video URL:")
        self.url_label.pack(pady=5)
        self.url_entry = ctk.CTkEntry(root, width=400)
        self.url_entry.pack(pady=5)

        # Format Selector
        self.format_label = ctk.CTkLabel(root, text="Select Format:")
        self.format_label.pack(pady=5)
        self.format_selector = ctk.CTkComboBox(root, values=[
            "Audio Only (MP3)", "144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p"
        ], width=400)
        self.format_selector.pack(pady=5)
        self.format_selector.set("720p")

        # Save Path
        self.save_path_label = ctk.CTkLabel(root, text="Save Path:")
        self.save_path_label.pack(pady=5)
        self.save_path_entry = ctk.CTkEntry(root, width=400)
        self.save_path_entry.pack(pady=5)
        default_save_path = os.path.expanduser('~/Downloads')
        self.save_path_entry.insert(0, default_save_path)

        # Progress Bar
        self.download_progress = ctk.CTkProgressBar(root, orientation="horizontal", width=400)
        self.download_progress.pack(pady=10)
        self.download_progress.set(0)

        # Log Box
        self.log_textbox = ctk.CTkTextbox(root, height=100, width=400)
        self.log_textbox.pack(pady=10)

        # Download Button
        self.download_button = ctk.CTkButton(root, text="Download", command=self.on_download_button_clicked)
        self.download_button.pack(pady=10)

    def log_message(self, message):
        self.log_textbox.insert(ctk.END, message + '\n')
        self.log_textbox.see(ctk.END)

    def update_progress(self, fraction, text=""):
        self.download_progress.set(fraction)
        self.download_button.configure(text=text if text else "Download")

    def on_download_button_clicked(self):
        # Reset progress
        self.update_progress(0, "Starting...")

        # Get URL
        url = self.url_entry.get().strip()
        if not url:
            self.log_message("Error: Please enter a valid URL.")
            return

        # Get format
        selected_format = self.format_selector.get()

        # Get save path
        save_path = self.save_path_entry.get().strip()
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)

        # Start download thread
        threading.Thread(
            target=self.download_video,
            args=(url, save_path, selected_format),
            daemon=True
        ).start()

    def download_video(self, url, save_path, selected_format):
        try:
            # yt-dlp options
            ydl_opts = {
                'format': f'bestvideo[height<={selected_format.rstrip("p")}]'+
                          f'+bestaudio[ext=m4a]/best[height<={selected_format.rstrip("p")}]',
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
                'progress_hooks': [self.yt_dlp_progress],
                'noplaylist': True
            }

            if selected_format.lower().startswith("audio"):
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_title = info_dict.get('title', 'Unknown Title')
                
            self.log_message(f"Successfully downloaded: {video_title}")
            self.update_progress(1.0, "Download Complete!")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            self.update_progress(0, "Download Failed")

    def yt_dlp_progress(self, d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total > 0:
                progress = downloaded / total
                status = f"Downloading: {progress*100:.1f}%"
                self.update_progress(progress, status)
        elif d['status'] == 'finished':
            self.update_progress(1.0, "Processing...")

if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Modes: "System" (default), "Light", "Dark"
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = VideoDownloaderApp(root)
    root.mainloop()
# More infomation please visit https://github.com/nguyenhhoa03/video-downloader
