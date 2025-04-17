import time
import tracemalloc
from collections import deque

def BFS(start, goal, graph):
    
    nodes_expanded = 0

    tracemalloc.start()
    start_time = time.perf_counter()
    queue = deque([(start, [start])])
    visited = set()

    while queue:
        current_node, path = queue.popleft()
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
        nodes_expanded += 1
        visited.add(current_node)
        for neighbor in graph[current_node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    end_time = time.perf_counter()
    tracemalloc.stop()
    return None


def blue_ghost_path(ghost_pos, pacman_pos, graph):    
    #  Check if the ghost is already at the pacman's position
    if ghost_pos == pacman_pos:
        return []  # No path needed
    #  Record search time, memory usage, and number of expanded nodes    
    result = BFS(ghost_pos, pacman_pos, graph)
    if result:
        print("Blue ghost path found:")
        print("Path found:", result['path'])
        print("Nodes expanded:", result['nodes_expanded'])
        print("Time (ms):", round(result['time_ms'], 3))
        print("Memory (KB):", round(result['memory_kb'], 2))
        print("Path length:", len(result['path'])-1)
    else:
        print(f"No path found from ghost{ghost_pos} to pacman{pacman_pos}.\n")
        return []
    return result['path'] # Exclude the ghost's current position

