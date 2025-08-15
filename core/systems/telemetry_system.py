from ..ecs.world import World

def telemetry_system(world: World):
    # Hook dành cho mở rộng (ví dụ: ghi log tick, snapshot memory).
    # Hiện tại profiler đã chạy trong TickManager; có thể thêm logic aggregate custom ở đây sau.
    return
