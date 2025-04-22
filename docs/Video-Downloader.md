# Video Downloader

Ứng dụng desktop đơn giản cho phép tải video hoặc chỉ audio từ nhiều nguồn (YouTube, v.v.) sử dụng `yt-dlp`, với giao diện đẹp và mượt mà từ `customtkinter`.

## 🚀 Tính năng chính

- Quét tự động các định dạng (chất lượng) video có sẵn.
- Chọn tải video ở các chất lượng phổ biến: 144p, 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p, 4320p.
- Chế độ chỉ tải audio (MP3).
- Hiển thị tiến trình tải rõ ràng (phần trăm, trạng thái).
- Không làm đơ giao diện nhờ chạy tác vụ quét và tải trên các luồng riêng.

## 📋 Yêu cầu

- Python 3.8+
- `yt-dlp`
- `customtkinter`

## 🚦 Cách sử dụng

1. Chạy ứng dụng từ **Mini Apps Laucher**
2. Nhập URL video/audio vào ô **Video URL**.
3. Nhấn **Scan Formats** để quét định dạng có sẵn.
4. Chọn chất lượng video hoặc chế độ **Audio Only (MP3)**.
5. Chọn đường dẫn lưu file (mặc định là `~/Downloads`).
6. Nhấn **Download** và theo dõi tiến trình.

## 🔧 Cấu hình tùy chỉnh

- **ALLOWED_VIDEO_QUALITIES**: Danh sách các chất lượng video cho phép trong mã (`main.py`).
- **Đường dẫn lưu**: Mặc định là `~/Downloads`. Bạn có thể thay đổi trong giao diện.


## 📝 Giấy phép

Project được phát hành theo giấy phép [GNU General Public License v3.0](LICENSE)

