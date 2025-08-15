# Chỉ snippet thay đổi thứ tự gọi system – trong project thực tế thay trong main_pygame simulation_step:
# Thêm:
#   defs_system(w) đầu vòng
#   item_stack_system(w) sau gather/task
#   blueprint_system + construction_def_system trước storage calc
#   leader_def_system cuối chu kỳ hoặc sau leader_system
#
# (Giữ nguyên code còn lại, vì full main file quá dài; tích hợp theo hướng dẫn)