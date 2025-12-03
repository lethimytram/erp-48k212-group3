# Highland Training System - Module Đào tạo Highland Coffee

## 🎯 Tổng quan Module

**Tên module**: Highland Training  
**Phiên bản**: 18.0.1.0.0  
**Mô hình**: Blended Learning (Lý thuyết + Thực hành)  
**3 Actors**: Admin, Quản lý cửa hàng, Nhân viên

---

## ⭐ DANH SÁCH CHỨC NĂNG

### 1. Quản lý khóa học

- Tạo/sửa/xóa khóa học
- Phân loại khóa học: Định hướng, Bắt buộc, Nâng cao
- Cấu hình điểm đạt (lý thuyết ≥70%, thực hành ≥80%)
- Quản lý thời lượng khóa học
- Kanban view với màu sắc theo loại

### 2. Quản lý nội dung đào tạo

- **Video**: Link YouTube/Vimeo, transcript văn bản
- **Tài liệu**: Upload PDF/Word/PowerPoint
- **Recipe**: Công thức pha chế (nguyên liệu, bước thực hiện, lưu ý)
- Sắp xếp thứ tự nội dung học tuần tự
- Ghi chú hướng dẫn bổ sung

### 3. Quản lý ngân hàng câu hỏi trắc nghiệm

- Tạo câu hỏi: Một đáp án / Nhiều đáp án / Đúng-Sai
- Quản lý đáp án và đánh dấu đáp án đúng
- Cấu hình điểm số cho từng câu
- Phân loại câu hỏi theo khóa học
- Import/Export câu hỏi hàng loạt

### 4. Thi lý thuyết trực tuyến

- Random câu hỏi khi tạo bài thi
- Đếm thời gian làm bài (timer tự động)
- Chấm điểm tự động khi nộp bài
- Xem lại đáp án đúng/sai sau khi chấm
- Giới hạn 1 bài thi hợp lệ/enrollment
- Cho phép thi lại nếu không đạt

### 5. Quản lý checklist đánh giá thực hành

- 5 danh mục: Recipe, Hygiene, Technique, Service, Time
- Cấu hình tiêu chí bắt buộc/không bắt buộc
- Thiết lập điểm số cho từng tiêu chí
- Ghi chú hướng dẫn đánh giá
- Template checklist theo khóa học

### 6. Đánh giá thực hành tại chỗ

- Manager/Admin chấm điểm trực tiếp
- Đánh giá từng tiêu chí: Đạt/Không đạt
- Tự động tính % hoàn thành
- Ghi chú phản hồi và góp ý cải thiện
- Lịch sử các lần đánh giá
- Mobile-friendly (chấm trên tablet/phone)

### 7. Ghi danh học viên (Enrollment)

- Admin/Manager gán nhân viên vào khóa học
- Ghi danh thủ công (từng người)
- Ghi danh hàng loạt (từ kế hoạch quý)
- Liên kết với training request
- Theo dõi trạng thái: Draft → Learning → Completed

### 8. Theo dõi tiến độ học tập

- **Lý thuyết**: Chưa bắt đầu → Đang học → Đạt/Không đạt
- **Thực hành**: Chưa bắt đầu → Đang đánh giá → Đạt/Không đạt
- Hiển thị điểm số lý thuyết + thực hành
- Progress bar % hoàn thành
- Thống kê số lượng: Hoàn thành / Đang học / Chưa bắt đầu
- Xem lịch sử bài thi và đánh giá

### 9. Cấp chứng nhận tự động

- Kiểm tra điều kiện: Đạt cả lý thuyết VÀ thực hành
- Tự động tạo certificate khi đạt yêu cầu
- Mã chứng chỉ tự động: CERT/2025/00001
- Lưu điểm lý thuyết + thực hành
- Tính ngày hết hạn (nếu có)
- In PDF chứng chỉ chuyên nghiệp
- Quản lý trạng thái: Hợp lệ / Hết hạn / Thu hồi

### 10. Báo cáo và thống kê

- **Pivot Table**: Phân tích đa chiều (khóa học × nhân viên × phòng ban)
- **Graph/Chart**: Xu hướng học tập, so sánh hiệu suất team
- **Dashboard Admin**: Tổng quan toàn hệ thống
- **Dashboard Manager**: Hiệu suất cửa hàng
- Filter nâng cao: Thời gian, trạng thái, phòng ban
- Export báo cáo Excel/PDF
- Thống kê: Tỷ lệ đạt, điểm TB, số lượng học viên

### 11. Yêu cầu đào tạo (Training Request)

- Manager tạo yêu cầu đào tạo cho nhân viên
- Chọn khóa học và danh sách nhân viên
- Ghi rõ lý do và mức độ ưu tiên
- Workflow: Draft → Submitted → Approved/Rejected
- Admin phê duyệt/từ chối (kèm lý do)
- Mã tự động: REQ/00001
- Lịch sử theo dõi toàn bộ yêu cầu

### 12. Kế hoạch đào tạo theo quý

- Lập kế hoạch theo quý: Q1, Q2, Q3, Q4
- Chọn nhiều nhân viên cùng lúc
- Chọn nhiều khóa học cùng lúc
- 4 tab: Thông tin chung / Nhân viên / Khóa học / Đăng ký
- Theo dõi progress bar % hoàn thành
- Thống kê: Hoàn thành / Đang học / Chưa bắt đầu

### 13. Enrollment hàng loạt

- Button "Tạo đăng ký" trong training.plan
- Tự động tạo enrollment cho (nhân viên × khóa học)
- VD: 10 nhân viên × 3 khóa học = 30 enrollments
- Liên kết với kế hoạch quý
- Tối ưu hóa cho số lượng lớn
- Thông báo kết quả sau khi tạo

---

## ⭐ CHI TIẾT TÍNH NĂNG

### 📚 1. QUẢN LÝ KHÓA HỌC

#### Khóa học (training.course)

- **Phân loại**: Định hướng / Bắt buộc / Nâng cao
- **Thông tin**: Tên, mã, mô tả, thời lượng, điểm đạt
- **Kanban view**: Hiển thị theo màu sắc (xanh/vàng/đỏ)
- **Chi tiết**: Nội dung học, câu hỏi, checklist thực hành

#### Nội dung đào tạo (training.content)

- **3 loại nội dung**:
  - 📹 **Video**: Link YouTube/Vimeo + transcript
  - 📄 **Tài liệu**: PDF/Word/PowerPoint
  - ☕ **Recipe**: Công thức pha chế (nguyên liệu, bước thực hiện)
- **Quản lý thứ tự**: Sắp xếp nội dung học tuần tự
- **Ghi chú**: Hướng dẫn bổ sung cho từng nội dung

---

### 📝 2. SÁT HẠCH LÝ THUYẾT TRỰC TUYẾN

#### Ngân hàng câu hỏi (training.question)

- **3 loại câu hỏi**:
  - ✅ **Một đáp án đúng**: Single choice
  - ☑️ **Nhiều đáp án đúng**: Multiple choice
  - ⭕ **Đúng/Sai**: True/False
- **Quản lý đáp án**: Đánh dấu đáp án đúng
- **Điểm số**: Cấu hình điểm cho từng câu
- **Phân loại**: Gắn với khóa học cụ thể

#### Bài thi (training.exam)

- **Workflow**: Nháp → Đang làm → Nộp bài → Đã chấm
- **Tính năng**:
  - 🕐 **Đếm thời gian**: Timer tự động
  - 📊 **Chấm tự động**: Tính điểm ngay khi nộp
  - 🎯 **Điều kiện đạt**: ≥70% = Đạt
  - 📋 **Xem lại đáp án**: Hiển thị đúng/sai sau khi chấm
- **Giới hạn**: Mỗi enrollment chỉ 1 bài thi hợp lệ

---

### 🛠️ 3. ĐÁNH GIÁ THỰC HÀNH TẠI CHỖ

#### Checklist đánh giá (training.checklist)

- **5 danh mục**:
  - ☕ **Recipe**: Công thức pha chế chính xác
  - 🧼 **Hygiene**: Vệ sinh an toàn thực phẩm
  - 🎨 **Technique**: Kỹ thuật thực hiện
  - 😊 **Service**: Phục vụ khách hàng
  - ⏱️ **Time**: Thời gian hoàn thành
- **Cấu hình**: Bắt buộc/Không bắt buộc
- **Điểm số**: Điểm cho từng tiêu chí

#### Đánh giá thực hành (training.practice)

- **Người đánh giá**: Quản lý cửa hàng hoặc Admin
- **Chấm điểm**:
  - ✅ Đạt / ❌ Không đạt cho từng tiêu chí
  - Tự động tính % đạt
  - Điều kiện: ≥80% = Đạt
- **Phản hồi**: Ghi chú và góp ý cải thiện
- **Lịch sử**: Theo dõi các lần đánh giá

---

### 📋 4. QUẢN LÝ HỌC VIÊN

#### Đăng ký khóa học (training.enrollment)

- **Ghi danh**: Admin/Manager gán nhân viên vào khóa học
- **Enrollment hàng loạt**: Tạo nhiều đăng ký từ kế hoạch đào tạo
- **Theo dõi tiến độ**:
  - 📊 **Lý thuyết**: Chưa bắt đầu → Đang học → Đạt/Không đạt
  - 🛠️ **Thực hành**: Chưa bắt đầu → Đang đánh giá → Đạt/Không đạt
  - 🎓 **Tổng thể**: Draft → Đang học → Hoàn thành
- **Điểm số**: Lưu điểm lý thuyết + thực hành
- **Liên kết**: Với kế hoạch đào tạo quý

---

### 🎖️ 5. CHỨNG NHẬN TỰ ĐỘNG

#### Chứng chỉ (training.certificate)

- **Cấp tự động**: Khi đạt CẢ lý thuyết VÀ thực hành
- **Mã chứng chỉ**: CERT/2025/00001 (sequence tự động)
- **Thông tin**:
  - Nhân viên, khóa học
  - Điểm lý thuyết + thực hành
  - Ngày cấp, ngày hết hạn
- **Trạng thái**: Hợp lệ / Hết hạn / Thu hồi
- **In PDF**: Template chứng chỉ chuyên nghiệp

---

### 📊 6. BÁO CÁO VÀ THỐNG KÊ

#### Dashboard Admin (training.report)

- **Pivot Table**: Phân tích đa chiều
  - Theo khóa học, nhân viên, phòng ban
  - Điểm trung bình, tỷ lệ đạt
- **Graph/Chart**:
  - 📈 Xu hướng học tập theo thời gian
  - 📊 So sánh hiệu suất giữa các team
  - 🎯 Tỷ lệ hoàn thành khóa học
- **Filter nâng cao**: Lọc theo khoảng thời gian, trạng thái

#### Báo cáo Manager

- **Team performance**: Hiệu suất đào tạo của cửa hàng
- **Danh sách nhân viên**: Tiến độ từng người
- **Thực hành cần chấm**: Danh sách chờ đánh giá

---

### 📅 7. KẾ HOẠCH ĐÀO TẠO QUÝ (Training Plan)

#### Lập kế hoạch (training.plan)

- **Chu kỳ**: Theo quý (Q1, Q2, Q3, Q4)
- **Phạm vi**:
  - 👥 Chọn nhiều nhân viên
  - 📚 Chọn nhiều khóa học
- **Enrollment hàng loạt**:
  - Button "Tạo đăng ký"
  - Tự động tạo enrollment cho (nhân viên × khóa học)
- **Theo dõi**:
  - Progressbar % hoàn thành
  - Thống kê số lượng: Hoàn thành / Đang học / Chưa bắt đầu

#### 4 Tab quản lý

1. **Thông tin chung**: Tên, quý, năm, ghi chú
2. **Nhân viên**: Danh sách nhân viên tham gia
3. **Khóa học**: Danh sách khóa học trong kế hoạch
4. **Đăng ký**: Danh sách enrollment đã tạo (readonly)

---

### 📨 8. YÊU CẦU ĐÀO TẠO (Training Request)

#### Đề xuất nhu cầu (training.request)

- **Người tạo**: Quản lý cửa hàng
- **Nội dung**:
  - Khóa học đề xuất
  - Danh sách nhân viên cần đào tạo
  - Lý do và ghi chú
  - Mức độ ưu tiên: Thấp / Trung bình / Cao
- **Workflow**:
  - 📝 **Draft**: Manager soạn thảo
  - 📤 **Submitted**: Gửi lên Admin
  - ✅ **Approved**: Admin phê duyệt
  - ❌ **Rejected**: Admin từ chối (ghi rõ lý do)
- **Mã tự động**: REQ/00001
- **Lịch sử**: Theo dõi toàn bộ yêu cầu

---

## 🔐 PHÂN QUYỀN 3 CẤP

### 👨‍💼 Admin Đào tạo (group_training_admin)

**Quyền hạn**: Toàn quyền quản trị

**Menu Admin** (13 chức năng):

1. ✏️ Khóa học - Tạo/sửa/xóa
2. ❓ Câu hỏi - Quản lý ngân hàng câu hỏi
3. ✅ Checklist - Quản lý tiêu chí thực hành
4. 📨 Yêu cầu đào tạo - Duyệt yêu cầu từ Manager
5. 📅 Kế hoạch quý - Lập kế hoạch đào tạo
6. 📋 Đăng ký - Gán học viên
7. 📝 Bài thi - Xem kết quả thi
8. 🛠️ Thực hành - Chấm đánh giá
9. 🎖️ Chứng nhận - Quản lý chứng chỉ
10. 📊 Báo cáo - Dashboard tổng quan

**Chức năng đặc biệt**:

- Phê duyệt/từ chối yêu cầu đào tạo
- Tạo enrollment hàng loạt từ kế hoạch
- Xem báo cáo toàn hệ thống
- Chấm thực hành cho bất kỳ ai

---

### 🏪 Quản lý cửa hàng (group_training_manager)

**Quyền hạn**: Quản lý nhân viên cửa hàng mình

**Menu Manager** (7 chức năng):

1. 📨 Yêu cầu của tôi - Tạo/xem yêu cầu đào tạo
2. 📋 Đăng ký nhân viên - Xem tiến độ team
3. 🛠️ Thực hành cần chấm - Chấm điểm nhân viên
4. 📊 Báo cáo team - Thống kê cửa hàng

**Record Rule**:

- Chỉ thấy nhân viên báo cáo trực tiếp (`parent_id = user.employee_id`)
- Chỉ chấm được thực hành của nhân viên dưới quyền

**Chức năng đặc biệt**:

- Tạo training request đề xuất nhu cầu
- Chấm thực hành cho nhân viên
- Theo dõi tiến độ team

---

### 👤 Nhân viên (group_training_employee)

**Quyền hạn**: Xem và học khóa học của mình

**Menu Employee** (4 chức năng):

1. 📚 Khóa học của tôi - Xem enrollment
2. 📝 Bài thi của tôi - Làm bài thi
3. 🎖️ Chứng chỉ của tôi - Xem chứng nhận

**Record Rule**:

- Chỉ thấy enrollment của chính mình (`employee_id.user_id = user.id`)
- Chỉ làm được bài thi của enrollment mình
- Chỉ xem được chứng chỉ của mình

**Chức năng**:

- Học nội dung (video, tài liệu, recipe)
- Làm bài thi lý thuyết trực tuyến
- Xem kết quả và chứng chỉ

---

## 🔄 WORKFLOW BLENDED LEARNING

### Quy trình hoàn chỉnh

```
1. [ADMIN] Tạo khóa học
   ├── Thêm nội dung (video/tài liệu/recipe)
   ├── Tạo câu hỏi trắc nghiệm
   └── Thiết lập checklist thực hành

2. [MANAGER] Đề xuất nhu cầu đào tạo
   ├── Tạo training.request
   ├── Chọn khóa học + nhân viên
   └── Gửi lên Admin

3. [ADMIN] Duyệt yêu cầu → Lập kế hoạch quý
   ├── Tạo training.plan
   ├── Chọn nhiều nhân viên + khóa học
   └── Enrollment hàng loạt

4. [EMPLOYEE] Học lý thuyết
   ├── Xem nội dung đào tạo
   ├── Làm bài thi trắc nghiệm
   └── Đạt ≥70% = Pass lý thuyết

5. [MANAGER/ADMIN] Chấm thực hành
   ├── Đánh giá từng tiêu chí checklist
   ├── Ghi phản hồi
   └── Đạt ≥80% = Pass thực hành

6. [SYSTEM] Tự động cấp chứng chỉ
   ├── Kiểm tra: theory_state=passed AND practice_state=passed
   ├── Tạo training.certificate
   └── Gửi thông báo cho nhân viên
```

---

## 📁 Cấu trúc thư mục

```
highland_training/
├── __init__.py
├── __manifest__.py
├── README.md
├── GUIDE.md
│
├── models/
│   ├── __init__.py
│   ├── course.py              # Khóa học
│   ├── content.py             # Nội dung đào tạo (video, recipe, document)
│   ├── question.py            # Câu hỏi + Đáp án
│   ├── checklist.py           # Tiêu chí đánh giá thực hành
│   ├── enrollment.py          # Đăng ký học của nhân viên
│   ├── exam.py                # Bài thi lý thuyết + Câu trả lời
│   ├── practice.py            # Đánh giá thực hành + Chi tiết
│   └── certificate.py         # Chứng nhận
│
├── views/
│   ├── course_views.xml       # Views cho khóa học
│   ├── question_views.xml     # Views cho câu hỏi
│   ├── checklist_views.xml    # Views cho checklist
│   ├── enrollment_views.xml   # Views cho enrollment
│   ├── certificate_views.xml  # Views cho chứng nhận
│   ├── report_views.xml       # Báo cáo (Pivot, Graph)
│   ├── manager_views.xml      # Views cho Quản lý cửa hàng
│   ├── portal_templates.xml   # Portal templates cho Nhân viên
│   └── menu.xml               # Menu structure
│
├── controllers/
│   ├── __init__.py
│   └── portal.py              # Portal controllers (routes)
│
├── security/
│   ├── security.xml           # Groups & Record Rules
│   └── ir.model.access.csv    # Access Rights
│
├── data/
│   ├── sequence.xml           # Sequences cho mã tự động
│   └── demo_data.xml          # Demo data (khóa học mẫu)
│
└── static/
    ├── description/
    │   ├── icon.png           # Icon module
    │   └── index.html         # Module description
    ├── src/
    │   ├── css/
    │   │   └── portal.css     # Portal styles
    │   └── js/
    │       └── portal.js      # Portal scripts (timer, validation)
    └── img/
        └── training_icon.png  # Icon cho menu
```

## 🎯 Models và Relationships

### 1. training.course (Khóa học)

**Purpose**: Khóa học đào tạo  
**Key Fields**:

- name, code, course_type
- content_ids (O2M → training.content)
- question_ids (O2M → training.question)
- checklist_ids (O2M → training.checklist)
- exam_pass_score, practice_pass_percent

### 2. training.content (Nội dung)

**Purpose**: Nội dung học tập  
**Types**: video, document, recipe  
**Key Fields**:

- course_id (M2O → training.course)
- content_type, video_url, recipe_ingredients

### 3. training.question (Câu hỏi)

**Purpose**: Ngân hàng câu hỏi  
**Types**: single (1 đáp án), multiple (nhiều đáp án)  
**Key Fields**:

- course_id (M2O → training.course)
- answer_ids (O2M → training.answer)
- question_type, points

### 4. training.answer (Đáp án)

**Purpose**: Đáp án cho câu hỏi  
**Key Fields**:

- question_id (M2O → training.question)
- name, is_correct

### 5. training.checklist (Checklist)

**Purpose**: Tiêu chí đánh giá thực hành  
**Categories**: recipe, hygiene, technique, service, time  
**Key Fields**:

- course_id (M2O → training.course)
- category, is_required

### 6. training.enrollment (Đăng ký học)

**Purpose**: Gán nhân viên vào khóa học  
**Key Fields**:

- employee_id (M2O → hr.employee)
- course_id (M2O → training.course)
- theory_state: not_started → in_progress → passed/failed
- practice_state: not_started → in_progress → passed/failed
- state: draft → learning → completed
- exam_ids (O2M → training.exam)
- practice_ids (O2M → training.practice)
- certificate_id (M2O → training.certificate)

### 7. training.exam (Bài thi)

**Purpose**: Bài thi lý thuyết  
**Key Fields**:

- enrollment_id (M2O → training.enrollment)
- answer_ids (O2M → training.exam.answer)
- score, is_passed
- state: draft → in_progress → submitted → graded

### 8. training.exam.answer (Câu trả lời)

**Purpose**: Câu trả lời của học viên  
**Key Fields**:

- exam_id (M2O → training.exam)
- question_id (M2O → training.question)
- selected_answer_ids (M2M → training.answer)
- is_correct

### 9. training.practice (Đánh giá thực hành)

**Purpose**: Đánh giá kỹ năng thực tế  
**Key Fields**:

- enrollment_id (M2O → training.enrollment)
- assessor_id (M2O → hr.employee) # Quản lý đánh giá
- line_ids (O2M → training.practice.line)
- score, is_passed

### 10. training.practice.line (Chi tiết đánh giá)

**Purpose**: Đánh giá từng tiêu chí  
**Key Fields**:

- practice_id (M2O → training.practice)
- checklist_id (M2O → training.checklist)
- is_passed, assessor_notes

### 11. training.certificate (Chứng nhận)

**Purpose**: Chứng nhận hoàn thành  
**Key Fields**:

- employee_id (M2O → hr.employee)
- course_id (M2O → training.course)
- enrollment_id (M2O → training.enrollment)
- theory_score, practice_score
- issue_date, expiry_date
- state: valid, expired, revoked

## 🔐 Security (3 Actors)

### 1. Admin Đào tạo (group_training_admin)

**Quyền**: Full CRUD tất cả models  
**Chức năng**:

- Tạo/sửa khóa học
- Quản lý câu hỏi, checklist
- Phân công học viên
- Xem báo cáo toàn hệ thống

### 2. Quản lý cửa hàng (group_training_manager)

**Quyền**: Read khóa học, RU enrollment/practice của cửa hàng  
**Record Rule**: Chỉ thấy nhân viên trong cửa hàng (department_id.manager_id = user.employee_id)  
**Chức năng**:

- Xem danh sách nhân viên
- Đánh giá thực hành
- Chấm checklist

### 3. Nhân viên (group_training_employee)

**Quyền**: Read khóa học, RU enrollment/exam của mình  
**Record Rule**: [('employee_id.user_id', '=', user.id)]  
**Chức năng**:

- Xem khóa học (Portal)
- Làm bài thi
- Xem chứng nhận

## 🌐 Portal Routes

| Route                          | Method | Mô tả                            |
| ------------------------------ | ------ | -------------------------------- |
| `/my/trainings`                | GET    | Danh sách khóa học của nhân viên |
| `/my/training/<id>`            | GET    | Chi tiết khóa học                |
| `/my/training/<id>/start_exam` | POST   | Bắt đầu thi mới                  |
| `/my/exam/<id>`                | GET    | Xem bài thi                      |
| `/my/exam/start`               | POST   | Start timer                      |
| `/my/exam/<id>/submit`         | POST   | Nộp bài                          |
| `/my/certificates`             | GET    | Danh sách chứng nhận             |

## 📊 Quy trình nghiệp vụ (Workflow)

```
[ADMIN] Tạo Course → Content, Question, Checklist
           ↓
[ADMIN] Phân công → Create Enrollment (state=draft)
           ↓
[EMPLOYEE] Login Portal → Xem content → Học
           ↓
[EMPLOYEE] enrollment.action_start_exam() → Create Exam (random questions)
           ↓
[EMPLOYEE] Làm bài → exam.action_submit() → Auto grade
           ↓
    Is passed? → YES: theory_state=passed → practice_state=not_started
              → NO: theory_state=failed (có thể thi lại)
           ↓
[MANAGER] Create Practice → Load checklist
           ↓
[MANAGER] Quan sát nhân viên → Check từng tiêu chí
           ↓
[MANAGER] practice.action_submit() → Tính điểm
           ↓
    Is passed? → YES: practice_state=passed
              → NO: practice_state=failed (đánh giá lại)
           ↓
[SYSTEM] Check: theory_state=passed AND practice_state=passed?
           ↓ YES
[SYSTEM] enrollment.state=completed
         Create Certificate
         Update HR record
```

## 🎨 Views Structure

### Admin

- Khóa học: Kanban, Tree, Form (với tabs)
- Enrollment: Kanban (group by state), Tree, Form
- Certificate: Tree, Form
- Report: Pivot, Graph

### Manager

- My Store: Kanban (group by theory_state)
- Practice Assessment: Tree, Form (mobile-friendly)

### Portal (Nhân viên)

- My Trainings: Grid cards
- Training Detail: Single page với tabs
- Exam: Step-by-step form
- Certificates: Grid cards

## 🚀 Điểm nổi bật

1. **Mobile-first**: Manager có thể chấm điểm trên tablet/phone
2. **Auto-grading**: Thi trắc nghiệm tự động chấm điểm
3. **Random questions**: Mỗi lần thi random câu hỏi khác nhau
4. **Record Rules**: Đảm bảo data isolation giữa các cửa hàng
5. **Portal**: Nhân viên học trên bất kỳ thiết bị nào
6. **Certificates**: Tự động cấp và lưu trữ điện tử
7. **Reports**: Pivot & Graph cho Admin phân tích

## 📝 Notes

- Tất cả models có `mail.thread` cho chatter (trừ content, answer, checklist, practice.line)
- Sử dụng Sequence cho mã tự động (ENR/, EX/, PRC/, CERT/)
- State machines rõ ràng với transitions hợp lệ
- Demo data có sẵn 1 khóa học mẫu "Barista Cơ bản"

---

Version: 18.0.1.0.0  
Author: Highland Coffee Vietnam  
License: LGPL-3
