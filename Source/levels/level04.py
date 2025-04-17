import time
import tracemalloc
import heapq
import math

def astar_search(start, goal, graph):
    """
    Thuật toán tìm kiếm A* (A-star)

    Thuật toán này tìm đường đi tối ưu từ điểm xuất phát đến đích
    bằng cách kết hợp chi phí thực tế (g_score) và ước lượng heuristic (h_score).
    Công thức: f_score = g_score + h_score, trong đó:
    - g_score: Chi phí thực tế từ vị trí bắt đầu đến vị trí hiện tại
    - h_score: Ước tính chi phí từ vị trí hiện tại đến đích (Manhattan distance)

    Tham số:
        start: Vị trí bắt đầu của Ghost, dạng tuple (x, y)
        goal: Vị trí của Pac-Man, dạng tuple (x, y)
        graph: Đồ thị biểu diễn mê cung (dạng dictionary của adjacency list)
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

    # Khởi tạo hàng đợi ưu tiên với các thành phần:
    # - f_score: tổng chi phí ước tính (g_score + h_score)
    # - counter: bộ đếm để đảm bảo tính ổn định khi hai nút có cùng f_score
    # - node: nút hiện tại đang xét
    # - path: đường đi từ điểm bắt đầu đến nút hiện tại
    # - g_score: chi phí thực tế từ điểm bắt đầu đến nút hiện tại
    frontier = [(heuristic(start, goal), 0, start, [start], 0)]

    # Từ điển theo dõi các nút trong frontier với chi phí g_score tương ứng
    # Cấu trúc: {nút: g_score}
    frontier_dict = {start: 0}

    # Tập hợp các nút đã khám phá để tránh xét lại
    explored = set()

    # Bộ đếm tăng dần để đảm bảo tính ổn định của hàng đợi ưu tiên
    counter = 1

    while frontier:
        # Lấy nút có độ ưu tiên cao nhất (f_score thấp nhất) từ hàng đợi
        f_score, _, current, path, g_score = heapq.heappop(frontier)
        nodes_expanded += 1

        # Nếu đã đến đích, kết thúc tìm kiếm và trả về kết quả
        if current == goal:
            # Kết thúc đo thời gian và bộ nhớ
            end_time = time.perf_counter()
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # Trả về kết quả chi tiết về đường đi tìm được
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
            # Bỏ qua nút kề nếu đã khám phá
            if neighbor in explored:
                continue

            # Tính toán chi phí g_score mới khi đi từ nút hiện tại đến nút kề
            new_g_score = g_score + calculate_cost(current, neighbor)

            if neighbor in frontier_dict:
                # Nếu nút kề đã có trong frontier với chi phí cao hơn, cập nhật
                if frontier_dict[neighbor] > new_g_score:
                    # Cập nhật chi phí trong frontier_dict
                    frontier_dict[neighbor] = new_g_score

                    # Tính toán h_score và f_score mới
                    h_score = heuristic(neighbor, goal)
                    f_score = new_g_score + h_score

                    # Thêm nút với chi phí cập nhật vào frontier
                    heapq.heappush(frontier, (f_score, counter, neighbor, path + [neighbor], new_g_score))
                    counter += 1  # Tăng bộ đếm để đảm bảo tính ổn định
            else:
                # Nếu nút kề chưa có trong frontier, thêm vào
                frontier_dict[neighbor] = new_g_score

                # Tính toán h_score và f_score
                h_score = heuristic(neighbor, goal)
                f_score = new_g_score + h_score

                # Thêm nút mới vào frontier
                heapq.heappush(frontier, (f_score, counter, neighbor, path + [neighbor], new_g_score))
                counter += 1  # Tăng bộ đếm để đảm bảo tính ổn định

    # Nếu không tìm thấy đường đi đến đích
    end_time = time.perf_counter()
    tracemalloc.stop()
    return None


def heuristic(current, goal):
    """
    Hàm heuristic dựa trên khoảng cách Manhattan

    Ước tính khoảng cách từ vị trí hiện tại đến đích sử dụng khoảng cách Manhattan.
    Công thức: |x1 - x2| + |y1 - y2|

    Đây là heuristic admissible (không bao giờ ước tính quá thực tế), đảm bảo
    thuật toán A* tìm ra đường đi tối ưu. Phù hợp cho chuyển động trên lưới
    (lên, xuống, trái, phải) trong không gian 2D như trong trò chơi Pac-Man.

    Tham số:
        current: Vị trí hiện tại, dạng tuple (x, y)
        goal: Vị trí đích cần đến, dạng tuple (x, y)

    Trả về:
        int: Khoảng cách Manhattan giữa hai vị trí
    """
    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])


def calculate_cost(current, next_node):
    """
    Hàm tính chi phí di chuyển từ nút hiện tại đến nút tiếp theo cho Ma Đỏ

    Hàm này cung cấp giá trị g_score trong thuật toán A* (chi phí thực tế
    để di chuyển từ vị trí bắt đầu đến vị trí hiện tại).

    Ma Đỏ được đặc trưng bởi tính hung hăng và quyết đoán:
    - Luôn tìm đường đi ngắn nhất đến Pac-Man
    - Không quan tâm đến rủi ro hay an toàn
    - Sử dụng hàm chi phí đồng đều (mỗi bước = 1) để tìm đường đi ngắn nhất

    Chi phí đồng đều phù hợp với Ma Đỏ vì nó giúp tìm đường đi với số bước ít nhất,
    đúng với tính cách truy đuổi trực tiếp của Ma Đỏ trong trò chơi Pac-Man.

    Tham số:
        current: Vị trí hiện tại, dạng tuple (x, y)
        next_node: Vị trí kề đang xét để di chuyển đến, dạng tuple (x, y)

    Trả về:
        int: Chi phí di chuyển từ vị trí hiện tại đến vị trí kề (luôn là 1)
    """
    # Chi phí cơ bản cho mỗi bước di chuyển là 1
    # Hàm chi phí đơn giản vì Ma đỏ không quan tâm đến yếu tố khác
    # ngoài việc đến được Pac-Man nhanh nhất có thể
    base_cost = 1

    # Không có chi phí bổ sung cho bất kỳ loại di chuyển nào
    # Khác với các ma khác có thể tránh khu vực nguy hiểm hoặc có chiến lược phức tạp hơn
    return base_cost

def red_ghost_path(ghost_pos, pacman_pos, graph):
    """
    Xác định đường đi cho Ma Đỏ theo Pac-Man sử dụng thuật toán A*

    Đặc điểm của Ma Đỏ trong Pac-Man:
    - Rất hung hăng và trực tiếp trong việc đuổi theo Pac-Man
    - Luôn tìm kiếm đường đi ngắn nhất để bắt Pac-Man
    - Sử dụng thuật toán A* với heuristic khoảng cách Manhattan để tối ưu hóa đường đi

    Hàm này xử lý các trường hợp đặc biệt:
    1. Ma đã ở cùng vị trí với Pac-Man
    2. Không tìm thấy đường đi đến Pac-Man (có thể do bị chặn hoàn toàn)

    Tham số:
        ghost_pos: Vị trí hiện tại của Ma Đỏ, dạng tuple (x, y)
        pacman_pos: Vị trí hiện tại của Pac-Man, dạng tuple (x, y)
        graph: Đồ thị biểu diễn mê cung (dictionary với key là vị trí và
               value là danh sách các vị trí kề có thể di chuyển đến)
        blocked_positions: Danh sách vị trí bị chặn (các ma khác hoặc vật cản),
                          mặc định là None

    Trả về:
        list: Danh sách các vị trí trên đường đi từ Ma Đỏ đến Pac-Man
              hoặc danh sách rỗng nếu không tìm thấy đường đi hoặc đã ở vị trí Pac-Man
    """
    # Kiểm tra trường hợp đặc biệt: Ma đã ở cùng vị trí với Pac-Man
    if ghost_pos == pacman_pos:
        return []  # Không cần đường đi vì đã đến đích

    # Thực hiện tìm kiếm A* để tìm đường đi tối ưu
    result = astar_search(ghost_pos, pacman_pos, graph)

    # Xử lý kết quả tìm kiếm
    if result:
        # In thông tin chi tiết về đường đi tìm được
        print(f"Red ghost path found")
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
    Tìm đường thoát cho Ma Đỏ khi Pac-Man đã ăn năng lượng (power pellet)

    Khi Pac-Man ăn năng lượng:
    - Ma trở nên dễ bị tổn thương và cần tránh Pac-Man
    - Mục tiêu chuyển từ đuổi theo thành thoát khỏi Pac-Man
    - Sử dụng A* biến thể để tối đa hóa khoảng cách với Pac-Man

    Chiến lược thoát:
    - Tìm đường đi đến vị trí có khoảng cách an toàn từ Pac-Man
    - Ưu tiên các hướng di chuyển làm tăng khoảng cách với Pac-Man
    - Sử dụng khoảng cách Euclidean để đánh giá mức độ an toàn

    Tham số:
        ghost_pos: Vị trí hiện tại của Ma Đỏ, dạng tuple (x, y)
        pacman_pos: Vị trí hiện tại của Pac-Man, dạng tuple (x, y)
        graph: Đồ thị biểu diễn mê cung

    Trả về:
        list: Danh sách các vị trí trên đường thoát
              hoặc danh sách rỗng nếu không tìm thấy đường thoát
    """
    # Xác định khoảng cách an toàn tối thiểu cần đạt được
    # Ma Đỏ cần khoảng cách an toàn lớn hơn các ma khác do thiếu chiến thuật phức tạp
    safe_distance = 80

    # Bắt đầu đo lường hiệu suất
    tracemalloc.start()
    start_time = time.perf_counter()

    # Khởi tạo hàng đợi ưu tiên cho thuật toán A* biến thể với các thành phần:
    # - ưu tiên (f_score): điểm ưu tiên tổng (g_score + h_score)
    # - counter: bộ đếm cho tính ổn định khi hai nút có cùng f_score
    # - node: nút hiện tại đang xét
    # - path: đường đi từ điểm bắt đầu đến nút hiện tại
    # - distance: khoảng cách đến Pac-Man
    frontier = [(0, 0, ghost_pos, [ghost_pos], 0)]

    # Tập hợp các nút đã khám phá
    explored = set()

    # Bộ đếm để đảm bảo tính ổn định của hàng đợi ưu tiên
    counter = 1

    while frontier:
        # Lấy nút có độ ưu tiên cao nhất từ hàng đợi
        _, _, current, path, _ = heapq.heappop(frontier)

        # Tính khoảng cách Euclidean từ vị trí hiện tại đến Pac-Man
        # Sử dụng Euclidean vì nó cho đánh giá chính xác hơn về khoảng cách thực tế
        distance_to_pacman = math.sqrt((current[0] - pacman_pos[0]) ** 2 + (current[1] - pacman_pos[1]) ** 2)

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
                new_distance = math.sqrt((neighbor[0] - pacman_pos[0]) ** 2 + (neighbor[1] - pacman_pos[1]) ** 2)

                # Tính h_score - giá trị âm vì muốn TỐI ĐA HÓA khoảng cách đến Pac-Man
                # (khác với A* thông thường muốn tối thiểu hóa khoảng cách)
                h_score = -new_distance

                # g_score là chi phí thực tế, ở đây dùng độ dài đường đi
                # Ưu tiên đường đi ngắn nhất đến vị trí an toàn
                g_score = len(path)

                # f_score = g_score + h_score: tổng chi phí ước tính
                priority = g_score + h_score

                # Thêm nút kề vào hàng đợi ưu tiên
                heapq.heappush(frontier,
                               (priority, counter, neighbor, path + [neighbor], new_distance))
                counter += 1  # Tăng bộ đếm để đảm bảo tính ổn định

    # Không tìm thấy đường thoát an toàn
    tracemalloc.stop()
    return []  # Trả về danh sách rỗng