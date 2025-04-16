import time
import tracemalloc
import heapq


def ucs(start, goal, graph, blocked_positions=None):
    """
    Thuật toán tìm kiếm theo chi phí đồng nhất (Uniform Cost Search)

    Thuật toán này giúp Ghost tìm đường đi tối ưu đến Pac-Man dựa trên một hàm
    chi phí tùy chỉnh. UCS luôn mở rộng nút có chi phí tích lũy thấp nhất, đảm
    bảo tìm được đường đi tối ưu.

    Tham số:
        start: Vị trí bắt đầu của Ghost, dạng tuple (x, y)
        goal: Vị trí của Pac-Man, dạng tuple (x, y)
        graph: Đồ thị mê cung dạng từ điển (dạng dictionary của adjacency list)
        blocked_positions: Danh sách vị trí bị chặn (các ma khác hoặc tường)

    Trả về:
        dict: Thông tin về đường đi tìm được, bao gồm:
            - path: Danh sách các vị trí trên đường đi
            - nodes_expanded: Số nút đã được mở rộng/khám phá
            - time_ms: Thời gian thực thi (miligiây)
            - memory_kb: Bộ nhớ sử dụng (KB)
            - cost: Tổng chi phí của đường đi
        Hoặc None nếu không tìm thấy đường đi
    """
    nodes_expanded = 0

    # Bắt đầu đo thời gian và bộ nhớ để đánh giá hiệu suất thuật toán
    # tracemalloc theo dõi việc sử dụng bộ nhớ, time.perf_counter() đo thời gian chính xác
    tracemalloc.start()
    start_time = time.perf_counter()

    # Hàng đợi ưu tiên với cấu trúc (cost, counter, node, path, actual_cost)
    # Bộ đếm được sử dụng để đảm bảo tính ổn định khi hai nút có cùng chi phí
    frontier = [(0, 0, start, [start], 0)]

    # Từ điển lưu trữ các nút trong frontier cùng chi phí tương ứng
    # Giúp kiểm tra nhanh xem một nút có trong frontier không và chi phí là bao nhiêu
    # Cấu trúc: {nút: chi_phí}
    frontier_dict = {start: 0}

    # Từ điển lưu trữ các nút đã khám phá và chi phí tối ưu đến nút đó
    # Giúp tránh xét lại các nút đã có đường đi tối ưu
    # Cấu trúc: {nút: chi_phí_tối_ưu}
    explored = {}

    # Bộ đếm tăng dần, dùng để đảm bảo ổn định khi so sánh các nút cùng chi phí
    counter = 1

    while frontier:
        # Lấy nút có chi phí thấp nhất từ hàng đợi ưu tiên
        priority, _, current, path, actual_cost = heapq.heappop(frontier)

        # Loại bỏ nút hiện tại khỏi frontier_dict vì đã được xử lý
        if current in frontier_dict:
            del frontier_dict[current]

        # Kiểm tra xem đã đến đích chưa
        if current == goal:
            # Kết thúc đo thời gian và bộ nhớ
            end_time = time.perf_counter()
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # Trả về thông tin chi tiết về đường đi tìm được
            return {
                'path': path,  # Danh sách các vị trí trên đường đi
                'nodes_expanded': nodes_expanded,  # Số nút đã mở rộng trong quá trình tìm kiếm
                'time_ms': (end_time - start_time) * 1000,  # Thời gian thực thi (ms)
                'memory_kb': peak_mem / 1024,  # Lượng bộ nhớ tối đa sử dụng (KB)
                'cost': actual_cost  # Tổng chi phí đường đi
            }

        # Nếu nút đã được khám phá với chi phí tối ưu hơn, bỏ qua
        if current in explored and explored[current] <= actual_cost:
            continue

        # Đánh dấu nút hiện tại đã được khám phá với chi phí mới
        explored[current] = actual_cost
        nodes_expanded += 1

        # Xét tất cả các nút kề với nút hiện tại
        for neighbor in graph[current]:
            # Bỏ qua các vị trí bị chặn
            if neighbor in blocked_positions:
                continue

            # Tính toán chi phí khi di chuyển từ nút hiện tại đến nút kề
            step_cost = calculate_cost(current, neighbor, pacman_pos=goal)
            new_actual_cost = actual_cost + step_cost

            # Chỉ xét nút kề nếu thỏa mãn một trong hai điều kiện:
            # 1. Nút chưa từng được khám phá, hoặc đã tìm được đường đi tốt hơn
            # 2. Nút đang trong frontier nhưng tìm được đường đi tốt hơn
            if (neighbor not in explored or explored[neighbor] > new_actual_cost) and \
                    (neighbor not in frontier_dict or frontier_dict[neighbor] > new_actual_cost):
                # Cập nhật hoặc thêm mới vào frontier
                frontier_dict[neighbor] = new_actual_cost
                heapq.heappush(frontier,
                               (new_actual_cost, counter, neighbor, path + [neighbor], new_actual_cost))
                counter += 1  # Tăng bộ đếm để đảm bảo tính ổn định của hàng đợi ưu tiên

    # Kết thúc quá trình tìm kiếm nếu không tìm thấy đường đi
    end_time = time.perf_counter()
    tracemalloc.stop()
    return None


def manhattan_distance(a, b):
    """
    Tính khoảng cách Manhattan giữa hai điểm

    Khoảng cách Manhattan là tổng của hiệu tuyệt đối giữa các tọa độ tương ứng.
    Phù hợp cho di chuyển theo lưới (lên, xuống, trái, phải) trong không gian 2D.

    Tham số:
        a: Điểm thứ nhất, dạng tuple (x, y)
        b: Điểm thứ hai, dạng tuple (x, y)

    Trả về:
        int: Khoảng cách Manhattan giữa hai điểm
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def calculate_cost(current, neighbor, pacman_pos):
    """
    Hàm tính chi phí cho Ma Cam (Orange Ghost)

    Ma Cam có chiến lược di chuyển đặc biệt:
    - Tránh khu vực trung tâm bản đồ (nơi thường có nhiều nguy hiểm)
    - Duy trì khoảng cách vừa phải với Pac-Man: không quá gần để không
      chạm trán trực tiếp, nhưng cũng không quá xa để có thể theo dõi

    Tham số:
        current: Vị trí hiện tại của Ma Cam, dạng tuple (x, y)
        neighbor: Vị trí kề đang xét, dạng tuple (x, y)
        pacman_pos: Vị trí của Pac-Man, dạng tuple (x, y)

    Trả về:
        float: Chi phí di chuyển đến vị trí kề (càng thấp càng được ưu tiên)
    """
    # Trung tâm bản đồ - nơi Ma Cam muốn tránh
    map_center = (14, 14)

    CENTER_WEIGHT = 10  # Mức độ ưu tiên việc tránh trung tâm
    PACMAN_FOLLOW_WEIGHT = 3  # Mức độ ưu tiên việc duy trì khoảng cách với Pac-Man

    # Càng gần trung tâm, chi phí càng cao -> Ghost sẽ có xu hướng tránh
    center_distance = manhattan_distance(neighbor, map_center)

    # Ước tính khoảng cách tối đa từ bất kỳ điểm nào đến trung tâm
    # Lấy nửa kích thước bản đồ làm chuẩn (bản đồ khoảng 30x32)
    max_possible_distance = max(30, 32) / 2

    # Chuẩn hóa khoảng cách về đoạn [0,1]
    # 0: Đang ở trung tâm, 1: Đang ở rìa bản đồ
    normalized_distance = min(1.0, center_distance / max_possible_distance)

    # Tính chi phí phạt cho vị trí gần trung tâm
    # Sử dụng hàm phi tuyến (1-d)^2:
    # - Khi d=0 (ở trung tâm): Phạt = CENTER_WEIGHT * 1 = 10
    # - Khi d=1 (xa trung tâm): Phạt = CENTER_WEIGHT * 0 = 0
    center_penalty = CENTER_WEIGHT * (1 - normalized_distance) ** 2

    # Khoảng cách hiện tại đến Pac-Man
    pacman_distance = manhattan_distance(neighbor, pacman_pos)

    # Khoảng cách lý tưởng mà Ma Cam muốn duy trì với Pac-Man
    # Không quá gần để tránh đối đầu, không quá xa để không mất dấu
    ideal_distance = 8

    # Chi phí dựa trên độ chênh lệch với khoảng cách lý tưởng
    # Càng khác biệt với 8 ô, chi phí càng cao
    pacman_factor = PACMAN_FOLLOW_WEIGHT * abs(pacman_distance - ideal_distance) / 10

    # Chi phí cơ bản cho mỗi bước di chuyển
    base_cost = 1

    # Tổng chi phí = chi phí cơ bản + chi phí tránh trung tâm + chi phí theo dõi Pac-Man
    # Chi phí càng thấp càng được ưu tiên trong thuật toán UCS
    total_cost = base_cost + center_penalty + pacman_factor

    return total_cost


def orange_ghost_path(ghost_pos, pacman_pos, graph, blocked_positions=[]):
    """
    Xác định đường đi cho Ma Cam theo Pac-Man sử dụng thuật toán UCS

    Chiến lược của Ma Cam:
    - Sử dụng UCS với hàm chi phí đặc biệt để tìm đường đến Pac-Man
    - Di chuyển thận trọng hơn Ma Đỏ, ưu tiên khu vực ngoại vi
    - Có xu hướng "lần" theo Pac-Man thay vì tấn công trực diện

    Tham số:
        ghost_pos: Vị trí hiện tại của Ma Cam, dạng tuple (x, y)
        pacman_pos: Vị trí hiện tại của Pac-Man, dạng tuple (x, y)
        graph: Đồ thị biểu diễn mê cung
        blocked_positions: Danh sách vị trí bị chặn (các ma khác)

    Trả về:
        list: Danh sách các vị trí trên đường đi từ Ma Cam đến Pac-Man
              hoặc danh sách rỗng nếu không tìm thấy đường đi
    """
    # Kiểm tra trường hợp đặc biệt: Ma đã ở cùng vị trí với Pac-Man
    if ghost_pos == pacman_pos:
        return []  # Không cần đường đi vì đã đến đích

    # Gọi thuật toán UCS để tìm đường đi tối ưu
    result = ucs(ghost_pos, pacman_pos, graph, blocked_positions)

    # Xử lý kết quả tìm kiếm
    if result:
        # In thông tin chi tiết về đường đi tìm được
        print(f"Orange ghost path found")
        print("Path:", result['path'])  # Danh sách các vị trí trên đường đi
        print("Nodes expanded:", result['nodes_expanded'])  # Số nút đã xét trong quá trình tìm kiếm
        print("Time (ms):", round(result['time_ms'], 3))  # Thời gian thực thi (làm tròn 3 chữ số)
        print("Memory (KB):", round(result['memory_kb'], 2))  # Lượng bộ nhớ sử dụng (làm tròn 2 chữ số)
        print("Path cost:", result['cost'])  # Tổng chi phí đường đi
        return result['path']
    else:
        # In thông báo nếu không tìm thấy đường đi
        print(f"No path found from ghost{ghost_pos} to pacman{pacman_pos}.\n")
        return []


def escape_path_for_powerup(ghost_pos, pacman_pos, graph):
    """
    Tìm đường thoát cho Ma Cam khi Pac-Man đã ăn năng lượng (power pellet)

    Khi Pac-Man ăn năng lượng:
    - Ma trở nên dễ bị tổn thương và cần tránh Pac-Man
    - Ma Cam là ma rụt rè nhất nên sẽ chạy xa hơn các ma khác
    - Thuật toán tìm đường đi tối ưu để tối đa hóa khoảng cách với Pac-Man

    Chiến lược thoát:
    - Tìm đường đi đến vị trí có khoảng cách an toàn từ Pac-Man
    - Ưu tiên khu vực ngoại vi và các góc xa của bản đồ

    Tham số:
        ghost_pos: Vị trí hiện tại của Ma Cam, dạng tuple (x, y)
        pacman_pos: Vị trí hiện tại của Pac-Man, dạng tuple (x, y)
        graph: Đồ thị biểu diễn mê cung

    Trả về:
        list: Danh sách các vị trí trên đường thoát
              hoặc danh sách rỗng nếu không tìm thấy đường thoát
    """
    # Xác định khoảng cách an toàn tối thiểu cần đạt được
    # Khoảng cách được đặt lớn hơn so với các ma khác để phù hợp với tính cách rụt rè của Ma Cam
    safe_distance = 50

    # Bắt đầu đo thời gian và bộ nhớ
    tracemalloc.start()
    start_time = time.perf_counter()

    # Khởi tạo hàng đợi ưu tiên với cấu trúc (độ_ưu_tiên, bộ_đếm, nút_hiện_tại, đường_đi, khoảng_cách)
    frontier = [(0, 0, ghost_pos, [ghost_pos], 0)]
    explored = set()  # Tập hợp các nút đã khám phá
    counter = 1  # Bộ đếm để đảm bảo tính ổn định của hàng đợi ưu tiên

    while frontier:
        # Lấy nút có độ ưu tiên cao nhất từ hàng đợi
        _, _, current, path, _ = heapq.heappop(frontier)

        # Tính khoảng cách hiện tại đến Pac-Man
        distance_to_pacman = manhattan_distance(current, pacman_pos)

        # Kiểm tra xem đã đạt được khoảng cách an toàn chưa
        if distance_to_pacman >= safe_distance:
            # Đã đạt khoảng cách an toàn, kết thúc tìm kiếm
            end_time = time.perf_counter()
            tracemalloc.stop()
            return path  # Trả về đường đi đến vị trí an toàn

        # Bỏ qua nút đã khám phá
        if current in explored:
            continue

        # Đánh dấu nút hiện tại đã được khám phá
        explored.add(current)

        # Xét tất cả các nút kề
        for neighbor in graph[current]:
            if neighbor not in explored:
                # Tính khoảng cách mới từ nút kề đến Pac-Man
                new_distance = manhattan_distance(neighbor, pacman_pos)

                # Tính độ ưu tiên - lấy giá trị âm vì muốn tối đa hóa khoảng cách
                # (hàng đợi ưu tiên luôn lấy ra phần tử có giá trị nhỏ nhất trước)
                priority = -new_distance

                # Thêm nút kề vào hàng đợi ưu tiên
                heapq.heappush(frontier,
                               (priority, counter, neighbor, path + [neighbor], new_distance))
                counter += 1  # Tăng bộ đếm để đảm bảo tính ổn định

    # Kết thúc tìm kiếm nếu không tìm thấy vị trí an toàn
    tracemalloc.stop()
    return []  # Trả về danh sách rỗng