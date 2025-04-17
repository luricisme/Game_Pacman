
def is_walkable(cell):
    return cell <= 2  or cell == 9 # 0, 1, 2, 9 are walkable cells (0: empty, 1, 2: food, 9: for ghosts)
'''
def is_node(i, j, grid): 
    #      
    if not is_walkable(grid[i][j]):
        return False
    # Check if the cell has neighbors on different sides, not just two in the same direction
    horizontal_neighbors = is_walkable(grid[i][j - 1]) if j > 0 else False
    horizontal_neighbors += is_walkable(grid[i][j + 1]) if j < len(grid[0]) - 1 else False
    vertical_neighbors = is_walkable(grid[i - 1][j]) if i > 0 else False
    vertical_neighbors += is_walkable(grid[i + 1][j]) if i < len(grid) - 1 else False
    return horizontal_neighbors + vertical_neighbors != 2
'''
def extract_graph(grid):
    """
    Tạo đồ thị không trọng số từ map.
    """
    nodes = {}
    rows, cols = len(grid), len(grid[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Lên, xuống, trái, phải

    for i in range(rows):
        for j in range(cols):
            if not is_walkable(grid[i][j]):
                continue
            current_node = (i, j)
            nodes[current_node] = []

            for dx, dy in directions:
                x, y = i + dx, j + dy
                if 0 <= x < rows and 0 <= y < cols and is_walkable(grid[x][y]):
                    neighbor_node = (x, y)
                    nodes[current_node].append(neighbor_node)

    '''#draw the graph like a matrix
    print("Graph:")
    print(" ", end='  ')
    for j in range(cols):
        print(j, end=' '*(1 + (j<10)))
    print()
    for i in range(rows):
        print(i, end=' '*(1 + (i<10)))
        for j in range(cols):
            if (i, j) in nodes:
                print("X", end='  ')
            else:
                print(int(grid[i][j]>2), end='  ')
        print()
    #print the graph

    print("Graph extracted successfully")'''
    return nodes
