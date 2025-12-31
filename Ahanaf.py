from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math
#change

WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800



khela_choltese = True
pause = False
auto_pilot = False
khela_sesh = False

#player
player_jibon = 3
max_jibon = 5
score = 0
level = 1



#player car
garir_x = 0
garir_y = 10
garir_z = 200
garir_speed = 5
garir_width = 30
garir_length = 50
p_speed=garir_speed

rastar_width = 200
segment_length = 1000
road_segments = [(i - 5 // 2) * segment_length for i in range(1,6,1)]

shield_active = False
missile_count = 0
shield_timer = 0
shield_duration = 1000 


enemies = [] 
enemy_speed =1.2
enemy_spawn_timmer = 0
enemy_spawn_rate = 30  

bus_speed = 1.0
enemy_gari_speed = 1.5
police_speed = 1.8

fly_active = False
fly_cars_left = 0
fly_count = 0
max_fly = 3
fly_bar = 0
fly_bar_step = 150  


powerups = [] 
powerup_spawn_timer = 0


rastar_width = 200
segment_length = 1000

num_parts = 5
part_length = segment_length 
road_parts = [(i - num_parts // 2) * part_length for i in range(1,6,1)]






level_distance = 0
level_threshold = 2500  




bg_colors = [
    [0.1, 0.1, 0.3],  
    [0.5, 0.7, 1.0],  
    [0.9, 0.7, 0.5],  
    [0.2, 0.2, 0.2],  
]
current_bg = 0

missiles = []  
missile_fired = 0
max_missiles = 3
missile_bar = 0
max_missile_bar = 100

def init_game():

    global player_jibon, score, level, khela_sesh, enemies, powerups, missiles
    global level_distance, missile_bar, missile_count, auto_pilot, pause
    global shield_active, current_bg, garir_x
    global enemy_spawn_timmer, powerup_spawn_timer, collision_flash, screen_shake
    global fly_active, fly_cars_left, fly_count, fly_bar
    player_jibon = 3
    score = 0
    level = 1
    khela_sesh = False
    garir_x = 0
  
    enemies = []
    
    level_distance = 0
    
    pause = False
    
    current_bg = 0
    enemy_spawn_timmer = 0

    
    fly_active = False
    fly_cars_left = 0
    fly_count = 0
    fly_bar = 0

    powerups = []  
        
    print("KHELA START ! GOOD LUCK ! ")

def draw_road():
    glPushMatrix()
    for seg_z in road_segments:
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex3f(-rastar_width/2, 0, -seg_z)
        glVertex3f( rastar_width/2, 0, -seg_z)
        glVertex3f( rastar_width/2, 0, seg_z + segment_length)
        glVertex3f(-rastar_width/2, 0, seg_z + segment_length)
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
            glVertex3f(-rastar_width/2 - 3, 1, i)
            glVertex3f(-rastar_width/2, 1, i)
            glVertex3f(-rastar_width/2, 1, i + 20)
            glVertex3f(-rastar_width/2 - 3, 1, i + 20)
            glEnd()
            # right edge
            glBegin(GL_QUADS)
            glVertex3f( rastar_width/2, 1, i)
            glVertex3f( rastar_width/2 + 3, 1, i)
            glVertex3f( rastar_width/2 + 3, 1, i + 20)
            glVertex3f( rastar_width/2, 1, i + 20)
            glEnd()
        
    glPopMatrix()


def draw_car(x, y, z, color):
    glPushMatrix()
    glTranslatef(x, y, z)
    #body
    glColor3f(color[0], color[1], color[2])
    glPushMatrix()
    glTranslatef(0, 6, 0)
    glScalef(garir_width/18, 6/18, garir_length/18)
    glutSolidCube(18)
    glPopMatrix()
    # hood
    glColor3f(color[0]*0.9, color[1]*0.9, color[2]*0.9)
    glPushMatrix()
    glTranslatef(0, 8, garir_length*0.25)
    glScalef(garir_width*0.9/18, 4/18, garir_length*0.35/18)
    glutSolidCube(18)
    glPopMatrix()
    # trunk
    glPushMatrix()
    glTranslatef(0, 7, -garir_length*0.25)
    glScalef(garir_width*0.85/18, 4/18, garir_length*0.30/18)
    glutSolidCube(18)
    glPopMatrix()
    # cabin
    glColor3f(color[0]*0.75, color[1]*0.75, color[2]*0.75)
    glPushMatrix()
    glTranslatef(0, 13, -2)
    glScalef(garir_width*0.7/18, 6/18, garir_length*0.45/18)
    glutSolidCube(18)
    glPopMatrix()
    # windows
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0, 14, 2)
    glScalef(garir_width*0.6/18, 4/18, garir_length*0.35/18)
    glutSolidCube(18)
    glPopMatrix()
    #wheels
    glColor3f(0.05, 0.05, 0.05)
    wheel_radius = 4
    wheel_width = 3
    quad = gluNewQuadric()
    wheel_positions = [
        (-garir_width/2 - 2, 2,  garir_length/3),
        ( garir_width/2 - 1, 2,  garir_length/3),
        (-garir_width/2 - 2, 2, -garir_length/3),
        ( garir_width/2 - 1, 2, -garir_length/3),
    ]

    for wx, wy, wz in wheel_positions:
        glPushMatrix()
        glTranslatef(wx, wy, wz)
        glRotatef(90, 0, 1, 0)
        gluCylinder(quad, wheel_radius, wheel_radius, wheel_width, 12, 1)
        glPopMatrix()
    glPopMatrix()

def draw_enemy_car(x, y, z):
    glPushMatrix()
    glTranslatef(x, y , z)   
    glScalef(0.95, 0.95, 0.95)    
    enemy_color = [1, 0.1, 0.1]  
    draw_car(0, 0, 0, enemy_color)   
    glPopMatrix()
    glPopMatrix()
def draw_police_car(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(1.0, 1.0, 1.1)
    # Body (blue)
    draw_car(0, 0, 0, [0.1, 0.1, 0.8])
    # police light bar
    glPushMatrix()
    glTranslatef(0, 22, 5)
    glScalef(1.2, 0.3, 0.4)
    # red light
    glColor3f(1, 0, 0)
    glutSolidCube(10)
    glTranslatef(0.8, 0, 0)
    glColor3f(0, 0, 1)
    glutSolidCube(10)
    glPopMatrix()
    glPopMatrix()

def draw_bus(x, y, z):
    glPushMatrix()
    glTranslatef(x, y + 6, z)
    glColor3f(0.9, 0.8, 0.1)
    glScalef(2.2, 1.3, 3.5)
    glutSolidCube(20)
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


def spawn_obstacle():
    lane_positions = [-rastar_width/3, 0, rastar_width/3]
    
    obstacle_lane = random.choice([0, 1, 2])  
    x = lane_positions[obstacle_lane]
    
    x += random.randint(-15, 15)
    
    obs_type = random.randint(0, 2)
    enemies.append([x, 0, 2000, obs_type])
    
    if not hasattr(spawn_obstacle, 'last_lane'):
        spawn_obstacle.last_lane = obstacle_lane
    else:
        
        if obstacle_lane == spawn_obstacle.last_lane and random.random() < 0.5:
            return
        spawn_obstacle.last_lane = obstacle_lane


def check_collision(x1, z1, w1, l1, x2, z2, w2, l2):
    
    return (abs(x1 - x2) < (w1 + w2) / 2 and
            abs(z1 - z2) < (l1 + l2) / 2)
 

def update_game():
    
    global score, level, player_jibon, khela_sesh, collision_flash, screen_shake
    global enemy_spawn_timmer, powerup_spawn_timer, level_distance, missile_bar
    global shield_active
    global current_bg, garir_x, enemies, powerups, missiles
    global fly_active, fly_cars_left, fly_count, fly_bar
   
    if khela_sesh or pause:
        return
        
    garir_x = max(-rastar_width/2 + garir_width/2, min(rastar_width/2 - garir_width/2, garir_x))
        
    enemy_spawn_timmer += 10
    spawn_interval = enemy_spawn_rate / (1 + level*0.1)
    
    if enemy_spawn_timmer >= spawn_interval:
        can_spawn = True
        for obs in enemies:
            if obs[2] > 1350:  
                can_spawn = False
                break
        
        if can_spawn:
            spawn_obstacle()
        enemy_spawn_timmer = 10
    
    
    
    current_speed = enemy_speed * (1 + level * 0.2)
    

    for i in range(len(road_segments)):
        road_segments[i] -= current_speed  
        if road_segments[i] < garir_z - segment_length:
            road_segments[i] += 5 * segment_length
    

    for obs in enemies[:]:
        if obs[3] == 2: #bus
            speed = current_speed * bus_speed
        elif obs[3] == 0:  #normal enemy car
            speed = current_speed * enemy_gari_speed
        elif obs[3] == 1: #police car
            speed = current_speed * police_speed
        else:
            speed = current_speed
        obs[2] -= speed
        
        
        if check_collision(garir_x, garir_z, garir_width, garir_length, 
                          obs[0], obs[2], 20, 35):
            if fly_active:
                fly_cars_left -= 1
                enemies.remove(obs)
                if fly_cars_left <= 0:
                    fly_active = False
                continue
            if not shield_active and not auto_pilot:
                player_jibon -= 1
                collision_flash = 20
                screen_shake = 10
                if player_jibon <= 0:
                    khela_sesh = True
            enemies.remove(obs)
        

        elif obs[2] < garir_z - 100:
            enemies.remove(obs)
            score += 10  
            missile_bar = min(missile_bar + 5, max_missile_bar)
            fly_bar += 10
            if fly_bar >= fly_bar_step and fly_count < max_fly:
                fly_bar = 0
                fly_count += 1
                print(f"Flying power gained! ({fly_count}/{max_fly})")
    
    for pup in powerups[:]:
        pup[2] -= current_speed * 0.8  # Power-ups move slower
        
        
        if check_collision(garir_x, garir_z, garir_width, garir_length, 
                          pup[0], pup[2], 20, 20):
            if pup[3] == 0:  # Health
                player_jibon = min(player_jibon + 1, max_jibon)
                print(f"Health collected! Lives: {player_jibon}")
            elif pup[3] == 1 and not fly_active:  # Shield
                shield_active = True
                shield_timer = shield_duration

    for mis in missiles[:]:
        mis[2] += 3.5  
        
        for obs in enemies[:]:
            if check_collision(mis[0], mis[2], 6, 20, 
                             obs[0], obs[2], 25, 40):
                enemies.remove(obs)
                missiles.remove(mis)
                score += 20  # Bonus points for destroying
                print("Obstacle destroyed!")
                break
        

    



def keyboardListener(key, x, y):
    global garir_x, pause, auto_pilot, khela_choltese,garir_z,khela_sesh,shield_active
    global fly_active, fly_cars_left, fly_count


    if not pause and not khela_sesh:
        
        if key == b'a' or key == b'A':
            garir_x += garir_speed
        
        elif key == b'd' or key == b'D':
            garir_x -= garir_speed
        
        if key == b'f' or key == b'F':
            if fly_count > 0 and not fly_active:
                fly_active = True
                fly_cars_left = 7
                fly_count -= 1
                shield_active = False
            return
def draw_wings(x, y, z):
   
    glPushMatrix()
    glTranslatef(x, y + 5, z)  

    glColor3f(0.8, 0.8, 1.0) 
    wing_length = 60
    wing_width = 10

    glBegin(GL_TRIANGLES)
    glVertex3f(-garir_width / 2, 60, 0)                  
    glVertex3f(-garir_width / 2 - wing_length, 60, -wing_width)  
    glVertex3f(-garir_width / 2 - wing_length, 60, wing_width)   
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex3f(garir_width / 2, 60, 0)                   
    glVertex3f(garir_width / 2 + wing_length, 60, -wing_width)  
    glVertex3f(garir_width / 2 + wing_length, 60, wing_width)   
    glEnd()

    glPopMatrix()

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


def showScreen():
    global fly_active


    bg = bg_colors[current_bg]
    glClearColor(bg[0], bg[1], bg[2], 1.0)
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    

    

    draw_road()
    car_color = [0,1, 0]

    fly_y = garir_y + 60 if fly_active else garir_y
    draw_car(garir_x, fly_y, garir_z, car_color)
    if fly_active:
        draw_wings(garir_x, garir_y, garir_z)
    
    for obs in enemies:
        draw_obstacle(obs[0], obs[1], obs[2], obs[3])
    
    draw_text(10, 770, f"Lives: {player_jibon}/{max_jibon}")
    draw_text(10, 740, f"Score: {score}")

    draw_text(10, 620, f"Fly: {fly_bar}/{fly_bar_step} [{fly_count}/{max_fly}]")
    
    draw_text(10, 680, f"Missile: {int(missile_bar)}/{max_missile_bar} [{missile_count}/{max_missiles}]")

    
    glutSwapBuffers()
def idle():
    update_game()
    glutPostRedisplay()
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(b"Car Rush - 3D Driving Survival Game")
    
    glEnable(GL_DEPTH_TEST)
    
    init_game()
    
    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    #glutSpecialFunc(specialKeyListener)
    

    glutMainLoop()


if __name__ == "__main__":

    main()
