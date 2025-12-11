import pygame
import sys
import random
import time

pygame.init()

# Game settings
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
FPS = 10

# Colors
BLACK = (0, 0, 0)
SNAKE_COLOR = (0, 255, 0)
WHITE = (255, 255, 255)
DARK_GREEN = (0, 180, 0)
BLOCK_COLOR = (255, 165, 0)
PURPLE = (128, 0, 128)

# Food colors
REGULAR_FOOD = (255, 0, 0)      # Red - normal food
GOLDEN_FOOD = (255, 215, 0)     # Gold - bonus points
SPEED_FOOD = (0, 191, 255)      # Blue - speed up
SLOW_FOOD = (255, 0, 255)       # Purple - slow down
DOUBLE_FOOD = (50, 205, 50)     # Lime - double points
GHOST_FOOD = (192, 192, 192)    # Silver - ghost mode

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game - Collect Food Edition!')

# Fonts
font = pygame.font.SysFont('arial', 20)
large_font = pygame.font.SysFont('arial', 40, bold=True)

class Snake:
    def __init__(self):
        self.body = [(100, 50), (90, 50), (80, 50)]
        self.direction = 'RIGHT'
        self.next_direction = 'RIGHT'
        self.grow = False
        self.growth_amount = 1  # Normal growth
        self.score_multiplier = 1
        self.ghost_mode = False
        self.ghost_timer = 0
        self.speed_multiplier = 1.0
        self.speed_timer = 0
        
    def move(self, current_time):
        # Apply speed multiplier
        effective_speed = FPS * self.speed_multiplier
        move_delay = 1000 / effective_speed
        
        if current_time - getattr(self, 'last_move_time', 0) < move_delay:
            return
            
        # Update direction
        self.direction = self.next_direction
        
        head = self.body[0]
        
        # Calculate new head position with wrapping
        if self.direction == 'RIGHT':
            new_head = ((head[0] + CELL_SIZE) % WIDTH, head[1])
        elif self.direction == 'LEFT':
            new_head = ((head[0] - CELL_SIZE) % WIDTH, head[1])
        elif self.direction == 'UP':
            new_head = (head[0], (head[1] - CELL_SIZE) % HEIGHT)
        elif self.direction == 'DOWN':
            new_head = (head[0], (head[1] + CELL_SIZE) % HEIGHT)
        
        # Add new head
        self.body.insert(0, new_head)
        
        # Grow if needed
        if self.grow and self.growth_amount > 0:
            self.growth_amount -= 1
            if self.growth_amount == 0:
                self.grow = False
        else:
            # Remove tail if not growing
            if not self.grow:
                self.body.pop()
        
        self.last_move_time = current_time
        
        # Update power-up timers
        if self.ghost_mode and current_time > self.ghost_timer:
            self.ghost_mode = False
            
        if self.speed_multiplier != 1.0 and current_time > self.speed_timer:
            self.speed_multiplier = 1.0
    
    def change_direction(self, direction):
        if (direction == 'UP' and self.direction != 'DOWN'):
            self.next_direction = 'UP'
        elif (direction == 'DOWN' and self.direction != 'UP'):
            self.next_direction = 'DOWN'
        elif (direction == 'LEFT' and self.direction != 'RIGHT'):
            self.next_direction = 'LEFT'
        elif (direction == 'RIGHT' and self.direction != 'LEFT'):
            self.next_direction = 'RIGHT'
    
    def draw(self):
        for i, segment in enumerate(self.body):
            # Ghost mode effect
            if self.ghost_mode:
                # Transparent effect for ghost mode
                color = (SNAKE_COLOR[0], SNAKE_COLOR[1], SNAKE_COLOR[2], 128)
                surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(surface, color, (0, 0, CELL_SIZE, CELL_SIZE))
                screen.blit(surface, segment)
            else:
                # Normal snake with gradient
                if i == 0:
                    color = DARK_GREEN  # Head
                else:
                    intensity = max(100, 255 - (i * 10))
                    color = (0, intensity, 0)
                
                pygame.draw.rect(screen, color, 
                               pygame.Rect(segment[0], segment[1], 
                                          CELL_SIZE, CELL_SIZE))
            
            # Draw eyes on head
            if i == 0:
                eye_size = 4
                if self.direction == 'RIGHT':
                    eye_pos = (segment[0] + CELL_SIZE - 6, segment[1] + 5)
                elif self.direction == 'LEFT':
                    eye_pos = (segment[0] + 6, segment[1] + 5)
                elif self.direction == 'UP':
                    eye_pos = (segment[0] + 5, segment[1] + 6)
                else:  # DOWN
                    eye_pos = (segment[0] + 5, segment[1] + CELL_SIZE - 6)
                
                pygame.draw.circle(screen, WHITE, eye_pos, eye_size)
    
    def check_self_collision(self):
        if self.ghost_mode:
            return False  # No collision in ghost mode
        head = self.body[0]
        return head in self.body[1:]

class Food:
    def __init__(self, food_type='regular'):
        self.food_type = food_type
        self.color = REGULAR_FOOD
        self.points = 10
        self.duration = 0
        self.regenerate()
        
    def set_type(self, food_type):
        self.food_type = food_type
        types = {
            'regular': {'color': REGULAR_FOOD, 'points': 10, 'duration': 0},
            'golden': {'color': GOLDEN_FOOD, 'points': 50, 'duration': 0},
            'speed': {'color': SPEED_FOOD, 'points': 20, 'duration': 5000},
            'slow': {'color': SLOW_FOOD, 'points': 15, 'duration': 5000},
            'double': {'color': DOUBLE_FOOD, 'points': 10, 'duration': 10000},
            'ghost': {'color': GHOST_FOOD, 'points': 25, 'duration': 8000}
        }
        
        if food_type in types:
            self.color = types[food_type]['color']
            self.points = types[food_type]['points']
            self.duration = types[food_type]['duration']
    
    def regenerate(self):
        self.position = (random.randrange(0, (WIDTH // CELL_SIZE)) * CELL_SIZE,
                        random.randrange(0, (HEIGHT // CELL_SIZE)) * CELL_SIZE)
        # Randomly select food type with different probabilities
        food_types = ['regular', 'regular', 'regular',  # 60% chance
                     'golden',                         # 20% chance
                     'speed', 'slow', 'double', 'ghost']  # 5% each
        
        self.set_type(random.choice(food_types))
    
    def draw(self):
        # Draw main food body
        pygame.draw.rect(screen, self.color, 
                        pygame.Rect(self.position[0], self.position[1],
                                   CELL_SIZE, CELL_SIZE))
        
        # Special effects for different food types
        if self.food_type == 'golden':
            # Golden shine effect
            pygame.draw.circle(screen, (255, 255, 200), 
                             (self.position[0] + 10, self.position[1] + 10), 6)
        elif self.food_type == 'speed':
            # Speed lines
            for i in range(3):
                offset = i * 3
                pygame.draw.line(screen, WHITE,
                               (self.position[0] + offset, self.position[1] + 5),
                               (self.position[0] + offset, self.position[1] + 15), 2)
        elif self.food_type == 'ghost':
            # Ghost effect (transparent)
            surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(surface, (*self.color, 180), (0, 0, CELL_SIZE, CELL_SIZE))
            screen.blit(surface, self.position)

class DangerousBlock:
    def __init__(self):
        self.width = random.randint(1, 2) * CELL_SIZE
        self.speed = random.randint(1, 2)
        self.regenerate()
    
    def regenerate(self):
        self.x = random.randint(0, WIDTH - self.width)
        self.y = 0
        self.active = True
    
    def move(self):
        if self.active:
            self.y += self.speed
            if self.y > HEIGHT:
                self.regenerate()
    
    def draw(self):
        if self.active:
            pygame.draw.rect(screen, BLOCK_COLOR,
                           pygame.Rect(self.x, self.y, self.width, CELL_SIZE))
    
    def check_collision(self, snake):
        if snake.ghost_mode:
            return False  # No collision in ghost mode
            
        if not self.active:
            return False
        
        for segment in snake.body:
            snake_rect = pygame.Rect(segment[0], segment[1], 
                                    CELL_SIZE, CELL_SIZE)
            block_rect = pygame.Rect(self.x, self.y, self.width, CELL_SIZE)
            
            if snake_rect.colliderect(block_rect):
                return True
        return False

def display_game_info(score, level, snake, current_time):
    # Score display
    score_text = font.render(f'Score: {score}', True, WHITE)
    level_text = font.render(f'Level: {level}', True, WHITE)
    
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 35))
    
    # Active power-ups display
    y_offset = 60
    if snake.score_multiplier > 1:
        multi_text = font.render(f'x{snake.score_multiplier} Points!', True, DOUBLE_FOOD)
        screen.blit(multi_text, (10, y_offset))
        y_offset += 25
        
    if snake.ghost_mode:
        time_left = max(0, (snake.ghost_timer - current_time) // 1000)
        ghost_text = font.render(f'Ghost: {time_left}s', True, GHOST_FOOD)
        screen.blit(ghost_text, (10, y_offset))
        y_offset += 25
        
    if snake.speed_multiplier != 1.0:
        time_left = max(0, (snake.speed_timer - current_time) // 1000)
        speed_text = font.render(f'Speedy: {time_left}s', True, SPEED_FOOD)
        screen.blit(speed_text, (10, y_offset))
        y_offset += 25

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, (30, 30, 30), (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, (30, 30, 30), (0, y), (WIDTH, y), 1)

def start_screen():
    screen.fill(BLACK)
    
    title = large_font.render('Snake Food Collector!', True, SNAKE_COLOR)
    
    instructions = [
        "Collect different types of food:",
        "Red - Normal food (10 points)",
        "Gold - Golden apple (50 points!)",
        "Blue - Speed boost (20 points)",
        "Purple - Slow down (15 points)",
        "Lime - Double points (10 points)",
        "Silver - Ghost mode (25 points)",
        "",
        "Avoid orange falling blocks",
        "Snake wraps around edges",
        "Press SPACE to start"
    ]
    
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
    
    for i, instruction in enumerate(instructions):
        color = WHITE
        if "Red" in instruction: color = REGULAR_FOOD
        elif "Gold" in instruction: color = GOLDEN_FOOD
        elif "Blue" in instruction: color = SPEED_FOOD
        elif "Purple" in instruction: color = SLOW_FOOD
        elif "Lime" in instruction: color = DOUBLE_FOOD
        elif "Silver" in instruction: color = GHOST_FOOD
        
        text = font.render(instruction, True, color)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 100 + i * 25))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

def game_over_screen(score):
    screen.fill(BLACK)
    
    game_over = large_font.render('Game Over!', True, REGULAR_FOOD)
    final_score = font.render(f'Final Score: {score}', True, SNAKE_COLOR)
    high_score = font.render(f'High Score: {get_high_score(score)}', True, GOLDEN_FOOD)
    restart_text = font.render('Press R to restart or ESC to quit', True, WHITE)
    
    screen.blit(game_over, (WIDTH//2 - game_over.get_width()//2, 80))
    screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, 150))
    screen.blit(high_score, (WIDTH//2 - high_score.get_width()//2, 180))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 250))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False
    return False

def get_high_score(new_score):
    try:
        with open('snake_high_score.txt', 'r') as f:
            high_score = int(f.read())
    except:
        high_score = 0
    
    if new_score > high_score:
        high_score = new_score
        with open('snake_high_score.txt', 'w') as f:
            f.write(str(high_score))
    
    return high_score

def main_game():
    snake = Snake()
    foods = [Food() for _ in range(3)]  # Multiple foods on screen
    
    blocks = [DangerousBlock() for _ in range(2)]
    
    score = 0
    level = 1
    game_speed = FPS
    
    clock = pygame.time.Clock()
    
    while True:
        current_time = pygame.time.get_ticks()
        
        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction('UP')
                elif event.key == pygame.K_DOWN:
                    snake.change_direction('DOWN')
                elif event.key == pygame.K_LEFT:
                    snake.change_direction('LEFT')
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction('RIGHT')
        
        # Move snake
        snake.move(current_time)
        
        # Move blocks
        for block in blocks:
            block.move()
            
            if block.check_collision(snake):
                return score
        
        # Check food collision for all foods
        for food in foods[:]:  # Use slice to avoid modification during iteration
            if snake.body[0] == food.position:
                # Calculate score with multiplier
                points_earned = food.points * snake.score_multiplier
                score += points_earned
                
                # Apply food effects
                if food.food_type == 'regular':
                    snake.grow = True
                    snake.growth_amount = 1
                    
                elif food.food_type == 'golden':
                    snake.grow = True
                    snake.growth_amount = 3  # Grow more
                    
                elif food.food_type == 'speed':
                    snake.speed_multiplier = 1.5
                    snake.speed_timer = current_time + food.duration
                    snake.grow = True
                    
                elif food.food_type == 'slow':
                    snake.speed_multiplier = 0.7
                    snake.speed_timer = current_time + food.duration
                    snake.grow = True
                    
                elif food.food_type == 'double':
                    snake.score_multiplier = 2
                    snake.grow = True
                    # Set timer for double points
                    setattr(snake, 'double_timer', current_time + food.duration)
                    
                elif food.food_type == 'ghost':
                    snake.ghost_mode = True
                    snake.ghost_timer = current_time + food.duration
                    snake.grow = True
                
                # Regenerate food
                food.regenerate()
                
                # Level up system
                if score % 50 == 0:
                    level += 1
                    if game_speed < 15:
                        game_speed += 1
                    
                    if level <= 6:
                        blocks.append(DangerousBlock())
                    
                    # Add more food at higher levels
                    if level % 2 == 0 and len(foods) < 5:
                        foods.append(Food())
        
        # Check timer for double points
        if hasattr(snake, 'double_timer') and current_time > snake.double_timer:
            snake.score_multiplier = 1
            delattr(snake, 'double_timer')
        
        # Check self collision
        if snake.check_self_collision():
            return score
        
        # Make sure food doesn't spawn on snake
        for food in foods:
            while food.position in snake.body:
                food.regenerate()
        
        # Draw everything
        screen.fill(BLACK)
        draw_grid()
        
        snake.draw()
        for food in foods:
            food.draw()
        for block in blocks:
            block.draw()
        
        display_game_info(score, level, snake, current_time)
        
        # Draw border
        pygame.draw.rect(screen, (60, 60, 60), (0, 0, WIDTH, HEIGHT), 2)
        
        pygame.display.flip()
        clock.tick(game_speed)

# Main game loop
while True:
    start_screen()
    final_score = main_game()
    
    if not game_over_screen(final_score):
        break

pygame.quit()
sys.exit()
