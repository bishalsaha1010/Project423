# ===== Bishal Saha =====

# Power-up states
shield_active = False
shield_timer = 0
shield_duration = 1000  # frames or ticks

speed_boost_active = False
speed_boost_timer = 0
speed_boost_duration = 500  # frames or ticks

auto_pilot = False

# ===== DRAWING FUNCTIONS =====

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

def draw_shield(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)

    # Outer shield sphere
    glColor3f(0.0, 0.6, 1.0)
    glutSolidSphere(8, 16, 16)

    # Decorative shield rings
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


def draw_powerup(x, y, z, ptype):
    glPushMatrix()
    glTranslatef(x, y, z)

    if ptype == 1:    # Shield
        draw_shield(0, 0, 0)
    elif ptype == 2:  # Speed Boost
        draw_speedboost(0, 0, 0)

    glPopMatrix()


powerups = []  # Format: [x, y, z, type]
powerup_spawn_timer = 0

def spawn_powerup():
    x = random.randint(-int(rastar_width/2) + 20, int(rastar_width/2) - 20)
    ptype = random.choice([1, 2])  # Only shield or speed boost
    powerups.append([x, 30, 700, ptype])


# ===== AUTO-PILOT LOGIC =====
def autopilot_cheat():
    global garir_x

    if not auto_pilot:
        return

    lane_positions = {
        'left': -rastar_width/3,
        'center': 0,
        'right': rastar_width/3
    }

    danger_zone = 200
    lanes_blocked = {'left': False, 'center': False, 'right': False}

    for i in shotrus:
        if garir_z < i[2] < garir_z + danger_zone:
            if i[0] < -rastar_width/6:
                lanes_blocked['left'] = True
            elif i[0] > rastar_width/6:
                lanes_blocked['right'] = True
            else:
                lanes_blocked['center'] = True

    if garir_x < -rastar_width/6:
        current_lane = 'left'
    elif garir_x > rastar_width/6:
        current_lane = 'right'
    else:
        current_lane = 'center'

    safe_lane = None
    if not lanes_blocked[current_lane]:
        safe_lane = current_lane
    else:
        for lane in ['center', 'left', 'right']:
            if not lanes_blocked[lane]:
                safe_lane = lane
                break

    if safe_lane:
        target_x = lane_positions[safe_lane]
        distance_to_target = target_x - garir_x

        if abs(distance_to_target) > 5:
            garir_x += garir_speed * 1.2 if distance_to_target > 0 else -garir_speed * 1.2
        else:
            garir_x = target_x



def setupCamera():
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    
    
    if view_mode == 0:  # Third-person 
        gluLookAt(0 + shake_x + camera_x_offset, 200 + cam_zoom, garir_z - 300,
                  0 + camera_x_offset, garir_y, garir_z + 100,
                  0, 1, 0)
    
    elif view_mode == 1:  # First-person 
        if fly_active==False:
            gluLookAt(garir_x + shake_x + camera_x_offset, garir_y + 30 + shake_y, garir_z + 10,
                  garir_x + camera_x_offset, garir_y + 30, garir_z + 500,
                  0, 1, 0)
        else:
            gluLookAt(garir_x + shake_x + camera_x_offset, garir_y + 90 + shake_y, garir_z + 10,
                  garir_x + camera_x_offset, garir_y + 90, garir_z + 500,
                  0, 1, 0)

def update():
    global shield_active, shield_timer, speed_boost_active, speed_boost_timer
    global powerup_spawn_timer, player_lives

    # Spawn power-ups periodically
    powerup_spawn_timer += 1
    if powerup_spawn_timer >= 180:  # spawn interval
        if random.random() < 0.3:
            spawn_powerup()
        powerup_spawn_timer = 0

    # Update timers
    if shield_active:
        shield_timer -= 1
        if shield_timer <= 0:
            shield_active = False

    if speed_boost_active:
        speed_boost_timer -= 1
        if speed_boost_timer <= 0:
            speed_boost_active = False

    # ===== POWER-UP COLLISION =====
    for pup in powerups[:]:
        pup_x, pup_y, pup_z, pup_type = pup
        if check_collision(garir_x, garir_z, car_width, car_length, pup_x, pup_z, 20, 20):
            if pup_type == 1:  # Shield
                shield_active = True
                shield_timer = shield_duration
                print("Shield activated!")
            elif pup_type == 2:  # Speed Boost
                speed_boost_active = True
                speed_boost_timer = speed_boost_duration
                print("Speed boost activated!")

            powerups.remove(pup)
        elif pup_z < garir_z - 100:
            # Remove power-ups that passed behind player
            powerups.remove(pup)

def draw_simple_sphere_outline(r, parts=16):
    import math
    
    for i in range(parts):
        angle_v = (i / parts) * 3.14159  # Vertical angle (0 to pi)
        y = r * math.cos(angle_v)
        r = r * math.sin(angle_v)
        
        glBegin(GL_LINE_LOOP)
        for j in range(parts):
            angle_h = (j / parts) * 2 * 3.14159  # Horizontal angle (0 to 2*pi)
            x = r * math.cos(angle_h)
            z = r * math.sin(angle_h)
            glVertex3f(x, y, z)
        glEnd()
    
    for i in range(4):
        angle = (i / 4) * 2 * 3.14159
        glBegin(GL_LINE_LOOP)
        for j in range(parts):
            angle_v = (j / parts) * 2 * 3.14159
            y = r * math.cos(angle_v)
            r = r * math.sin(angle_v)
            x = r * math.cos(angle)
            z = r * math.sin(angle)
            glVertex3f(x, y, z)
        glEnd()

def draw_speedboost_effect_simple(x, y, z):
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
    wing_l = 60
    wing_w = 10
    wing_height = 2

    glBegin(GL_TRIANGLES)
    glVertex3f(-car_width / 2, 60, 0)                  
    glVertex3f(-car_width / 2 - wing_l, 60, -wing_w)  
    glVertex3f(-car_width / 2 - wing_l, 60, wing_w)   
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex3f(car_width / 2, 60, 0)                   
    glVertex3f(car_width / 2 + wing_l, 60, -wing_w)  
    glVertex3f(car_width / 2 + wing_l, 60, wing_w)   
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
    
    car_color = [0,1, 0]  # green

    if shield_active and not fly_active:
        car_color = [0,0.5,1]  # Blue shield

    if auto_pilot:
        car_color = [1, 1,0]  # Yellow auto-pilot
    
    
    if shield_active==True and  fly_active== False:
        glPushMatrix()
        glTranslatef(garir_x, garir_y + 10, garir_z)
        glColor4f(0.0, 0.5, 1.0, 0.3)
        draw_sheild_visual(car_width, 12)
        glPopMatrix()

    if speed_boost_active==True and fly_active==False:
        draw_speedboost_visual(garir_x, garir_y, garir_z)

    if fly_active==True:
        draw_wings(garir_x, garir_y, garir_z)

def keyboardListener(key, x, y):
    global garir_x, pause, auto_pilot, view_mode, game_running,garir_z
    global fly_active, fly_cars_left, fly_count
    
    if key == b'r' or key == b'R':
        if khela_sesh:
            init_game()
        return
    
    if key == b'p' or key == b'P':
        pause = not pause
        return
    
    if key == b'c' or key == b'C':
        auto_pilot = not auto_pilot
        return
    
    if key == b'v' or key == b'V':
        view_mode = (view_mode + 1) % 3
        
        return
    

def specialKeyListener(key, x, y):
    global cam_zoom, camera_x_offset
    
    if key == GLUT_KEY_UP:
        cam_zoom += 10
        
    elif key == GLUT_KEY_DOWN:
        cam_zoom -= 10
        
    elif key == GLUT_KEY_LEFT:
        camera_x_offset += 15
        if camera_x_offset > cam_left:
            camera_x_offset = cam_left

    elif key == GLUT_KEY_RIGHT:
        camera_x_offset -= 15
        if camera_x_offset < cam_right:
            camera_x_offset = cam_right