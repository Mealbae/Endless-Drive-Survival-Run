from OpenGL.GL import *
from OpenGL.GLUT import *  
from OpenGL.GLUT.fonts import GLUT_BITMAP_HELVETICA_18 
from OpenGL.GLU import *
import math
import time
import random

# Window size
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800

# Car state
car_pos = [0, 0, 0]
car_angle = 0
camera_distance = 200
track_length = 4000  # Increased the track length
arena_size = 100  # Define the size of the arena
checkpoints = []  # Initialize checkpoints list
for _ in range(int(track_length / 500)):
    x = random.uniform(-arena_size, arena_size)  # Random x-coordinate within the arena
    z = random.uniform(0, track_length)  # Random z-coordinate along the track
    checkpoints.append((x, z))
score = 0  # Initialize score

# Added a power-up feature that spawns randomly and increases the car's speed when collected.
power_up_active = False
power_up_position = [random.randint(-100, 100), -9.5, random.randint(-2000, 0)]  # Random initial position
power_up_timer = 0
power_up_duration = 5000  # Power-up lasts for 5 seconds

# Added an obstacle system with penalties for hitting obstacles.
obstacles = []
penalty = 0

# Added a fuel system with a fuel gauge and fuel pickups.
fuel = 100  # Initialize fuel level
fuel_pickup_position = None  # Position of the fuel pickup
fuel_depletion_timer = 0  # Timer to track fuel depletion
fuel_spawn_timer = 0  # Timer to track fuel pickup spawning
fuel_depletion_interval = 7000  # Fuel starts depleting after 7 seconds (in milliseconds)
fuel_spawn_interval = 6000  # Fuel pickup spawns every 6 seconds (in milliseconds)

# Added random challenges like collecting points or fuel pickups.
current_challenge = None  # Stores the current challenge
challenge_progress = 0  # Tracks progress of the current challenge
challenge_target = 0  # Target to complete the challenge
challenge_timer = 0  # Timer to track challenge duration
challenge_duration = 20000  # Challenges last for 20 seconds (in milliseconds)

# Added a feature to spawn mines every 15 seconds, causing an instant game over on collision.
mine_position = None  # Position of the mine
mine_spawn_timer = 0  # Timer to track mine spawning
mine_spawn_interval = 15000  # Mine spawns every 15 seconds (in milliseconds)

# Added a cheat mode feature to make the car invulnerable to obstacles and mines.
cheat_mode = False  # Initialize cheat mode as disabled

# Added a flag to track game over state
game_over = False


# Add a global variable to track input state
input_enabled = True  # Initially, all inputs are enabled

def toggle_cheat_mode():
    global cheat_mode
    cheat_mode = not cheat_mode  # Toggle cheat mode on/off
    if cheat_mode:
        print("Cheat mode enabled! Car is now invulnerable.")
    else:
        print("Cheat mode disabled! Car is now vulnerable.")

# Added a night mode feature with a toggle function and updated lighting setup.
night_mode = False  # Initialize night mode as disabled

def toggle_night_mode():
    global night_mode
    night_mode = not night_mode  # Toggle night mode on/off
    if night_mode:
        print("Night mode enabled! Enjoy the stars.")
    else:
        print("Night mode disabled! Back to daylight.")

# Adjusted night mode to only change the lighting to deep navy blue while keeping other components' colors unchanged.
def set_lighting():
    if night_mode:
        glClearColor(0.0, 0.0, 0.1, 1)  # Deep navy blue sky for night mode
    else:
        glClearColor(0.5, 0.8, 0.95, 1)  # Light blue sky for day mode
    glDisable(GL_LIGHTING)  # No additional lighting for both modes

# Generate random obstacles on the road
def generate_obstacles():
    global obstacles
    for i in range(10):  # Generate 10 obstacles initially
        x = random.randint(-90, 90)  # Ensure obstacles are within road bounds
        z = random.randint(-track_length, 0)
        obstacles.append([x, -9.5, z])

def draw_obstacles():
    glColor3f(1, 0, 0)  # Red color for obstacles
    for obstacle in obstacles:
        glPushMatrix()
        glTranslatef(*obstacle)
        glutSolidCone(10, 20, 20, 20)  # Draw a cone as an obstaclewww
        glPopMatrix()

# Created a reusable function for handling game over conditions.
def trigger_game_over():
    global penalty, mine_position, game_over
    penalty = 5  # Set penalty to 5 to trigger the game over overlay
    mine_position = None  # Clear mine position to prevent further collisions
    game_over = True  # Set the game over flag
    print("Game Over! Press 'R' to restart.")

# Added a function to reset the game state
def reset_game():
    global car_pos, car_angle, camera_distance, score, penalty, fuel, game_over, input_enabled
    car_pos = [0, 0, 0]
    car_angle = 0
    camera_distance = 200
    score = 0
    penalty = 0
    fuel = 100
    game_over = False
    input_enabled = True  # Re-enable inputs
    print("Game restarted!")

# Move the handle_game_over function above check_obstacle_collision
def handle_game_over(reason):
    global penalty, mine_position, game_over, input_enabled
    penalty = 5  # Set penalty to 5 to trigger the game over overlay
    mine_position = None  # Clear mine position to prevent further collisions
    game_over = True  # Set the game over flag
    input_enabled = False  # Disable all inputs except 'R'
    print(f"Game Over! Reason: {reason}. Press 'R' to restart.")

# Updated penalty logic to show the same game over overlay as when a mine is hit.
def check_obstacle_collision():
    global penalty, score, car_pos
    if cheat_mode:
        return  # Skip collision logic if cheat mode is enabled
    for obstacle in obstacles[:]:
        if abs(car_pos[0] - obstacle[0]) < 15 and abs(car_pos[2] - obstacle[2]) < 15:
            penalty += 1  # Increment penalty for hitting an obstacle
            score = max(0, score - 1)  # Deduct a point, ensuring score doesn't go below 0
            print(f"Obstacle hit! Penalty: {penalty}, Score: {score}")
            obstacles.remove(obstacle)  # Remove the obstacle after collision

            if penalty >= 5:  # Check if penalty reaches 5
                handle_game_over("Hit too many obstacles")  # Use the new function
                return

# Adjusted the wheel positions to ensure they remain on the road.
def draw_car():
    glPushMatrix()
    glTranslatef(*car_pos)
    glRotatef(car_angle, 0, 1, 0)

    # Draw car body
    glPushMatrix()
    glScalef(1.5, 0.5, 3)
    glColor3f(1, 0, 0)  # Red body
    glutSolidCube(20)
    glPopMatrix()

    # Draw car roof
    glPushMatrix()
    glTranslatef(0, 10, 0)  # Position the roof above the body
    glScalef(1.2, 0.5, 2)
    glColor3f(0.8, 0.8, 0.8)  # Light gray roof
    glutSolidCube(20)
    glPopMatrix()

    # Draw front windshield
    glPushMatrix()
    glTranslatef(0, 5, 15)  # Position the windshield
    glRotatef(-45, 1, 0, 0)  # Tilt the windshield
    glScalef(1.2, 0.1, 0.8)
    glColor4f(0.2, 0.6, 1, 0.5)  # Transparent blue glass
    glutSolidCube(20)
    glPopMatrix()

    # Draw wheels
    glColor3f(0, 0, 0)  # Black wheels
    for x_offset in [-10, 10]:  # Adjusted wheel positions for better alignment
        for z_offset in [-25, 25]:
            glPushMatrix()
            glTranslatef(x_offset, -5, z_offset)  # Raised wheels slightly to keep them on the road
            glRotatef(90, 0, 1, 0)
            glutSolidTorus(2, 5, 12, 12)
            glPopMatrix()

    # Draw headlights
    glColor3f(1, 1, 0)  # Yellow headlights
    for x_offset in [-7, 7]:
        glPushMatrix()
        glTranslatef(x_offset, 0, 30)  # Position headlights at the front
        glutSolidSphere(3, 10, 10)
        glPopMatrix()

    # Draw taillights
    glColor3f(1, 0, 0)  # Red taillights
    for x_offset in [-7, 7]:
        glPushMatrix()
        glTranslatef(x_offset, 0, -30)  # Position taillights at the back
        glutSolidSphere(3, 10, 10)
        glPopMatrix()

    glPopMatrix()

def draw_sidewalks():
    glColor3f(0.5, 0.5, 0.5)  # Gray color for sidewalks
    glBegin(GL_QUADS)
    # Left sidewalk
    glVertex3f(-110, -10, 0)
    glVertex3f(-100, -10, 0)
    glVertex3f(-100, -10, -track_length)
    glVertex3f(-110, -10, -track_length)

    # Right sidewalk
    glVertex3f(100, -10, 0)
    glVertex3f(110, -10, 0)
    glVertex3f(110, -10, -track_length)
    glVertex3f(100, -10, -track_length)
    glEnd()

def draw_road():
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-100, -10, 0)
    glVertex3f(100, -10, 0)
    glVertex3f(100, -10, -track_length)
    glVertex3f(-100, -10, -track_length)
    glEnd()

    # Add lane markings
    glColor3f(1, 1, 1)
    for i in range(0, int(track_length / 50)):
        glBegin(GL_QUADS)
        glVertex3f(-5, -9.9, -i * 50 - 10)
        glVertex3f(5, -9.9, -i * 50 - 10)
        glVertex3f(5, -9.9, -i * 50 - 40)
        glVertex3f(-5, -9.9, -i * 50 - 40)
        glEnd()

    # Draw sidewalks
    draw_sidewalks()

# Enhanced the infinite road system to spawn checkpoints, obstacles, and power-ups dynamically.
def update_road():
    global track_length, checkpoints, obstacles, power_up_position
    if car_pos[2] < -track_length + 500:  # If the car is near the end of the road
        track_length += 1000  # Extend the road by 1000 units

        # Add new checkpoints
        for i in range(track_length - 1000, track_length, 500):
            x = random.uniform(-arena_size, arena_size)  # Random x-coordinate within the arena
            z = i  # Use the current track segment as the z-coordinate
            checkpoints.append((x, z))

        # Add new obstacles
        for _ in range(5):  # Add 5 obstacles for the new segment
            x = random.randint(-90, 90)  # Ensure obstacles are within road bounds
            z = random.randint(-track_length, -track_length + 1000)
            obstacles.append([x, -9.5, z])

        # Add a new power-up
        power_up_position = [random.randint(-100, 100), -9.5, random.randint(-track_length, -track_length + 1000)]

        # Add new lane markings
        for i in range(int(track_length / 50) - 20, int(track_length / 50)):
            glBegin(GL_QUADS)
            glVertex3f(-5, -9.9, -i * 50 - 10)
            glVertex3f(5, -9.9, -i * 50 - 10)
            glVertex3f(5, -9.9, -i * 50 - 40)
            glVertex3f(-5, -9.9, -i * 50 - 40)
            glEnd()

        # Add new side boundaries
        glBegin(GL_QUADS)
        glVertex3f(-110, -10, -track_length + 1000)
        glVertex3f(-100, -10, -track_length + 1000)
        glVertex3f(-100, -10, -track_length)
        glVertex3f(-110, -10, -track_length)
        glEnd()

        glBegin(GL_QUADS)
        glVertex3f(100, -10, -track_length + 1000)
        glVertex3f(110, -10, -track_length + 1000)
        glVertex3f(110, -10, -track_length)
        glVertex3f(100, -10, -track_length)
        glEnd()

# Adjusted the building height to make them shorter.
def draw_buildings():
    for i in range(0, int(track_length / 100)):
        # Left side buildings
        glPushMatrix()
        glTranslatef(-150, 10, -i * 100 - 50)  # Reduced height
        glScalef(1, 1.5, 3)  # Shorter buildings
        glColor3f(0.6, 0.6, 0.6)  # Light gray for the main building
        glutSolidCube(50)
        glPopMatrix()

        # Add windows to the left buildings
        glPushMatrix()
        glTranslatef(-150, 10, -i * 100 - 50)
        glColor3f(0.2, 0.2, 0.2)  # Dark gray for windows
        for x_offset in [-15, 0, 15]:
            for y_offset in [-5, 5]:  # Adjusted window positions for shorter buildings
                glPushMatrix()
                glTranslatef(x_offset, y_offset, 26)  # Slightly in front of the building
                glScalef(0.3, 0.3, 0.1)
                glutSolidCube(20)
                glPopMatrix()
        glPopMatrix()

        # Right side buildings
        glPushMatrix()
        glTranslatef(150, 10, -i * 100 - 50)  # Reduced height
        glScalef(1, 1.5, 3)  # Shorter buildings
        glColor3f(0.6, 0.6, 0.6)  # Light gray for the main building
        glutSolidCube(50)
        glPopMatrix()

        # Add windows to the right buildings
        glPushMatrix()
        glTranslatef(150, 10, -i * 100 - 50)
        glColor3f(0.2, 0.2, 0.2)  # Dark gray for windows
        for x_offset in [-15, 0, 15]:
            for y_offset in [-5, 5]:  # Adjusted window positions for shorter buildings
                glPushMatrix()
                glTranslatef(x_offset, y_offset, 26)  # Slightly in front of the building
                glScalef(0.3, 0.3, 0.1)
                glutSolidCube(20)
                glPopMatrix()
        glPopMatrix()

def check_collision():
    global car_pos
    # Check if the car is out of the road bounds
    if car_pos[0] < -100 or car_pos[0] > 100:
        print("Car crashed! Game Over.")
        trigger_game_over()  # Call the trigger_game_over function

    # Check if the car hits the buildings
    for i in range(0, int(track_length / 100)):
        building_z = -i * 100 - 50
        if abs(car_pos[2] - building_z) < 50 and (car_pos[0] < -100 or car_pos[0] > 100):
            trigger_game_over()  # Use the trigger_game_over function
            break

def draw_checkpoints():
    glColor3f(0, 1, 0)  # Green for checkpoints
    for checkpoint in checkpoints:
        glPushMatrix()
        glTranslatef(checkpoint[0], -9.5, -checkpoint[1])
        glScalef(2, 0.5, 0.5)
        glutSolidCube(20)
        glPopMatrix()

# Update challenge progress when points or fuel pickups are collected
def check_checkpoint():
    global score, checkpoints, challenge_progress
    for checkpoint in checkpoints[:]:
        # Refined collision logic to ensure touching any part of the checkpoint grants a score
        checkpoint_x, checkpoint_z = checkpoint[0], checkpoint[1]
        car_x, car_z = car_pos[0], car_pos[2]

        # Define the bounds of the checkpoint area
        checkpoint_width = 40  # Adjust width as needed
        checkpoint_height = 50  # Adjust height as needed

        if (checkpoint_x - checkpoint_width / 2 <= car_x <= checkpoint_x + checkpoint_width / 2 and
            checkpoint_z - checkpoint_height / 2 <= -car_z <= checkpoint_z + checkpoint_height / 2):
            score += 1
            if current_challenge == "Collect Points":
                challenge_progress += 1  # Increment challenge progress for points
            show_update_message(f"Checkpoint crossed! Score: {score}")
            checkpoints.remove(checkpoint)

def draw_power_up():
    if not power_up_active:
        glPushMatrix()
        glTranslatef(*power_up_position)
        glColor3f(1, 1, 0)  # Yellow color for the power-up
        glutSolidSphere(10, 20, 20)
        glPopMatrix()

def check_power_up():
    global power_up_active, power_up_position, power_up_timer, car_pos
    if not power_up_active and abs(car_pos[0] - power_up_position[0]) < 15 and abs(car_pos[2] - power_up_position[2]) < 15:
        power_up_active = True
        power_up_timer = glutGet(GLUT_ELAPSED_TIME)  # Start the power-up timer
        print("Power-up collected! Speed increased.")

    if power_up_active:
        current_time = glutGet(GLUT_ELAPSED_TIME)
        if current_time - power_up_timer > power_up_duration:
            power_up_active = False
            power_up_position = [random.randint(-100, 100), -9.5, random.randint(-2000, 0)]  # Respawn power-up
            print("Power-up expired. Speed returned to normal.")

# Add a global variable to track the camera mode
camera_mode = "third_person"  # Default to third-person view

def toggle_camera_mode():
    global camera_mode
    if camera_mode == "third_person":
        camera_mode = "first_person"
        print("Switched to first-person view.")
    else:
        camera_mode = "third_person"
        print("Switched to third-person view.")

# Update the setup_camera function to handle both modes
def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WINDOW_WIDTH / WINDOW_HEIGHT, 1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    cx, cy, cz = car_pos

    if camera_mode == "third_person":
        cam_x = cx - camera_distance * math.sin(math.radians(car_angle)) + car_pos[0] * 0.1  # Adjust camera horizontally
        cam_y = cy + 50
        cam_z = cz + camera_distance * math.cos(math.radians(car_angle))
        gluLookAt(cam_x, cam_y, cam_z, cx, cy, cz - 100, 0, 1, 0)
    elif camera_mode == "first_person":
        cam_x = cx + car_pos[0] * 0.1  # Adjust camera horizontally
        cam_y = cy + 20  # Increased height to avoid obstruction
        cam_z = cz
        look_x = cx + 300 * math.sin(math.radians(car_angle))  # Look further ahead
        look_y = cy + 20  # Maintain the same height as the camera
        look_z = cz - 300 * math.cos(math.radians(car_angle))  # Look further ahead
        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)

# Add a mouse callback function to handle right-click events
def mouse_callback(button, state, x, y):
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        toggle_camera_mode()

def draw_stats():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 1)  # White color for text
    glRasterPos2f(10, WINDOW_HEIGHT - 20)  # Position for the first line of text
    for ch in f"Score: {score}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glRasterPos2f(10, WINDOW_HEIGHT - 40)  # Position for the penalty score
    for ch in f"Penalty: {penalty}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    if power_up_active:  # Display power-up message when active
        glRasterPos2f(10, WINDOW_HEIGHT - 60)
        for ch in "Power-Up Active! Speed Boost!":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# Added an overlay to display "GAME OVER" when the game ends.
def draw_game_over_overlay():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 0, 0)  # Red color for the "GAME OVER" text
    glRasterPos2f(WINDOW_WIDTH / 2 - 50, WINDOW_HEIGHT / 2)  # Center the text
    for ch in "GAME OVER":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_fuel_gauge():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Display fuel level
    glColor3f(1, 1, 1)  # White color for text
    glRasterPos2f(10, WINDOW_HEIGHT - 80)
    for ch in f"Fuel: {fuel}%":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_fuel_pickup():
    if fuel_pickup_position:
        glPushMatrix()
        glTranslatef(*fuel_pickup_position)
        glColor3f(0, 1, 0)  # Green color for the fuel pickup
        glutSolidSphere(10, 20, 20)
        glPopMatrix()

# Update challenge progress when points or fuel pickups are collected
def check_fuel_pickup():
    global fuel, fuel_pickup_position, challenge_progress
    if fuel_pickup_position and abs(car_pos[0] - fuel_pickup_position[0]) < 15 and abs(car_pos[2] - fuel_pickup_position[2]) < 15:
        fuel = min(100, fuel + 30)  # Refuel the car, max fuel is 100
        if current_challenge == "Collect Fuel Pickups":
            challenge_progress += 1  # Increment challenge progress for fuel pickups
        fuel_pickup_position = None  # Remove the fuel pickup
        show_update_message("Fuel Collected! Fuel Restored.")

# Updated fuel depletion logic to trigger game over when fuel reaches 0.
def update_fuel():
    global fuel, fuel_pickup_position, fuel_depletion_timer, fuel_spawn_timer

    current_time = glutGet(GLUT_ELAPSED_TIME)

    # Deplete fuel every 10 seconds
    if current_time - fuel_depletion_timer > fuel_depletion_interval:
        fuel = max(0, fuel - 10)  # Decrease fuel by 10%
        fuel_depletion_timer = current_time
        if fuel == 0:
            trigger_game_over()  # Trigger game over when fuel is 0

    # Spawn fuel pickup every 8 seconds
    if current_time - fuel_spawn_timer > fuel_spawn_interval:
        fuel_pickup_position = [random.randint(-90, 90), -9.5, car_pos[2] - 500]  # Spawn in front of the car
        fuel_spawn_timer = current_time

# Added a definition for the missing `show_update_message` function.
def show_update_message(message):
    global latest_update, update_timer
    latest_update = message
    update_timer = glutGet(GLUT_ELAPSED_TIME)  # Record the time when the message is set

# Function to generate a new random challenge
def generate_challenge():
    global current_challenge, challenge_progress, challenge_target, challenge_timer
    challenge_timer = glutGet(GLUT_ELAPSED_TIME)  # Start the challenge timer
    challenge_progress = 0  # Reset progress

    # Randomly select a challenge type
    if random.choice([True, False]):
        current_challenge = "Collect Points"
        challenge_target = 5  # Target to collect 5 points
    else:
        current_challenge = "Collect Fuel Pickups"
        challenge_target = 5  # Target to collect 5 fuel pickups

# Function to update challenge progress
def update_challenge():
    global current_challenge, challenge_progress, challenge_timer

    if current_challenge:
        # Check if the challenge is completed
        if challenge_progress >= challenge_target:
            show_update_message(f"Challenge Completed: {current_challenge}!")
            current_challenge = None  # Clear the challenge
            return

        # Check if the challenge duration has expired
        current_time = glutGet(GLUT_ELAPSED_TIME)
        if current_time - challenge_timer > challenge_duration:
            show_update_message(f"Challenge Failed: {current_challenge}.")
            current_challenge = None  # Clear the challenge

# Function to draw the current challenge on the top-left of the screen
def draw_challenge():
    if current_challenge:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glColor3f(1, 1, 0)  # Yellow color for the challenge text
        glRasterPos2f(10, WINDOW_HEIGHT - 100)
        for ch in f"Challenge: {current_challenge} ({challenge_progress}/{challenge_target})":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

def draw_mine():
    if mine_position:
        glPushMatrix()
        glTranslatef(*mine_position)
        glColor3f(0.5, 0, 0)  # Dark red color for the mine
        glutSolidSphere(10, 20, 20)  # Draw the mine as a sphere
        glPopMatrix()

# Updated mine collision to show the game over overlay instead of restarting.
def check_mine_collision():
    global mine_position, penalty
    if cheat_mode:
        return  # Skip collision logic if cheat mode is enabled
    if mine_position and abs(car_pos[0] - mine_position[0]) < 15 and abs(car_pos[2] - mine_position[2]) < 15:
        trigger_game_over()  # Use the reusable game over function

def update_mine():
    global mine_position, mine_spawn_timer

    current_time = glutGet(GLUT_ELAPSED_TIME)

    # Spawn a mine every 15 seconds
    if current_time - mine_spawn_timer > mine_spawn_interval:
        mine_position = [random.randint(-90, 90), -9.5, car_pos[2] - 500]  # Spawn in front of the car
        mine_spawn_timer = current_time

def draw_green_field():
    glColor3f(0.0, 0.8, 0.0)  # Green color for the field
    glBegin(GL_QUADS)
    glVertex3f(-200, -10, 100)  # Extend the field further back
    glVertex3f(200, -10, 100)
    glVertex3f(200, -10, 0)
    glVertex3f(-200, -10, 0)
    glEnd()

def draw_scene():
    set_lighting()  # Apply default lighting
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    setup_camera()
    draw_green_field()  # Draw the green field
    draw_road()
    draw_buildings()
    draw_checkpoints()  # Draw checkpoints on the road
    draw_power_up()  # Draw the power-up
    draw_obstacles()  # Draw obstacles on the road
    draw_fuel_pickup()  # Draw the fuel pickup
    draw_mine()  # Draw the mine
    draw_car()
    draw_stats()  # Display stats on the top-left side of the screen
    draw_fuel_gauge()  # Display the fuel gauge
    draw_challenge()  # Display the current challenge

    if penalty >= 5:  # Check if the game is over
        draw_game_over_overlay()  # Display the "GAME OVER" overlay

    glutSwapBuffers()

# Updated the main game loop to freeze the screen on game over
def game_loop():
    global game_over
    if game_over:
        return  # Freeze the game if game over

    if fuel > 0:  # Only update game elements if the car has fuel
        update_road()  # Dynamically extend the road
        check_collision()  # Check for collisions with buildings or going off-road
        check_checkpoint()  # Check if a checkpoint is crossed
        check_power_up()  # Check if the car collects a power-up
        check_obstacle_collision()  # Check if the car hits an obstacle
        check_fuel_pickup()  # Check if the car collects a fuel pickup
        check_mine_collision()  # Check if the car hits a mine
    update_fuel()  # Update fuel level and spawn pickups
    update_challenge()  # Update the current challenge
    update_mine()  # Update mine spawning

    # Generate a new challenge if none exists
    if not current_challenge:
        generate_challenge()

def idle():
    game_loop()
    glutPostRedisplay()

# Updated keyboard handler to toggle night mode with 'n' key
def keyboard_handler(key, x, y):
    global game_over, input_enabled
    if game_over:
        if key == b'r':  # Allow only 'R' to restart the game
            reset_game()
        return  # Ignore all other keys if game over

    if not input_enabled and key != b'r':
        return  # Ignore all inputs except 'R' when input is disabled

    global car_angle
    speed = 10 if power_up_active else 5  # Increase speed when power-up is active
    if key == b'w':
        car_pos[2] -= speed * math.cos(math.radians(car_angle))
        car_pos[0] -= speed * math.sin(math.radians(car_angle))
    elif key == b's':
        car_pos[2] += speed * math.cos(math.radians(car_angle))
        car_pos[0] += speed * math.sin(math.radians(car_angle))
    elif key == b'a':
        car_angle += 5
    elif key == b'd':
        car_angle -= 5
    elif key == b'r':
        reset_game()
    elif key == b'c':
        toggle_cheat_mode()  # Toggle cheat mode when 'c' is pressed
    elif key == b'n':
        toggle_night_mode()  # Toggle night mode when 'n' is pressed

# Updated mouse handler to disable actions during game over
def mouse_handler(button, state, x, y):
    global game_over, input_enabled
    if game_over or not input_enabled:
        return  # Ignore all mouse actions if game over or inputs are disabled

    # ...existing mouse handling logic...
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        toggle_camera_mode()

# Added functionality to increase the camera height using the UP arrow key.
def special_keys(key, x, y):
    global camera_distance
    if key == GLUT_KEY_DOWN:
        camera_distance += 10  # Increase the camera height
    elif key == GLUT_KEY_UP:
        camera_distance -= 10  # Decrease the camera height

# Initialize obstacles when the game starts
def init():
    glClearColor(0.5, 0.8, 0.95, 1)
    glEnable(GL_DEPTH_TEST)
    generate_obstacles()  # Generate initial obstacles

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"3D Car Driving Game")
    init()
    glutDisplayFunc(draw_scene)
    glutKeyboardFunc(keyboard_handler)
    glutSpecialFunc(special_keys)  # Register special keys for camera height adjustment
    glutIdleFunc(idle)
    glutMouseFunc(mouse_handler)  # Register the updated mouse handler
    glutMainLoop()

if __name__ == "__main__":
    main()

def display_hud():
    global score, penalty, cheat_mode
    # ...existing code...
    hud_text = f"Score: {score}  Penalty: {penalty}"
    if cheat_mode:
        hud_text += "  Cheat: ON"  # Add cheat mode status to the HUD
    # ...existing code to render hud_text on the screen...

def update_hud():
    # Update the HUD to reflect the current cheat mode status
    if cheat_mode:
        show_update_message("Cheat Mode Enabled! Car is now invulnerable.")
    else:
        show_update_message("Cheat Mode Disabled! Car is now vulnerable.")

def enable_first_person_camera():
    # Set the camera mode to first person
    set_camera_mode("first_person")

    # Display a message to the player
    display_message("First Person Camera Enabled", position="top")

    # Set the camera position and orientation for first person view
enable_first_person_camera()

def set_camera_mode(mode):
    # Placeholder logic to set the camera mode
    if mode == "first_person":
        print("Camera mode set to First Person")
    else:
        print(f"Camera mode set to {mode}")

def display_message(message, position="center"):
    # Placeholder logic to display a message on the screen
    print(f"Message: {message} (Position: {position})")
