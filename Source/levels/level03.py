import time
import tracemalloc
import heapq


def ucs(start, goal, graph):
    """
    Thuật toán tìm kiếm theo chi phí đồng nhất
    """
    nodes_expanded = 0

    # Bắt đầu đo thời gian và bộ nhớ để đánh giá hiệu suất thuật toán
    tracemalloc.start()
    start_time = time.perf_counter()

    # Hàng đợi ưu tiên với cấu trúc (cost, counter, node, path, actual_cost)
    # - cost: chi phí ưu tiên để sắp xếp trong hàng đợi
    # - counter: bộ đếm để đảm bảo tính ổn định khi chi phí bằng nhau
    # - node: nút hiện tại đang xét
    # - path: đường đi từ điểm bắt đầu đến nút hiện tại
    # - actual_cost: chi phí thực tế tích lũy để đến nút này
    frontier = [(0, 0, start, [start], 0)]

    # Tập hợp các nút đã khám phá để tránh xét lại
    explored = set()
    counter = 1

    while frontier:
        # Lấy nút có chi phí thấp nhất từ hàng đợi
        priority, _, current, path, actual_cost = heapq.heappop(frontier)
        nodes_expanded += 1

        # Kiểm tra xem đã đến đích chưa
        if current == goal:
            end_time = time.perf_counter()
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            # Trả về thông tin chi tiết về đường đi tìm được
            return {
                'path': path,  # Danh sách các nút trên đường đi
                'nodes_expanded': nodes_expanded,  # Số nút đã khám phá
                'time_ms': (end_time - start_time) * 1000,  # Thời gian thực thi (ms)
                'memory_kb': peak_mem / 1024,  # Bộ nhớ tối đa đã sử dụng (KB)
                'cost': actual_cost  # Tổng chi phí thực tế của đường đi
            }

        # Bỏ qua nút hiện tại nếu đã khám phá trước đó
        if current in explored:
            continue

        # Đánh dấu nút hiện tại đã được khám phá
        explored.add(current)

        # Xét tất cả các nút kề với nút hiện tại
        for neighbor in graph[current]:
            if neighbor not in explored:
                step_cost = calculate_cost(current, neighbor)
                new_actual_cost = actual_cost + step_cost

                # heuristic = manhattan_distance(neighbor, goal)
                # priority = new_actual_cost + heuristic
                priority = new_actual_cost

                # Thêm nút kề vào hàng đợi ưu tiên
                heapq.heappush(frontier,
                               (priority, counter, neighbor, path + [neighbor], new_actual_cost))
                counter += 1  # Tăng bộ đếm để đảm bảo tính ổn định khi sắp xếp

    # Nếu không tìm thấy đường đi đến đích
    end_time = time.perf_counter()
    tracemalloc.stop()
    return None


def manhattan_distance(a, b):
    """
    Tính khoảng cách Manhattan giữa hai điểm

    Khoảng cách Manhattan là tổng của hiệu tuyệt đối giữa các tọa độ,
    phù hợp cho di chuyển theo lưới (lên, xuống, trái, phải)
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def calculate_cost(next_node, goal):
    """
    Hàm tính chi phí cho Ma Cam (Orange Ghost)

    Chi phí được tính dựa trên:
    - Khoảng cách đến đích (Pacman)
    - Khoảng cách đến trung tâm bản đồ
    - Yếu tố rủi ro tùy thuộc vào vị trí

    Ma Cam thích di chuyển ở vùng ngoại vi và tránh trung tâm
    khi có thể, thể hiện đặc tính rụt rè hơn so với các ma khác
    """
    # Tính khoảng cách đến đích (Pacman)
    distance_to_goal = manhattan_distance(next_node, goal)

    # Xác định trung tâm bản đồ
    map_center = (14, 14)

    # Tính khoảng cách đến trung tâm bản đồ
    center_distance = manhattan_distance(next_node, map_center)

    # Tính yếu tố rủi ro - càng gần trung tâm càng nguy hiểm
    # Giá trị từ 5 đến 10, giảm dần khi xa trung tâm
    risk_factor = 10 - min(center_distance / 2, 5)

    # Công thức tính chi phí tổng hợp:
    # - Chi phí cơ bản là 1
    # - Phần trăm của yếu tố rủi ro (càng cao càng tránh)
    # - Phần trăm của khoảng cách đến đích (ưu tiên nhẹ cho đường đi ngắn)
    return 1 + (risk_factor / 20) + (distance_to_goal / 100)


def orange_ghost_path(ghost_pos, pacman_pos, graph):
    """
    Chiến lược của Ma Cam: Sử dụng thuật toán Uniform Cost Search với hàm
    chi phí đặc biệt để tìm đường đến Pacman.

    Đặc điểm của Ma Cam trong Pac-Man:
    - Thận trọng hơn so với Ma Đỏ
    - Ưu tiên di chuyển ở khu vực ngoại vi, tránh trung tâm bản đồ
    - Có xu hướng "lần" theo Pacman thay vì tấn công trực diện

    Hàm này sử dụng UCS để tìm đường đi có chi phí thấp nhất theo định nghĩa
    chi phí riêng của Ma Cam.
    """
    # Kiểm tra trường hợp đặc biệt: Ma đã ở cùng vị trí với Pacman
    if ghost_pos == pacman_pos:
        return []  # Không cần đường đi vì đã đến đích

    result = ucs(ghost_pos, pacman_pos, graph)

    # Xử lý kết quả tìm kiếm
    if result:
        print(f"Orange ghost path found")
        print("Path:", result['path'])  # Danh sách các vị trí trên đường đi
        print("Nodes expanded:", result['nodes_expanded'])  # Số nút đã xét trong quá trình tìm kiếm
        print("Time (ms):", round(result['time_ms'], 3))  # Thời gian thực thi (làm tròn 3 chữ số)
        print("Memory (KB):", round(result['memory_kb'], 2))  # Lượng bộ nhớ sử dụng (làm tròn 2 chữ số)
        print("Path cost:", result['cost'])  # Tổng chi phí đường đi
        return result['path']
    else:
        print(f"No path found from ghost{ghost_pos} to pacman{pacman_pos}.\n")
        return []


def escape_path_for_powerup(ghost_pos, pacman_pos, graph):
    """
    Tìm đường thoát cho Ma Cam khi Pacman đã ăn năng lượng (power pellet).

    Khi Pacman ăn năng lượng:
    - Ma trở nên dễ bị tổn thương và cần tránh Pacman
    - Ma Cam là ma rụt rè nhất nên chạy xa hơn so với các ma khác
    - Sử dụng UCS nhưng với ưu tiên ngược để tối đa hóa khoảng cách

    Chiến lược thoát:
    - Tìm đường đi đến vị trí có khoảng cách an toàn rất xa từ Pacman
    - Ưu tiên đường đi dẫn đến khu vực ngoại vi và góc xa của bản đồ
    """
    # Xác định khoảng cách an toàn tối thiểu cần đạt được
    # safe_distance = 8  # Khoảng cách an toàn tùy ý
    safe_distance = 50  # Khoảng cách an toàn lớn hơn cho Ma Cam do tính cách rụt rè

    # Bắt đầu đo thời gian và bộ nhớ
    tracemalloc.start()
    start_time = time.perf_counter()

    # Hàng đợi ưu tiên với (priority, counter, node, path, distance)
    frontier = [(0, 0, ghost_pos, [ghost_pos], 0)]
    explored = set()
    counter = 1

    while frontier:
        # Lấy nút có độ ưu tiên cao nhất từ hàng đợi
        _, _, current, path, _ = heapq.heappop(frontier)

        # Kiểm tra xem đã đạt được khoảng cách an toàn chưa
        distance_to_pacman = manhattan_distance(current, pacman_pos)
        if distance_to_pacman >= safe_distance:
            # Đã đạt khoảng cách an toàn, kết thúc tìm kiếm
            end_time = time.perf_counter()
            tracemalloc.stop()
            return path

        # Bỏ qua nút đã khám phá
        if current in explored:
            continue

        explored.add(current)

        # Xét tất cả các nút kề
        for neighbor in graph[current]:
            if neighbor not in explored:
                # Tính ưu tiên dựa trên việc tăng khoảng cách từ Pacman
                # Giá trị âm vì chúng ta muốn tối đa hóa khoảng cách
                new_distance = manhattan_distance(neighbor, pacman_pos)
                priority = -new_distance  # Âm để ưu tiên nút có khoảng cách lớn hơn

                # Thêm nút kề vào hàng đợi ưu tiên
                heapq.heappush(frontier,
                               (priority, counter, neighbor, path + [neighbor], new_distance))
                counter += 1  # Tăng bộ đếm để đảm bảo tính ổn định

    tracemalloc.stop()
    return []