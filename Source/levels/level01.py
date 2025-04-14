import time
import tracemalloc
from collections import deque

def BFS(start, goal, graph, blocked_positions=[]):
    nodes_expanded = 0

    blocked_set = set(blocked_positions)

    tracemalloc.start()
    start_time = time.perf_counter()
    queue = deque([(start, [start])])
    visited = set()

    while queue:
        current_node, path = queue.popleft()
        nodes_expanded += 1
        if current_node == goal:
            end_time = time.perf_counter()
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            return {
                'path': path,
                'nodes_expanded': nodes_expanded,
                'time_ms': (end_time - start_time) * 1000,
                'memory_kb': peak_mem / 1024
            }
        visited.add(current_node)
        for neighbor in graph[current_node]:
            if neighbor not in visited and neighbor not in blocked_set:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    end_time = time.perf_counter()
    tracemalloc.stop()
    return None

def calculate_path_length(path):
    if not path:
        return 0
    length = 0
    for i in range(len(path) - 1):
        length += abs(path[i][0] - path[i + 1][0]) + abs(path[i][1] - path[i + 1][1])
    return length

def blue_ghost_path(ghost_pos, pacman_pos, graph, blocked_positions=[]):    
    #  Check if the ghost is already at the pacman's position
    if ghost_pos == pacman_pos:
        return []  # No path needed
    #  Record search time, memory usage, and number of expanded nodes    
    result = BFS(ghost_pos, pacman_pos, graph, blocked_positions)
    if result:
        print(f"Blue ghost path found:")
        print("Path found:", result['path'])
        print("Nodes expanded:", result['nodes_expanded'])
        print("Time (ms):", round(result['time_ms'], 3))
        print("Memory (KB):", round(result['memory_kb'], 2))
        print("Path length:", calculate_path_length(result['path']))
    else:
        print(f"No path found from ghost{ghost_pos} to pacman{pacman_pos}.\n")

        return []
    return result['path'] # Exclude the ghost's current position

