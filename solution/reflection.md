# Reflection (≤1 page)

Fill this in before you submit.

**Which fault types were hardest to catch, and why?**

Khó nhất là các lỗi lệch dữ liệu rất nhẹ, nhất là feature drift và embedding drift. Giá trị của chúng có thể nằm sát vùng dữ liệu bình thường nên chỉ dùng một ngưỡng cố định sẽ dễ bỏ sót hoặc báo nhầm. Ở Practice mình bắt được hết lỗi, nhưng sang Private tỷ lệ bắt trúng còn 64,81%. Điều đó cho thấy cách đặt ngưỡng hiện tại vẫn chưa đủ tốt với các lỗi khó hơn.

**What would you change about your cost/coverage tradeoff, if you had another pass?**

Mình gọi đúng một tool cho mỗi sự kiện để có dữ liệu kiểm tra, rồi dùng baseline để quyết định. Practice dùng 180/220 credits; Public dùng 240/220 nên bị trừ điểm vì vượt ngân sách. Nếu làm tiếp, mình sẽ lưu thống kê của các sự kiện đã qua trong `ctx.state` để nhận ra sự thay đổi dần theo thời gian và chỉ gọi thêm kiểm tra khi cần. Mình cũng sẽ thử các ngưỡng trên nhiều luồng khác nhau, thay vì chỉnh theo một bộ Practice. Trước mắt mình giữ ngưỡng thận trọng: Private không có báo động giả và không vượt ngân sách, dù vẫn bỏ sót một số lỗi.
