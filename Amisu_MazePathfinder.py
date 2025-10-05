"""
Maze Solver and Pathfinder - Lab 1

This script generates a maze, finds the shortest path using A*,
and provides an animated visualization with Pygame.

Acknowledgments:
Portions of this code were developed with assistance from Google's Gemini AI,
which was used for algorithm implementation, optimization, and debugging.
"""





import pygame
import random
import heapq
import time

# --- Constants ---

# Maze dimensions (must be odd numbers for the generator to work well)
WIDTH = 21
HEIGHT = 21

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (40, 148, 80)     # Start
RED = (148, 57, 40)       # End
PURPLE = (148, 40, 117)   # Solution Path
MUSTARD = (148, 110, 40) # Visited Cells
GRAY = (211, 211, 211)    # Grid lines
FAINT_BLUE = (173, 216, 230) # Dead end Paths

# Screen dimensions
CELL_SIZE = 30
MARGIN = 1
SCREEN_WIDTH = (CELL_SIZE + MARGIN) * WIDTH + MARGIN
SCREEN_HEIGHT = (CELL_SIZE + MARGIN) * HEIGHT + MARGIN


# --- Maze Generation (Randomized DFS) ---
def geneerate_maze(width, height):
    """Generates a maze using Randomized DFS and adds an entrance/exit."""
    maze = [[1 for _ in range(width)] for _ in range(height)]
    stack = []
    start_x = random.randrange(1, width, 2)
    start_y = random.randrange(1, height, 2)
    maze[start_y][start_x] = 0
    stack.append((start_x, start_y))

    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
            nx, ny = x + dx, y + dy
            if 0 < nx < width and 0 < ny < height and maze[ny][nx] == 1:
                neighbors.append((nx, ny))
        
        if neighbors:
            next_x, next_y = random.choice(neighbors)
            wall_x = x + (next_x - x) // 2
            wall_y = y + (next_y - y) // 2
            maze[wall_y][wall_x] = 0
            maze[next_y][next_x] = 0
            stack.append((next_x, next_y))
        else:
            stack.pop()
    
     # Tese: Add loops by knocking down a small percentage of remaining walls
    walls_to_remove = int(width * height * 0.05) # Remove 5% of walls
    for _ in range(walls_to_remove):
        wall_x, wall_y = random.randint(1, width - 2), random.randint(1, height - 2)
        # Ensure it's a wall that separates two paths
        if maze[wall_y][wall_x] == 1:
            # Horizontal wall
            if maze[wall_y][wall_x-1] == 0 and maze[wall_y][wall_x+1] == 0:
                maze[wall_y][wall_x] = 0
            # Vertical wall
            elif maze[wall_y-1][wall_x] == 0 and maze[wall_y+1][wall_x] == 0:
                maze[wall_y][wall_x] = 0
            
    # Create a clear entrance and exit on the maze border
    maze[1][0] = 0  # Entrance near the top-left
    maze[height - 2][width - 1] = 0  # Exit near the bottom-right
            
    return maze

# TEST: Function to find all dead-end cells in the maze
def find_dead_ends(maze):
    dead_ends = set()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if maze[y][x] == 0: # It's a path
                neighbors = 0
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    if 0 <= x + dx < WIDTH and 0 <= y + dy < HEIGHT and maze[y + dy][x + dx] == 0:
                        neighbors += 1
                if neighbors == 1: # A path cell with only one neighbor is a dead end
                    dead_ends.add((x, y))
    return dead_ends


# --- Pathfinding (A* Search Algorithm) ---
def heuristic(a, b):
    """Calculates the Manhattan distance heuristic."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(maze, start, end):
    """Finds the shortest path and tracks visited cells using A*."""
    open_list = []
    heapq.heappush(open_list, (0, start))
    
    came_from = {}
    g_cost = { (x,y): float('inf') for y, row in enumerate(maze) for x, val in enumerate(row) }
    g_cost[start] = 0
    f_cost = { (x,y): float('inf') for y, row in enumerate(maze) for x, val in enumerate(row) }
    f_cost[start] = heuristic(start, end)
    
    visited_cells = set()
    
    while open_list:
        current_f_cost, current_node = heapq.heappop(open_list)
        visited_cells.add(current_node)
        
        if current_node == end:
            path = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            path.append(start)
            return path[::-1], visited_cells

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current_node[0] + dx, current_node[1] + dy)
            if not (0 <= neighbor[0] < len(maze[0]) and 0 <= neighbor[1] < len(maze)):
                continue
            if maze[neighbor[1]][neighbor[0]] == 1:
                continue
            tentative_g_cost = g_cost[current_node] + 1
            if tentative_g_cost < g_cost[neighbor]:
                came_from[neighbor] = current_node
                g_cost[neighbor] = tentative_g_cost
                f_cost[neighbor] = tentative_g_cost + heuristic(neighbor, end)
                heapq.heappush(open_list, (f_cost[neighbor], neighbor))

    return None, visited_cells


# --- Main Application Function ---
def main():
    """Main function with animated A* search, legend, and stats."""
    pygame.init()
    
    legend_width = 250
    screen = pygame.display.set_mode((SCREEN_WIDTH + legend_width, SCREEN_HEIGHT))
    pygame.display.set_caption("Maze Solver")
    
    font = pygame.font.SysFont('Arial', 20)
    
    # --- Data Generation ---
    maze = geneerate_maze(WIDTH, HEIGHT)
    dead_ends = find_dead_ends(maze)
    start_point = (0, 1)
    end_point = (WIDTH - 1, HEIGHT - 2)
    
    # --- A* Initialization ---
    open_list = []
    heapq.heappush(open_list, (0, start_point))
    came_from = {}

    # CORRECTED: Simplified and corrected dictionary initialization
    g_cost = {}
    f_cost = {}
    for y in range(HEIGHT):
        for x in range(WIDTH):
            g_cost[(x,y)] = float('inf')
            f_cost[(x,y)] = float('inf')
            
    g_cost[start_point] = 0
    f_cost[start_point] = heuristic(start_point, end_point)
    
    # --- Stats variables ---
    visited_cells = set()
    solution_path = None
    path_found = False
    path_length = 0
    start_time = time.time()
    elapsed_time = 0

    # Main Game Loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        # --- Animated A* Step ---
        if open_list and not path_found:
            _, current_node = heapq.heappop(open_list)
            visited_cells.add(current_node)
            
            if current_node == end_point:
                path_found = True
                elapsed_time = time.time() - start_time
                
                path = []
                while current_node in came_from:
                    path.append(current_node)
                    current_node = came_from[current_node]
                path.append(start_point)
                solution_path = path[::-1]
                path_length = len(solution_path)

            # Check neighbors
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current_node[0] + dx, current_node[1] + dy)
                if not (0 <= neighbor[0] < WIDTH and 0 <= neighbor[1] < HEIGHT) or maze[neighbor[1]][neighbor[0]] == 1:
                    continue
                
                tentative_g_cost = g_cost[current_node] + 1
                if tentative_g_cost < g_cost[neighbor]:
                    came_from[neighbor] = current_node
                    g_cost[neighbor] = tentative_g_cost
                    f_cost[neighbor] = tentative_g_cost + heuristic(neighbor, end_point)
                    heapq.heappush(open_list, (f_cost[neighbor], neighbor))

        # --- Drawing Logic ---
        screen.fill(GRAY)
        
        solution_set = set(solution_path) if solution_path else set()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                pos = (x, y)
                color = WHITE
                if maze[y][x] == 1: color = BLACK
                elif pos in solution_set: color = PURPLE
                elif pos in dead_ends: color = FAINT_BLUE
                elif pos in visited_cells: color = MUSTARD
                
                if pos == start_point: color = GREEN
                elif pos == end_point: color = RED
                
                pygame.draw.rect(screen, color,
                                 [(MARGIN + CELL_SIZE) * x + MARGIN,
                                  (MARGIN + CELL_SIZE) * y + MARGIN,
                                  CELL_SIZE,
                                  CELL_SIZE])
                                  
        # --- Draw Legend and Stats ---
        pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH, 0, legend_width, SCREEN_HEIGHT))
        
        legend_items = [
            (GREEN, "Start"), (RED, "End"), (PURPLE, "Solution Path"),
            (MUSTARD, "Visited Cell"), (FAINT_BLUE, "Dead End"),
            (WHITE, "Path"), (BLACK, "Wall")
        ]
        
        legend_y_start = 40
        for i, (color, text) in enumerate(legend_items):
            pygame.draw.rect(screen, color, (SCREEN_WIDTH + 20, legend_y_start + i * 30, 20, 20))
            text_surface = font.render(text, True, BLACK)
            screen.blit(text_surface, (SCREEN_WIDTH + 50, legend_y_start + i * 30))
        
        stats_y_start = legend_y_start + len(legend_items) * 30 + 20
        visited_text = font.render(f"Visited Cells: {len(visited_cells)}", True, BLACK)
        screen.blit(visited_text, (SCREEN_WIDTH + 20, stats_y_start))
        
        path_text = font.render(f"Path Length: {path_length}", True, BLACK)
        screen.blit(path_text, (SCREEN_WIDTH + 20, stats_y_start + 30))

        time_text = font.render(f"Time: {elapsed_time:.2f} s", True, BLACK)
        screen.blit(time_text, (SCREEN_WIDTH + 20, stats_y_start + 60))
        
        pygame.display.flip()
        pygame.time.delay(25)

    pygame.quit()
# --- Script Entry Point ---
if __name__ == '__main__':
    main()
