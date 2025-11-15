# Module Đào tạo nội bộ cho nhân viên

## Thông tin dự án

- **Tên dự án**: Module Đào tạo nội bộ cho nhân viên
- **Nhóm thực hiện**: Nhóm 3 (Mỹ Trâm, Kim Cương, Thu Hà, Tố Như, Trọng Khang)
- **Thời gian**: Tháng 10/2025
- **Người hướng dẫn**: Phạm Viết Phú

## Mô tả

Module quản lý toàn diện hệ thống đào tạo nội bộ cho nhân viên, bao gồm:

- Quản lý khóa học, giảng viên, và tài liệu học
- Lập kế hoạch đào tạo theo phòng ban
- Đăng ký và phê duyệt khóa học
- Tích hợp lịch đào tạo với calendar
- Đánh giá và cấp chứng chỉ
- Khảo sát hài lòng

## Tính năng

### Tính năng 1: Quản lý khóa học, giảng viên và tài liệu

**Người phụ trách**: Mỹ Trâm

### Tính năng 2: Lập kế hoạch đào tạo (training.plan)

**Người phụ trách**: Kim Cương  
**Deadline**: 12/11/2025

### Tính năng 3: Đăng ký và phê duyệt khóa học (training.enrollment)

**Người phụ trách**: Thu Hà  
**Deadline**: 15/11/2025

### Tính năng 4: Quản lý giảng viên và học viên (hr.employee)

**Người phụ trách**: Tố Như  
**Deadline**: 15/11/2025

### Tính năng 5: Tích hợp lịch đào tạo (training.session)

**Người phụ trách**: Trọng Khang  
**Deadline**: 25/11/2025

### Tính năng 6: Thông báo tự động qua email

**Người phụ trách**: Mỹ Trâm  
**Deadline**: 27/11/2025

### Tính năng 7: Dashboard tiến độ

**Người phụ trách**: Kim Cương  
**Deadline**: 30/11/2025

### Tính năng 8-9: Quiz và bài kiểm tra (training.test)

**Người phụ trách**: Thu Hà & Tố Như  
**Deadline**: 15/12/2025

### Tính năng 10-11: Cấp chứng chỉ (training.certificate)

**Người phụ trách**: Trọng Khang  
**Deadline**: 25/12/2025

### Tính năng 12: Khảo sát hài lòng (training.feedback)

**Người phụ trách**: Mỹ Trâm  
**Deadline**: 30/12/2025

## Cài đặt

### Yêu cầu

- Odoo 17.0+
- Python 3.11+
- Module dependencies: hr, mail, calendar, survey, hr_skills

### Các bước cài đặt

1. **Copy module vào thư mục addons**

   ```bash
   cp -r training_management /path/to/odoo/custom_addons/
   ```

2. **Cập nhật danh sách module**

   - Vào Settings → Apps → Update Apps List
   - Tìm kiếm "Training Management"
   - Click Install

3. **Cấu hình ban đầu**
   - Tạo danh mục khóa học
   - Thêm giảng viên
   - Tạo khóa học đầu tiên

## Cấu trúc thư mục

```
training_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── training_course.py          # ✅ Hoàn thành
│   ├── training_trainer.py         # ✅ Hoàn thành
│   ├── training_material.py        # ✅ Hoàn thành
│   ├── training_plan.py            # 🔄 Skeleton
│   ├── training_need.py            # 🔄 Skeleton
│   ├── training_enrollment.py      # 🔄 Skeleton
│   ├── training_session.py         # 🔄 Skeleton
│   ├── training_test.py            # 🔄 Skeleton
│   ├── training_certificate.py     # 🔄 Skeleton
│   ├── training_feedback.py        # 🔄 Skeleton
│   └── hr_employee.py              # 🔄 Skeleton
├── views/
│   ├── training_course_views.xml   # ✅ Hoàn thành
│   ├── training_trainer_views.xml  # ✅ Hoàn thành
│   ├── training_material_views.xml # ✅ Hoàn thành
│   ├── training_plan_views.xml     # 🔄 Basic
│   ├── training_need_views.xml     # 🔄 Basic
│   ├── training_enrollment_views.xml # 🔄 Basic
│   ├── training_session_views.xml  # 🔄 Basic
│   ├── training_test_views.xml     # 🔄 Basic
│   ├── training_certificate_views.xml # 🔄 Basic
│   ├── training_feedback_views.xml # 🔄 Basic
│   └── training_menu_views.xml     # ✅ Hoàn thành
├── security/
│   ├── training_security.xml       # ✅ Hoàn thành
│   └── ir.model.access.csv         # ✅ Hoàn thành
├── data/
│   └── training_data.xml           # ✅ Hoàn thành
└── README.md                        # ✅ File này
```

## Hướng dẫn sử dụng

### Tạo khóa học mới

1. Vào menu **Đào tạo → Khóa học → Khóa học**
2. Click **Create**
3. Điền thông tin:
   - Tên khóa học và mã
   - Chọn danh mục và cấp độ
   - Gán giảng viên
   - Thêm mô tả và mục tiêu
4. Thêm tài liệu trong tab "Tài liệu"
5. Cấu hình đánh giá và chứng chỉ
6. Click **Công bố** để công bố khóa học

### Thêm giảng viên

1. Vào menu **Đào tạo → Khóa học → Giảng viên**
2. Click **Create**
3. Chọn loại giảng viên (Nội bộ/Bên ngoài)
4. Nếu nội bộ: chọn nhân viên từ HR
5. Điền thông tin liên hệ và chuyên môn
6. Lưu

### Upload tài liệu

1. Mở khóa học cần thêm tài liệu
2. Vào tab "Tài liệu"
3. Click **Add a line**
4. Điền tên và chọn loại tài liệu
5. Upload file hoặc nhập URL
6. Đánh dấu "Bắt buộc" nếu cần
7. Lưu

## Quyền truy cập

### Học viên (Trainee)

- Xem danh sách khóa học công bố
- Xem tài liệu khóa học
- Đăng ký khóa học
- Xem lịch học của mình
- Xem chứng chỉ của mình

### Giảng viên (Trainer)

- Tất cả quyền của Học viên
- Chỉnh sửa khóa học của mình
- Thêm/sửa tài liệu
- Xem danh sách học viên
- Chấm điểm và đánh giá

### Quản lý đào tạo (Manager)

- Toàn quyền quản lý tất cả
- Tạo/sửa/xóa khóa học
- Quản lý giảng viên
- Phê duyệt đăng ký
- Cấp chứng chỉ
- Xem báo cáo

## Báo lỗi và đóng góp

Nếu phát hiện lỗi hoặc có đề xuất cải tiến, vui lòng:

1. Tạo issue trên repository
2. Hoặc liên hệ nhóm phát triển

## Giấy phép

LGPL-3

## Tác giả

Nhóm 3:

- Mỹ Trâm
- Kim Cương
- Thu Hà
- Tố Như
- Trọng Khang

---

**Lưu ý**: Module này đang trong quá trình phát triển. Tính năng 1 đã hoàn thiện, các tính năng còn lại đang được triển khai theo kế hoạch.
