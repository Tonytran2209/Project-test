# Outreach Operations frontend

Dashboard cho Connect, Acceptance, Recipients, Messages, Replies và báo cáo Campaigns.

Backend phục vụ thư mục này tại `/dashboard/`. Cấu hình Supabase của trình duyệt nằm trong `config.js` (tham khảo `config.example.js`); không đặt service-role key trong frontend.

Các stylesheet theo workspace được nạp từ `index.html`. Giữ giao diện dropdown tùy chỉnh đồng bộ với Connect; không dùng dropdown native hiển thị trực tiếp.

Worker chạy riêng trên máy có browser profile LinkedIn. Hai script dịch vụ Replies vẫn nằm tại `git-meta/reply_check_schedule_service.sh` và `git-meta/reply_send_workers_service.sh`.
