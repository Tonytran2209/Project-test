# Write discoverable code

Quy ước giúp người và agent tìm đúng code, lần theo luồng dữ liệu và sửa đúng phạm vi trong Outreach Operations.

## Không đổi tên hàng loạt

Không rename toàn bộ hàm chỉ để đồng bộ hình thức. Các tên hiện tại như `prepare_connect_entries`, `classify_message_direction`, `get_prepared_message_batch` và `renderConnectMatchPreview` đã mô tả đúng công việc.

Chỉ đổi tên khi tên sai nghĩa, quá chung chung hoặc dễ nhầm với hàm khác. Khi rename, tìm mọi nơi gọi, import và test; sửa trong một thay đổi nhỏ rồi kiểm tra lại. Không tự đổi API route, tên bảng/cột, account ID, biến môi trường, service label hoặc đường dẫn script đang dùng trên máy worker.

## Tag tìm kiếm theo layer và feature

Dùng hai tag comment ngay trước hàm hoặc nhóm hàm cùng trách nhiệm:

```js
// @layer presentation
// @feature connect
function renderConnectMatchPreview() { /* ... */ }
```

```python
# @layer business
# @feature replies
def classify_message_direction(...):
    ...
```

Ba giá trị layer thống nhất:

- `presentation`: render giao diện, nhận sự kiện, ánh xạ request/response tại biên API. Không dùng để gắn nhãn mọi hàm trong frontend.
- `business`: validation, matching, phân loại người gửi, quy tắc tính toán; có thể nằm ở frontend hoặc Python.
- `database`: đọc/ghi Supabase, thực thi truy vấn hoặc RPC. Không gắn nhãn này cho hàm chỉ vì nó nằm trong file `_store.py`.

Feature dùng từ vựng cố định: `connect`, `acceptance`, `recipients`, `messages`, `replies`, `campaigns`, `accounts`. Chọn theo trách nhiệm thực tế, không theo nơi gọi tình cờ.

Tag chỉ là chỉ dẫn tìm kiếm, không phải ID duy nhất, không tạo thêm layer runtime và không chứng minh code đã được tách kiến trúc. Hàm điều phối trộn validation, browser và lưu dữ liệu không nên được gắn đại một layer; cần mô tả luồng hoặc tách trách nhiệm trước. Chưa đánh dấu cả file nếu các hàm thuộc nhiều layer.

Lần áp dụng thử đánh dấu các điểm vào tiêu biểu của Connect và Replies, không rename hàm hoặc thay đổi hành vi. Tìm layer và feature độc lập; đọc cặp tag cạnh nhau để xác nhận đúng chức năng:

```sh
rg -n -A 2 '@layer business' app frontend
rg -n -B 1 -A 1 '@feature replies' app frontend
```

## Đặt tên theo hành động và đối tượng

- Python dùng `snake_case`; JavaScript dùng `camelCase`. Giữ quy ước của module hiện có.
- Tên hàm nêu hành động và đối tượng nghiệp vụ: `prepare_connect_entries`, `queue_message_batch`, `classify_message_direction`.
- Dùng cùng từ vựng xuyên suốt: campaign, connect batch, message batch, prospect, account, reply, conversation.
- Phân biệt `connect_job_id`, `message_batch_id`, `prospect_id`, `account_id`; tránh `id` hoặc `data` nếu có thể hiểu thành nhiều loại trong cùng luồng.
- Không tạo tên kiểu `handleData`, `processStuff`, `helper2`, `newLogic` hoặc `fixReply`. Helper ngắn như `_utc_now` vẫn phù hợp khi phạm vi và mục đích rõ ràng.
- Không thêm tiền tố dài lặp lại thông tin module vào mọi helper nội bộ.

## Làm rõ tác dụng phụ

- `parse`, `normalize`, `classify`, `build`: biến đổi hoặc phân loại dữ liệu; không ngầm ghi DB hay điều khiển browser.
- `load`, `fetch`, `list`: đọc dữ liệu; `render`: cập nhật giao diện.
- `save`, `create`, `queue`, `send`, `delete`, `prune`: chỉ rõ loại thay đổi được thực hiện.
- Nếu một luồng có nhiều tác dụng phụ, mô tả ngắn trong docstring: đọc từ đâu, ghi vào đâu, có gửi tin thật hoặc thay đổi trạng thái LinkedIn không.
- Tách việc lấy dữ liệu, xác định role, lưu dữ liệu và render UI để có thể kiểm tra độc lập.

## Bản đồ code hiện tại

| Khu vực | Điểm bắt đầu |
| --- | --- |
| UI, sự kiện và gọi API | `frontend/index.html`, `frontend/app.js` |
| Parse và preview URL–company | `frontend/connect-input.js`, `app/outreach_connect_input.py` |
| API | `backend/main.py` |
| Connect | `app/outreach_job_store.py`, `app/outreach_scheduler.py`, `outreach_connect_worker.py` |
| Acceptance | `app/outreach_acceptance_store.py`, `app/linkedin_acceptance_checker.py`, `outreach_acceptance_worker.py` |
| Lịch recheck Acceptance | `app/outreach_acceptance_schedule.py`, `app/outreach_acceptance_recheck.py`, `git-meta/acceptance_schedule_service.sh` |
| Recipients | `app/outreach_accepted_pool_store.py`, `app/outreach_message_preparation_store.py` |
| Message template và queue | `app/linkedin_message_template.py`, `app/outreach_message_company.py`, `app/outreach_message_queue_store.py` |
| Gửi tin nhắn | `app/outreach_message_batch_executor.py`, `app/outreach_message_executor.py`, `outreach_message_worker.py` |
| Quét và phân vai Replies | `outreach_reply_check_worker.py`, `app/outreach_reply_direction.py` |
| Đối chiếu URL Replies với target đã gửi | `app/outreach_reply_identity.py` |
| Lưu Replies và yêu cầu scan | `app/outreach_reply_store.py`, `app/outreach_reply_check_requests.py` |
| Gửi trả lời | `app/outreach_reply_send_store.py`, `outreach_reply_send_worker.py` |
| Account và session | `app/outreach_account_pool.py`, `app/outreach_session_status.py`, `outreach_session_worker.py` |
| Campaign performance | `app/outreach_campaign_performance_store.py` |
| Dịch vụ Replies trên Mac | `git-meta/reply_check_schedule_service.sh`, `git-meta/reply_send_workers_service.sh` |

`git-meta` chỉ giữ script và hướng dẫn dịch vụ worker; không tạo lại bản sao `app`, `backend` hoặc `frontend` trong đó. Cập nhật bảng này nếu chuyển module hoặc đổi trách nhiệm của module.

## Giữ cấu trúc dễ tìm

- Một module tập trung vào một trách nhiệm nghiệp vụ; mở rộng module hiện có trước khi tạo helper hoặc abstraction mới.
- Nếu tách `frontend/app.js`, tách theo feature và cập nhật thứ tự nạp script, nơi gọi và test. Không vừa tách module vừa rename hàng loạt trong cùng thay đổi.
- Docstring và comment giải thích ràng buộc, quyết định và trường hợp biên; không diễn giải lại từng dòng code.
- Không thêm lời giải thích kỹ thuật vào UI nếu người dùng không yêu cầu. Tài liệu và comment là nơi lưu thông tin đó.
- Giữ test tự động độc lập browser/DB thật khi có thể. Script mở LinkedIn, gửi tin thật hoặc sửa dữ liệu cần cảnh báo tác dụng phụ rõ ràng; không chạy chúng như một bước kiểm tra thông thường.

## Cách tìm và kiểm tra trước khi sửa

Tìm theo tên nghiệp vụ, API route hoặc định danh UI, rồi lần theo nơi gọi:

```sh
rg -n 'classify_message_direction|prepare_connect_entries' app frontend
rg -n '/api/outreach/reply-check' backend frontend
rg -n 'outreachReplyCheckButton' frontend
```

Sau khi thay đổi, tìm lại tên cũ, kiểm tra nơi gọi và chạy các test liên quan. Các lệnh sau chỉ kiểm tra cú pháp và test JavaScript tự động, không gửi tin:

```sh
node --check frontend/app.js
node --test test_connect_company_input.cjs test_reply_account_tabs.cjs test_settings_removed.cjs
python3 -m unittest test_outreach_cleanup test_connect_company_input test_message_company test_outreach_accounts
git diff --check
```

Không dùng chạy toàn bộ `test*.py` một cách mù quáng: repo còn test thủ công có thể gửi tin LinkedIn thật, ví dụ `test_message_account_02_profile_guard.py`. Test local qua không đồng nghĩa đã xác minh worker hoặc database production.
