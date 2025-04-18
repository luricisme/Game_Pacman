import time
import tracemalloc


def dfs(graph, start, goal):
    start_time = time.time()
    tracemalloc.start()

    stack = [(start, [start])]
    visited = set()
    nodes_expanded = 0

    while stack:
        current, path = stack.pop()
        if current in visited:
            continue
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
        visited.add(current)
        nodes_expanded += 1
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                stack.append((neighbor, path + [neighbor]))

    end_time = time.time()
    tracemalloc.stop()
    return None


def pink_ghost_path(ghost_pos, pacman_pos, graph):    
    #  Check if the ghost is already at the pacman's position
    if ghost_pos == pacman_pos:
        return []  # No path needed
    #  Record search time, memory usage, and number of expanded nodes 
    # print("graph", graph)   
    result = dfs(graph, ghost_pos, pacman_pos)
    if result:
        print(f"Pink ghost path found:")
        print("Path found:", result['path'])
        print("Nodes expanded:", result['nodes_expanded'])
        print("Time (ms):", round(result['time_ms'], 5))
        print("Memory (KB):", round(result['memory_kb'], 4))
        print("Path length:", len(result['path'])-1)
    else:
        print(f"No path found from pink ghost{ghost_pos} to pacman{pacman_pos}.\n")
        return []
    return result['path'] 
