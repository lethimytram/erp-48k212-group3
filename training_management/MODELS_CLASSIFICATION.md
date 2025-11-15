# PHÂN LOẠI CÁC MODEL TRONG MODULE TRAINING_MANAGEMENT

## 📌 TỔNG QUAN

Module **training_management** bao gồm **24 models** được chia thành 3 nhóm chính:

- **1 Model kế thừa** từ Odoo có sẵn (`hr.employee`)
- **19 Models mới** được tạo riêng cho module (model chính)
- **3 Models mở rộng** kế thừa từ các model mới trong cùng module (extend functionality)

**Lưu ý:** Tất cả models đều kế thừa Mixin `mail.thread` và `mail.activity.mixin` từ Odoo để có chức năng Chatter và Activity.

---

## 🔄 1. MODEL KẾ THỪA TỪ ODOO CÓ SẴN

### 1.1. `hr.employee` (Kế thừa - Inherit)

**Loại:** Model có sẵn của Odoo (module `hr`)

**File:** `models/hr_employee.py`

**Mô tả:** Kế thừa và mở rộng model `hr.employee` của module `hr` trong Odoo

**Kế thừa cách nào:**

```python
_inherit = 'hr.employee'
```

**Không tạo bảng mới:** Model này chỉ mở rộng bảng `hr_employee` có sẵn, KHÔNG tạo bảng database mới

**Các trường được thêm vào:**

- `is_trainer` - Đánh dấu nhân viên là giảng viên
- `is_trainee` - Đánh dấu nhân viên là học viên (mặc định True)
- `trainer_id` - Liên kết với hồ sơ giảng viên
- `enrollment_ids` - Danh sách đăng ký khóa học
- `enrollment_count` - Số lượng khóa học đã đăng ký
- `certificate_ids` - Danh sách chứng chỉ
- `certificate_count` - Số lượng chứng chỉ
- `training_hours` - Tổng số giờ đào tạo
- `last_training_date` - Ngày đào tạo gần nhất

**Mục đích:** Bổ sung thông tin đào tạo cho nhân viên, tích hợp module đào tạo với quản lý nhân sự

---

## ✨ 2. CÁC MODEL MỚI TẠO (19 MODELS)

**Đặc điểm chung:** Tất cả models này đều:

- Có `_name` riêng → Tạo bảng database mới
- Kế thừa Mixin từ Odoo: `mail.thread` và `mail.activity.mixin`
- **KHÔNG kế thừa** từ bất kỳ model có sẵn nào của Odoo

---

### 2.1. `training.course` - Khóa học đào tạo

**File:** `models/training_course.py`

**Mô tả:** Model chính quản lý thông tin về các khóa học đào tạo

**Kế thừa Mixin:**

```python
_name = 'training.course'
_inherit = ['mail.thread', 'mail.activity.mixin']
```

- `mail.thread` - Chatter (theo dõi, bình luận)
- `mail.activity.mixin` - Hoạt động và lịch hẹn

**Chức năng chính:**

- Quản lý thông tin khóa học (tên, mã, mô tả, nội dung)
- Phân loại theo danh mục
- Quản lý tài liệu và giảng viên
- Theo dõi học viên và buổi học
- Tính toán thống kê (số học viên, tỷ lệ hoàn thành)
- Quản lý chi phí đào tạo

---

### 2.2. `training.course.category` - Danh mục khóa học

**File:** `models/training_course.py`

**Mô tả:** Phân loại khóa học theo danh mục có cấu trúc cây (parent-child)

**Đặc điểm:**

- Hỗ trợ phân cấp danh mục (danh mục cha - danh mục con)
- Đa ngôn ngữ (translate=True)
- Thống kê số lượng khóa học trong danh mục

---

### 2.3. `training.trainer` - Giảng viên đào tạo

**File:** `models/training_trainer.py`

**Mô tả:** Quản lý thông tin giảng viên (nội bộ và bên ngoài)

**Kế thừa Mixin:**

```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**Chức năng chính:**

- Quản lý thông tin giảng viên (tên, email, phone)
- Liên kết với nhân viên nội bộ (employee_id)
- Quản lý chuyên môn và chứng chỉ
- Theo dõi khóa học và buổi học đã giảng dạy
- Đánh giá hiệu suất giảng dạy
- Quản lý lịch trình và tính khả dụng

---

### 2.4. `training.material` - Tài liệu đào tạo

**File:** `models/training_material.py`

**Mô tả:** Quản lý tài liệu học tập cho khóa học

**Kế thừa Mixin:**

```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**Chức năng chính:**

- Hỗ trợ nhiều loại tài liệu (PDF, Video, Link, Document, Presentation, Worksheet)
- Upload file hoặc liên kết URL
- Quản lý quyền truy cập (public/restricted)
- Yêu cầu hoàn thành tài liệu
- Theo dõi tiến độ học tập
- Tải về và xem trước tài liệu

---

### 2.5. `training.plan` - Kế hoạch đào tạo

**File:** `models/training_plan.py`

**Mô tả:** Quản lý kế hoạch đào tạo theo năm và phòng ban

**Kế thừa Mixin:**

```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**Chức năng chính:**

- Lập kế hoạch đào tạo theo năm
- Phân theo phòng ban
- Quản lý trạng thái (nháp, phê duyệt, đang thực hiện, hoàn thành, hủy)
- Chỉ định người phụ trách

---

### 2.6. `training.need` - Nhu cầu đào tạo

**File:** `models/training_need.py`

**Mô tả:** Thu thập và quản lý nhu cầu đào tạo từ nhân viên

**Kế thừa Mixin:**

```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**Chức năng chính:**

- Nhân viên đề xuất nhu cầu đào tạo
- Quản lý trạng thái (nháp, đã gửi, phê duyệt, từ chối)
- Liên kết với phòng ban
- Quy trình phê duyệt

---

### 2.7. `training.enrollment` - Đăng ký khóa học

**File:** `models/training_enrollment.py`

**Mô tả:** Quản lý đăng ký tham gia khóa học của học viên

**Kế thừa Mixin:**

```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**Chức năng chính:**

- Đăng ký học viên vào khóa học
- Quản lý trạng thái (nháp, chờ duyệt, phê duyệt, từ chối, hoàn thành, hủy)
- Tự động tạo mã đăng ký
- Theo dõi ngày đăng ký

---

### 2.8. `training.session` - Buổi học

**File:** `models/training_session.py`

**Mô tả:** Quản lý các buổi học trong khóa đào tạo

**Kế thừa Mixin:**

```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**Chức năng chính:**

- Lên lịch buổi học với thời gian và địa điểm
- Phân công giảng viên
- Liên kết với lịch (calendar.event)
- Quản lý trạng thái (đã lên lịch, đang diễn ra, hoàn thành, hủy)
- Điểm danh học viên

---

### 2.9. `training.test` - Bài kiểm tra

**File:** `models/training_test.py`

**Mô tả:** Quản lý bài kiểm tra đánh giá kết quả học tập

**Kế thừa Mixin:**

```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**Chức năng chính:**

- Tạo bài thi (trắc nghiệm, tự luận, kết hợp)
- Cấu hình thời gian, điểm đạt, số lần thi
- Trộn câu hỏi ngẫu nhiên
- Thống kê kết quả (tỷ lệ đạt, điểm trung bình)
- Quản lý trạng thái (nháp, công bố, đóng)
- Liên kết với mẫu chứng chỉ

---

### 2.10. `training.test.question` - Câu hỏi bài kiểm tra

**File:** `models/training_test.py`

**Mô tả:** Quản lý câu hỏi trong bài kiểm tra

**Chức năng chính:**

- Nhiều loại câu hỏi (trắc nghiệm nhiều đáp án, 1 đáp án, đúng/sai, tự luận)
- Gán điểm cho từng câu
- Đính kèm hình ảnh và tài liệu
- Giải thích đáp án
- Validation đáp án đúng

---

### 2.11. `training.test.option` - Đáp án trắc nghiệm

**File:** `models/training_test.py`

**Mô tả:** Quản lý các đáp án cho câu hỏi trắc nghiệm

**Chức năng chính:**

- Tạo đáp án cho câu hỏi
- Đánh dấu đáp án đúng
- Sắp xếp thứ tự đáp án

---

### 2.12. `training.test.result` - Kết quả bài kiểm tra

**File:** `models/training_test.py`

**Mô tả:** Lưu trữ kết quả làm bài thi của học viên

**Kế thừa Mixin:**

```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**Chức năng chính:**

- Theo dõi thời gian làm bài
- Tính điểm tự động
- Xác định đạt/không đạt
- Xếp loại (A, B, C, D, F)
- Quản lý trạng thái (đang làm, đã nộp, đã chấm)
- Gửi kết quả qua email
- Tự động cấp chứng chỉ khi đạt

---

### 2.13. `training.test.answer` - Câu trả lời

**File:** `models/training_test.py`

**Mô tả:** Lưu câu trả lời của học viên cho từng câu hỏi

**Chức năng chính:**

- Lưu đáp án trắc nghiệm (1 hoặc nhiều đáp án)
- Lưu câu trả lời tự luận
- Chấm điểm
- Nhận xét của giảng viên

---

### 2.14. `training.certificate` - Chứng chỉ đào tạo

**File:** `models/training_certificate.py`

**Mô tả:** Quản lý chứng chỉ hoàn thành khóa học

**Kế thừa Mixin:**

```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**Chức năng chính:**

- Tự động sinh số chứng chỉ
- Quản lý hiệu lực (ngày hết hạn)
- Tạo mã QR code cho xác thực
- In chứng chỉ PDF
- Gửi chứng chỉ qua email
- Xếp loại (xuất sắc, giỏi, khá, trung bình)
- Kiểm tra tính hợp lệ và hết hạn

---

### 2.15. `training.certificate.template` - Mẫu chứng chỉ

**File:** `models/training_certificate.py`

**Mô tả:** Quản lý mẫu thiết kế chứng chỉ

**Chức năng chính:**

- Tạo layout HTML cho chứng chỉ
- Hỗ trợ các biến động (tên học viên, khóa học, điểm số, v.v.)
- Upload logo và hình nền
- Thiết lập lề và kích thước trang

---

### 2.16. `training.feedback` - Khảo sát hài lòng

**File:** `models/training_feedback.py`

**Mô tả:** Thu thập đánh giá từ học viên về khóa học

**Kế thừa Mixin:**

```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**Chức năng chính:**

- Đánh giá tổng quan (1-5 sao)
- Đánh giá chi tiết (nội dung, giảng viên, tài liệu, tổ chức)
- Góp ý và đề xuất cải thiện
- Thống kê điểm trung bình

---

### 2.17. `training.reminder` - Nhắc nhở đào tạo

**File:** `models/training_reminder.py`

**Mô tả:** Tự động gửi nhắc nhở về các sự kiện đào tạo

**Kế thừa Mixin:**

```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**Chức năng chính:**

- Nhiều loại nhắc nhở (buổi học, đăng ký, deadline)
- Lên lịch gửi nhắc nhở
- Gửi qua email hoặc thông báo
- Theo dõi trạng thái gửi (chờ gửi, đã gửi, đã hủy)
- Tự động tạo nhắc nhở từ buổi học/đăng ký

---

### 2.18. `training.approval.config` - Cấu hình phê duyệt

**File:** `models/training_approval.py`

**Mô tả:** Cấu hình quy trình phê duyệt đào tạo

**Chức năng chính:**

- Thiết lập điều kiện áp dụng (danh mục, thời lượng, chi phí)
- Định nghĩa các bước phê duyệt
- Kích hoạt/vô hiệu hóa cấu hình

---

### 2.19. `training.approval.step` - Bước phê duyệt

**File:** `models/training_approval.py`

**Mô tả:** Định nghĩa từng bước trong quy trình phê duyệt

**Chức năng chính:**

- Xác định người phê duyệt (quản lý, HR, giám đốc, người cụ thể)
- Cài đặt quyền chỉnh sửa
- Yêu cầu ghi chú
- Sắp xếp thứ tự các bước

---

### 2.20. `training.approval` - Phê duyệt đào tạo

**File:** `models/training_approval.py`

**Mô tả:** Quản lý quy trình phê duyệt đăng ký đào tạo

**Kế thừa Mixin:**

```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**Chức năng chính:**

- Liên kết với đăng ký khóa học
- Quản lý các bước phê duyệt
- Theo dõi trạng thái tổng thể
- Xử lý phê duyệt/từ chối
- Tạo hoạt động cho người phê duyệt tiếp theo

---

### 2.21. `training.approval.line` - Chi tiết bước phê duyệt

**File:** `models/training_approval.py`

**Mô tả:** Lưu trữ trạng thái từng bước phê duyệt cụ thể

**Chức năng chính:**

- Gán người phê duyệt cho từng bước
- Theo dõi trạng thái (chờ, đang chờ duyệt, đã duyệt, từ chối)
- Lưu lý do từ chối
- Ghi chú và thời gian phê duyệt

---

## 🔧 3. CÁC MODEL MỞ RỘNG (EXTEND) - 3 MODELS

**Đặc điểm:** Các model này kế thừa (\_inherit) từ các model ĐÃ TẠO TRONG MODULE để bổ sung thêm chức năng, KHÔNG tạo bảng database mới.

### 3.1. `training.enrollment` (Mở rộng - Approval)

**File:** `models/training_approval.py` (class `TrainingEnrollmentApproval`)

**Kế thừa:**

```python
_inherit = 'training.enrollment'
```

**Mục đích:** Thêm chức năng phê duyệt cho đăng ký khóa học

**Các trường bổ sung:**

- `approval_id` - Liên kết với quy trình phê duyệt
- `approval_state` - Trạng thái phê duyệt (related field)

**Chức năng thêm:**

- `action_submit_approval()` - Gửi yêu cầu phê duyệt
- `action_view_approval()` - Xem chi tiết phê duyệt

---

### 3.2. `training.session` (Mở rộng - Reminder)

**File:** `models/training_reminder.py` (class `TrainingSessionReminder`)

**Kế thừa:**

```python
_inherit = 'training.session'
```

**Mục đích:** Thêm chức năng nhắc nhở cho buổi học

**Các trường bổ sung:**

- `reminder_ids` - Danh sách nhắc nhở
- `reminder_count` - Số lượng nhắc nhở
- `auto_create_reminder` - Tự động tạo nhắc nhở

**Chức năng thêm:**

- `action_view_reminders()` - Xem danh sách nhắc nhở
- `action_create_reminder()` - Tạo nhắc nhở thủ công
- `_create_session_reminder()` - Tự động tạo nhắc nhở

---

### 3.3. `training.enrollment` (Mở rộng - Reminder)

**File:** `models/training_reminder.py` (class `TrainingEnrollmentReminder`)

**Kế thừa:**

```python
_inherit = 'training.enrollment'
```

**Mục đích:** Thêm chức năng nhắc nhở cho đăng ký khóa học

**Các trường bổ sung:**

- `reminder_ids` - Danh sách nhắc nhở

**Chức năng thêm:**

- Override `create()` - Tự động tạo nhắc nhở khi đăng ký mới
- `_create_enrollment_reminder()` - Tạo nhắc nhở phê duyệt

---

## 📊 THỐNG KÊ TỔNG HỢP

| Loại Model                    | Số lượng | Tạo bảng DB mới? |
| ----------------------------- | -------- | ---------------- |
| **1. Kế thừa từ Odoo**        | 1        | ❌ Không         |
| **2. Model mới tạo**          | 19       | ✅ Có            |
| **3. Model mở rộng (extend)** | 3        | ❌ Không         |
| **Tổng cộng**                 | **23**   | 19 bảng mới      |

### Phân loại theo nhóm chức năng:

1. **Quản lý nhân sự** (1 model): `hr.employee`
2. **Khóa học** (2 models): `training.course`, `training.course.category`
3. **Giảng viên & Tài liệu** (2 models): `training.trainer`, `training.material`
4. **Kế hoạch & Nhu cầu** (2 models): `training.plan`, `training.need`
5. **Đăng ký & Buổi học** (2 models + 2 extend): `training.enrollment`, `training.session` + 2 mở rộng
6. **Kiểm tra** (5 models): `training.test`, `training.test.question`, `training.test.option`, `training.test.result`, `training.test.answer`
7. **Chứng chỉ** (2 models): `training.certificate`, `training.certificate.template`
8. **Đánh giá** (1 model): `training.feedback`
9. **Nhắc nhở** (1 model): `training.reminder`
10. **Phê duyệt** (4 models + 1 extend): `training.approval.config`, `training.approval.step`, `training.approval`, `training.approval.line` + 1 mở rộng

### Bảng so sánh loại kế thừa:

| Loại kế thừa           | Ví dụ                                                       | Tạo bảng DB? | Mục đích                            |
| ---------------------- | ----------------------------------------------------------- | ------------ | ----------------------------------- |
| **Inherit model Odoo** | `_inherit = 'hr.employee'`                                  | ❌           | Mở rộng model có sẵn của Odoo       |
| **New model + Mixin**  | `_name = 'training.course'`<br>`_inherit = ['mail.thread']` | ✅           | Tạo model mới với tính năng Chatter |
| **Extend own model**   | `_inherit = 'training.enrollment'`                          | ❌           | Thêm chức năng cho model đã tạo     |

---

## 🔗 LIÊN KẾT VỚI MODULE ODOO CÓ SẴN

Module training_management tích hợp với các module Odoo chuẩn:

1. **hr (Human Resources)**:

   - ✅ **Kế thừa:** `hr.employee` (mở rộng model)
   - 🔗 **Liên kết:** `hr.department`

2. **mail**:

   - ✅ **Kế thừa Mixin:** `mail.thread` và `mail.activity.mixin` (20/23 models)
   - 🔗 **Chức năng:** Chatter, Activities, Email templates

3. **calendar**:

   - 🔗 **Liên kết:** `calendar.event` (cho quản lý buổi học)

4. **base**:
   - 🔗 **Liên kết:** `res.users`, `res.company`, `ir.attachment`

### ⚠️ LƯU Ý QUAN TRỌNG:

**Về Mixin (`mail.thread`, `mail.activity.mixin`):**

- Mixin **KHÔNG PHẢI** là model độc lập
- Mixin chỉ cung cấp **chức năng** (methods, fields) để tái sử dụng
- Khi model kế thừa Mixin → Model đó có thêm chức năng, KHÔNG tạo quan hệ kế thừa model
- **VD:** `training.course` kế thừa `mail.thread` → Có Chatter nhưng KHÔNG phải là "con" của model nào cả

**Phân biệt 2 loại kế thừa:**

| Kiểu                  | Code                         | Ý nghĩa                 | Tạo bảng?           |
| --------------------- | ---------------------------- | ----------------------- | ------------------- |
| **Model Inheritance** | `_inherit = 'hr.employee'`   | Mở rộng model có sẵn    | ❌                  |
| **Mixin Inheritance** | `_inherit = ['mail.thread']` | Thêm chức năng từ Mixin | ✅ (nếu có `_name`) |

---

**Ngày cập nhật:** 15/11/2025
**Module version:** 18.0.1.0.0
