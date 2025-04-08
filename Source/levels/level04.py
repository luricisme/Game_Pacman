import time
import tracemalloc
import heapq
import math


def astar_search(start, goal, graph):
    nodes_expanded = 0

    # Bắt đầu đo thời gian và bộ nhớ để đánh giá hiệu suất thuật toán
    # tracemalloc theo dõi việc sử dụng bộ nhớ, time.perf_counter() đo thời gian chính xác
    tracemalloc.start()
    start_time = time.perf_counter()

    # Khởi tạo hàng đợi ưu tiên với các thành phần:
    # - f_score: tổng chi phí ước tính (g_score + h_score)
    # - counter: bộ đếm để đảm bảo tính ổn định khi hai nút có cùng f_score
    # - node: nút hiện tại đang xét
    # - path: đường đi từ điểm bắt đầu đến nút hiện tại
    # - g_score: chi phí thực tế từ điểm bắt đầu đến nút hiện tại
    frontier = [(heuristic(start, goal), 0, start, [start], 0)]

    # Tập hợp các nút đã khám phá để tránh xét lại
    explored = set()
    counter = 1

    while frontier:
        # Lấy nút có độ ưu tiên cao nhất (f_score thấp nhất) từ hàng đợi
        _, _, current, path, g_score = heapq.heappop(frontier)
        nodes_expanded += 1

        # Nếu đã đến đích, kết thúc tìm kiếm và trả về kết quả
        if current == goal:
            end_time = time.perf_counter()
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            # Trả về kết quả chi tiết: đường đi, số nút đã mở rộng, thời gian thực thi,
            # lượng bộ nhớ sử dụng và tổng chi phí đường đi
            return {
                'path': path,  # Danh sách các nút trên đường đi
                'nodes_expanded': nodes_expanded,  # Số nút đã khám phá
                'time_ms': (end_time - start_time) * 1000,  # Thời gian thực thi (ms)
                'memory_kb': peak_mem / 1024,  # Bộ nhớ tối đa đã sử dụng (KB)
                'cost': g_score  # Tổng chi phí đường đi
            }

        # Bỏ qua nút hiện tại nếu đã khám phá trước đó
        if current in explored:
            continue

        # Đánh dấu nút hiện tại đã được khám phá
        explored.add(current)

        # Xét tất cả các nút kề với nút hiện tại
        for neighbor in graph[current]:
            if neighbor not in explored:
                # Tính toán chi phí g_score mới khi đi từ nút hiện tại đến nút kề
                new_g_score = g_score + calculate_cost(current, neighbor)

                # Tính toán chi phí heuristic (h_score) từ nút kề đến đích
                h_score = heuristic(neighbor, goal)

                # Tính toán tổng chi phí ước tính (f_score = g_score + h_score)
                f_score = new_g_score + h_score

                # Thêm nút kề vào hàng đợi ưu tiên với các thông tin cần thiết
                heapq.heappush(frontier,
                               (f_score, counter, neighbor, path + [neighbor], new_g_score))
                counter += 1  # Tăng bộ đếm để đảm bảo tính ổn định khi sắp xếp

    # Nếu không tìm thấy đường đi đến đích
    end_time = time.perf_counter()
    tracemalloc.stop()
    return None


def heuristic(current, goal):
    """
    Hàm heuristic kết hợp để ước tính khoảng cách từ vị trí hiện tại đến đích.

    Kết hợp hai phương pháp:
    - Khoảng cách Euclidean: đo khoảng cách đường chim bay, chính xác hơn trong không gian 2D
    - Khoảng cách Manhattan: phù hợp với chuyển động trên lưới vuông góc

    Tỷ lệ kết hợp được điều chỉnh để ưu tiên tính chủ động trong việc tiếp cận mục tiêu.
    """
    # Khoảng cách Euclidean: căn bậc hai của tổng bình phương hiệu tọa độ
    # Mô phỏng đường thẳng trong không gian, cho ước lượng thực tế hơn
    euclidean = math.sqrt((current[0] - goal[0]) ** 2 + (current[1] - goal[1]) ** 2)

    # Khoảng cách Manhattan: tổng giá trị tuyệt đối của hiệu tọa độ
    # Phù hợp cho chuyển động trên lưới (lên, xuống, trái, phải)
    manhattan = abs(current[0] - goal[0]) + abs(current[1] - goal[1])

    # Kết hợp hai khoảng cách với trọng số:
    # - 60% Euclidean: ưu tiên đường đi trực tiếp, giúp ma đỏ chủ động hơn
    # - 40% Manhattan: giúp điều hướng tốt hơn trong môi trường lưới
    return 0.6 * euclidean + 0.4 * manhattan


def calculate_cost(current, next_node):
    """
    Hàm tính chi phí di chuyển từ nút hiện tại đến nút tiếp theo cho Ma Đỏ.

    Ma Đỏ được đặc trưng bởi tính hung hăng và quyết đoán:
    - Luôn tìm đường đi ngắn nhất đến Pacman
    - Không quan tâm đến rủi ro hay an toàn
    - Sử dụng hàm chi phí đơn giản để tối ưu khoảng cách
    """
    # Chi phí cơ bản cho mỗi bước di chuyển là 1
    # Hàm chi phí đơn giản vì Ma đỏ không quan tâm đến yếu tố khác
    # ngoài việc đến được Pacman nhanh nhất có thể
    base_cost = 1

    # Không có chi phí bổ sung cho bất kỳ loại di chuyển nào
    # Khác với các ma khác có thể tránh khu vực nguy hiểm hoặc có chiến lược phức tạp hơn
    return base_cost


def red_ghost_path(ghost_pos, pacman_pos, graph):
    """
    Triển khai chiến lược tìm đường cho Ma đỏ.

    Đặc điểm của Ma đỏ trong Pac-Man:
    - Rất hung hăng và trực tiếp trong việc đuổi theo Pacman
    - Luôn tìm kiếm đường đi ngắn nhất để bắt Pacman
    - Sử dụng thuật toán A* với heuristic kết hợp để tối ưu hóa đường đi

    Hàm này tìm và trả về đường đi tối ưu từ vị trí của Ma đỏ đến vị trí của Pacman.
    """
    # Kiểm tra trường hợp đặc biệt: Ma đã ở cùng vị trí với Pacman
    if ghost_pos == pacman_pos:
        return []  # Không cần đường đi vì đã đến đích

    # Thực hiện tìm kiếm A* để tìm đường đi tối ưu
    result = astar_search(ghost_pos, pacman_pos, graph)

    # Xử lý kết quả tìm kiếm
    if result:
        print(f"Red ghost path found")
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
    Tìm đường thoát cho Ma đỏ khi Pacman đã ăn năng lượng (power pellet).

    Khi Pacman ăn năng lượng:
    - Ma trở nên dễ bị tổn thương và cần tránh Pacman
    - Mục tiêu chuyển từ đuổi theo thành thoát khỏi Pacman
    - Hàm này sử dụng A* với heuristic ngược để tối đa hóa khoảng cách

    Chiến lược thoát:
    - Tìm đường đi đến vị trí có khoảng cách an toàn từ Pacman
    - Ưu tiên các hướng di chuyển làm tăng khoảng cách với Pacman
    """
    # Xác định khoảng cách an toàn tối thiểu cần đạt được
    safe_distance = 80

    # Bắt đầu đo lường hiệu suất
    tracemalloc.start()
    start_time = time.perf_counter()

    # Khởi tạo hàng đợi ưu tiên cho thuật toán A* với các thành phần:
    # - ưu tiên (f_score): điểm ưu tiên tổng
    # - counter: bộ đếm cho tính ổn định
    # - node: nút hiện tại
    # - path: đường đi hiện tại
    # - distance: khoảng cách đến Pacman
    frontier = [(0, 0, ghost_pos, [ghost_pos], 0)]
    explored = set()
    counter = 1

    while frontier:
        # Lấy nút có độ ưu tiên cao nhất từ hàng đợi
        _, _, current, path, _ = heapq.heappop(frontier)

        # Kiểm tra xem đã đạt được khoảng cách an toàn chưa
        # Sử dụng khoảng cách Euclidean để đo khoảng cách thực tế đến Pacman
        distance_to_pacman = math.sqrt((current[0] - pacman_pos[0]) ** 2 + (current[1] - pacman_pos[1]) ** 2)
        if distance_to_pacman >= safe_distance:
            # Đã đạt khoảng cách an toàn, kết thúc tìm kiếm
            end_time = time.perf_counter()
            tracemalloc.stop()
            return path

        # Bỏ qua nút đã khám phá
        if current in explored:
            continue

        # Đánh dấu nút hiện tại đã được khám phá
        explored.add(current)

        # Xét tất cả các nút kề
        for neighbor in graph[current]:
            if neighbor not in explored:
                # Tính khoảng cách mới từ nút kề đến Pacman
                new_distance = math.sqrt((neighbor[0] - pacman_pos[0]) ** 2 + (neighbor[1] - pacman_pos[1]) ** 2)

                # Tính điểm heuristic - giá trị âm vì chúng ta muốn TỐI ĐA HÓA khoảng cách
                # Khác với thuật toán A* thông thường, ở đây ta ưu tiên các nút xa Pacman
                h_score = -new_distance

                # Sử dụng độ dài đường đi làm chi phí thực tế (g_score)
                # Ưu tiên đường đi ngắn nhất đến vị trí an toàn
                g_score = len(path)

                # Tính điểm ưu tiên tổng thể (f_score = g_score + h_score)
                priority = g_score + h_score

                # Thêm nút kề vào hàng đợi ưu tiên
                heapq.heappush(frontier,
                               (priority, counter, neighbor, path + [neighbor], new_distance))
                counter += 1  # Tăng bộ đếm để đảm bảo tính ổn định

    # Không tìm thấy đường thoát an toàn
    tracemalloc.stop()
    return []  # Trả về danh sách rỗng