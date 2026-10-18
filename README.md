YouTube Data ELT Pipeline
Giới thiệu (Overview)
Dự án này là một hệ thống ELT (Extract - Load - Transform) tự động được triển khai trên máy ảo Google Cloud Compute Engine (GCP VM).

Mục tiêu cốt lõi của dự án là thu thập và phân tích dữ liệu từ các kênh YouTube của Top 100 nghệ sĩ US-UK có lượt xem cao nhất. Dữ liệu này sẽ giúp theo dõi mức độ tương tác, xu hướng phát hành và phản hồi của khán giả đối với các sản phẩm âm nhạc hàng đầu.

Khác với mô hình ETL truyền thống, pipeline này áp dụng mô hình ELT hiện đại: Dữ liệu thô từ YouTube được tải (Load) trực tiếp lên kho dữ liệu, sau đó sức mạnh tính toán của Google BigQuery được tận dụng để thực thi các lệnh SQL làm sạch, gộp bảng và chuyển đổi (Transform) dữ liệu ngay trên Cloud.
Kiến trúc & Công nghệ (Tech Stack)
Ngôn ngữ: Python 3, Standard SQL
Môi trường triển khai: Google Cloud Compute Engine (Ubuntu VM)
Kho dữ liệu (Data Warehouse): Google BigQuery
Nguồn dữ liệu: YouTube Data API v3
Điều phối (Orchestration): Linux Cronjob
Cấu trúc Dữ liệu (Data Architecture)
Hệ thống lấy danh sách kênh từ tệp hạt giống (seed file) top100_artists_seed.csv và trích xuất dữ liệu thành 4 bảng thô (Raw Tables). Sau bước Load, quá trình Transform trên BigQuery sẽ hợp nhất và làm sạch dữ liệu thành 3 bảng chính (Core Tables):

dim_channel: Chứa thông tin tổng quan về kênh của 100 nghệ sĩ US-UK (Tên, ID, Lượt đăng ký, Tổng view, v.v.).
fact_video: Bảng thống kê video đã được tối ưu. Đây là kết quả của việc gộp 2 bảng thô (raw_latest_videos và raw_video_statistics) bằng SQL. Bảng này lưu trữ siêu dữ liệu (Tiêu đề, Ngày đăng) cùng với các chỉ số hiệu suất của từng video (View, Like, Comment count).
fact_comments: Chứa chi tiết hàng trăm nghìn bình luận từ người hâm mộ (Nội dung bình luận, Tác giả, Thời gian, Số lượt thích của bình luận).
Hướng dẫn triển khai (Deployment Guide)
1. Cấu hình môi trường (Environment Setup)
# Clone dự án từ GitHub

git clone [YOUR_GITHUB_REPO_URL]

cd youtube-artist-data-pipeline

# Tạo và kích hoạt môi trường ảo

python3 -m venv venv

source venv/bin/activate

# Cài đặt thư viện

pip install -r requirements.txt
2. Thiết lập bảo mật (.env)
Tạo file .env tại thư mục gốc và khai báo thông tin xác thực:

API_KEY=YOUR_YOUTUBE_API_KEY

(Lưu ý: Service account JSON cho BigQuery được đặt riêng theo cấu hình mã nguồn).
3. Cấu hình tự động hóa (Cronjob)
Theo yêu cầu dự án, pipeline được lập lịch chạy ngầm 2 lần mỗi ngày (07:00 sáng và 23:00 đêm) trên máy ảo VM.

Đảm bảo script có quyền thực thi: chmod +x run_elt.sh
Mở crontab: crontab -e
Thêm cấu hình sau:

# Chạy pipeline lúc 07:00 sáng mỗi ngày

0 7 * * * /home/hung/Project/Big_Project1/run_elt.sh

# Chạy pipeline lúc 23:00 đêm mỗi ngày

0 23 * * * /home/hung/Project/Big_Project1/run_elt.sh
Theo dõi (Monitoring)
Mọi kết quả và lỗi sinh ra trong quá trình chạy tự động sẽ được hệ thống ghi nhận chi tiết tại tệp elt_cron.log trên VM. Lệnh kiểm tra: cat elt_cron.log
