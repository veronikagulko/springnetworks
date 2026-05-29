from vpython import *

scene = canvas(
    title="Interactive Elastic Pendulum Simulator",
    width=800, height=600,
    background=color.black
)
scene.userzoom = False
scene.range    = 5
scene.center   = vec(0, 0, 0)
scene.lights   = []
local_light(pos=vector(5,  5,  5), color=color.red)
local_light(pos=vector(5,  5, -5), color=color.cyan)

dt           = 0.005          
gravity_on   = False
g_strength   = 5.0
k_spring     = 8.0
damping      = 0.999
neighbors    = 2
default_mass = 1.0
COR          = 0.5            
BASE_RADIUS  = 0.35

# Boundaries  (scene.range = 5  ⟹  coords run ±5)
FLOOR_Y = -4.6
WALL_X  =  4.6
CEIL_Y  =  4.6

# ── State ───────────────────────────────────────────────────────────────────
circles             = []
velocities          = []
masses              = []
fixed_nodes         = []

springs             = []
spring_pairs        = []       
spring_rest_lengths = []

selected_idx = [None]          

COL_FREE     = color.white
COL_FIXED    = vector(1, 0.35, 0.1)  
COL_SELECTED = color.cyan

def node_color(i):
    if selected_idx[0] == i: return COL_SELECTED
    if fixed_nodes[i]:       return COL_FIXED
    return COL_FREE

def refresh_colors():
    for i in range(len(circles)):
        circles[i].color = node_color(i)

def visual_radius(m):
    return BASE_RADIUS * (m / default_mass) ** (1/3)

def rebuild_springs():
    for s in springs:  s.visible = False; s.delete()
    springs.clear(); spring_pairs.clear(); spring_rest_lengths.clear()
    if len(circles) < 2:
        return
    seen = set()
    for i in range(len(circles)):
        dists = sorted(
            [(mag(circles[i].pos - circles[j].pos), j)
             for j in range(len(circles)) if j != i]
        )
        for _, j in dists[:int(neighbors)]:
            pair = tuple(sorted((i, j)))
            if pair not in seen:
                seen.add(pair)
                spring_pairs.append(pair)
    for i, j in spring_pairs:
        L0 = mag(circles[i].pos - circles[j].pos)
        spring_rest_lengths.append(L0)
        springs.append(helix(
            pos=circles[i].pos,
            axis=circles[j].pos - circles[i].pos,
            radius=0.06, thickness=0.025,
            color=color.yellow
        ))

def select_node(i):
    selected_idx[0] = i
    m = masses[i]
    status = "  [ANCHOR]" if fixed_nodes[i] else ""
    sel_label.text = ( f"  Node {i}{status} — mass: {m:.2f} kg   ")
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
    b.text = "⏸  Pause Gravity" if gravity_on else "▶  Start Gravity"
button(bind=toggle_gravity, text="▶  Start Gravity")
scene.append_to_caption("   ")

g_label = wtext(text=f"  g = {g_strength:.1f} m/s²  ")
def set_g(s):
    global g_strength
    g_strength = s.value
    g_label.text = f"  g = {g_strength:.1f} m/s²  "
slider(bind=set_g, min=0.5, max=25.0, value=g_strength, length=190)
scene.append_to_caption("\n\n")

k_label = wtext(text=f"Spring k = {k_spring:.1f} N/m  ")
def set_k(s):
    global k_spring
    k_spring = s.value
    k_label.text = f"Spring k = {k_spring:.1f} N/m  "
slider(bind=set_k, min=0.5, max=60.0, value=k_spring, length=190)
scene.append_to_caption("\n\n")

nb_label = wtext(text=f"Neighbors = {int(neighbors)}  ")
def set_neighbors(s):
    global neighbors
    neighbors = int(s.value)
    nb_label.text = f"Neighbors = {neighbors}  "
    rebuild_springs()
slider(bind=set_neighbors, min=1, max=6, value=neighbors, length=190)
scene.append_to_caption("\n\n")

damp_label = wtext(text=f"Damping  = {damping:.4f}  ")
def set_damping(s):
    global damping
    damping = s.value
    damp_label.text = f"Damping  = {damping:.4f}  "
slider(bind=set_damping, min=0.980, max=1.000, value=damping, length=190)
scene.append_to_caption("\n\n")

sel_label = wtext(text="  Click a node to select it           ")
scene.append_to_caption("\n\n")

wtext(text="  Node mass: ")
def set_sel_mass(s):
    if selected_idx[0] is not None:
        i = selected_idx[0]
        masses[i] = s.value
        circles[i].radius = visual_radius(s.value)
        sel_label.text = (
            f"  Node {i}{'  [ANCHOR]' if fixed_nodes[i] else ''}"
            f" — mass: {s.value:.2f} kg   "
        )
mass_slider = slider(bind=set_sel_mass, min=0.1, max=20.0,
                     value=default_mass, length=190)
scene.append_to_caption("\n\n")

def toggle_anchor(b):
    if selected_idx[0] is None:
        return
    i = selected_idx[0]
    fixed_nodes[i] = not fixed_nodes[i]
    if fixed_nodes[i]:
        velocities[i] = vec(0, 0, 0)
    select_node(i)          # refresh label

def reset_velocities(b):
    for i in range(len(velocities)):
        velocities[i] = vec(0, 0, 0)

def clear_all(b):
    for c in circles: c.visible = False; c.delete()
    for s in springs: s.visible = False; s.delete()
    circles.clear(); velocities.clear(); masses.clear(); fixed_nodes.clear()
    springs.clear(); spring_pairs.clear(); spring_rest_lengths.clear()
    deselect()

button(bind=toggle_anchor,    text="⚓  Toggle Anchor")
scene.append_to_caption("   ")
button(bind=reset_velocities, text="↺  Reset Velocities")
scene.append_to_caption("   ")
button(bind=clear_all,        text="🗑  Clear All")
scene.append_to_caption("\n\n")

wtext(text=(
    "  Left-click empty space → place node   |"
    "   Left-click node → select / edit   |"
    "   Anchor nodes (red) ignore all forces\n"
))


def on_click(evt):
    click_pos = evt.pos
    hit_idx = None
    for i, c in enumerate(circles):
        dx = click_pos.x - c.pos.x
        dy = click_pos.y - c.pos.y
        if (dx*dx + dy*dy) ** 0.5 < c.radius * 1.5:
            hit_idx = i
            break

    if hit_idx is not None:
        select_node(hit_idx)
    else:
        pos = vec(click_pos.x, click_pos.y, 0)
        overlaps = any(
            mag(vec(pos.x, pos.y, 0) - vec(c.pos.x, c.pos.y, 0))
            < circles[k].radius + BASE_RADIUS
            for k, c in enumerate(circles)
        )
        if not overlaps:
            m = default_mass
            circles.append(
                sphere(pos=pos, radius=visual_radius(m), color=COL_FREE)
            )
            velocities.append(vec(0, 0, 0))
            masses.append(m)
            fixed_nodes.append(False)
            rebuild_springs()
        deselect()

scene.bind("mousedown", on_click)

while True:
    rate(120)                          
    if not circles:
        continue
    forces = [vec(0, 0, 0) for _ in circles]
    if gravity_on:
        for i in range(len(circles)):
            if not fixed_nodes[i]:
                forces[i].y -= g_strength * masses[i]
    for s_idx in range(len(springs)):
        i, j  = spring_pairs[s_idx]
        L0    = spring_rest_lengths[s_idx]
        delta = circles[j].pos - circles[i].pos
        dist  = mag(delta)
        if dist < 1e-9:
            continue
        f = k_spring * (dist - L0) * norm(delta)   # Hooke's law
        if not fixed_nodes[i]: forces[i] +=  f
        if not fixed_nodes[j]: forces[j] -= f
    for i in range(len(circles)):
        if fixed_nodes[i]:
            continue

        accel        = forces[i] / masses[i]
        velocities[i] = (velocities[i] + accel * dt) * damping
        circles[i].pos += velocities[i] * dt

        r = circles[i].radius

        # Floor
        if circles[i].pos.y - r < FLOOR_Y:
            circles[i].pos.y  = FLOOR_Y + r
            velocities[i].y   = abs(velocities[i].y) * COR

        # Ceiling
        if circles[i].pos.y + r > CEIL_Y:
            circles[i].pos.y  = CEIL_Y - r
            velocities[i].y   = -abs(velocities[i].y) * COR

        # Left wall
        if circles[i].pos.x - r < -WALL_X:
            circles[i].pos.x  = -WALL_X + r
            velocities[i].x   = abs(velocities[i].x) * COR

        # Right wall
        if circles[i].pos.x + r > WALL_X:
            circles[i].pos.x  = WALL_X - r
            velocities[i].x   = -abs(velocities[i].x) * COR

    for s_idx in range(len(springs)):
        i, j = spring_pairs[s_idx]
        springs[s_idx].pos  = circles[i].pos
        springs[s_idx].axis = circles[j].pos - circles[i].pos
