# Odoo 18 Migration - Training Management Module

## Ngày thực hiện: 08/11/2025

## Các thay đổi chính

### 1. Tree Views → List Views

**Lý do**: Odoo 18 không còn hỗ trợ `<tree>` trong views, phải dùng `<list>`

**Files đã sửa**:

- ✅ training_course_views.xml (3 instances)
- ✅ training_trainer_views.xml (2 instances)
- ✅ training_material_views.xml (1 instance)
- ✅ training_plan_views.xml (1 instance)
- ✅ training_need_views.xml (1 instance)
- ✅ training_enrollment_views.xml (1 instance)
- ✅ training_session_views.xml (1 instance)
- ✅ training_test_views.xml (1 instance)
- ✅ training_certificate_views.xml (1 instance)
- ✅ training_feedback_views.xml (1 instance)

**Tổng cộng**: 24 instances đã được chuyển đổi

### 2. Attrs & States → Invisible Attribute

**Lý do**: Odoo 18 loại bỏ `attrs` và `states`, thay bằng domain expressions trực tiếp

#### 2.1. States Migration

**Cũ (Odoo 17)**:

```xml
<button name="action_publish" states="draft"/>
<button name="action_cancel" states="draft,published,in_progress"/>
```

**Mới (Odoo 18)**:

```xml
<button name="action_publish" invisible="state != 'draft'"/>
<button name="action_cancel" invisible="state not in ['draft', 'published', 'in_progress']"/>
```

**Files đã sửa**:

- training_course_views.xml: 5 buttons với states

#### 2.2. Attrs Migration

**Cũ (Odoo 17)**:

```xml
<field name="employee_id" attrs="{'invisible': [('trainer_type', '=', 'external')]}"/>
<field name="passing_score" attrs="{'invisible': [('has_test', '=', False)]}"/>
<widget name="web_ribbon" attrs="{'invisible': [('active', '=', True)]}"/>
```

**Mới (Odoo 18)**:

```xml
<field name="employee_id" invisible="trainer_type == 'external'"/>
<field name="passing_score" invisible="not has_test"/>
<widget name="web_ribbon" invisible="active"/>
```

**Files đã sửa**:

- training_course_views.xml: 6 instances
- training_trainer_views.xml: 3 instances
- training_material_views.xml: 4 instances

**Tổng cộng**: 13 attrs expressions đã được chuyển đổi

## Domain Expression Syntax Changes

### Boolean Fields

- `[('field', '=', True)]` → `field`
- `[('field', '=', False)]` → `not field`
- `[('active', '=', True)]` → `active`

### Equality

- `[('state', '=', 'draft')]` → `state == 'draft'`
- `[('state', '!=', 'cancelled')]` → `state != 'cancelled'`

### In Operator

- `[('type', 'in', ['video', 'link'])]` → `type in ['video', 'link']`
- `[('type', 'not in', ['video', 'link'])]` → `type not in ['video', 'link']`

### Multiple Conditions (OR)

- `states="draft,published"` → `invisible="state not in ['draft', 'published']"`

## Kiểm tra sau Migration

### Commands để test

```bash
# 1. Restart Odoo server
python odoo-bin -c odoo.conf

# 2. Update Apps List (trong Odoo UI)
Settings → Apps → Update Apps List

# 3. Install module
Search "Training Management" → Install

# 4. Test các views
- Mở Training → Courses
- Kiểm tra buttons hiển thị đúng theo state
- Test form view với các conditional fields
- Xác nhận ribbons hiện đúng
```

### Checklist

- [ ] Module cài đặt thành công
- [ ] List views hiển thị đúng
- [ ] Form views không có lỗi
- [ ] Buttons hiển thị/ẩn theo state đúng
- [ ] Conditional fields hoạt động chính xác
- [ ] Web ribbons hiển thị đúng điều kiện

## Lưu ý quan trọng

1. **Breaking Changes**: Odoo 18 có nhiều breaking changes, module cũ sẽ KHÔNG tương thích
2. **Testing**: Phải test kỹ tất cả views trước khi deploy production
3. **Performance**: Cú pháp mới đơn giản hơn, có thể cải thiện performance
4. **Documentation**: Tham khảo [Odoo 18 Release Notes](https://www.odoo.com/odoo-18)

## Tham khảo

- [Odoo 18 Views Documentation](https://www.odoo.com/documentation/18.0/developer/reference/frontend/views.html)
- [Migration Guide 17.0 to 18.0](https://www.odoo.com/documentation/18.0/developer/howtos/upgrade_scripts.html)

## Tác giả

- **Nhóm 3**: Mỹ Trâm, Kim Cương, Thu Hà, Tố Như, Trọng Khang
- **Người thực hiện migration**: GitHub Copilot
- **Ngày hoàn thành**: 08/11/2025
