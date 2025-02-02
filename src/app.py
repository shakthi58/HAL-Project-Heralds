import pygame
import random
import time

# Pygame Configuration
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Control Simulation with Emergency Vehicles")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (169, 169, 169)
BLUE = (0, 0, 255)  # Emergency vehicle color
YELLOW = (255, 255, 0)  # Yellow for emergency vehicle flashing
LIGHT_BLUE = (173, 216, 230)  # Light blue for background
ROAD_COLOR = (50, 50, 50)  # Dark grey road color
DIVIDER_COLOR = (255, 255, 255)  # White divider color

# Constants
ROAD_WIDTH = 100
VEHICLE_WIDTH = 30  # Adjusted for image size
VEHICLE_HEIGHT = 60  # Adjusted for image size
TRAFFIC_LIGHT_RADIUS = 20
GREEN_LIGHT_DURATION = 3  # Duration in seconds
MAX_VEHICLES = 10
EMERGENCY_VEHICLE_PROBABILITY = 0.1  # 10% chance to spawn an emergency vehicle

# Load vehicle images
normal_car_image = pygame.image.load("regular_car.png")  # Use your own image path
emergency_car_image = pygame.image.load("emergency_car.png")  # Use your own image path

# Scale images to fit the vehicle size
normal_car_image = pygame.transform.scale(normal_car_image, (VEHICLE_WIDTH, VEHICLE_HEIGHT))
emergency_car_image = pygame.transform.scale(emergency_car_image, (VEHICLE_WIDTH, VEHICLE_HEIGHT))

# Load Background Image (Replace with an actual background image)
background_image = pygame.image.load("background1.jpg")  # Use your own background image
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Traffic system state
traffic_queues = {
    "North": [],
    "South": [],
    "East": [],
    "West": [],
}

roads = list(traffic_queues.keys())

# Fonts for UI elements
font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 30)


class Vehicle:
    def __init__(self, x, y, road, is_emergency=False):
        self.x = x
        self.y = y
        self.road = road
        self.is_emergency = is_emergency
        self.image = emergency_car_image if is_emergency else normal_car_image
        self.flash_timer = 1  # To make emergency vehicles flash

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def move(self, current_green_road):
        """Move the vehicle only if the light for its road is green or it is an emergency vehicle."""
        speed = 4 if self.is_emergency else 2

        # Check if the current road has a green light or if it's an emergency vehicle
        if self.road == current_green_road or self.is_emergency:
            if self.road == "North":
                self.y += speed
            elif self.road == "South":
                self.y -= speed
            elif self.road == "East":
                self.x -= speed
            elif self.road == "West":
                self.x += speed

            # If it's an emergency vehicle, make it flash
            if self.is_emergency:
                self.flash_timer += 1
                if self.flash_timer % 20 < 10:
                    self.image = pygame.transform.flip(emergency_car_image, False, True)  # Flash effect
                else:
                    self.image = emergency_car_image


def spawn_vehicle(road, is_emergency=False):
    """Spawn a new vehicle at the start of the given road."""
    if road == "North":
        x, y = WIDTH // 2 - ROAD_WIDTH // 4, 0
    elif road == "South":
        x, y = WIDTH // 2 + ROAD_WIDTH // 4, HEIGHT
    elif road == "East":
        x, y = WIDTH, HEIGHT // 2 + ROAD_WIDTH // 4
    elif road == "West":
        x, y = 0, HEIGHT // 2 - ROAD_WIDTH // 4

    traffic_queues[road].append(Vehicle(x, y, road, is_emergency))


def draw_road():
    """Draw the roads and intersection with smooth rounded corners."""
    # Draw background image
    screen.blit(background_image, (0, 0))
    
    # Draw the road with smoother, rounded corners
    pygame.draw.rect(screen, ROAD_COLOR, (WIDTH // 2 - ROAD_WIDTH // 2, 0, ROAD_WIDTH, HEIGHT), border_radius=0)
    pygame.draw.rect(screen, ROAD_COLOR, (0, HEIGHT // 2 - ROAD_WIDTH // 2, WIDTH, ROAD_WIDTH), border_radius=0)
    
    # Draw lane dividers
    divider_y = HEIGHT // 2
    pygame.draw.line(screen, DIVIDER_COLOR, (WIDTH // 10- ROAD_WIDTH // 1, divider_y), (WIDTH // 1 + ROAD_WIDTH // 1, divider_y), 6)
    pygame.draw.line(screen, DIVIDER_COLOR, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 6)

    # Draw dashed lines on the roads for lanes
    #for i in range(0, WIDTH, 60):
        #pygame.draw.rect(screen, DIVIDER_COLOR, (i, HEIGHT // 2 - ROAD_WIDTH // 4, 10, 15))
    
    #for i in range(0, HEIGHT, 60):
        #pygame.draw.rect(screen, DIVIDER_COLOR, (WIDTH // 2 - ROAD_WIDTH // 4, i, 15, 10))


def draw_traffic_lights(current_green_road):
    """Draw traffic lights for each road with smooth glowing effect."""
    light_positions = {
        "North": (WIDTH // 2, HEIGHT // 2 - ROAD_WIDTH),
        "South": (WIDTH // 2, HEIGHT // 2 + ROAD_WIDTH),
        "East": (WIDTH // 2 + ROAD_WIDTH, HEIGHT // 2),
        "West": (WIDTH // 2 - ROAD_WIDTH, HEIGHT // 2),
    }

    for road, position in light_positions.items():
        color = GREEN if road == current_green_road else RED
        pygame.draw.circle(screen, color, position, TRAFFIC_LIGHT_RADIUS)
        pygame.draw.circle(screen, (0, 0, 0), position, TRAFFIC_LIGHT_RADIUS - 6)


def update_traffic_lights():
    """Select the road with the most vehicles or emergency vehicle priority."""
    # First, prioritize roads with emergency vehicles
    for road, vehicles in traffic_queues.items():
        if any(vehicle.is_emergency for vehicle in vehicles):
            return road

    # If no emergency vehicle, prioritize the road with the most vehicles
    road_vehicle_counts = {road: len(vehicles) for road, vehicles in traffic_queues.items()}
    # Sort roads based on the number of vehicles in descending order
    sorted_roads = sorted(road_vehicle_counts, key=road_vehicle_counts.get, reverse=True)
    return sorted_roads[0]  # Return the road with the most vehicles


def update_and_draw_vehicles(current_green_road):
    """Move and draw vehicles for all roads based on traffic lights."""
    for road, vehicles in traffic_queues.items():
        for vehicle in vehicles[:]:  # Copy the list to safely remove elements
            vehicle.move(current_green_road)
            vehicle.draw()

            # Remove vehicles that have crossed the intersection
            if (road == "North" and vehicle.y > HEIGHT // 2) or \
               (road == "South" and vehicle.y < HEIGHT // 2) or \
               (road == "East" and vehicle.x < WIDTH // 2) or \
               (road == "West" and vehicle.x > WIDTH // 2):
                vehicles.remove(vehicle)


def display_vehicle_counts():
    """Display vehicle counts for each road."""
    y_offset = 10
    for road, vehicles in traffic_queues.items():
        emergency_count = sum(1 for v in vehicles if v.is_emergency)
        text = f"{road} Road: {len(vehicles)} vehicles (Emergencies: {emergency_count})"
        text_surface = small_font.render(text, True, WHITE)
        screen.blit(text_surface, (10, y_offset))
        y_offset += 30


def total_vehicle_count():
    """Calculate the total number of vehicles on all roads."""
    return sum(len(vehicles) for vehicles in traffic_queues.values())


def main():
    clock = pygame.time.Clock()
    running = True
    current_green_road = random.choice(roads)  # Start with a random road
    time_last_switch = time.time()
    spawn_timer = time.time()

    while running:
        screen.fill(LIGHT_BLUE)  # Fill background with a light blue color
        draw_road()  # Draw roads and intersection
        draw_traffic_lights(current_green_road)  # Draw traffic lights
        update_and_draw_vehicles(current_green_road)  # Move vehicles and draw them
        display_vehicle_counts()  # Display the counts of vehicles and emergencies

        # Update traffic light every GREEN_LIGHT_DURATION seconds
        if time.time() - time_last_switch >= GREEN_LIGHT_DURATION:
            time_last_switch = time.time()
            current_green_road = update_traffic_lights()

        # Spawn new vehicles randomly if total vehicle count is below the max limit
        if time.time() - spawn_timer >= 0.5 and total_vehicle_count() < MAX_VEHICLES:
            is_emergency = random.random() < EMERGENCY_VEHICLE_PROBABILITY  # Random chance to spawn emergency
            spawn_vehicle(random.choice(roads), is_emergency)
            spawn_timer = time.time()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    spawn_vehicle("North", is_emergency=True)  # Emergency vehicle spawn
                elif event.key == pygame.K_DOWN:
                    spawn_vehicle("South", is_emergency=True)  # Emergency vehicle spawn
                elif event.key == pygame.K_LEFT:
                    spawn_vehicle("West", is_emergency=True)  # Emergency vehicle spawn
                elif event.key == pygame.K_RIGHT:
                    spawn_vehicle("East", is_emergency=True)  # Emergency vehicle spawn

        pygame.display.flip()
        clock.tick(30)  # Limit the frame rate

    pygame.quit()


if __name__ == "__main__":
    main()
