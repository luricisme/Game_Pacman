import time
import tracemalloc


def calculate_path_length(path):
    if not path:
        return 0
    length = 0
    for i in range(len(path) - 1):
        length += abs(path[i][0] - path[i + 1][0]) + abs(path[i][1] - path[i + 1][1])
    return length

def dfs(graph, start, goal, blocked_positions=[]):
    start_time = time.time()
    tracemalloc.start()

    blocked_set = set(blocked_positions)

    stack = [(start, [start])]
    visited = set()
    nodes_expanded = 0

    while stack:
        current, path = stack.pop()
        if current in visited or current in blocked_set:
            continue
        visited.add(current)
        nodes_expanded += 1

        if current == goal:
            end_time = time.time()
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            return {
                'path': path,
                'nodes_expanded': nodes_expanded,
                'time_ms': (end_time - start_time) * 1000,
                'memory_kb': peak_mem/ 1024
            }
        for neighbor in reversed(graph.get(current, [])):
            if neighbor not in visited and neighbor not in blocked_set:
                stack.append((neighbor, path + [neighbor]))

    end_time = time.time()
    tracemalloc.stop()
    return None


def pink_ghost_path(ghost_pos, pacman_pos, graph, blocked_positions=[]):    
    #  Check if the ghost is already at the pacman's position
    if ghost_pos == pacman_pos:
        return []  # No path needed
    #  Record search time, memory usage, and number of expanded nodes 
    # print("graph", graph)   
    result = dfs(graph, ghost_pos, pacman_pos, blocked_positions)
    if result:
        print(f"Pink ghost path found:")
        print("Path found:", result['path'])
        print("Nodes expanded:", result['nodes_expanded'])
        print("Time (ms):", round(result['time_ms'], 5))
        print("Memory (KB):", round(result['memory_kb'], 4))
        print("Path length:", calculate_path_length(result['path']))
    else:
        print(f"No path found from ghost{ghost_pos} to pacman{pacman_pos}.\n")
        return []
    return result['path'] 
