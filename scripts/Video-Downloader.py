import os
import threading
import yt_dlp
import customtkinter as ctk

ALLOWED_VIDEO_QUALITIES = [
    "144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p"
]

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader (Base on yt-dlp)")
        self.root.geometry("500x500")

        # URL Entry
        self.url_label = ctk.CTkLabel(root, text="Video URL:")
        self.url_label.pack(pady=5)
        self.url_entry = ctk.CTkEntry(root, width=400)
        self.url_entry.pack(pady=5)

        # Scan Button
        self.scan_button = ctk.CTkButton(root, text="Scan Formats", command=self.on_scan_button_clicked)
        self.scan_button.pack(pady=5)

        # Format Selector (khởi tạo rỗng, sẽ được cập nhật sau khi quét)
        self.format_label = ctk.CTkLabel(root, text="Available Formats:")
        self.format_label.pack(pady=5)
        self.format_selector = ctk.CTkComboBox(root, values=[], width=400)
        self.format_selector.pack(pady=5)
        self.format_selector.set("Chọn định dạng sau khi quét")  # Placeholder

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
        self.log_textbox = ctk.CTkTextbox(root, height=120, width=400)
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

    def on_scan_button_clicked(self):
        # Khi người dùng nhấn nút quét, tiến hành lấy URL và quét các định dạng có sẵn
        url = self.url_entry.get().strip()
        if not url:
            self.log_message("Error: Vui lòng nhập URL hợp lệ!")
            return

        # Khởi chạy luồng riêng để quét, nhằm không làm đơ giao diện
        threading.Thread(target=self.scan_formats, args=(url,), daemon=True).start()

    def scan_formats(self, url):
        self.log_message("Đang quét các định dạng có sẵn...")
        opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            self.log_message(f"Error khi quét: {str(e)}")
            return

        # Lấy danh sách các format có sẵn từ info
        formats = info.get('formats', [])
        # Tập hợp các chất lượng video được tìm thấy (dựa theo chiều cao)
        available_qualities = set()
        audio_available = False

        for fmt in formats:
            # Nếu định dạng chứa video (vcodec khác 'none') và có height thì thêm vào tập hợp
            if fmt.get('vcodec') != 'none' and fmt.get('height'):
                quality_str = f"{fmt['height']}p"
                available_qualities.add(quality_str)
            # Nếu đây là định dạng âm thanh (vcodec == 'none'), đánh dấu có định dạng âm thanh
            if fmt.get('vcodec') == 'none':
                audio_available = True

        # Sắp xếp và giữ lại các chất lượng nằm trong danh sách cho phép nếu có trong video
        video_options = [q for q in ALLOWED_VIDEO_QUALITIES if q in available_qualities]
        options = []
        if audio_available:
            options.append("Audio Only (MP3)")
        options.extend(video_options)

        if not options:
            self.log_message("Không tìm thấy định dạng phù hợp cho video này.")
        else:
            # Cập nhật combo box trên giao diện chính (thread chính)
            self.root.after(0, lambda: self.format_selector.configure(values=options))
            self.root.after(0, lambda: self.format_selector.set(options[0]))
            self.log_message("Quét hoàn tất! Các định dạng có sẵn đã được cập nhật.")

    def on_download_button_clicked(self):
        # Reset progress
        self.update_progress(0, "Starting...")

        url = self.url_entry.get().strip()
        if not url:
            self.log_message("Error: Vui lòng nhập URL hợp lệ!")
            return

        selected_format = self.format_selector.get()
        if not selected_format or selected_format.startswith("Chọn"):
            self.log_message("Error: Vui lòng quét và chọn định dạng trước khi tải!")
            return

        save_path = self.save_path_entry.get().strip()
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)

        # Start download in new thread
        threading.Thread(
            target=self.download_video,
            args=(url, save_path, selected_format),
            daemon=True
        ).start()

    def download_video(self, url, save_path, selected_format):
        try:
            # Cấu hình các tùy chọn cho yt-dlp dựa vào lựa chọn của người dùng
            if selected_format == "Audio Only (MP3)":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                    }],
                    'progress_hooks': [self.yt_dlp_progress],
                    'noplaylist': True
                }
            else:
                # Với các định dạng video, sử dụng điều kiện về chiều cao, và ép merge về mp4
                # Lấy số chiều cao từ chuỗi (ví dụ "720p" -> 720)
                height = int(selected_format.rstrip("p"))
                ydl_opts = {
                    'format': f'bestvideo[height<={height}]+bestaudio[ext=m4a]/best[height<={height}]',
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'merge_output_format': 'mp4',
                    'progress_hooks': [self.yt_dlp_progress],
                    'noplaylist': True
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_title = info_dict.get('title', 'Unknown Title')

            self.log_message(f"Downloaded successfully: {video_title}")
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
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = VideoDownloaderApp(root)
    root.mainloop()
