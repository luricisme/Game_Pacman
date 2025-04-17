import sys
import time
import tracemalloc
import heapq
import pygame
from PIL import Image, ImageDraw

# Constants for the visualization
CELL_SIZE = 20  # Smaller cell size for smaller screen
CELL_BORDER = 1
BACKGROUND_COLOR = (0, 0, 0)  # Black
WALL_COLOR = (40, 40, 40)  # Dark gray
START_COLOR = (255, 165, 0)  # Orange (for ghost)
GOAL_COLOR = (255, 255, 0)  # Yellow (for pacman)
EXPLORED_COLOR = (212, 97, 85)  # Similar to the original code's explored color
PATH_COLOR = (220, 235, 113)  # Similar to the original code's solution color
EMPTY_COLOR = (237, 240, 252)  # Light gray
FRONTIER_COLOR = (255, 140, 0)  # Dark orange


class Node():
    def __init__(self, state, parent, action, cost):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost


class OrangeGhostUCS():
    def __init__(self, filename):
        # Read file and initialize maze
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal positions
        if contents.count("G") != 1:
            raise Exception("maze must have exactly one ghost start point")
        if contents.count("P") != 1:
            raise Exception("maze must have exactly one pacman position")

        # Parse the maze file
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Initialize walls, start, and goal positions
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "G":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "P":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        # Store visualization data
        self.solution = None
        self.explored = {}
        self.num_explored = 0
        self.center_point = (self.width // 2, self.height // 2)
        self.steps = []  # To store snapshots for visualization

    def manhattan_distance(self, a, b):
        """
        Tính khoảng cách Manhattan giữa hai điểm
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def calculate_cost(self, current, neighbor):
        """
        Hàm tính chi phí cho Ma Cam (Orange Ghost)
        Chi phí được tính dựa trên:
        - Khoảng cách đến đích (Pacman)
        - Khoảng cách đến trung tâm bản đồ
        - Yếu tố rủi ro tùy thuộc vào vị trí
        """
        # Tính khoảng cách đến trung tâm bản đồ
        map_center = (14, 14)

        # Hệ số điều chỉnh (có thể thay đổi để tinh chỉnh hành vi)
        CENTER_WEIGHT = 10  # Giảm xuống từ 15
        PACMAN_FOLLOW_WEIGHT = 3  # Thêm yếu tố theo dõi Pac-Man

        center_distance = self.manhattan_distance(neighbor, map_center)

        # Tính khoảng cách tối đa có thể từ bất kỳ điểm nào đến trung tâm
        max_possible_distance = max(30, 32) / 2

        # Chuẩn hóa khoảng cách (giá trị từ 0 đến 1, 1 là xa nhất)
        normalized_distance = min(1.0, center_distance / max_possible_distance)

        # Hàm phi tuyến để tăng chi phí mạnh mẽ cho các vị trí gần trung tâm
        center_penalty = CENTER_WEIGHT * (1 - normalized_distance) ** 2

        pacman_distance = self.manhattan_distance(neighbor, self.goal)

        ideal_distance = 8
        pacman_factor = PACMAN_FOLLOW_WEIGHT * abs(pacman_distance - ideal_distance) / 10

        base_cost = 1
        total_cost = base_cost + center_penalty + pacman_factor

        # Công thức chi phí tổng hợp
        return total_cost

    def neighbors(self, state):
        """Trả về các vị trí liền kề có thể đi được"""
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))

        return result

    def take_snapshot(self, frontier, current_node, added_to_frontier=None, solution_path=None):
        """Lưu trạng thái hiện tại của thuật toán để hiển thị sau này"""
        # Extract states from frontier nodes for visualization
        frontier_states = [item[2].state for item in frontier]

        # Extract current costs for nodes in frontier
        frontier_costs = {}
        for _, _, node in frontier:
            frontier_costs[node.state] = node.cost

        # Create a snapshot of the current state
        snapshot = {
            'frontier': frontier_states,
            'frontier_costs': frontier_costs,
            'explored': dict(self.explored),
            'current': current_node,
            'added_to_frontier': added_to_frontier,
            'solution_path': solution_path
        }

        self.steps.append(snapshot)

    def solve(self):
        """Thuật toán Uniform-Cost Search"""
        # Start measuring time and memory
        tracemalloc.start()
        start_time = time.perf_counter()

        # Initialize
        self.num_explored = 0
        self.explored = {}
        self.steps = []  # Reset steps

        # Initialize frontier with start node
        start_node = Node(state=self.start, parent=None, action=None, cost=0)
        frontier = [(0, 0, start_node)]  # (priority, counter, node)
        frontier_dict = {self.start: 0}  # {state: cost}
        counter = 1

        # Take initial snapshot
        self.take_snapshot(frontier, None)

        while frontier:
            # Get the node with lowest cost
            _, _, current_node = heapq.heappop(frontier)
            current = current_node.state

            # Update frontier dictionary
            del frontier_dict[current]

            # Snapshot before processing
            self.take_snapshot(frontier, current)

            # Check if we reached the goal
            if current == self.goal:
                end_time = time.perf_counter()
                current_mem, peak_mem = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                # Build the path from start to goal
                actions = []
                cells = []
                node = current_node
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent

                actions.reverse()
                cells.reverse()

                self.solution = (actions, cells)
                self.time_ms = (end_time - start_time) * 1000
                self.memory_kb = peak_mem / 1024

                # Final snapshot with solution path
                self.take_snapshot(frontier, current, solution_path=cells)

                return {
                    'actions': actions,
                    'path': cells,
                    'nodes_expanded': self.num_explored,
                    'time_ms': self.time_ms,
                    'memory_kb': self.memory_kb,
                    'cost': current_node.cost
                }

            # Check if we already explored this node with a better cost
            if current in self.explored and self.explored[current] <= current_node.cost:
                continue

            # Mark node as explored
            self.explored[current] = current_node.cost
            self.num_explored += 1

            # Add neighbors to frontier
            for action, next_state in self.neighbors(current):
                step_cost = self.calculate_cost(current, next_state)
                new_cost = current_node.cost + step_cost

                # Check if we should add or update this node
                if (next_state not in self.explored or self.explored[next_state] > new_cost) and \
                        (next_state not in frontier_dict or frontier_dict[next_state] > new_cost):
                    # Add to frontier with priority = cost
                    next_node = Node(state=next_state, parent=current_node, action=action, cost=new_cost)
                    heapq.heappush(frontier, (new_cost, counter, next_node))
                    frontier_dict[next_state] = new_cost
                    counter += 1

                    # Snapshot after adding to frontier
                    self.take_snapshot(frontier, current, added_to_frontier=next_state)

        # No solution found
        tracemalloc.stop()
        return None

    def print(self):
        """Print the maze with solution path if any"""
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("G", end="")
                elif (i, j) == self.goal:
                    print("P", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    def output_image(self, filename, show_solution=True, show_explored=False):
        """Save an image of the maze solution, similar to the original code"""
        img = Image.new(
            "RGBA",
            (self.width * CELL_SIZE, self.height * CELL_SIZE),
            BACKGROUND_COLOR
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                # Determine the color based on the cell type
                if col:
                    fill = WALL_COLOR
                elif (i, j) == self.start:
                    fill = START_COLOR
                elif (i, j) == self.goal:
                    fill = GOAL_COLOR
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = PATH_COLOR
                elif show_explored and (i, j) in self.explored:
                    fill = EXPLORED_COLOR
                else:
                    fill = EMPTY_COLOR

                # Draw the cell
                draw.rectangle(
                    [
                        (j * CELL_SIZE + CELL_BORDER, i * CELL_SIZE + CELL_BORDER),
                        ((j + 1) * CELL_SIZE - CELL_BORDER, (i + 1) * CELL_SIZE - CELL_BORDER)
                    ],
                    fill=fill
                )

        img.save(filename)
        print(f"Image saved as {filename}")
        return filename

    def visualize_pygame(self):
        """Interactive visualization using Pygame"""
        pygame.init()

        # Calculate the appropriate window size (with info panel)
        info_panel_height = 100
        window_width = self.width * CELL_SIZE
        window_height = self.height * CELL_SIZE + info_panel_height

        screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Orange Ghost UCS Visualization")
        clock = pygame.time.Clock()

        # Fonts
        font = pygame.font.SysFont('Arial', 14)
        title_font = pygame.font.SysFont('Arial', 18)

        # Current step being displayed
        current_step_idx = 0
        auto_play = False
        frame_delay = 30  # frames between auto-advancing
        frame_counter = 0

        # Main visualization loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        current_step_idx = min(current_step_idx + 1, len(self.steps) - 1)
                    elif event.key == pygame.K_LEFT:
                        current_step_idx = max(current_step_idx - 1, 0)
                    elif event.key == pygame.K_SPACE:
                        auto_play = not auto_play
                    elif event.key == pygame.K_UP:
                        frame_delay = max(frame_delay - 5, 5)
                    elif event.key == pygame.K_DOWN:
                        frame_delay += 5
                    elif event.key == pygame.K_s:
                        # Save current view as PNG
                        filename = f"orange_ghost_step_{current_step_idx}.png"
                        pygame.image.save(screen, filename)
                        print(f"Screenshot saved as {filename}")

            # Auto-advance if in auto-play mode
            if auto_play:
                frame_counter += 1
                if frame_counter >= frame_delay:
                    frame_counter = 0
                    current_step_idx += 1
                    if current_step_idx >= len(self.steps):
                        current_step_idx = 0

            # Clear screen
            screen.fill((30, 30, 30))

            # Get current step data
            step = self.steps[current_step_idx]

            # Draw maze
            for i_row in range(self.height):
                for j_col in range(self.width):
                    # Determine color based on cell type
                    if self.walls[i_row][j_col]:
                        fill = WALL_COLOR
                    elif (i_row, j_col) == self.start:
                        fill = START_COLOR
                    elif (i_row, j_col) == self.goal:
                        fill = GOAL_COLOR
                    elif step['solution_path'] and (i_row, j_col) in step['solution_path']:
                        fill = PATH_COLOR
                    elif (i_row, j_col) in step['explored']:
                        fill = EXPLORED_COLOR
                    elif (i_row, j_col) in step['frontier']:
                        fill = FRONTIER_COLOR
                    elif (i_row, j_col) == step['added_to_frontier']:
                        fill = (255, 100, 0)  # Bright orange for newly added
                    elif (i_row, j_col) == step['current']:
                        fill = (255, 80, 0)  # Very bright orange for current
                    else:
                        fill = EMPTY_COLOR

                    # Draw cell
                    pygame.draw.rect(
                        screen,
                        fill,
                        (
                            j_col * CELL_SIZE + CELL_BORDER,
                            i_row * CELL_SIZE + CELL_BORDER,
                            CELL_SIZE - 2 * CELL_BORDER,
                            CELL_SIZE - 2 * CELL_BORDER
                        )
                    )

            # Draw info panel
            info_y = self.height * CELL_SIZE + 10

            # Step counter
            step_text = f"Step: {current_step_idx + 1}/{len(self.steps)}"
            step_surf = font.render(step_text, True, (255, 255, 255))
            screen.blit(step_surf, (10, info_y))

            # Nodes info
            nodes_text = f"Explored: {len(step['explored'])} | Frontier: {len(step['frontier'])}"
            nodes_surf = font.render(nodes_text, True, (255, 255, 255))
            screen.blit(nodes_surf, (10, info_y + 20))

            # Current node info
            if step['current'] is not None:
                pos = step['current']
                cost = step['explored'].get(pos, 0)
                current_text = f"Current: {pos} (Cost: {cost:.3f})"
                current_surf = font.render(current_text, True, (255, 200, 0))
                screen.blit(current_surf, (10, info_y + 40))

            # Controls info
            controls_text = "Space: Toggle Auto | ←/→: Navigate | ↑/↓: Speed | S: Save Screenshot"
            controls_surf = font.render(controls_text, True, (200, 200, 200))
            screen.blit(controls_surf, (10, info_y + 60))

            # Auto-play indicator
            auto_text = "Auto: ON" if auto_play else "Auto: OFF"
            auto_surf = font.render(auto_text, True, (0, 255, 0) if auto_play else (255, 0, 0))
            screen.blit(auto_surf, (window_width - 100, info_y))

            # Title
            title_text = "Orange Ghost UCS Algorithm Visualization"
            title_surf = title_font.render(title_text, True, (255, 165, 0))
            screen.blit(title_surf, (window_width // 2 - title_surf.get_width() // 2, info_y + 5))

            # Update display
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python orange_ghost_visualization.py maze.txt")
        sys.exit(1)

    # Initialize and solve
    ghost = OrangeGhostUCS(sys.argv[1])
    print("Solving with Orange Ghost UCS algorithm...")
    result = ghost.solve()

    if result:
        print(f"Path found! Length: {len(result['path'])}")
        print(f"Nodes expanded: {result['nodes_expanded']}")
        print(f"Time (ms): {result['time_ms']:.3f}")
        print(f"Memory (KB): {result['memory_kb']:.2f}")
        print(f"Cost: {result['cost']}")

        # Print the maze with solution
        ghost.print()

        # Generate images
        ghost.output_image("orange_ghost.png", show_solution=True, show_explored=False)
        ghost.output_image("orange_ghost_explored.png", show_solution=True, show_explored=True)

        # Start visualization
        print("\nStarting visualization...")
        print("Controls:")
        print("  Left/Right arrows: Navigate through steps")
        print("  Space: Toggle auto-play")
        print("  Up/Down arrows: Adjust auto-play speed")
        print("  S: Save current view as PNG")
        print("  Close window to exit")
        ghost.visualize_pygame()
    else:
        print("No solution found!")