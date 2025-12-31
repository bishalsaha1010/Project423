from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800

camera_mode = 0  # 0: Third-person, 1: First-person, 2: Dynamic
camera_pos = (0, 200, -300)
camera_zoom = 0
camera_x_offset = 0  # Horizontal
camera_x_min = -200  # Left threshold
camera_x_max = 200   # Right threshold
fovY = 60

game_running = True
paused = False
auto_pilot = False
game_over = False

player_lives = 3
max_lives = 5
score = 0
level = 1

p_speed=10

car_x = 0
car_y = 10
car_z = 200
car_speed = 5
car_width = 30
car_length = 50
#player_pos=[car_x,car_y,car_z]
p_speed=car_speed

road_width = 200
road_length = 1000

segment_length = road_length  
road_segments = [(i - 5 // 2) * segment_length for i in range(1,6,1)]


# ===== OBSTACLES =====
obstacles = []  # Format: [x, y, z, type]
obstacle_speed =1.2
obstacle_spawn_timer = 0
obstacle_spawn_rate = 30  # frames between spawns

powerups = []  # Format: [x, y, z, type]
powerup_spawn_timer = 0
# Types: 0=health, 1=shield, 2=speed_boost

shield_active = False
shield_timer = 0
shield_duration = 1000 

speed_boost_active = False
speed_boost_timer = 0
speed_boost_duration = 500

missiles = []  # Format: [x, y, z]
missile_count = 0
max_missiles = 3
missile_bar = 0
max_missile_bar = 100


level_distance = 0
level_threshold = 2500  

collision_flash = 0
screen_shake = 0

bg_colors = [
    [0.1, 0.1, 0.3],  # Night blue
    [0.5, 0.7, 1.0],  # Day blue
    [0.9, 0.7, 0.5],  # Desert orange
    [0.2, 0.2, 0.2],  # Dark gray
]
current_bg = 0
BUS_SPEED_MULTIPLIER = 1.0
ENEMY_SPEED_MULTIPLIER = 1.5
POLICE_SPEED_MULTIPLIER = 1.8
# ===== FLY POWER =====
fly_active = False
fly_cars_left = 0

fly_count = 0
max_fly = 3

fly_bar = 0
fly_bar_step = 150   # score needed for 1 fly



def init_game():
    global player_lives, score, level, game_over, obstacles, powerups, missiles
    global level_distance, missile_bar, missile_count, auto_pilot, paused
    global shield_active, speed_boost_active, current_bg, car_x
    global obstacle_spawn_timer, powerup_spawn_timer, collision_flash, screen_shake
    global fly_active, fly_cars_left, fly_count, fly_bar
    player_lives = 3
    score = 0
    level = 1
    game_over = False
    car_x = 0
    
    obstacles = []
    powerups = []
    missiles = []
    
    level_distance = 0
    missile_bar = 0
    missile_count = 0
    
    auto_pilot = False
    paused = False
    shield_active = False
    speed_boost_active = False
    
    current_bg = 0
    obstacle_spawn_timer = 0
    powerup_spawn_timer = 0
    collision_flash = 0
    screen_shake = 0
    
    fly_active = False
    fly_cars_left = 0
    fly_count = 0
    fly_bar = 0
    
    print("🏁 GAME STARTED! GOOD LUCK! 🏁")


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_road():
    glPushMatrix()
    for seg_z in road_segments:
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex3f(-road_width/2, 0, -seg_z)
        glVertex3f( road_width/2, 0, -seg_z)
        glVertex3f( road_width/2, 0, seg_z + segment_length)
        glVertex3f(-road_width/2, 0, seg_z + segment_length)
        glEnd()
        
        # Center lines
        glColor3f(1, 1, 1)
        for i in range(int(seg_z), int(seg_z + segment_length), 60):
            glBegin(GL_QUADS)
            glVertex3f(-2, 1, i)
            glVertex3f( 2, 1, i)
            glVertex3f( 2, 1, i + 30)
            glVertex3f(-2, 1, i + 30)
            glEnd()
        
        # Edge lines
        glColor3f(1, 1, 0)
        for i in range(int(seg_z), int(seg_z + segment_length), 40):
            # left edge
            glBegin(GL_QUADS)
            glVertex3f(-road_width/2 - 3, 1, i)
            glVertex3f(-road_width/2, 1, i)
            glVertex3f(-road_width/2, 1, i + 20)
            glVertex3f(-road_width/2 - 3, 1, i + 20)
            glEnd()
            # right edge
            glBegin(GL_QUADS)
            glVertex3f( road_width/2, 1, i)
            glVertex3f( road_width/2 + 3, 1, i)
            glVertex3f( road_width/2 + 3, 1, i + 20)
            glVertex3f( road_width/2, 1, i + 20)
            glEnd()
        
    glPopMatrix()



def draw_car(x, y, z, color):
   
    glPushMatrix()
    glTranslatef(x, y, z)

    # ================= MAIN BODY =================
    glColor3f(color[0], color[1], color[2])
    glPushMatrix()
    glTranslatef(0, 6, 0)
    glScalef(car_width/18, 6/18, car_length/18)
    glutSolidCube(18)
    glPopMatrix()

    # ================= HOOD =================
    glColor3f(color[0]*0.9, color[1]*0.9, color[2]*0.9)
    glPushMatrix()
    glTranslatef(0, 8, car_length*0.25)
    glScalef(car_width*0.9/18, 4/18, car_length*0.35/18)
    glutSolidCube(18)
    glPopMatrix()

    # ================= TRUNK =================
    glPushMatrix()
    glTranslatef(0, 7, -car_length*0.25)
    glScalef(car_width*0.85/18, 4/18, car_length*0.30/18)
    glutSolidCube(18)
    glPopMatrix()

    # ================= CABIN =================
    glColor3f(color[0]*0.75, color[1]*0.75, color[2]*0.75)
    glPushMatrix()
    glTranslatef(0, 13, -2)
    glScalef(car_width*0.7/18, 6/18, car_length*0.45/18)
    glutSolidCube(18)
    glPopMatrix()

    # ================= WINDOWS =================
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0, 14, 2)
    glScalef(car_width*0.6/18, 4/18, car_length*0.35/18)
    glutSolidCube(18)
    glPopMatrix()

    glColor3f(0.05, 0.05, 0.05)
    wheel_radius = 5

    wheel_positions = [
        (-car_width/2 + 4, 2,  car_length/3),
        ( car_width/2 - 4, 2,  car_length/3),
        (-car_width/2 + 4, 2, -car_length/3),
        ( car_width/2 - 4, 2, -car_length/3),
    ]

    for wx, wy, wz in wheel_positions:
        glPushMatrix()
        glTranslatef(wx, wy, wz)
        glutSolidSphere(wheel_radius, 12, 12)
        glPopMatrix()

    glPopMatrix()

def draw_enemy_car(x, y, z):
    glPushMatrix()
    glTranslatef(x, y , z)   
    glScalef(0.95, 0.95, 0.95) 
    
    enemy_color = [1, 0.1, 0.1]  
    draw_car(0, 0, 0, enemy_color)
    
    glPopMatrix()
def draw_police_car(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(1.0, 1.0, 1.1)

    # Body (blue)
    draw_car(0, 0, 0, [0.1, 0.1, 0.8])

    # Police light bar
    glPushMatrix()
    glTranslatef(0, 22, 5)
    glScalef(1.2, 0.3, 0.4)

    # Red light
    glColor3f(1, 0, 0)
    glutSolidCube(10)

    glTranslatef(0.8, 0, 0)
    glColor3f(0, 0, 1)
    glutSolidCube(10)
    glPopMatrix()

    glPopMatrix()


def draw_obstacle(x, y, z, obs_type):

    glPushMatrix()
    glTranslatef(x, y, z)
    
    if obs_type == 0:  
        draw_enemy_car(0, 10, 0)
    elif obs_type == 1:  
        draw_police_car(0,0,0)
    elif obs_type == 2:  
        draw_bus(0,10,0)
    
    glPopMatrix()
def draw_bus(x, y, z):
    glPushMatrix()
    glTranslatef(x, y + 6, z)

    glColor3f(0.9, 0.8, 0.1)
    glScalef(2.2, 1.3, 3.5)
    glutSolidCube(20)

    glPopMatrix()



def draw_powerup(x, y, z, ptype):
    glPushMatrix()
    glTranslatef(x, y, z)

    if ptype == 0:      # Health
        draw_heart(0, 0, 0)

    elif ptype == 1:    # Shield
        draw_shield(0, 0, 0)

    elif ptype == 2:    # Speed Boost
        draw_speedboost(0, 0, 0)

    glPopMatrix()

    



def draw_missile(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 0.0, 0.0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 1, 20, 10, 10)
    glPopMatrix()

def draw_heart(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 0.0, 0.0)

    # Left lobe
    glPushMatrix()
    glTranslatef(-4, 2, 0)
    glutSolidSphere(5, 12, 12)
    glPopMatrix()

    # Right lobe
    glPushMatrix()
    glTranslatef(4, 2, 0)
    glutSolidSphere(5, 12, 12)
    glPopMatrix()

    # Bottom cone
    glPushMatrix()
    glTranslatef(0, -5, 0)
    glRotatef(180, 1, 0, 0)
    glutSolidCone(6, 10, 12, 12)
    glPopMatrix()

    glPopMatrix()
def draw_speedboost(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)

    

    glColor3f(1.0, 1.0, 0.0)
    glutSolidSphere(7, 16, 16)

    glColor3f(1.0, 0.8, 0.0)
    glPushMatrix()
    glTranslatef(0, -10, 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 3, 20, 12, 1)
    glPopMatrix()

    glColor3f(1.0, 0.7, 0.0)
    glPushMatrix()
    glTranslatef(0, -3, 0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 9, 9, 1.5, 20, 1)
    glPopMatrix()

    glColor3f(1.0, 0.6, 0.0)
    glPushMatrix()
    glTranslatef(0, 4, 0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 11, 11, 1.5, 20, 1)
    glPopMatrix()

    glPopMatrix()

def draw_shield(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)


    glColor3f(0.0, 0.6, 1.0)
    glutSolidSphere(8, 16, 16)

    glColor3f(0.2, 0.8, 1.0)
    glPushMatrix()
    glTranslatef(0, -2, 0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 11, 11, 1.5, 24, 1)
    glPopMatrix()

    glColor3f(0.1, 0.7, 0.9)
    glPushMatrix()
    glTranslatef(0, 3, 0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 13, 13, 1.5, 24, 1)
    glPopMatrix()

    glPopMatrix()



def spawn_obstacle():
    lane_positions = [-road_width/3, 0, road_width/3] #left center rifht
    
    obstacle_lane = random.choice([0, 1, 2])  
    x = lane_positions[obstacle_lane]
    
    x += random.randint(-15, 15)
    
    obs_type = random.randint(0, 2)
    obstacles.append([x, 0, 2000, obs_type])
    
    if not hasattr(spawn_obstacle, 'last_lane'):
        spawn_obstacle.last_lane = obstacle_lane
    else:
        # If same lane as last time, skip to ensure variety
        if obstacle_lane == spawn_obstacle.last_lane and random.random() < 0.5:
            return
        spawn_obstacle.last_lane = obstacle_lane


def spawn_powerup():
    
    x = random.randint(-int(road_width/2) + 20, int(road_width/2) - 20)
    ptype = random.randint(0, 2)
    powerups.append([x, 30,700, ptype])


# ===== COLLISION DETECTION =====
def check_collision(x1, z1, w1, l1, x2, z2, w2, l2):
    
    return (abs(x1 - x2) < (w1 + w2) / 2 and
            abs(z1 - z2) < (l1 + l2) / 2)

# ===== SMART AUTO-PILOT FUNCTION =====
def smart_autopilot():
    
    global car_x
    
    if not auto_pilot:
        return
    
    # Define lane positions
    lane_positions = {
        'left': -road_width/3,
        'center': 0,
        'right': road_width/3
    }
    
    danger_zone = 200  
    
    lanes_blocked = {'left': False, 'center': False, 'right': False}
    
    for obs in obstacles:
        # Check if obstacle is in danger zone (ahead of car)
        if car_z < obs[2] < car_z + danger_zone:
            # Determine which lane the obstacle is in
            if obs[0] < -road_width/6:  # Left lane
                lanes_blocked['left'] = True
            elif obs[0] > road_width/6:  # Right lane
                lanes_blocked['right'] = True
            else:  # Center lane
                lanes_blocked['center'] = True
    
    if car_x < -road_width/6:
        current_lane = 'left'
    elif car_x > road_width/6:
        current_lane = 'right'
    else:
        current_lane = 'center'
    
    safe_lane = None
    
    if lanes_blocked[current_lane]==False:
        safe_lane = current_lane
    else:
        if not lanes_blocked['center']:
            safe_lane = 'center'
        elif not lanes_blocked['left']:
            safe_lane = 'left'
        elif not lanes_blocked['right']:
            safe_lane = 'right'
        else:
            # All lanes blocked - pick the one with furthest obstacle
            furthest_dist = 0
            for lane_name, pos in lane_positions.items():
                # Find closest obstacle in this lane
                min_obs_dist = danger_zone
                for obs in obstacles:
                    if car_z < obs[2] < car_z + danger_zone:
                        if lane_name == 'left' and obs[0] < -road_width/6:
                            min_obs_dist = min(min_obs_dist, obs[2] - car_z)
                        elif lane_name == 'right' and obs[0] > road_width/6:
                            min_obs_dist = min(min_obs_dist, obs[2] - car_z)
                        elif lane_name == 'center' and -road_width/6 <= obs[0] <= road_width/6:
                            min_obs_dist = min(min_obs_dist, obs[2] - car_z)
                
                if min_obs_dist > furthest_dist:
                    furthest_dist = min_obs_dist
                    safe_lane = lane_name
    
    if safe_lane:
        target_x = lane_positions[safe_lane]
        
        distance_to_target = target_x - car_x
        
        if abs(distance_to_target) > 5:  
            if distance_to_target > 0:
                car_x += car_speed * 1.2  
            else:
                car_x -= car_speed * 1.2  
        else:
            car_x = target_x


def fire_missile():
    global missile_count, missile_bar
    
    if missile_count < max_missiles and missile_bar >= max_missile_bar:
        missiles.append([car_x, car_y + 10, car_z + 50])
        missile_count += 1
        
        # Reset bar after firing all missiles
        if missile_count >= max_missiles:
            missile_bar = 0
            missile_count = 0
        
        print(f"Missile fired! ({missile_count}/{max_missiles})")


def update_game():
    global score, level, player_lives, game_over, collision_flash, screen_shake
    global obstacle_spawn_timer, powerup_spawn_timer, level_distance, missile_bar
    global shield_timer, speed_boost_timer, shield_active, speed_boost_active
    global current_bg, car_x, obstacles, powerups, missiles
    global fly_active, fly_cars_left, fly_count, fly_bar

    if game_over or paused:
        return
        

    smart_autopilot()
    car_x = max(-road_width/2 + car_width/2, min(road_width/2 - car_width/2, car_x))
    
    if shield_active and not fly_active:
        shield_timer -= 1
        if shield_timer <= 0:
            shield_active = False
            
    
    if speed_boost_active:
        speed_boost_timer -= 1
        if speed_boost_timer <= 0:
            speed_boost_active = False
            
    
    obstacle_spawn_timer += 10
    spawn_interval = obstacle_spawn_rate / (1 + level*0.1)
    
    if obstacle_spawn_timer >= spawn_interval:
        can_spawn = True
        for obs in obstacles:
            if obs[2] > 1350:  
                can_spawn = False
                break
        
        if can_spawn:
            spawn_obstacle()
        obstacle_spawn_timer = 10
    
    powerup_spawn_timer += 1
    if powerup_spawn_timer >= 180: 
        if random.random() < 0.3:  
            spawn_powerup()
        powerup_spawn_timer = 0
    
    
    current_speed = obstacle_speed * (1 + level * 0.2)
    if speed_boost_active:
        current_speed *= 1.5
    
    for i in range(len(road_segments)):
        road_segments[i] -= current_speed  
        # if segment is behind the car, loop it to the front
        if road_segments[i] < car_z - segment_length:
            road_segments[i] += 5 * segment_length

    
    for obs in obstacles[:]:
        if obs[3] == 2:          # Bus
            speed = current_speed * BUS_SPEED_MULTIPLIER
        elif obs[3] == 0:        # Normal enemy car
            speed = current_speed * ENEMY_SPEED_MULTIPLIER
        elif obs[3] == 1:        # Police car
            speed = current_speed * POLICE_SPEED_MULTIPLIER
        else:
            speed = current_speed

        obs[2] -= speed
        
        if check_collision(car_x, car_z, car_width, car_length, 
                          obs[0], obs[2], 20, 35):
            if fly_active:
                fly_cars_left -= 1

                obstacles.remove(obs)

                if fly_cars_left <= 0:
                    fly_active = False

                continue
            if not shield_active and not auto_pilot:
                player_lives -= 1
                collision_flash = 20
                screen_shake = 10
                
                if player_lives <= 0:
                    game_over = True
            
            obstacles.remove(obs)
        
        # Remove obstacle if it passed the player
        elif obs[2] < car_z - 100:
            obstacles.remove(obs)
            score += 10  
            missile_bar = min(missile_bar + 5, max_missile_bar)
            # ===== FLY BAR FILL =====
            fly_bar += 10
            if fly_bar >= fly_bar_step and fly_count < max_fly:
                fly_bar = 0
                fly_count += 1
                
    
    for pup in powerups[:]:
        pup[2] -= current_speed * 0.8  # Power-ups move slower
        
        
        if check_collision(car_x, car_z, car_width, car_length, 
                          pup[0], pup[2], 20, 20):
            if pup[3] == 0:  # Health
                player_lives = min(player_lives + 1, max_lives)
                print(f"Health collected! Lives: {player_lives}")

            elif pup[3] == 1 and not fly_active:  # Shield
                shield_active = True
                shield_timer = shield_duration
                print("Shield activated!")

            elif pup[3] == 2:  # Speed boost
                speed_boost_active = True
                speed_boost_timer = speed_boost_duration
                print("Speed boost activated!")
            
            powerups.remove(pup)
        
        elif pup[2] < car_z - 100:
            powerups.remove(pup)
    
    for mis in missiles[:]:
        mis[2] += 3.5  
        
        for obs in obstacles[:]:
            if check_collision(mis[0], mis[2], 6, 20, 
                             obs[0], obs[2], 25, 40):
                obstacles.remove(obs)
                missiles.remove(mis)
                score += 20  # Bonus points for destroying
                print("Obstacle destroyed!")
                break
        
        if mis[2] > 700:
            missiles.remove(mis)
    
    level_distance += current_speed

    level_distance += current_speed
    
    if level_distance >= level_threshold and level < 100:  
        level += 1
        level_distance = 0
        current_bg = (current_bg + 1) % len(bg_colors)
        
        
       
        if level >= 100:
            game_over = True
            
    
        
    
    if collision_flash > 0:
        collision_flash -= 1
    if screen_shake > 0:
        screen_shake -= 1



def setupCamera():
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    
    shake_x = random.uniform(-screen_shake, screen_shake) if screen_shake > 0 else 0
    shake_y = random.uniform(-screen_shake, screen_shake) if screen_shake > 0 else 0
    
    if camera_mode == 0:  # Third-person 
        gluLookAt(0 + shake_x + camera_x_offset, 200 + camera_zoom, car_z - 300,
                  0 + camera_x_offset, car_y, car_z + 100,
                  0, 1, 0)
    
    elif camera_mode == 1:  # First-person 
        if fly_active==False:
            gluLookAt(car_x + shake_x + camera_x_offset, car_y + 30 + shake_y, car_z + 10,
                  car_x + camera_x_offset, car_y + 30, car_z + 500,
                  0, 1, 0)
        else:
            gluLookAt(car_x + shake_x + camera_x_offset, car_y + 90 + shake_y, car_z + 10,
                  car_x + camera_x_offset, car_y + 90, car_z + 500,
                  0, 1, 0)

    
    else:  # Dynamic view 
        dynamic_dist = 300 - (obstacle_speed * 20)
        gluLookAt(0 + shake_x + camera_x_offset, 250 + camera_zoom, car_z - dynamic_dist,
                  0 + camera_x_offset, car_y, car_z + 50,
                  0, 1, 0)



def keyboardListener(key, x, y):
    global car_x, paused, auto_pilot, camera_mode, game_running,car_z
    global fly_active, fly_cars_left, fly_count
    
    # Restart game
    if key == b'r' or key == b'R':
        if game_over:
            init_game()
        return
    
    # Pause/Resume
    if key == b'p' or key == b'P':
        paused = not paused
        return
    
    if key == b'c' or key == b'C':
        auto_pilot = not auto_pilot
        return
    
    if key == b'v' or key == b'V':
        camera_mode = (camera_mode + 1) % 3
        
        return
    
    if key == b' ':
        fire_missile()
        return
    
    if key == b'\x1b': 
        glutLeaveMainLoop()
        return
    
    
    if not paused and not game_over:
        # Move left
        if key == b'a' or key == b'A':
            car_x += car_speed
        
        elif key == b'd' or key == b'D':
            car_x -= car_speed
        
        if key == b'f' or key == b'F':
            if fly_count > 0 and not fly_active:
                fly_active = True
                fly_cars_left = 7
                fly_count -= 1
                shield_active = False
            return

        


def specialKeyListener(key, x, y):
    global camera_zoom, camera_x_offset
    
    if key == GLUT_KEY_UP:
        camera_zoom += 10
        
    elif key == GLUT_KEY_DOWN:
        camera_zoom -= 10
        
    elif key == GLUT_KEY_LEFT:
        camera_x_offset += 15
        if camera_x_offset > camera_x_max:
            camera_x_offset = camera_x_max

    elif key == GLUT_KEY_RIGHT:
        camera_x_offset -= 15
        if camera_x_offset < camera_x_min:
            camera_x_offset = camera_x_min

def draw_sheild_visual(rad, parts=16):
    import math
    
    for i in range(parts):
        angle_v = (i / parts) * 3.14159  
        y = rad * math.cos(angle_v)
        r = rad * math.sin(angle_v)
        
        glBegin(GL_LINE_LOOP)
        for j in range(parts):
            angle_h = (j / parts) * 2*3.14159 
            x = r * math.cos(angle_h)
            z = r * math.sin(angle_h)
            glVertex3f(x, y, z)
        glEnd()
    
    for i in range(4):
        angle = (i / 4) * 2 * 3.14159
        glBegin(GL_LINE_LOOP)
        for j in range(parts):
            angle_v = (j / parts) * 2 * 3.14159
            y = rad * math.cos(angle_v)
            r = rad * math.sin(angle_v)
            x = r * math.cos(angle)
            z = r * math.sin(angle)
            glVertex3f(x, y, z)
        glEnd()

def draw_speedboost_visual(x, y, z):
    glPushMatrix()
    glTranslatef(x, y + 5, z)  

    glColor3f(1.0, 1.0, 0.0)  
    for i in range(-2, 3):
        glBegin(GL_LINES)
        glVertex3f(i * 5, 0, -car_length/2)     
        glVertex3f(i * 5, 0, -car_length/2 - 40)  
        glEnd()

    glPopMatrix()

def draw_wings(x, y, z):
   
    glPushMatrix()
    glTranslatef(x, y + 5, z)  

    glColor3f(0.8, 0.8, 1.0) 
    wing_length = 60
    wing_width = 10

    glBegin(GL_TRIANGLES)
    glVertex3f(-car_width / 2, 60, 0)                  
    glVertex3f(-car_width / 2 - wing_length, 60, -wing_width)  
    glVertex3f(-car_width / 2 - wing_length, 60, wing_width)   
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex3f(car_width / 2, 60, 0)                   
    glVertex3f(car_width / 2 + wing_length, 60, -wing_width)  
    glVertex3f(car_width / 2 + wing_length, 60, wing_width)   
    glEnd()

    glPopMatrix()




def showScreen():
    global fly_active
    bg = bg_colors[current_bg]
    glClearColor(bg[0], bg[1], bg[2], 1.0)
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    
    setupCamera()
    
    draw_road()
    
    car_color = [0,1, 0]  

    if shield_active and not fly_active:
        car_color = [0,0.5,1] 

    if auto_pilot==True:
        car_color = [1, 1,0]  
    
    fly_y = car_y + 60 if fly_active else car_y
    draw_car(car_x, fly_y, car_z, car_color)
    
    if shield_active==True and  fly_active== False:
        glPushMatrix()
        glTranslatef(car_x, car_y + 10, car_z)
        glColor4f(0.0, 0.5, 1.0, 0.3)
        draw_sheild_visual(car_width, 12)
        glPopMatrix()

    if speed_boost_active and not fly_active:
        draw_speedboost_visual(car_x, car_y, car_z)

    if fly_active:
        draw_wings(car_x, car_y, car_z)

    
    for obs in obstacles:
        draw_obstacle(obs[0], obs[1], obs[2], obs[3])
    
    for pup in powerups:
        draw_powerup(pup[0], pup[1], pup[2], pup[3])
    
    for mis in missiles:
        draw_missile(mis[0], mis[1], mis[2])
    
    glClear(GL_DEPTH_BUFFER_BIT)   

    draw_text(10, 770, f"Lives: {player_lives}/{max_lives}")
    draw_text(10, 740, f"Score: {score}")
    draw_text(10, 710, f"Level: {level}")

    draw_text(10, 620, f"Fly: {fly_bar}/{fly_bar_step} [{fly_count}/{max_fly}]")


    draw_text(10, 680, f"Missile: {int(missile_bar)}/{max_missile_bar} [{missile_count}/{max_missiles}]")

    progress = int((level_distance / level_threshold) * 100)
    draw_text(10, 650, f"Progress: {progress}%")

    # Level progress
    progress = int((level_distance / level_threshold) * 100)
    draw_text(10, 650, f"Progress: {progress}%")
    
    # Status indicators (top right)
    if shield_active and  not fly_active:
        draw_text(800, 770, "SHIELD ON", GLUT_BITMAP_HELVETICA_18)
    if speed_boost_active:
        draw_text(800, 740, "SPEED BOOST", GLUT_BITMAP_HELVETICA_18)
    if auto_pilot:
        draw_text(760, 710, "AUTO-PILOT ON", GLUT_BITMAP_HELVETICA_18)
    
    # Pause message
    if paused:
        draw_text(WINDOW_WIDTH//2 - 70, WINDOW_HEIGHT//2, "=== PAUSED ===")
        draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 30, "Press P to Resume")
    
    # Game over screen
    if game_over:
        if level >= 100:
            draw_text(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 50, "=== CONGRATULATIONS! ===", GLUT_BITMAP_HELVETICA_18)
            draw_text(WINDOW_WIDTH//2 - 140, WINDOW_HEIGHT//2 + 10, "YOU'VE REACHED LEVEL 100! You are the king!!", GLUT_BITMAP_HELVETICA_18)
            draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 30, f"Final Score: {score}")
            draw_text(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 - 70, "Press R to Play Again")
        else:
            draw_text(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 20, "=== GAME OVER ===")
            draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 20, f"Final Score: {score}")
            draw_text(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 - 60, "Press R to Restart")
    
    
    if collision_flash > 0:
        glColor4f(1, 0, 0, 0.3)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(WINDOW_WIDTH, 0)
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        glVertex2f(0, WINDOW_HEIGHT)
        glEnd()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    glutSwapBuffers()



def idle():
    update_game()
    glutPostRedisplay()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(b"Car Rush - 3D Endless Driving Survival Game")
    
    glEnable(GL_DEPTH_TEST)
    
    init_game()
    
    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    

    glutMainLoop()


if __name__ == "__main__":
    main()