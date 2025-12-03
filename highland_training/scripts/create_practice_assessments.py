#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để tạo practice assessment cho các học sinh đã đạt lý thuyết
Chạy từ Odoo shell: 
  python odoo-bin shell -c odoo.conf
  >>> from odoo.addons.highland_training.scripts.create_practice_assessments import run
  >>> run(env)
"""

def run(env):
    """Tạo practice assessment cho các enrollment đã đạt lý thuyết"""
    PracticeModel = env['training.practice']
    count = PracticeModel.create_for_passed_enrollments()
    print(f"✅ Đã tạo {count} bản ghi đánh giá thực hành cho các học sinh đạt lý thuyết")
    return count

if __name__ == '__main__':
    print("Script này phải chạy từ Odoo shell")
