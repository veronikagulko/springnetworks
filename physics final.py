from vpython import *

scene = canvas(
    title="Click to Draw Circles",
    width=800,
    height=600,
    background=color.black
)
scene.userzoom = False
scene.range = 5
scene.center = vec(0, 0, 0)

scene.lights = []
light1 = local_light(pos=vector(5, 5, 5), color=color.red)
light2 = local_light(pos=vector(5, 5, -5), color=color.cyan)

run      = True
radius   = 0.5
neighbors = 2
gravity  = vec(0, -3, 0)
dt       = 0.01
damping  = 0.995
mass     = 1.0          
k_spring = 5.0          

circles            = []
velocities         = []
springs            = []
spring_pairs       = []
spring_rest_lengths = []

def clear_action(b):
    for c in circles:
        c.visible = False
        c.delete()
    for s in springs:
        s.visible = False
        s.delete()
    circles.clear()
    velocities.clear()
    springs.clear()
    spring_pairs.clear()
    spring_rest_lengths.clear()

button(bind=clear_action, text="Clear Screen")
scene.append_to_caption("\n\n")

mass_label = wtext(text=f"Node Mass: {mass:.2f} kg    ")

def set_mass(s):
    global mass
    mass = s.value
    mass_label.text = f"Node Mass: {mass:.2f} kg    "

slider(bind=set_mass, min=0.1, max=10.0, value=mass, length=220)
scene.append_to_caption("\n\n")

k_label = wtext(text=f"Spring k:  {k_spring:.1f} N/m  ")

def set_k(s):
    global k_spring
    k_spring = s.value
    k_label.text = f"Spring k:  {k_spring:.1f} N/m  "

slider(bind=set_k, min=0.5, max=30.0, value=k_spring, length=220)
scene.append_to_caption("\n")

def not_overlapping_nodes(new_pos):
    for c in circles:
        if mag(c.pos - new_pos) < radius * 2:
            return False
    return True

def spring_generator():
    if len(circles) < 2:
        return
    for s in springs:
        s.visible = False
        s.delete()
    springs.clear()
    spring_pairs.clear()
    spring_rest_lengths.clear()

    for i in range(len(circles)):
        dists = []
        for j in range(len(circles)):
            if i != j:
                dists.append((mag(circles[i].pos - circles[j].pos), j))
        dists.sort()
        for dist, j in dists[:neighbors]:
            pair = tuple(sorted((i, j)))
            if pair not in spring_pairs:
                spring_pairs.append(pair)

    for i, j in spring_pairs:
        rest = mag(circles[i].pos - circles[j].pos)
        spring_rest_lengths.append(rest)
        springs.append(helix(
            pos=circles[i].pos,
            axis=circles[j].pos - circles[i].pos,
            radius=0.08,
            thickness=0.03,
            color=color.yellow
        ))

def draw_circle(evt):
    click_pos = evt.pos + vec(0, 0, 0.1)
    if not_overlapping_nodes(click_pos):
        circles.append(sphere(pos=click_pos, radius=radius, color=color.white))
        velocities.append(vec(0, 0, 0))
        spring_generator()
    else:
        print("Circle overlaps! Not drawing.")

scene.bind("mousedown", draw_circle)

def update_springs():
    for s in range(len(springs)):
        i, j = spring_pairs[s]
        springs[s].pos  = circles[i].pos
        springs[s].axis = circles[j].pos - circles[i].pos

while run:
    rate(60)
    if len(circles) == 0:
        continue

    forces = [gravity * mass for _ in circles]

    for s_idx in range(len(springs)):
        i, j   = spring_pairs[s_idx]
        L0     = spring_rest_lengths[s_idx]
        delta  = circles[j].pos - circles[i].pos
        dist   = mag(delta)
        if dist == 0:
            continue
        stretch      = dist - L0
        force_mag    = k_spring * stretch
        force_dir    = norm(delta)
        spring_force = force_mag * force_dir
        forces[i] += spring_force        
        forces[j] -= spring_force        

    for i in range(len(circles)):
        accel         = forces[i] / mass
        velocities[i] = (velocities[i] + accel * dt) * damping
        if circles[i].pos.y > -4:
            circles[i].pos += velocities[i] * dt

    update_springs()