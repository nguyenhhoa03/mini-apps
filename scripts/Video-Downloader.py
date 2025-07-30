import os
import sys
import threading
import yt_dlp
import customtkinter as ctk
import platform

ALLOWED_VIDEO_QUALITIES = [
    "Auto", "144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p"
]

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader (Base on yt-dlp)")
        self.root.geometry("500x500")
        
        # Thiết lập đường dẫn ffmpeg nội bộ
        self.setup_ffmpeg_path()

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

    def setup_ffmpeg_path(self):
        """Thiết lập đường dẫn đến ffmpeg nội bộ"""
        # Lấy thư mục chứa script hiện tại
        if getattr(sys, 'frozen', False):
            # Nếu chạy từ file exe (đã được đóng gói)
            base_dir = os.path.dirname(sys.executable)
        else:
            # Nếu chạy từ script Python
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Xác định tên file ffmpeg dựa trên hệ điều hành
        system = platform.system().lower()
        if system == 'windows':
            ffmpeg_name = 'ffmpeg.exe'
            ffprobe_name = 'ffprobe.exe'
        else:
            ffmpeg_name = 'ffmpeg'
            ffprobe_name = 'ffprobe'
        
        # Đường dẫn đến thư mục ffmpeg
        ffmpeg_dir = os.path.join(base_dir, 'ffmpeg')
        self.ffmpeg_path = os.path.join(ffmpeg_dir, ffmpeg_name)
        self.ffprobe_path = os.path.join(ffmpeg_dir, ffprobe_name)
        
        # Kiểm tra xem ffmpeg có tồn tại không
        if os.path.exists(self.ffmpeg_path):
            self.log_message(f"✓ FFmpeg found: {self.ffmpeg_path}")
            # Đặt quyền thực thi cho Linux/Mac
            if system != 'windows':
                try:
                    os.chmod(self.ffmpeg_path, 0o755)
                    os.chmod(self.ffprobe_path, 0o755)
                except:
                    pass
        else:
            self.log_message(f"⚠ FFmpeg not found at: {self.ffmpeg_path}")
            self.log_message("Please place ffmpeg files in 'ffmpeg' folder")

    def get_ydl_opts_base(self):
        """Trả về cấu hình cơ bản cho yt-dlp với ffmpeg nội bộ"""
        opts = {
            'progress_hooks': [self.yt_dlp_progress],
            'noplaylist': True
        }
        
        # Nếu ffmpeg tồn tại, sử dụng đường dẫn nội bộ
        if os.path.exists(self.ffmpeg_path):
            opts['ffmpeg_location'] = os.path.dirname(self.ffmpeg_path)
        
        return opts

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
        
        # Thêm ffmpeg location nếu có
        if os.path.exists(self.ffmpeg_path):
            opts['ffmpeg_location'] = os.path.dirname(self.ffmpeg_path)
        
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
        video_options = [q for q in ALLOWED_VIDEO_QUALITIES if q in available_qualities or q == "Auto"]
        options = []
        if audio_available:
            options.append("Audio Only (MP3)")
        # Thêm Auto làm tùy chọn đầu tiên nếu có video
        if video_options and "Auto" in video_options:
            options.append("Auto")
            # Thêm các chất lượng cụ thể (loại bỏ Auto để không trùng)
            options.extend([q for q in video_options if q != "Auto"])
        else:
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

        # Kiểm tra ffmpeg trước khi download
        if not os.path.exists(self.ffmpeg_path):
            self.log_message("⚠ Warning: FFmpeg not found. Some formats may not work properly.")
            self.log_message("Please place ffmpeg.exe in 'ffmpeg' folder for full functionality.")

        # Start download in new thread
        threading.Thread(
            target=self.download_video,
            args=(url, save_path, selected_format),
            daemon=True
        ).start()

    def download_video(self, url, save_path, selected_format):
        try:
            # Lấy cấu hình cơ bản với ffmpeg nội bộ
            ydl_opts = self.get_ydl_opts_base()
            ydl_opts['outtmpl'] = os.path.join(save_path, '%(title)s.%(ext)s')
            
            # Cấu hình các tùy chọn cho yt-dlp dựa vào lựa chọn của người dùng
            if selected_format == "Audio Only (MP3)":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
                
                # Nếu không có ffmpeg nội bộ, thử fallback
                if not os.path.exists(self.ffmpeg_path):
                    self.log_message("Attempting to download audio without internal FFmpeg...")
                    ydl_opts['postprocessors'] = []
                    ydl_opts['format'] = 'bestaudio[ext=mp3]/bestaudio'
                    
            elif selected_format == "Auto":
                # Chế độ Auto: tải chất lượng tốt nhất có sẵn (như yt-dlp mặc định)
                ydl_opts.update({
                    'format': 'best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                })
                
                # Thêm postprocessor nếu có ffmpeg
                if os.path.exists(self.ffmpeg_path):
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }]
                    
                self.log_message("Auto mode: Downloading best quality available")
                    
            else:
                # Với các định dạng video cụ thể, sử dụng điều kiện về chiều cao
                height = int(selected_format.rstrip("p"))
                ydl_opts.update({
                    'format': f'bestvideo[height<={height}]+bestaudio[ext=m4a]/best[height<={height}]',
                    'merge_output_format': 'mp4',
                })
                
                # Nếu có ffmpeg nội bộ, thêm postprocessor để đảm bảo chất lượng
                if os.path.exists(self.ffmpeg_path):
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }]

            self.log_message(f"Starting download with format: {selected_format}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_title = info_dict.get('title', 'Unknown Title')

            self.log_message(f"✓ Downloaded successfully: {video_title}")
            self.update_progress(1.0, "Download Complete!")
            
        except Exception as e:
            error_msg = str(e)
            self.log_message(f"✗ Error: {error_msg}")
            
            # Gợi ý nếu lỗi liên quan đến ffmpeg
            if 'ffmpeg' in error_msg.lower() or 'postprocess' in error_msg.lower():
                self.log_message("💡 Tip: Make sure ffmpeg files are in 'ffmpeg' folder")
                self.log_message("   Download from: https://ffmpeg.org/download.html")
                
            self.update_progress(0, "Download Failed")

    def yt_dlp_progress(self, d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total > 0:
                progress = downloaded / total
                speed = d.get('speed', 0)
                speed_str = f" ({speed/1024/1024:.1f} MB/s)" if speed else ""
                status = f"Downloading: {progress*100:.1f}%{speed_str}"
                self.update_progress(progress, status)
        elif d['status'] == 'finished':
            self.update_progress(0.9, "Processing...")
        elif d['status'] == 'error':
            self.update_progress(0, "Error occurred")

def create_ffmpeg_structure():
    """Tạo cấu trúc thư mục cho ffmpeg nếu chưa có"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(script_dir, 'ffmpeg')
    
    if not os.path.exists(ffmpeg_dir):
        os.makedirs(ffmpeg_dir)
        print(f"Created ffmpeg directory: {ffmpeg_dir}")
        print("Please place ffmpeg executable files in this directory:")
        if platform.system().lower() == 'windows':
            print("  - ffmpeg.exe")
            print("  - ffprobe.exe")
        else:
            print("  - ffmpeg")
            print("  - ffprobe")

if __name__ == "__main__":
    # Tạo cấu trúc thư mục ffmpeg nếu cần
    create_ffmpeg_structure()
    
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = VideoDownloaderApp(root)
    root.mainloop()
