from vpython import *

scene = canvas(
    title="Spring Network",
    width=800,
    height=600,
    background=color.black
)

scene.userzoom = False
scene.range = 5
scene.center = vec(0, 0, 0)
scene.lights = []

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

SPRING_POINTS = 36
SPRING_COILS = 8
SPRING_AMP = 0.12

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

def pair_seen(seen, a, b):
    key = str(a) + "-" + str(b)

    for i in range(len(seen)):
        if seen[i] == key:
            return True

    seen.append(key)
    return False

def sort_distances(dists):
    for i in range(len(dists)):
        for j in range(0, len(dists) - 1):
            if dists[j][0] > dists[j + 1][0]:
                temp = dists[j]
                dists[j] = dists[j + 1]
                dists[j + 1] = temp

def spring_points(a, b):
    pts = []
    delta = b - a
    L = mag(delta)

    if L < 1e-9:
        for q in range(SPRING_POINTS):
            pts.append(a)
        return pts

    direction = norm(delta)
    side = vec(-direction.y, direction.x, 0)

    for q in range(SPRING_POINTS):
        t = q / (SPRING_POINTS - 1)
        center = a + delta * t

        end_fade = sin(pi * t)
        wiggle = sin(2 * pi * SPRING_COILS * t)
        offset = side * SPRING_AMP * wiggle * end_fade

        pts.append(center + offset)

    return pts

def update_spring_visual(spring_obj, a, b):
    pts = spring_points(a, b)

    for q in range(SPRING_POINTS):
        spring_obj.modify(q, pos=pts[q])

def rebuild_springs():
    global springs, spring_pairs, spring_rest_lengths

    for s in springs:
        s.visible = False

    springs = []
    spring_pairs = []
    spring_rest_lengths = []

    if len(circles) < 2:
        return

    seen = []

    for i in range(len(circles)):
        dists = []

        for j in range(len(circles)):
            if j != i:
                distance = mag(circles[i].pos - circles[j].pos)
                dists.append([distance, j])

        sort_distances(dists)

        max_neighbors = int(neighbors)

        if max_neighbors > len(dists):
            max_neighbors = len(dists)

        for n in range(max_neighbors):
            j2 = dists[n][1]
            a = i
            b = j2

            if b < a:
                temp = a
                a = b
                b = temp

            if not pair_seen(seen, a, b):
                spring_pairs.append([a, b])

    for p in range(len(spring_pairs)):
        i = spring_pairs[p][0]
        j = spring_pairs[p][1]
        L0 = mag(circles[i].pos - circles[j].pos)

        spring_rest_lengths.append(L0)

        springs.append(
            curve(
                pos=spring_points(circles[i].pos, circles[j].pos),
                radius=0.025,
                color=color.yellow
            )
        )

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

k_label = wtext(text="Spring k = " + str(round(k_spring, 1)) + " N/m  ")

def set_k(s):
    global k_spring

    k_spring = s.value
    k_label.text = "Spring k = " + str(round(k_spring, 1)) + " N/m  "

slider(bind=set_k, min=0.5, max=60.0, value=k_spring, length=190)

scene.append_to_caption("\n\n")

nb_label = wtext(text="Neighbors = " + str(int(neighbors)) + "  ")

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
        springs[j].visible = False

    circles = []
    velocities = []
    masses = []
    fixed_nodes = []
    springs = []
    spring_pairs = []
    spring_rest_lengths = []

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
    click_pos = evt.pos
    hit_idx = None

    for i in range(len(circles)):
        dx = click_pos.x - circles[i].pos.x
        dy = click_pos.y - circles[i].pos.y
        distance_2d = sqrt(dx * dx + dy * dy)

        if distance_2d < circles[i].radius * 1.5:
            hit_idx = i
            break

    if hit_idx != None:
        select_node(hit_idx)
        return

    pos = vec(click_pos.x, click_pos.y, 0)
    overlaps = False

    for k in range(len(circles)):
        test_pos = vec(pos.x, pos.y, 0)
        circle_pos = vec(circles[k].pos.x, circles[k].pos.y, 0)
        dist = mag(test_pos - circle_pos)

        if dist < circles[k].radius + BASE_RADIUS:
            overlaps = True

    if not overlaps:
        m = default_mass

        circles.append(sphere(pos=pos, radius=visual_radius(m), color=COL_FREE))
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

    for s_idx in range(len(springs)):
        i = spring_pairs[s_idx][0]
        j = spring_pairs[s_idx][1]

        update_spring_visual(springs[s_idx], circles[i].pos, circles[j].pos)
