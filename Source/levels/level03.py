import heapq

from ghost import Ghost


class Node:
    def __init__(self, state, parent, action, cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost  # Chi phí để đi từ nút bắt đầu đến nút hiện tại

class PriorityQueueFrontier:
    def __init__(self):
        self.frontier = []
        self.counter = 0  # Dùng để giải quyết trường hợp chi phí bằng nhau

    def add(self, node, cost=0):
        self.counter += 1
        heapq.heappush(self.frontier, (cost, self.counter, node))

    def contains_state(self, state):
        return any(node.state == state for _, _, node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            cost, _, node = heapq.heappop(self.frontier)
            return node

class OrangeGhost(Ghost):
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, id, screen, level, eaten_ghost, powerup, spooked_img, dead_img):
        super().__init__(x_coord, y_coord, target, speed, img, direct, dead, box, id, screen, level, eaten_ghost, powerup, spooked_img, dead_img)

    def move(self):
        pass

    def uniform_cost_search(self, start, goal):
        pass


def convert_to_maze_with_points(matrix, start_pos=(15, 1), goal_pos=(15, 28)):
    maze = []
    for row in matrix:
        maze_row = []
        for cell in row:
            if cell in [0, 1, 2, 9]:  # Các số đại diện cho đường đi
                maze_row.append(" ")
            else:  # Các số còn lại đại diện cho tường
                maze_row.append("#")
        maze.append("".join(maze_row))

    # Đặt A ở vị trí (15, 1) - gần giữa hàng trên cùng để dễ thấy
    # maze_row = list(maze[15])
    # maze_row[1] = "A"
    # maze[15] = "".join(maze_row)
    maze_row = list(maze[start_pos[0]])
    maze_row[start_pos[1]] = "A"
    maze[start_pos[0]] = "".join(maze_row)

    # Đặt B ở vị trí (15, 28) - gần giữa hàng dưới cùng để dễ thấy
    # maze_row = list(maze[15])
    # maze_row[28] = "B"
    # maze[15] = "".join(maze_row)
    maze_row = list(maze[goal_pos[0]])
    maze_row[goal_pos[1]] = "B"
    maze[goal_pos[0]] = "".join(maze_row)

    return maze

