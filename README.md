# Portfolio Manager - Quản Lý Danh Mục Đầu Tư Vàng/Bạc

Ứng dụng quản lý danh mục đầu tư vàng và bạc với giao diện web, hỗ trợ theo dõi tài sản, tính toán lãi/lỗ theo thời gian thực.

## 🌟 Tính Năng

### Quản Lý Tài Sản
- **Tài sản sẵn có**: Quản lý tài sản vàng đang sở hữu
- **Tài sản đầu tư**: Theo dõi đầu tư vàng/bạc với giá mua, ngày mua

### Cập Nhật Giá Thời Gian Thực
Lấy giá từ các cơ sở kinh doanh vàng bạc uy tín:
- 🥇 **Bảo Tín Minh Châu** (btmc.vn) - Nhẫn tròn trơn
- 🥇 **Bảo Tín Mạnh Hải** (baotinmanhhai.vn) - Nhẫn ép vỉ Vàng Rồng Thăng Long
- 🥈 **Phú Quý** - Bạc thỏi Phú Quý 999 1Kilo
- 🥇 **Phú Tài** (vangphutai.vn) - Nhẫn tròn trơn 999.9
- 🥈 **Ancarat** (giabac.ancarat.com) - Ngân Long Quảng Tiến 999 - 1 lượng

### Dashboard
- Bảng thống kê chi tiết từng tài sản
- Biểu đồ phân bổ danh mục (Pie chart)
- Biểu đồ lãi/lỗ theo tài sản (Bar chart)
- Biểu đồ tổng hợp cột + đường
- Biểu đồ lãi/lỗ theo thời gian nắm giữ (Scatter plot)

### Tính Toán
- Quy đổi đơn vị: Chỉ, Lượng, Kilogram
- Tính giá trị tài sản hiện tại
- Tính lãi/lỗ (VNĐ và %)
- Tính thời gian nắm giữ (tháng)

## 🚀 Cài Đặt

### Yêu Cầu
- Python 3.9+
- pip

### Cài Đặt Dependencies

```bash
cd /home/sangnv/Desktop/portfilio_manager
pip install -r requirements.txt
```

## 💻 Chạy Ứng Dụng

```bash
cd /home/sangnv/Desktop/portfilio_manager
streamlit run app.py
```

Mở trình duyệt và truy cập: http://localhost:8501

## 📁 Cấu Trúc Project

```
portfilio_manager/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
├── data/                 # Data storage (JSON files)
│   ├── existing_assets.json
│   └── investment_assets.json
└── src/
    ├── __init__.py
    ├── config.py         # Configuration and constants
    ├── models.py         # Pydantic data models
    ├── scraper.py        # Web scraping module
    ├── price_service.py  # Price calculation service
    ├── storage.py        # Data persistence
    └── charts.py         # Plotly chart builders
```

## 🎨 Theme

Ứng dụng sử dụng theme **Dark Sunset** với màu sắc:
- Background: #1a1a2e (Dark blue)
- Secondary: #16213e (Darker blue)
- Accent: #e94560 (Coral/sunset red)
- Gold: #ffd700
- Silver: #c0c0c0

## 📖 Hướng Dẫn Sử Dụng

### 1. Cập Nhật Giá
- Nhấn nút **"🔄 Cập Nhật Giá"** ở sidebar để lấy giá mới nhất từ các website

### 2. Thêm Tài Sản Sẵn Có
1. Chọn tab "Tài sản sẵn có" ở sidebar
2. Nhập thông tin: tên, loại (vàng/bạc), số lượng, đơn vị
3. Chọn cơ sở kinh doanh tham chiếu
4. Nhấn "Thêm Tài Sản"

### 3. Thêm Tài Sản Đầu Tư
1. Chọn tab "Tài sản đầu tư" ở sidebar
2. Nhập thông tin: tên, loại, số lượng, đơn vị
3. Nhập giá mua và ngày mua
4. Chọn cơ sở kinh doanh tham chiếu
5. Nhấn "Thêm Tài Sản"

### 4. Xem Thống Kê
- Tab **"📋 Bảng Thống Kê"**: Xem chi tiết từng tài sản
- Tab **"📈 Biểu Đồ"**: Xem các biểu đồ phân tích

### 5. Xóa Tài Sản
- Mở phần "🗑️ Xóa Tài Sản" trong tab Bảng Thống Kê
- Nhấn nút xóa bên cạnh tài sản muốn xóa

## 🔄 Quy Đổi Đơn Vị

| Từ | Sang | Hệ số |
|---|---|---|
| 1 Lượng | Chỉ | × 10 |
| 1 Kilogram | Lượng | × 26.67 |
| 1 Kilogram | Chỉ | × 266.7 |

## ⚠️ Lưu Ý

- Giá được lấy theo giá **mua vào** của cơ sở kinh doanh (giá bạn bán được)
- Dữ liệu được lưu local trong thư mục `data/`
- Cần kết nối internet để cập nhật giá

## 📝 License

MIT License

## 👤 Author

Portfolio Manager Team
