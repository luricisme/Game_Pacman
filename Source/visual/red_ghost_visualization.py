import sys
import time
import tracemalloc
import heapq
import math
import pygame
from PIL import Image, ImageDraw

# Constants for the visualization
CELL_SIZE = 20  # Smaller cell size for smaller screen
CELL_BORDER = 1
BACKGROUND_COLOR = (0, 0, 0)  # Black
WALL_COLOR = (40, 40, 40)  # Dark gray
START_COLOR = (255, 0, 0)  # Red (for red ghost)
GOAL_COLOR = (255, 255, 0)  # Yellow (for pacman)
EXPLORED_COLOR = (180, 60, 60)  # Darker red for explored
PATH_COLOR = (255, 120, 120)  # Light red for path
EMPTY_COLOR = (237, 240, 252)  # Light gray
FRONTIER_COLOR = (255, 80, 80)  # Medium red

# Highlight colors for visualization
CURRENT_COLOR = (255, 20, 20)  # Very bright red for current node
NEW_FRONTIER_COLOR = (255, 180, 180)  # Very light red for newly added frontier node
HIGH_G_SCORE_COLOR = (200, 30, 30)  # Darker red for high g-score
LOW_G_SCORE_COLOR = (255, 150, 150)  # Lighter red for low g-score


class Node():
    def __init__(self, state, parent, action, g_score, h_score):
        self.state = state
        self.parent = parent
        self.action = action
        self.g_score = g_score  # Cost from start to this node
        self.h_score = h_score  # Estimated cost from this node to goal
        self.f_score = g_score + h_score  # Total estimated cost


class RedGhostAStar():
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
        self.steps = []  # To store snapshots for visualization

    def manhattan_distance(self, a, b):
        """
        Tính khoảng cách Manhattan giữa hai điểm
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def euclidean_distance(self, a, b):
        """
        Tính khoảng cách Euclidean giữa hai điểm
        """
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    # def heuristic(self, current, goal):
    #     """
    #     Hàm heuristic kết hợp để ước tính khoảng cách từ vị trí hiện tại đến đích.
    #     """
    #     euclidean = self.euclidean_distance(current, goal)
    #     manhattan = self.manhattan_distance(current, goal)
    #
    #     # Yếu tố hung hăng tăng khi ma đỏ đến gần Pacman
    #     aggression_factor = 1.0
    #     if euclidean < 10:  # Khi gần Pacman
    #         aggression_factor = 1.2  # Tăng tính hung hăng
    #
    #     # Kết hợp hai khoảng cách với trọng số
    #     return (0.6 * euclidean + 0.4 * manhattan) / aggression_factor

    def heuristic(self, current, goal):
        manhattan = self.manhattan_distance(current, goal)

        return manhattan

    def calculate_cost(self, current, next_node):
        """
        Hàm tính chi phí di chuyển từ nút hiện tại đến nút tiếp theo cho Ma Đỏ.
        """
        return 1  # Chi phí cơ bản cho mỗi bước di chuyển

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

    def take_snapshot(self, frontier, frontier_dict, current_node, explored, added_to_frontier=None,
                      solution_path=None):
        """Lưu trạng thái hiện tại của thuật toán để hiển thị sau này"""
        # Extract states, g_scores, h_scores, and f_scores from frontier nodes for visualization
        frontier_states = [node.state for node in frontier]
        frontier_g_scores = {node.state: node.g_score for node in frontier}
        frontier_h_scores = {node.state: node.h_score for node in frontier}
        frontier_f_scores = {node.state: node.f_score for node in frontier}

        # Create a snapshot of the current state
        snapshot = {
            'frontier': frontier_states,
            'frontier_g_scores': frontier_g_scores,
            'frontier_h_scores': frontier_h_scores,
            'frontier_f_scores': frontier_f_scores,
            'frontier_dict': dict(frontier_dict),  # Make a copy to avoid reference issues
            'explored': dict(explored),
            'current': current_node.state if current_node else None,
            'added_to_frontier': added_to_frontier,
            'solution_path': solution_path
        }

        self.steps.append(snapshot)

    def solve(self):
        """Thuật toán A* để tìm đường đi tối ưu"""
        # Start measuring time and memory
        tracemalloc.start()
        start_time = time.perf_counter()

        # Initialize
        self.num_explored = 0
        self.explored = {}
        self.steps = []  # Reset steps

        # Initialize start node
        h_score = self.heuristic(self.start, self.goal)
        start_node = Node(state=self.start, parent=None, action=None, g_score=0, h_score=h_score)

        # Initialize frontier with priority queue and dictionary for O(1) lookup
        frontier = [start_node]
        frontier_dict = {self.start: 0}  # {state: g_score}

        # Take initial snapshot
        self.take_snapshot(frontier, frontier_dict, None, self.explored)

        while frontier:
            # Sort frontier by f_score (lowest first)
            frontier.sort(key=lambda x: (x.f_score, x.g_score))
            current_node = frontier.pop(0)
            current = current_node.state

            # Update frontier dictionary - safely remove with get method
            if current in frontier_dict:
                del frontier_dict[current]

            # Snapshot before processing
            self.take_snapshot(frontier, frontier_dict, current_node, self.explored)

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
                self.take_snapshot(frontier, frontier_dict, current_node, self.explored, solution_path=cells)

                return {
                    'actions': actions,
                    'path': cells,
                    'nodes_expanded': self.num_explored,
                    'time_ms': self.time_ms,
                    'memory_kb': self.memory_kb,
                    'cost': current_node.g_score
                }

            # Check if we already explored this node with a better cost
            if current in self.explored and self.explored[current] <= current_node.g_score:
                continue

            # Mark node as explored
            self.explored[current] = current_node.g_score
            self.num_explored += 1

            # Add neighbors to frontier
            for action, next_state in self.neighbors(current):
                # Skip if neighbor is in blocked positions
                step_cost = self.calculate_cost(current, next_state)
                new_g_score = current_node.g_score + step_cost

                # Check if we should add or update this node
                if (next_state not in self.explored or self.explored[next_state] > new_g_score) and \
                        (next_state not in frontier_dict or frontier_dict[next_state] > new_g_score):
                    h_score = self.heuristic(next_state, self.goal)
                    next_node = Node(state=next_state, parent=current_node, action=action,
                                     g_score=new_g_score, h_score=h_score)

                    # Update or add to frontier
                    frontier_dict[next_state] = new_g_score
                    frontier.append(next_node)

                    # Snapshot after adding to frontier
                    self.take_snapshot(frontier, frontier_dict, current_node, self.explored,
                                       added_to_frontier=next_state)

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
        """Save an image of the maze solution"""
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
        info_panel_height = 120
        window_width = max(800, self.width * CELL_SIZE)
        window_height = self.height * CELL_SIZE + info_panel_height

        screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Red Ghost A* Visualization")
        clock = pygame.time.Clock()

        # Fonts
        font = pygame.font.SysFont('Arial', 14)
        title_font = pygame.font.SysFont('Arial', 18)

        # Current step being displayed
        current_step_idx = 0
        auto_play = False
        frame_delay = 30  # frames between auto-advancing
        frame_counter = 0
        show_f_scores = False  # Toggle to show f-scores instead of g-scores

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
                    elif event.key == pygame.K_f:
                        show_f_scores = not show_f_scores  # Toggle f_score display
                    elif event.key == pygame.K_s:
                        # Save current view as PNG
                        filename = f"red_ghost_step_{current_step_idx}.png"
                        pygame.image.save(screen, filename)
                        print(f"Screenshot saved as {filename}")

            # Auto-advance if in auto-play mode
            if auto_play:
                frame_counter += 1
                if frame_counter >= frame_delay:
                    frame_counter = 0
                    current_step_idx += 1
                    if current_step_idx >= len(self.steps):
                        auto_play = False  # Stop at the end
                        current_step_idx = len(self.steps) - 1

            # Clear screen
            screen.fill((30, 30, 30))

            # Get current step data
            if self.steps and 0 <= current_step_idx < len(self.steps):
                step = self.steps[current_step_idx]

                # Find min and max scores for normalization
                if step['frontier']:
                    if show_f_scores and step['frontier_f_scores']:
                        min_score = min(step['frontier_f_scores'].values())
                        max_score = max(step['frontier_f_scores'].values())
                    elif step['frontier_g_scores']:
                        min_score = min(step['frontier_g_scores'].values())
                        max_score = max(step['frontier_g_scores'].values())
                    else:
                        min_score = 0
                        max_score = 1
                    score_range = max(1, max_score - min_score)  # Avoid division by zero
                else:
                    min_score = 0
                    max_score = 1
                    score_range = 1

                # Draw maze
                for i_row in range(self.height):
                    for j_col in range(self.width):
                        pos = (i_row, j_col)
                        # Determine color based on cell type
                        if self.walls[i_row][j_col]:
                            fill = WALL_COLOR
                        elif pos == self.start:
                            fill = START_COLOR
                        elif pos == self.goal:
                            fill = GOAL_COLOR
                        elif step['solution_path'] and pos in step['solution_path']:
                            fill = PATH_COLOR
                        elif pos == step['current']:
                            fill = CURRENT_COLOR  # Very bright red for current node
                        elif pos == step['added_to_frontier']:
                            fill = NEW_FRONTIER_COLOR  # Very light red for newly added
                        elif pos in step['frontier']:
                            try:
                                if show_f_scores and pos in step['frontier_f_scores']:
                                    # Color based on f_score (high = dark, low = light)
                                    normalized_score = (step['frontier_f_scores'][pos] - min_score) / score_range
                                elif pos in step['frontier_g_scores']:
                                    # Color based on g_score (high = dark, low = light)
                                    normalized_score = (step['frontier_g_scores'][pos] - min_score) / score_range
                                else:
                                    normalized_score = 0.5  # Default if no score available

                                # Interpolate between LOW_G_SCORE_COLOR and HIGH_G_SCORE_COLOR
                                r = LOW_G_SCORE_COLOR[0] + normalized_score * (
                                            HIGH_G_SCORE_COLOR[0] - LOW_G_SCORE_COLOR[0])
                                g = LOW_G_SCORE_COLOR[1] + normalized_score * (
                                            HIGH_G_SCORE_COLOR[1] - LOW_G_SCORE_COLOR[1])
                                b = LOW_G_SCORE_COLOR[2] + normalized_score * (
                                            HIGH_G_SCORE_COLOR[2] - LOW_G_SCORE_COLOR[2])
                                fill = (int(r), int(g), int(b))
                            except (KeyError, ZeroDivisionError):
                                fill = FRONTIER_COLOR  # Fallback
                        elif pos in step['explored']:
                            fill = EXPLORED_COLOR
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

                        # Optional: Draw scores on cells
                        if pos in step['frontier'] and CELL_SIZE > 15:
                            try:
                                if show_f_scores and pos in step['frontier_f_scores']:
                                    score_text = f"{step['frontier_f_scores'][pos]:.1f}"
                                elif pos in step['frontier_g_scores']:
                                    score_text = f"{step['frontier_g_scores'][pos]:.1f}"
                                else:
                                    score_text = "?"
                                score_surf = font.render(score_text, True, (255, 255, 255))
                                screen.blit(score_surf, (j_col * CELL_SIZE + 2, i_row * CELL_SIZE + 2))
                            except KeyError:
                                pass  # Skip if key doesn't exist

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
                    g_score = step['explored'].get(pos, 0)
                    h_score = 0
                    # Try to find h_score for current node
                    for node_state, node_h_score in step['frontier_h_scores'].items():
                        if node_state == pos:
                            h_score = node_h_score
                            break
                    current_text = f"Current: {pos} (g={g_score:.2f}, h={h_score:.2f}, f={g_score + h_score:.2f})"
                    current_surf = font.render(current_text, True, (255, 100, 100))
                    screen.blit(current_surf, (10, info_y + 40))

                # Score display mode
                score_mode_text = f"Showing: {'F-Scores' if show_f_scores else 'G-Scores'} (press F to toggle)"
                score_mode_surf = font.render(score_mode_text, True, (200, 200, 200))
                screen.blit(score_mode_surf, (10, info_y + 60))

                # Controls info
                controls_text = "Space: Toggle Auto | ←/→: Navigate | ↑/↓: Speed | S: Save Screenshot"
                controls_surf = font.render(controls_text, True, (200, 200, 200))
                screen.blit(controls_surf, (10, info_y + 80))

                # Auto-play indicator
                auto_text = "Auto: ON" if auto_play else "Auto: OFF"
                auto_surf = font.render(auto_text, True, (0, 255, 0) if auto_play else (255, 0, 0))
                screen.blit(auto_surf, (window_width - 100, info_y))

                # Title
                title_text = "Red Ghost A* Algorithm Visualization"
                title_surf = title_font.render(title_text, True, (255, 80, 80))
                screen.blit(title_surf, (window_width // 2 - title_surf.get_width() // 2, info_y + 5))

            # Update display
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python red_ghost_visualization.py maze.txt")
        sys.exit(1)

    # Initialize and solve
    ghost = RedGhostAStar(sys.argv[1])
    print("Solving with Red Ghost A* algorithm...")
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
        ghost.output_image("red_ghost.png", show_solution=True, show_explored=False)
        ghost.output_image("red_ghost_explored.png", show_solution=True, show_explored=True)

        # Start visualization
        print("\nStarting visualization...")
        print("Controls:")
        print("  Left/Right arrows: Navigate through steps")
        print("  Space: Toggle auto-play")
        print("  Up/Down arrows: Adjust auto-play speed")
        print("  F: Toggle between G-scores and F-scores display")
        print("  S: Save current view as PNG")
        print("  Close window to exit")
        ghost.visualize_pygame()
    else:
        print("No solution found!")