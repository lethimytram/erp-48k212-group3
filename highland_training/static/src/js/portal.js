/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";

// Exam Timer
document.addEventListener('DOMContentLoaded', function() {
    const examForm = document.querySelector('form[action*="/my/exam/"]');
    if (examForm && examForm.dataset.duration) {
        let timeLeft = parseInt(examForm.dataset.duration) * 60; // Convert to seconds
        
        const timerDisplay = document.createElement('div');
        timerDisplay.className = 'alert alert-warning position-fixed';
        timerDisplay.style.top = '10px';
        timerDisplay.style.right = '10px';
        timerDisplay.style.zIndex = '9999';
        document.body.appendChild(timerDisplay);
        
        const countdown = setInterval(() => {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerDisplay.innerHTML = `<i class="fa fa-clock-o"></i> Thời gian còn lại: ${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            if (timeLeft <= 0) {
                clearInterval(countdown);
                alert(_t('Hết giờ! Bài thi sẽ tự động nộp.'));
                examForm.submit();
            }
            timeLeft--;
        }, 1000);
    }
});

// Confirm before submit exam
const submitExamBtn = document.querySelector('button[type="submit"][form*="exam"]');
if (submitExamBtn) {
    submitExamBtn.addEventListener('click', function(e) {
        if (!confirm(_t('Bạn có chắc muốn nộp bài? Bạn sẽ không thể chỉnh sửa sau khi nộp.'))) {
            e.preventDefault();
        }
    });
}
