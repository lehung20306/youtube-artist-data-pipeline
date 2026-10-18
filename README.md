# YouTube Data ELT Pipeline

## Giới thiệu (Overview)
Dự án này là một hệ thống ELT (Extract - Load - Transform) tự động được triển khai trên máy ảo Google Cloud Compute Engine (GCP VM).

Mục tiêu cốt lõi của dự án là thu thập và phân tích dữ liệu từ các kênh YouTube của Top 100 nghệ sĩ US-UK có lượt xem cao nhất. Dữ liệu này sẽ giúp theo dõi mức độ tương tác, xu hướng phát hành và phản hồi của khán giả đối với các sản phẩm âm nhạc hàng đầu.

Khác với mô hình ETL truyền thống, pipeline này áp dụng mô hình ELT hiện đại: Dữ liệu thô từ YouTube được tải (Load) trực tiếp lên kho dữ liệu, sau đó sức mạnh tính toán của Google BigQuery được tận dụng để thực thi các lệnh SQL làm sạch, gộp bảng và chuyển đổi (Transform) dữ liệu ngay trên Cloud.

## Kiến trúc & Công nghệ (Tech Stack)
* **Ngôn ngữ:** Python 3, Standard SQL
* **Môi trường triển khai:** Google Cloud Compute Engine (Ubuntu VM)
* **Kho dữ liệu (Data Warehouse):** Google BigQuery
* **Nguồn dữ liệu:** YouTube Data API v3
* **Điều phối (Orchestration):** Linux Cronjob

## Chuẩn bị Dữ liệu (Data Preparation)
Hệ thống bắt đầu bằng việc đọc file seed (tệp hạt giống):
* `data/top100_artists_seed.csv`: File này chứa danh sách kênh YouTube (kèm theo Channel ID) của Top 100 nghệ sĩ US-UK. Mã nguồn sẽ tự động đọc file này bằng thư viện Pandas để lấy đầu vào cho quá trình Extract.

## Cấu trúc Dữ liệu (Data Schema)
Dữ liệu thô (raw) được kéo về gồm 4 file JSON, nhưng khi đưa lên BigQuery và qua bước Transform, chúng được tối ưu và gộp lại chỉ còn **3 bảng dữ liệu chính** (Relational Schema). Hệ thống sử dụng ID làm khóa ngoại để tối ưu không gian lưu trữ (ví dụ: không lưu lại tên kênh trong bảng video).

### 1. Bảng `channel_data` (Thông tin kênh):
* **channel_id (Primary Key):** Mã định danh duy nhất của kênh nghệ sĩ.
* **channel_name, description, published_at:** Thông tin cơ bản của kênh.
* **view_count, subscriber_count, video_count:** Các chỉ số tổng quan của kênh tại thời điểm quét.

### 2. Bảng `videos_data` (Thông tin & Thống kê Video):
Bảng này được gộp (JOIN) từ 2 tập dữ liệu thô là `latest_videos` (danh sách tối đa 50 video mới nhất/kênh) và `video_statistics` (chỉ số của từng video).
* **video_id (Primary Key):** Mã định danh duy nhất của video.
* **channel_id (Foreign Key):** Dùng để JOIN với bảng `channel_data`.
* **title, description, published_at:** Thông tin chi tiết của video.
* **view_count, like_count, comment_count:** Các chỉ số tương tác của video.
* **extract_at:** Thời gian cào dữ liệu (được chuẩn hóa theo múi giờ Asia/Ho_Chi_Minh (UTC+7) trên máy ảo).

### 3. Bảng `video_comments` (Bình luận):
Thu thập tối đa 30 bình luận Top cho mỗi video.
* **comment_id (Primary Key):** Mã định danh bình luận.
* **video_id (Foreign Key):** Liên kết với bảng `videos_data`.
* **author_display_name, text_display, published_at:** Thông tin người bình luận và nội dung phản hồi của khán giả.

## Quy trình Vận hành ELT (Pipeline Workflow)
Quá trình ELT được điều phối bởi file `main.py`, gọi lần lượt 3 module chính nằm trong thư mục `elt/`:

* **Extract (`elt/extract.py`):**
  * Kết nối với YouTube API v3.
  * Quét qua danh sách các kênh từ file `top100_artists_seed.csv`.
  * Lấy thông tin kênh, danh sách video mới nhất, số liệu thống kê (views, likes) và bình luận.
  * Lưu dữ liệu trích xuất dưới dạng 4 file JSON thô (raw) vào thư mục `data/raw/`.

* **Load (`elt/load.py`):**
  * Đọc các file JSON thô vừa được lưu ở bước Extract.
  * Tải (Upload) trực tiếp toàn bộ dữ liệu này vào các bảng tạm (staging tables) trên Google BigQuery.

* **Transform (`elt/transform.py`):**
  * Gửi các câu lệnh SQL trực tiếp lên BigQuery để xử lý.
  * Các lệnh SQL sẽ làm nhiệm vụ: chuẩn hóa kiểu dữ liệu, xử lý trùng lặp và đặc biệt là JOIN 2 bảng danh sách video và thống kê video lại thành 1 bảng `videos_data` duy nhất.

## Cấu trúc thư mục (Project Structure)
```text
Big_Project1/
├── venv/                   # Môi trường ảo Python
├── data/
│   ├── raw/                # Chứa các file JSON dữ liệu thô (channel, video, comments...)
│   └── top100_artists_seed.csv # File danh sách Top 100 nghệ sĩ US-UK
├── elt/
│   ├── __init__.py
│   ├── extract.py          # Script kéo dữ liệu từ YouTube API
│   ├── load.py             # Script đẩy dữ liệu JSON lên BQ
│   └── transform.py        # Script chạy SQL trên BigQuery để làm sạch, gộp bảng
├── utils/                  # Các module hỗ trợ (file I/O)
├── main.py                 # File chính điều phối luồng E-L-T
├── run_elt.sh              # Shell script để tự động hóa quy trình
├── elt_cron.log            # File ghi nhận lịch sử và lỗi khi chạy ngầm
├── requirements.txt        # Danh sách thư viện Python
└── README.md               # Tài liệu dự án
```

## Hướng dẫn cài đặt & Chạy tự động (Deployment)
Toàn bộ các bước cài đặt, cấp quyền, cấu hình tự động và theo dõi log được thực hiện liền mạch qua chuỗi lệnh sau:

```bash
# 1. Cài đặt môi trường ảo và thư viện
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Cấu hình môi trường bảo mật
# (Tạo file .env tại thư mục gốc và khai báo: API_KEY=YOUR_YOUTUBE_API_KEY)
# Đảm bảo máy ảo VM đã được cấp quyền (Scopes) truy cập BigQuery.

# 3. Cấp quyền thực thi cho file chạy tự động
chmod +x run_elt.sh

# 4. Lịch trình tự động (Cronjob)
crontab -e
# Thêm dòng sau vào crontab để chạy tự động lúc 07:00 sáng và 23:00 đêm mỗi ngày (Theo yêu cầu đề bài):
# 0 7,23 * * * /home/hung/Project/Big_Project1/run_elt.sh

# 5. Theo dõi tiến trình chạy hoặc debug lỗi (Monitoring)
tail -f elt_cron.log
```