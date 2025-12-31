from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

collision_flash = 0
screen_shake = 0

level = 1
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
missile_count = 0
max_missiles = 3
missile_bar = 0
max_missile_bar = 100

BUS_SPEED_MULTIPLIER = 1.0
ENEMY_SPEED_MULTIPLIER = 1.5
POLICE_SPEED_MULTIPLIER = 1.8

garir_width = 30
garir_length = 50
garir_x = 0
garir_y = 10
garir_z = 200
enemies = []
score = 0
player_jibon = 3
khela_sesh = False
shield_active = False
auto_pilot = False
fly_active = False
enemy_speed = 1.2


def apply_collision_effect():
    global collision_flash, screen_shake
    collision_flash = 20
    screen_shake = 10


def update_collision_effects():
    global collision_flash, screen_shake
    
    if collision_flash > 0:
        collision_flash -= 1
    if screen_shake > 0:
        screen_shake -= 1


def draw_collision_flash():
    if collision_flash > 0:
        glColor4f(1, 0, 0, 0.3)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(1000, 0)
        glVertex2f(1000, 800)
        glVertex2f(0, 800)
        glEnd()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)


def apply_screen_shake():
    if screen_shake > 0:
        shake_x = random.uniform(-screen_shake, screen_shake)
        shake_y = random.uniform(-screen_shake, screen_shake)
        return shake_x, shake_y
    return 0, 0


def update_level_system(current_speed):
    global level, level_distance, current_bg
    
    level_distance += current_speed
    
    if level_distance >= level_threshold and level < 100:
        level += 1
        level_distance = 0
        
        current_bg = (current_bg + 1) % len(bg_colors)
        
        print(f" LEVEL UP! Now at Level {level}")
        
        if level >= 100:
            return True
    
    return False


def get_level_speed_multiplier():
    return 1 + level * 0.2


def get_level_progress():
    return int((level_distance / level_threshold) * 100)


def set_background_color():
    bg = bg_colors[current_bg]
    glClearColor(bg[0], bg[1], bg[2], 1.0)


def get_car_color_modification():
    car_color = [0, 1, 0]
    
    if shield_active and not fly_active:
        car_color = [0, 0.5, 1]
    
    if auto_pilot:
        car_color = [1, 1, 0]
    
    return car_color


def fire_missile():
    global missile_count, missile_bar
    
    if missile_count < max_missiles and missile_bar >= max_missile_bar:
        missiles.append([garir_x, garir_y + 10, garir_z + 50])
        missile_count += 1
        
        if missile_count >= max_missiles:
            missile_bar = 0
            missile_count = 0
        
        print(f" Missile fired! ({missile_count}/{max_missiles})")


def update_missile_bar(amount):
    global missile_bar
    missile_bar = min(missile_bar + amount, max_missile_bar)


def update_missiles(current_speed):
    global missiles, enemies, score
    
    for mis in missiles[:]:
        mis[2] += 3.5
        
        for obs in enemies[:]:
            if check_collision(mis[0], mis[2], 6, 20, 
                             obs[0], obs[2], 25, 40):
                enemies.remove(obs)
                missiles.remove(mis)
                score += 20
                print(" Obstacle destroyed!")
                break
        
        if mis[2] > 700:
            missiles.remove(mis)


def draw_missile(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 0.0, 0.0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 1, 20, 10, 10)
    glPopMatrix()


def draw_all_missiles():
    for mis in missiles:
        draw_missile(mis[0], mis[1], mis[2])


def check_collision(x1, z1, w1, l1, x2, z2, w2, l2):
    return (abs(x1 - x2) < (w1 + w2) / 2 and
            abs(z1 - z2) < (l1 + l2) / 2)


def get_obstacle_speed(obs_type, current_speed):
    if obs_type == 2:
        return current_speed * BUS_SPEED_MULTIPLIER
    elif obs_type == 0:
        return current_speed * ENEMY_SPEED_MULTIPLIER
    elif obs_type == 1:
        return current_speed * POLICE_SPEED_MULTIPLIER
    else:
        return current_speed


def update_all_game_play_features(current_speed, paused, game_over_status):
    global khela_sesh
    
    if game_over_status or paused:
        return False
    
    update_collision_effects()
    
    game_won = update_level_system(current_speed)
    if game_won:
        khela_sesh = True
        return True
    
    update_missiles(current_speed)
    
    return False


def display_game_play_ui():
    from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
    
    def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
        glColor3f(1, 1, 1)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        
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
    
    draw_text(10, 680, f"Missile: {int(missile_bar)}/{max_missile_bar} [{missile_count}/{max_missiles}]")
    
    progress = get_level_progress()
    draw_text(10, 650, f"Progress: {progress}%")
    
    draw_text(10, 710, f"Level: {level}")
    
    draw_collision_flash()


def init_game_play_features():
    global collision_flash, screen_shake, level, level_distance
    global current_bg, missiles, missile_count, missile_bar
    
    collision_flash = 0
    screen_shake = 0
    level = 1
    level_distance = 0
    current_bg = 0
    missiles = []
    missile_count = 0
    missile_bar = 0
    
    print(" game_play's features initialized!")


if __name__ == "__main__":
    init_game_play_features()
