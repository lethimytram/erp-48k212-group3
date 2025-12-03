# Hướng dẫn cài đặt và sử dụng Highland Training System

## 1. Cài đặt Module

### Bước 1: Copy module vào thư mục addons

```bash
cp -r highland_training /path/to/odoo/custom_addons/
```

### Bước 2: Khởi động lại Odoo server

```bash
./odoo-bin -c odoo.conf -u highland_training
```

### Bước 3: Cập nhật Apps List

1. Đăng nhập Odoo với quyền Admin
2. Vào Apps → Update Apps List
3. Tìm "Highland Training System"
4. Click Install

## 2. Cấu hình ban đầu

### 2.1 Tạo Users và phân quyền

#### Admin Đào tạo

1. Settings → Users & Companies → Users
2. Tạo user mới hoặc chỉnh sửa user hiện có
3. Tab "Access Rights" → Highland Training → chọn "Admin Đào tạo"

#### Quản lý cửa hàng

1. Tạo user cho quản lý
2. Gán vào group "Quản lý cửa hàng"
3. Đảm bảo user có liên kết với Employee
4. Employee phải là Manager của Department (cửa hàng)

#### Nhân viên

1. Tạo Portal User cho nhân viên
2. Gán vào group "Nhân viên"
3. Liên kết với Employee record

### 2.2 Cấu trúc tổ chức

1. HR → Configuration → Departments
2. Tạo các Department đại diện cho cửa hàng
3. Gán Manager cho mỗi Department
4. Tạo Job Positions (Barista, Cashier, etc.)

## 3. Hướng dẫn sử dụng cho từng Actor

### 3.1 ADMIN (Hội sở)

#### A. Tạo khóa học mới

1. Đào tạo Highland → Quản trị → Khóa học
2. Click "Create"
3. Điền thông tin:
   - Tên khóa học
   - Mã khóa học
   - Loại khóa học
   - Vị trí công việc (target audience)

#### B. Thêm nội dung đào tạo

1. Mở khóa học
2. Tab "Nội dung đào tạo"
3. Add a line:
   - Video: Paste URL YouTube/Vimeo
   - Document: Upload file
   - Recipe: Nhập công thức chi tiết

#### C. Tạo ngân hàng câu hỏi

1. Tab "Ngân hàng câu hỏi"
2. Add a line cho mỗi câu hỏi
3. Điền:
   - Nội dung câu hỏi
   - Loại: Một đáp án / Nhiều đáp án
   - Điểm
4. Thêm các đáp án, check "Đáp án đúng" cho câu trả lời đúng

#### D. Thiết lập Checklist thực hành

1. Tab "Checklist thực hành"
2. Add a line cho mỗi tiêu chí
3. Chọn:
   - Nhóm tiêu chí (Công thức, Vệ sinh, Kỹ thuật...)
   - Bắt buộc: ON cho tiêu chí quan trọng

#### E. Cấu hình đánh giá

1. Tab "Cấu hình đánh giá"
2. Cài đặt:
   - Số câu hỏi thi: Số câu random từ ngân hàng
   - Thời gian thi: Phút
   - Điểm đạt lý thuyết: % (VD: 80)
   - Tỷ lệ đạt thực hành: % (VD: 80)

#### F. Kích hoạt khóa học

1. Click "Kích hoạt" trên header
2. Khóa học sẵn sàng để phân công

#### G. Phân công học viên

1. Đào tạo Highland → Quản trị → Quản lý học viên
2. Create → Chọn:
   - Nhân viên
   - Khóa học
   - Hạn hoàn thành (optional)
3. Save và click "Bắt đầu học"

#### H. Xem báo cáo

1. Đào tạo Highland → Quản trị → Báo cáo
2. Phân tích theo:
   - Khóa học
   - Cửa hàng
   - Trạng thái

### 3.2 QUẢN LÝ CỬA HÀNG

#### A. Xem danh sách nhân viên

1. Đào tạo Highland → Quản lý cửa hàng → Nhân viên của tôi
2. View theo trạng thái:
   - Chưa học
   - Đang học lý thuyết
   - Sẵn sàng thực hành
   - Hoàn thành

#### B. Tạo đánh giá thực hành

1. Đào tạo Highland → Quản lý cửa hàng → Đánh giá thực hành
2. Create:
   - Chọn Đăng ký học (Enrollment)
   - Hệ thống tự động load checklist
3. Click "Bắt đầu đánh giá"

#### C. Chấm điểm thực hành (Trên mobile)

1. Mở form đánh giá thực hành
2. Tab "Checklist đánh giá"
3. Quan sát nhân viên thực hiện
4. Check "Đạt" cho từng tiêu chí:
   - ✓ Đạt: Thực hiện đúng
   - ✗ Không đạt: Thực hiện sai
5. Ghi chú vào cột "Ghi chú của người đánh giá"

#### D. Hoàn thành đánh giá

1. Click "Hoàn thành"
2. Hệ thống kiểm tra:
   - Tất cả tiêu chí bắt buộc phải ĐẠT
   - Tỷ lệ đạt >= ngưỡng cấu hình
3. Nếu đạt → Tự động cấp chứng nhận

### 3.3 NHÂN VIÊN (Portal)

#### A. Truy cập Portal

1. Truy cập: `https://your-domain.com/my`
2. Đăng nhập bằng Portal credentials
3. Click vào "Đào tạo"

#### B. Xem khóa học được phân công

1. Danh sách các khóa học
2. Click "Xem chi tiết" khóa học muốn học

#### C. Học nội dung

1. Xem video hướng dẫn
2. Đọc tài liệu, công thức
3. Ghi nhớ các kiến thức

#### D. Thi lý thuyết

1. Khi sẵn sàng, click "Bắt đầu thi"
2. Làm bài trắc nghiệm:
   - Đọc kỹ câu hỏi
   - Chọn đáp án (radio/checkbox)
   - Có thể làm lại nếu chưa đạt
3. Click "Nộp bài"
4. Xem kết quả:
   - Điểm số
   - Đúng/Sai từng câu
   - Giải thích đáp án

#### E. Thực hành tại cửa hàng

1. Sau khi đạt lý thuyết
2. Liên hệ Quản lý cửa hàng
3. Thực hiện thao tác thực tế
4. Được đánh giá trực tiếp

#### F. Xem chứng nhận

1. Portal → Chứng nhận
2. Xem danh sách chứng chỉ đã đạt
3. Thông tin:
   - Số chứng nhận
   - Ngày cấp
   - Điểm lý thuyết & thực hành

## 4. Quy trình nghiệp vụ điển hình

### Kịch bản 1: Ra mắt sản phẩm mới "Highland Mocha"

**Bước 1: Admin tạo khóa học (30 phút)**

- Tên: "Highland Mocha - Sản phẩm mới Q4/2024"
- Loại: Sản phẩm mới
- Upload video demo pha chế
- Nhập công thức: Chocolate, Espresso, Sữa tươi, Đá
- Tạo 15 câu hỏi về công thức, kỹ thuật
- Tạo 8 tiêu chí checklist thực hành
- Cấu hình: 10 câu thi, 15 phút, đạt 80%

**Bước 2: Admin phân công (10 phút)**

- Chọn tất cả Barista trên toàn hệ thống
- Hạn: 7 ngày
- Mass assign

**Bước 3: Nhân viên học online (2 ngày)**

- 200 Barista login Portal
- Xem video, đọc công thức
- Thi lý thuyết
- Tỷ lệ đạt lần 1: 75%
- 25% còn lại thi lại

**Bước 4: Quản lý đánh giá (1 tuần)**

- 50 Quản lý cửa hàng
- Mỗi người đánh giá 4 nhân viên/ngày
- Dùng tablet/phone tại quầy bar
- Check từng tiêu chí khi nhân viên pha chế

**Bước 5: Hoàn thành**

- Sau 10 ngày: 190/200 nhân viên hoàn thành
- Tự động cấp 190 chứng nhận
- Admin xem báo cáo:
  - 10 cửa hàng chậm tiến độ
  - 5 nhân viên cần đào tạo lại

### Kịch bản 2: Onboarding nhân viên mới

**Bước 1: HR tạo Employee**

- Nhập thông tin cá nhân
- Gán Job Position: Barista
- Tạo Portal User

**Bước 2: Hệ thống tự động (qua Automated Action - nâng cao)**

- Detect nhân viên mới có Job = Barista
- Auto enroll vào:
  - Khóa 1: Giới thiệu Highland Coffee
  - Khóa 2: An toàn vệ sinh thực phẩm
  - Khóa 3: Barista cơ bản
  - Khóa 4: Kỹ năng phục vụ khách hàng

**Bước 3: Nhân viên học tuần tự**

- Tuần 1: Khóa 1 + 2 (Lý thuyết)
- Tuần 2: Khóa 3 (Lý thuyết + Thực hành)
- Tuần 3: Khóa 4 (Thực hành)

**Bước 4: Kết quả**

- Sau 1 tháng: Nhân viên có 4 chứng nhận
- Đủ điều kiện chuyển chính thức

## 5. Troubleshooting

### Lỗi thường gặp

**1. Nhân viên không thấy khóa học trên Portal**

- Check: User có group "Nhân viên"?
- Check: User có link với Employee?
- Check: Enrollment đã tạo chưa?

**2. Quản lý không thấy nhân viên trong cửa hàng**

- Check: Manager có phải là Department Manager?
- Check: Employee có thuộc Department đó?
- Check: Record rule có đúng?

**3. Không tạo được bài thi**

- Check: Khóa học có đủ câu hỏi?
- Check: Enrollment ở trạng thái nào?
- Check: Nhân viên đã đạt lý thuyết chưa?

**4. Tự động chấm điểm sai**

- Check: Đáp án có check "Đáp án đúng"?
- Check: Loại câu hỏi (Single/Multiple)?
- Check: Logic chấm điểm trong code

## 6. Nâng cấp & Mở rộng

### Tính năng có thể thêm

1. **Automated Actions**

   - Auto enroll theo Job Position
   - Reminder email trước deadline
   - Notify Manager khi nhân viên hoàn thành

2. **Gamification**

   - Ranking top learner
   - Badges cho achievements
   - Leaderboard

3. **Advanced Reporting**

   - Dashboard with charts
   - Export to Excel
   - Email báo cáo định kỳ

4. **Mobile App**

   - Native mobile app
   - Offline learning
   - Push notifications

5. **Integration**
   - Sync with HR Payroll (bonus cho chứng nhận)
   - Integration với POS (required certification)
   - API cho external systems

## 7. Liên hệ hỗ trợ

**IT Department - Highland Coffee**

- Email: it@highlandscoffee.com.vn
- Phone: (028) 1234 5678
- Slack: #highland-training-support

---

Cập nhật lần cuối: December 2024
