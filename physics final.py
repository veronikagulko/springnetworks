from vpython import *
#Web VPython 3.2

scene = canvas(
    title="Spring Network",
    width=800,
    height=600,
    background=color.black
)
scene.userzoom = True
scene.userspin = True
scene.range = 6
scene.center = vec(0, 0, 0)

local_light(pos=vector(5, 5, 5), color=color.red)
local_light(pos=vector(5, 5, -5), color=color.cyan)

dt = 0.005
gravity_on = False
g_strength = 5.0
k_spring = 8.0
damping = 0.999
neighbors = 2
default_mass = 1.0
COR = 0.5
BASE_RADIUS = 0.35

FLOOR_Y = -4.6
WALL_X = 4.6
CEIL_Y = 4.6
SPRING_CLEARANCE = 0.10
SPRING_Z = 0.5
SPRING_Z = 0.5
SPRING_CLEARANCE = 0.18
WALL_Z = 4.6
place_z = 0

def make_spring_visual(i, j):
    a = circles[i].pos
    b = circles[j].pos

    return helix(
        pos=a,
        axis=b - a,
        radius=0.12,
        thickness=0.035,
        color=color.yellow
    )

def update_spring_visual(spring_obj, i, j):
    a = circles[i].pos
    b = circles[j].pos

    spring_obj.pos = a
    spring_obj.axis = b - a
    
def hide_spring_visual(spring_obj):
    spring_obj.visible = False

circles = []
velocities = []
masses = []
fixed_nodes = []

springs = []
spring_pairs = []
spring_rest_lengths = []

selected_idx = [None]

COL_FREE = color.white
COL_FIXED = vector(1, 0.35, 0.1)
COL_SELECTED = color.cyan

def node_color(i):
    if selected_idx[0] == i:
        return COL_SELECTED
    if fixed_nodes[i]:
        return COL_FIXED
    return COL_FREE

def refresh_colors():
    for i in range(len(circles)):
        circles[i].color = node_color(i)

def visual_radius(m):
    return BASE_RADIUS * pow(m / default_mass, 1.0 / 3.0)

def pair_exists(a, b):
    for p in range(len(spring_pairs)):
        if spring_pairs[p][0] == a and spring_pairs[p][1] == b:
            return True
    return False

def make_spring_visual(i, j):
    a = circles[i].pos
    b = circles[j].pos

    return cylinder(
        pos=vec(a.x, a.y, SPRING_Z),
        axis=vec(b.x - a.x, b.y - a.y, 0),
        radius=0.055,
        color=color.green,
        emissive=True
    )

def update_spring_visual(spring_obj, i, j):
    a = circles[i].pos
    b = circles[j].pos

    spring_obj.pos = vec(a.x, a.y, SPRING_Z)
    spring_obj.axis = vec(b.x - a.x, b.y - a.y, 0)

def hide_spring_visual(spring_obj):
    spring_obj.visible = False

def rebuild_springs():
    global springs, spring_pairs, spring_rest_lengths

    for s in springs:
        hide_spring_visual(s)

    springs = []
    spring_pairs = []
    spring_rest_lengths = []

    if len(circles) < 2:
        spring_count_label.text = "  Springs = 0  "
        return

    for i in range(len(circles)):
        made = 0

        for j in range(i + 1, len(circles)):
            if made < int(neighbors):
                spring_pairs.append([i, j])
                spring_rest_lengths.append(mag(circles[i].pos - circles[j].pos))
                springs.append(make_spring_visual(i, j))
                made = made + 1

    spring_count_label.text = "  Springs = " + str(len(springs)) + "  "

def select_node(i):
    selected_idx[0] = i
    m = masses[i]
    status = ""

    if fixed_nodes[i]:
        status = "  [ANCHOR]"

    sel_label.text = "  Node " + str(i) + status + " - mass: " + str(round(m, 2)) + " kg   "
    mass_slider.value = m
    refresh_colors()

def deselect():
    selected_idx[0] = None
    sel_label.text = "  Click a node to select it           "
    refresh_colors()

scene.append_to_caption("\n")

def toggle_gravity(b):
    global gravity_on

    gravity_on = not gravity_on

    if gravity_on:
        b.text = "Pause Gravity"
    else:
        b.text = "Start Gravity"

button(bind=toggle_gravity, text="Start Gravity")
scene.append_to_caption("   ")


g_label = wtext(text="  g = " + str(round(g_strength, 1)) + " m/s^2  ")

def set_g(s):
    global g_strength

    g_strength = s.value
    g_label.text = "  g = " + str(round(g_strength, 1)) + " m/s^2  "

slider(bind=set_g, min=0.5, max=25.0, value=g_strength, length=190)

scene.append_to_caption("\n\n")

z_label = wtext(text="Placement z = " + str(round(place_z, 1)) + "  ")

def set_place_z(s):
    global place_z
    place_z = s.value
    z_label.text = "Placement z = " + str(round(place_z, 1)) + "  "

slider(bind=set_place_z, min=-4.0, max=4.0, value=place_z, length=190)

scene.append_to_caption("\n\n")

k_label = wtext(text="Spring k = " + str(round(k_spring, 1)) + " N/m  ")

def set_k(s):
    global k_spring

    k_spring = s.value
    k_label.text = "Spring k = " + str(round(k_spring, 1)) + " N/m  "

slider(bind=set_k, min=0.5, max=60.0, value=k_spring, length=190)

scene.append_to_caption("\n\n")

nb_label = wtext(text="Neighbors = " + str(int(neighbors)) + "  ")
spring_count_label = wtext(text="  Springs = 0  ")

def set_neighbors(s):
    global neighbors

    neighbors = int(s.value)
    nb_label.text = "Neighbors = " + str(neighbors) + "  "
    rebuild_springs()

slider(bind=set_neighbors, min=1, max=6, value=neighbors, length=190)

scene.append_to_caption("\n\n")

damp_label = wtext(text="Damping = " + str(round(damping, 4)) + "  ")

def set_damping(s):
    global damping

    damping = s.value
    damp_label.text = "Damping = " + str(round(damping, 4)) + "  "

slider(bind=set_damping, min=0.980, max=1.000, value=damping, length=190)

scene.append_to_caption("\n\n")

sel_label = wtext(text="  Click a node to select it           ")

scene.append_to_caption("\n\n")

wtext(text="  Node mass: ")

def set_sel_mass(s):
    if selected_idx[0] != None:
        i = selected_idx[0]
        masses[i] = s.value
        circles[i].radius = visual_radius(s.value)

        status = ""

        if fixed_nodes[i]:
            status = "  [ANCHOR]"

        sel_label.text = "  Node " + str(i) + status + " - mass: " + str(round(s.value, 2)) + " kg   "

mass_slider = slider(bind=set_sel_mass, min=0.1, max=20.0, value=default_mass, length=190)

scene.append_to_caption("\n\n")

def toggle_anchor(b):
    if selected_idx[0] == None:
        return

    i = selected_idx[0]
    fixed_nodes[i] = not fixed_nodes[i]

    if fixed_nodes[i]:
        velocities[i] = vec(0, 0, 0)

    select_node(i)

def reset_velocities(b):
    for i in range(len(velocities)):
        velocities[i] = vec(0, 0, 0)

def clear_all(b):
    global circles, velocities, masses, fixed_nodes
    global springs, spring_pairs, spring_rest_lengths

    for i in range(len(circles)):
        circles[i].visible = False

    for j in range(len(springs)):
        hide_spring_visual(springs[j])

    circles = []
    velocities = []
    masses = []
    fixed_nodes = []
    springs = []
    spring_pairs = []
    spring_rest_lengths = []

    spring_count_label.text = "  Springs = 0  "
    deselect()

button(bind=toggle_anchor, text="Toggle Anchor")
scene.append_to_caption("   ")

button(bind=reset_velocities, text="Reset Velocities")
scene.append_to_caption("   ")

button(bind=clear_all, text="Clear All")
scene.append_to_caption("\n\n")

wtext(
    text="  Left-click empty space: place node   |"
    "   Left-click node: select / edit   |"
    "   Anchor nodes ignore all forces\n"
)

def on_click(evt):
    picked = scene.mouse.pick

    if picked != None:
        for i in range(len(circles)):
            if picked == circles[i]:
                select_node(i)
                return

    click_pos = evt.pos
    pos = vec(click_pos.x, click_pos.y, place_z)

    overlaps = False

    for k in range(len(circles)):
        dist = mag(pos - circles[k].pos)

        if dist < circles[k].radius + BASE_RADIUS:
            overlaps = True

    if not overlaps:
        m = default_mass

        circles.append(
            sphere(
                pos=pos,
                radius=visual_radius(m),
                color=COL_FREE
            )
        )

        velocities.append(vec(0, 0, 0))
        masses.append(m)
        fixed_nodes.append(False)

        rebuild_springs()
        select_node(len(circles) - 1)
        
scene.bind("mousedown", on_click)
while True:
    rate(120)

    if len(circles) == 0:
        continue

    forces = []

    for i in range(len(circles)):
        forces.append(vec(0, 0, 0))

    if gravity_on:
        for i in range(len(circles)):
            if not fixed_nodes[i]:
                forces[i].y = forces[i].y - g_strength * masses[i]

    for s_idx in range(len(springs)):
        i = spring_pairs[s_idx][0]
        j = spring_pairs[s_idx][1]

        L0 = spring_rest_lengths[s_idx]
        delta = circles[j].pos - circles[i].pos
        dist = mag(delta)

        if dist < 1e-9:
            continue

        f = k_spring * (dist - L0) * norm(delta)

        if not fixed_nodes[i]:
            forces[i] = forces[i] + f

        if not fixed_nodes[j]:
            forces[j] = forces[j] - f

    for i in range(len(circles)):
        if fixed_nodes[i]:
            continue

        accel = forces[i] / masses[i]

        velocities[i] = (velocities[i] + accel * dt) * damping
        circles[i].pos = circles[i].pos + velocities[i] * dt

        r = circles[i].radius

        if circles[i].pos.y - r < FLOOR_Y:
            circles[i].pos.y = FLOOR_Y + r
            velocities[i].y = abs(velocities[i].y) * COR

        if circles[i].pos.y + r > CEIL_Y:
            circles[i].pos.y = CEIL_Y - r
            velocities[i].y = -abs(velocities[i].y) * COR

        if circles[i].pos.x - r < -WALL_X:
            circles[i].pos.x = -WALL_X + r
            velocities[i].x = abs(velocities[i].x) * COR

        if circles[i].pos.x + r > WALL_X:
            circles[i].pos.x = WALL_X - r
            velocities[i].x = -abs(velocities[i].x) * COR
        
        if circles[i].pos.z - r < -WALL_Z:
            circles[i].pos.z = -WALL_Z + r
            velocities[i].z = abs(velocities[i].z) * COR

        if circles[i].pos.z + r > WALL_Z:
            circles[i].pos.z = WALL_Z - r
            velocities[i].z = -abs(velocities[i].z) * COR

    # Elastic collisions between nodes
    for a in range(len(circles)):
        for b in range(a + 1, len(circles)):
            delta = circles[b].pos - circles[a].pos
            dist = mag(delta)
            min_dist = circles[a].radius + circles[b].radius

            if dist < 1e-9:
                delta = vec(1, 0, 0)
                dist = 1

            if dist < min_dist:
                n = norm(delta)
                overlap = min_dist - dist

                if fixed_nodes[a] and fixed_nodes[b]:
                    continue

                if fixed_nodes[a]:
                    circles[b].pos = circles[b].pos + n * overlap
                elif fixed_nodes[b]:
                    circles[a].pos = circles[a].pos - n * overlap
                else:
                    circles[a].pos = circles[a].pos - n * (overlap / 2)
                    circles[b].pos = circles[b].pos + n * (overlap / 2)

                rel_vel = velocities[b] - velocities[a]
                speed = dot(rel_vel, n)

                if speed < 0:
                    impulse = -(1 + COR) * speed
                    impulse = impulse / ((1 / masses[a]) + (1 / masses[b]))

                    if not fixed_nodes[a]:
                        velocities[a] = velocities[a] - n * impulse / masses[a]

                    if not fixed_nodes[b]:
                        velocities[b] = velocities[b] + n * impulse / masses[b]

    # Collisions between nodes and helix centerlines
    for n in range(len(circles)):
        if fixed_nodes[n]:
            continue

        p = circles[n].pos
        node_r = circles[n].radius

        for s_idx in range(len(spring_pairs)):
            a_idx = spring_pairs[s_idx][0]
            b_idx = spring_pairs[s_idx][1]

            if n == a_idx or n == b_idx:
                continue

            a = circles[a_idx].pos
            b = circles[b_idx].pos
            ab = b - a
            ab_len2 = dot(ab, ab)

            if ab_len2 < 1e-9:
                continue

            t = dot(p - a, ab) / ab_len2

            if t < 0:
                t = 0
            if t > 1:
                t = 1

            closest = a + ab * t
            delta = p - closest
            dist = mag(delta)

            min_dist = node_r + SPRING_CLEARANCE

            if dist < 1e-9:
                spring_dir = norm(ab)
                delta = vec(-spring_dir.y, spring_dir.x, 0)
                dist = 1

            if dist < min_dist:
                push_dir = norm(delta)
                overlap = min_dist - dist

                circles[n].pos = circles[n].pos + push_dir * overlap

                speed_toward_helix = dot(velocities[n], push_dir)

                if speed_toward_helix < 0:
                    velocities[n] = velocities[n] - (1 + COR) * speed_toward_helix * push_dir

    for s_idx in range(len(springs)):
        i = spring_pairs[s_idx][0]
        j = spring_pairs[s_idx][1]

        update_spring_visual(springs[s_idx], i, j)