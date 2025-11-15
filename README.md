# Hướng dẫn tạo thư mục custom_addons và copy code Odoo

## 1. Tạo thư mục `custom_addons`

Trên máy local, tạo thư mục `custom_addons` để chứa mã nguồn các module Odoo trong project "odoo":

## 2. Copy code Odoo vào thư mục `custom_addons`

Giả sử đã có code Odoo trên GitHub hoặc ở một nơi khác, có thể copy trực tiếp vào thư mục:

```bash
# Nếu đã clone repo từ GitHub
git clone https://github.com/username/repo_name.git ~/custom_addons/repo_name

# Hoặc copy trực tiếp từ thư mục hiện tại
cp -r path_to_your_code/* ~/custom_addons/
```

## 3. Cấu hình Odoo để nhận thư mục `custom_addons`

Chỉnh sửa file cấu hình Odoo (`odoo.conf`) và thêm đường dẫn thư mục:

```ini
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,~/custom_addons
```

Sau khi thực hiện xong, bạn khởi động lại Odoo, các module trong `custom_addons` sẽ được nhận diện và có thể cài đặt.
