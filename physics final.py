Web VPython 3.2

scene = canvas(
    title="Spring Network Simulation",
    width=760,
    height=560,
    background=color.white,
    align="left"
)

scene.userzoom = False
scene.userspin = True
scene.range = 6
scene.center = vec(0, 0, 0)
scene.lights = []

# lights used to be multi colored, no longer useful
local_light(pos=vector(5, 5, 5), color=color.white)
local_light(pos=vector(5, 5, -5), color=color.white)

# def + visualize the bound box + color in the floor
floorY = -4.6
ceilingY = 4.6
wallX = 4.6
wallZ = 4.6

floor_visual = box(canvas=scene, pos=vec(0, floorY - 0.03, 0), size=vec(2 * wallX, 0.06, 2 * wallZ), color=vector(0.85, 0.85, 0.85), opacity=0.35)
bounds_frame = box(canvas=scene, pos=vec(0, 0, 0), size=vec(2 * wallX, ceilingY - floorY, 2 * wallZ), color=color.gray(0.6),opacity=0.08)

# simulation frame rate controls
dt = 0.005
time = 0
energy_counter = 0
# plots graph every 2 frames (instead of every)
ENERGY_PLOT_EVERY = 2

simulation_running = False
gravity_on = False
show_vectors = True

# parameters for beginning of sim
g_strength = 9.8
k_spring = 8.0
damping = 0.999
neighbors = 2
default_mass = 1.0
bounceLoss = 0.5
baseRadius = 0.35
place_z = 0
springClearance = 0.18

forceScale = 0.12
selectForceScale = 0.28
maxForceArrow = 3.0
maxSelectArrow = 3.5


freeColor = color.black
fixedColor = vector(1, 0.35, 0.1)
selectedColor = color.red

gravityColor = color.red
springColor = color.black
normalColor = color.blue
totalColor = color.green

# storage lists
circles = []
velocities = []
masses = []
fixed_nodes = []

springs = []
springLinks = []
spring_rest_lengths = []

grav_force_arrows = []
normal_force_arrows = []
spring_force_arrows_a = []
spring_force_arrows_b = []

last_gravity_forces = []
last_normal_forces = []
last_spring_forces = []

selectedNode = [None]

def node_color(i):
    if selectedNode[0] == i:
        return selectedColor
    if fixed_nodes[i]:
        return fixedColor
    return freeColor

def refresh_colors():
    for i in range(len(circles)):
        circles[i].color = node_color(i)

def visual_radius(m):
    return baseRadius * pow(m / default_mass, 1.0 / 3.0)

def limited_axis(F, scale, max_len):
    if mag(F) < 1e-9:
        return vec(0, 0, 0)

    axis = F * scale

    if mag(axis) > max_len:
        axis = norm(axis) * max_len

    return axis

def show_arrow(arr, p, F, scale, max_len):
    arr.pos = p

    if not show_vectors:
        arr.visible = False
        return

    if mag(F) < 1e-9:
        arr.axis = vec(0, 0, 0)
        arr.visible = False
    else:
        arr.axis = limited_axis(F, scale, max_len)
        arr.visible = True

def hide_arrow(arr):
    arr.visible = False

def make_spring_visual(i, j):
    a = circles[i].pos
    b = circles[j].pos

    return cylinder(
        canvas=scene,
        pos=a,
        axis=b - a,
        radius=0.055,
        color=color.yellow,
        emissive=True
    )

def update_spring_visual(spring_obj, i, j):
    a = circles[i].pos
    b = circles[j].pos

    spring_obj.pos = a
    spring_obj.axis = b - a

def hide_spring_visual(spring_obj):
    spring_obj.visible = False

def create_node_force_arrows(pos):
    grav_force_arrows.append(
        arrow(canvas=scene, pos=pos, axis=vec(0, 0, 0), color=gravityColor, shaftwidth=0.08)
    )

    normal_force_arrows.append(
        arrow(canvas=scene, pos=pos, axis=vec(0, 0, 0), color=normalColor, shaftwidth=0.08)
    )

    last_gravity_forces.append(vec(0, 0, 0))
    last_normal_forces.append(vec(0, 0, 0))
    last_spring_forces.append(vec(0, 0, 0))

def create_spring_force_arrows(i, j):
    spring_force_arrows_a.append(
        arrow(canvas=scene, pos=circles[i].pos, axis=vec(0, 0, 0), color=springColor, shaftwidth=0.07)
    )

    spring_force_arrows_b.append(
        arrow(canvas=scene, pos=circles[j].pos, axis=vec(0, 0, 0), color=springColor, shaftwidth=0.07)
    )

def rebuild_springs():
    global springs, springLinks, spring_rest_lengths
    global spring_force_arrows_a, spring_force_arrows_b

    for s in springs:
        hide_spring_visual(s)

    for a in spring_force_arrows_a:
        hide_arrow(a)

    for b in spring_force_arrows_b:
        hide_arrow(b)

    springs = []
    springLinks = []
    spring_rest_lengths = []
    spring_force_arrows_a = []
    spring_force_arrows_b = []

    if len(circles) < 2:
        spring_count_label.text = "Springs = 0"
        return

    for i in range(len(circles)):
        made = 0

        for j in range(i + 1, len(circles)):
            if made < int(neighbors):
                springLinks.append([i, j])
                spring_rest_lengths.append(mag(circles[i].pos - circles[j].pos))
                springs.append(make_spring_visual(i, j))
                create_spring_force_arrows(i, j)
                made = made + 1

    spring_count_label.text = "Springs = " + str(len(springs))

def compute_energies():
    kinetic = 0
    spring_potential = 0
    gravity_potential = 0

    for i in range(len(circles)):
        kinetic = kinetic + 0.5 * masses[i] * mag2(velocities[i])

        if gravity_on:
            gravity_potential = gravity_potential + masses[i] * g_strength * (circles[i].pos.y - floorY)

    for s_idx in range(len(springLinks)):
        i = springLinks[s_idx][0]
        j = springLinks[s_idx][1]

        L0 = spring_rest_lengths[s_idx]
        dist = mag(circles[j].pos - circles[i].pos)

        spring_potential = spring_potential + 0.5 * k_spring * pow(dist - L0, 2)

    potential = spring_potential + gravity_potential
    total = kinetic + potential

    return [kinetic, potential, total]

scene.append_to_caption("<b>NODE CONTROLS</b><br><br>")

scene.append_to_caption("   ")
sel_label = wtext(text="No node selected")
scene.append_to_caption("<br><br>")

scene.append_to_caption("   ")
wtext(text="Node mass: ")

def set_sel_mass(s):
    if selectedNode[0] != None:
        i = selectedNode[0]
        masses[i] = s.value
        circles[i].radius = visual_radius(s.value)

        status = ""
        if fixed_nodes[i]:
            status = " [STATIONARY]"

        sel_label.text = "Node " + str(i) + status + " - mass: " + str(round(s.value, 2)) + " kg"

scene.append_to_caption("   ")
mass_slider = slider(bind=set_sel_mass, min=0.1, max=20.0, value=default_mass, length=210)

scene.append_to_caption("<br><br>")

def select_node(i):
    selectedNode[0] = i
    m = masses[i]

    status = ""
    if fixed_nodes[i]:
        status = " [STATIONARY]"

    sel_label.text = "Node " + str(i) + status + " - mass: " + str(round(m, 2)) + " kg"
    mass_slider.value = m
    refresh_colors()

def deselect():
    selectedNode[0] = None
    sel_label.text = "Click a node to see controls"
    refresh_colors()

def toggle_anchor(b):
    if selectedNode[0] == None:
        return

    i = selectedNode[0]
    fixed_nodes[i] = not fixed_nodes[i]

    if fixed_nodes[i]:
        velocities[i] = vec(0, 0, 0)

    select_node(i)

scene.append_to_caption("   ")
button(bind=toggle_anchor, text="Stationary On/Off")
scene.append_to_caption("<br><br><b>   ANIMATION CONTROLS</b><br><br>")

def toggle_gravity(b):
    global gravity_on, simulation_running
    global time, energy_counter
    global kinetic_curve, potential_curve, total_curve

    gravity_on = not gravity_on
    simulation_running = gravity_on

    if gravity_on:
        b.text = "Pause Gravity"

        time = 0
        energy_counter = 0

        kinetic_curve.delete()
        potential_curve.delete()
        total_curve.delete()

        kinetic_curve = gcurve(graph=energy_graph, color=color.red, label="Kinetic")
        potential_curve = gcurve(graph=energy_graph, color=color.blue, label="Potential")
        total_curve = gcurve(graph=energy_graph, color=color.black, label="Total")
    else:
        b.text = "Begin Gravity"

scene.append_to_caption("   ")
button(bind=toggle_gravity, text="Begin Gravity")
scene.append_to_caption("   ")

def reset_velocities(b):
    for i in range(len(velocities)):
        velocities[i] = vec(0, 0, 0)

button(bind=reset_velocities, text="Reset Velocities")
scene.append_to_caption("   ")

def toggle_vectors(b):
    global show_vectors

    show_vectors = not show_vectors

    if show_vectors:
        b.text = "Remove Vectors"
    else:
        b.text = "Show Vectors"

button(bind=toggle_vectors, text="Remove Vectors")
scene.append_to_caption("   ")

def clear_all(b):
    global circles, velocities, masses, fixed_nodes
    global springs, springLinks, spring_rest_lengths
    global grav_force_arrows, normal_force_arrows
    global spring_force_arrows_a, spring_force_arrows_b
    global last_gravity_forces, last_normal_forces, last_spring_forces
    global time, energy_counter
    global kinetic_curve, potential_curve, total_curve
    global gravity_on, simulation_running

    for i in range(len(circles)):
        circles[i].visible = False

    for s in springs:
        hide_spring_visual(s)

    for a in grav_force_arrows:
        hide_arrow(a)

    for a in normal_force_arrows:
        hide_arrow(a)

    for a in spring_force_arrows_a:
        hide_arrow(a)

    for a in spring_force_arrows_b:
        hide_arrow(a)

    circles = []
    velocities = []
    masses = []
    fixed_nodes = []

    springs = []
    springLinks = []
    spring_rest_lengths = []

    grav_force_arrows = []
    normal_force_arrows = []
    spring_force_arrows_a = []
    spring_force_arrows_b = []

    last_gravity_forces = []
    last_normal_forces = []
    last_spring_forces = []

    selectedNode[0] = None

    time = 0
    energy_counter = 0
    gravity_on = False
    simulation_running = False

    kinetic_curve.delete()
    potential_curve.delete()
    total_curve.delete()

    kinetic_curve = gcurve(graph=energy_graph, color=color.red, label="Kinetic")
    potential_curve = gcurve(graph=energy_graph, color=color.blue, label="Potential")
    total_curve = gcurve(graph=energy_graph, color=color.black, label="Total")

    spring_count_label.text = "Springs = 0"
    sel_label.text = "Click a node to see controls"
    mass_slider.value = default_mass

    sel_g_arrow.visible = False
    sel_s_arrow.visible = False
    sel_n_arrow.visible = False
    sel_total_arrow.visible = False

    sel_g_label.text = ""
    sel_s_label.text = ""
    sel_n_label.text = ""
    sel_total_label.text = ""

    refresh_colors()

scene.append_to_caption("   ")
button(bind=clear_all, text="Clear Screen")

scene.append_to_caption("<br><br><b>   SPRING CONTROLS</b><br><br>")

k_label = wtext(text="   Spring k = " + str(round(k_spring, 1)) + " N/m  ")

def set_k(s):
    global k_spring

    k_spring = s.value
    k_label.text = "   Spring k = " + str(round(k_spring, 1)) + " N/m  "

scene.append_to_caption("   ")
slider(bind=set_k, min=0.5, max=60.0, value=k_spring, length=210)

scene.append_to_caption("<br><br>")

nb_label = wtext(text="   Neighbors = " + str(int(neighbors)) + "  ")
spring_count_label = wtext(text="   Springs = 0  ")

def set_neighbors(s):
    global neighbors

    neighbors = int(s.value)
    nb_label.text = "   Neighbors = " + str(neighbors) + "  "
    rebuild_springs()

scene.append_to_caption("   ")
slider(bind=set_neighbors, min=1, max=6, value=neighbors, length=210)

scene.append_to_caption("<br><br>")

damp_label = wtext(text="   Damping = " + str(round(damping, 4)) + "  ")

def set_damping(s):
    global damping

    damping = s.value
    damp_label.text = "   Damping = " + str(round(damping, 4)) + "  "

scene.append_to_caption("   ")
slider(bind=set_damping, min=0.980, max=1.000, value=damping, length=210)

scene.append_to_caption("<br><br><b>   3D PLACEMENT</b><br><br>")

z_label = wtext(text="   Placement z = " + str(round(place_z, 1)) + "  ")

def set_place_z(s):
    global place_z

    place_z = s.value
    z_label.text = "   Placement z = " + str(round(place_z, 1)) + "  "

slider(bind=set_place_z, min=-4.0, max=4.0, value=place_z, length=210)

scene.append_to_caption("<br><br><b>   PLANET GRAVITY</b><br><br>")

scene.append_to_caption("   ")
g_label = wtext(text="g = " + str(round(g_strength, 1)) + " m/s^2  ")
scene.append_to_caption("<br>")

def set_mars(b):
    global g_strength
    g_strength = 3.7
    g_label.text = "g = " + str(round(g_strength, 1)) + " m/s^2  "

def set_earth(b):
    global g_strength
    g_strength = 9.8
    g_label.text = "g = " + str(round(g_strength, 1)) + " m/s^2  "

def set_jupiter(b):
    global g_strength
    g_strength = 24.8
    g_label.text = "g = " + str(round(g_strength, 1)) + " m/s^2  "

scene.append_to_caption("   ")
button(bind=set_mars, text="Mars")
scene.append_to_caption("   ")
button(bind=set_earth, text="Earth")
scene.append_to_caption("   ")
button(bind=set_jupiter, text="Jupiter")

scene.append_to_caption("<br><br><b></b><br><br>")
scene.append_to_caption("<br><br>")

force_scene = canvas(
    width=500,
    height=300,
    background=color.white,
    align="left"
)

force_scene.range = 6
force_scene.center = vec(0, 0, 0)
force_scene.userzoom = False
force_scene.userspin = False

force_origin = sphere(
    canvas=force_scene,
    pos=vec(0, 0.7, 0),
    radius=0.24,
    color=color.red
)

sel_g_arrow = arrow(canvas=force_scene, pos=vec(0, 0.7, 0), axis=vec(0, 0, 0), color=gravityColor, shaftwidth=0.14)
sel_s_arrow = arrow(canvas=force_scene, pos=vec(0, 0.7, 0), axis=vec(0, 0, 0), color=springColor, shaftwidth=0.14)
sel_n_arrow = arrow(canvas=force_scene, pos=vec(0, 0.7, 0), axis=vec(0, 0, 0), color=normalColor, shaftwidth=0.14)
sel_total_arrow = arrow(canvas=force_scene, pos=vec(0, 0.7, 0), axis=vec(0, 0, 0), color=totalColor, shaftwidth=0.16)

sel_g_label = label(canvas=force_scene, pos=vec(-5.4, -5.2, 0), text="", box=False, color=gravityColor)
sel_s_label = label(canvas=force_scene, pos=vec(-2.0, -5.2, 0), text="", box=False, color=springColor)
sel_n_label = label(canvas=force_scene, pos=vec(1.4, -5.2, 0), text="", box=False, color=normalColor)
sel_total_label = label(canvas=force_scene, pos=vec(4.7, -5.2, 0), text="", box=False, color=totalColor)

def update_selected_force_view():
    if selectedNode[0] == None:
        sel_g_arrow.visible = False
        sel_s_arrow.visible = False
        sel_n_arrow.visible = False
        sel_total_arrow.visible = False

        sel_g_label.text = ""
        sel_s_label.text = ""
        sel_n_label.text = ""
        sel_total_label.text = ""
        return

    i = selectedNode[0]

    Fg = last_gravity_forces[i]
    Fs = last_spring_forces[i]
    Fn = last_normal_forces[i]
    Ft = Fg + Fs + Fn

    origin = vec(0, 0.7, 0)

    show_arrow(sel_g_arrow, origin, Fg, selectForceScale, maxSelectArrow)
    show_arrow(sel_s_arrow, origin, Fs, selectForceScale, maxSelectArrow)
    show_arrow(sel_n_arrow, origin, Fn, selectForceScale, maxSelectArrow)
    show_arrow(sel_total_arrow, origin, Ft, selectForceScale, maxSelectArrow)

    sel_g_label.pos = vec(-5.4, -5.2, 0)
    sel_s_label.pos = vec(-2.0, -5.2, 0)
    sel_n_label.pos = vec(1.4, -5.2, 0)
    sel_total_label.pos = vec(4.7, -5.2, 0)
    
    sel_g_label.text = "G: " + str(round(mag(Fg), 2)) + " N"
    sel_s_label.text = "S: " + str(round(mag(Fs), 2)) + " N"
    sel_n_label.text = "N: " + str(round(mag(Fn), 2)) + " N"
    sel_total_label.text = "T: " + str(round(mag(Ft), 2)) + " N"

scene.append_to_caption("&nbsp;&nbsp;&nbsp;&nbsp;")
energy_graph = graph(
    title="Kinetic / Potential / Total Mechanical Energy",
    xtitle="time (s)",
    ytitle="energy (J)",
    width=900,
    height=250,
    xmin=0,
    xmax=10,
    scroll=True,
    fast=False,
    align="right"
)

kinetic_curve = gcurve(graph=energy_graph, color=color.red, label="Kinetic")
potential_curve = gcurve(graph=energy_graph, color=color.blue, label="Potential")
total_curve = gcurve(graph=energy_graph, color=color.black, label="Total")

def on_mousedown(evt):
    picked = scene.mouse.pick

    # Select an existing node without moving it.
    if picked != None:
        for i in range(len(circles)):
            if picked == circles[i]:
                select_node(i)
                return

    click_pos = evt.pos
    pos = vec(click_pos.x, click_pos.y, place_z)
    r_new = visual_radius(default_mass)

    # Prevent creation outside the simulation bounds.
    if pos.x - r_new < -wallX:
        return
    if pos.x + r_new > wallX:
        return
    if pos.y - r_new < floorY:
        return
    if pos.y + r_new > ceilingY:
        return
    if pos.z - r_new < -wallZ:
        return
    if pos.z + r_new > wallZ:
        return

    # Prevent nodes from being created on top of each other.
    for k in range(len(circles)):
        if mag(pos - circles[k].pos) < circles[k].radius + r_new:
            return

    circles.append(
        sphere(
            canvas=scene,
            pos=pos,
            radius=r_new,
            color=freeColor
        )
    )

    velocities.append(vec(0, 0, 0))
    masses.append(default_mass)
    fixed_nodes.append(False)

    create_node_force_arrows(pos)
    rebuild_springs()
    select_node(len(circles) - 1)
    

scene.bind("mousedown", on_mousedown)

while True:
    rate(120)

    if len(circles) == 0:
        update_selected_force_view()
        continue

    if not simulation_running:
        for s_idx in range(len(springs)):
            i = springLinks[s_idx][0]
            j = springLinks[s_idx][1]
            update_spring_visual(springs[s_idx], i, j)

        for i in range(len(circles)):
            velocities[i] = vec(0, 0, 0)

        update_selected_force_view()
        continue

    forces = []

    for i in range(len(circles)):
        forces.append(vec(0, 0, 0))
        last_gravity_forces[i] = vec(0, 0, 0)
        last_normal_forces[i] = vec(0, 0, 0)
        last_spring_forces[i] = vec(0, 0, 0)

    if gravity_on:
        for i in range(len(circles)):
            if not fixed_nodes[i]:
                Fg = vec(0, -g_strength * masses[i], 0)
                forces[i] = forces[i] + Fg
                last_gravity_forces[i] = Fg

    for s_idx in range(len(springs)):
        i = springLinks[s_idx][0]
        j = springLinks[s_idx][1]

        L0 = spring_rest_lengths[s_idx]
        delta = circles[j].pos - circles[i].pos
        dist = mag(delta)

        if dist < 1e-9:
            continue

        f = k_spring * (dist - L0) * norm(delta)

        if not fixed_nodes[i]:
            forces[i] = forces[i] + f
            last_spring_forces[i] = last_spring_forces[i] + f

        if not fixed_nodes[j]:
            forces[j] = forces[j] - f
            last_spring_forces[j] = last_spring_forces[j] - f

        show_arrow(spring_force_arrows_a[s_idx], circles[i].pos, f, forceScale, maxForceArrow)
        show_arrow(spring_force_arrows_b[s_idx], circles[j].pos, -f, forceScale, maxForceArrow)

    for i in range(len(circles)):
        if fixed_nodes[i]:
            velocities[i] = vec(0, 0, 0)
            continue

        accel = forces[i] / masses[i]

        velocities[i] = (velocities[i] + accel * dt) * damping
        circles[i].pos = circles[i].pos + velocities[i] * dt

        r = circles[i].radius

        if circles[i].pos.y - r < floorY:
            normal_mag = masses[i] * abs(velocities[i].y) * (1 + bounceLoss) / dt
            circles[i].pos.y = floorY + r
            velocities[i].y = abs(velocities[i].y) * bounceLoss
            last_normal_forces[i] = last_normal_forces[i] + vec(0, normal_mag, 0)

        if circles[i].pos.y + r > ceilingY:
            normal_mag = masses[i] * abs(velocities[i].y) * (1 + bounceLoss) / dt
            circles[i].pos.y = ceilingY - r
            velocities[i].y = -abs(velocities[i].y) * bounceLoss
            last_normal_forces[i] = last_normal_forces[i] + vec(0, -normal_mag, 0)

        if circles[i].pos.x - r < -wallX:
            normal_mag = masses[i] * abs(velocities[i].x) * (1 + bounceLoss) / dt
            circles[i].pos.x = -wallX + r
            velocities[i].x = abs(velocities[i].x) * bounceLoss
            last_normal_forces[i] = last_normal_forces[i] + vec(normal_mag, 0, 0)

        if circles[i].pos.x + r > wallX:
            normal_mag = masses[i] * abs(velocities[i].x) * (1 + bounceLoss) / dt
            circles[i].pos.x = wallX - r
            velocities[i].x = -abs(velocities[i].x) * bounceLoss
            last_normal_forces[i] = last_normal_forces[i] + vec(-normal_mag, 0, 0)

        if circles[i].pos.z - r < -wallZ:
            normal_mag = masses[i] * abs(velocities[i].z) * (1 + bounceLoss) / dt
            circles[i].pos.z = -wallZ + r
            velocities[i].z = abs(velocities[i].z) * bounceLoss
            last_normal_forces[i] = last_normal_forces[i] + vec(0, 0, normal_mag)

        if circles[i].pos.z + r > wallZ:
            normal_mag = masses[i] * abs(velocities[i].z) * (1 + bounceLoss) / dt
            circles[i].pos.z = wallZ - r
            velocities[i].z = -abs(velocities[i].z) * bounceLoss
            last_normal_forces[i] = last_normal_forces[i] + vec(0, 0, -normal_mag)

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
                    impulse = -(1 + bounceLoss) * speed
                    impulse = impulse / ((1 / masses[a]) + (1 / masses[b]))

                    if not fixed_nodes[a]:
                        velocities[a] = velocities[a] - n * impulse / masses[a]

                    if not fixed_nodes[b]:
                        velocities[b] = velocities[b] + n * impulse / masses[b]

    for n in range(len(circles)):
        if fixed_nodes[n]:
            continue

        p = circles[n].pos
        node_r = circles[n].radius

        for s_idx in range(len(springLinks)):
            a_idx = springLinks[s_idx][0]
            b_idx = springLinks[s_idx][1]

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

            min_dist = node_r + springClearance

            if dist < 1e-9:
                spring_dir = norm(ab)
                delta = vec(-spring_dir.y, spring_dir.x, 0)
                dist = 1

            if dist < min_dist:
                push_dir = norm(delta)
                overlap = min_dist - dist

                circles[n].pos = circles[n].pos + push_dir * overlap

                speed_toward_spring = dot(velocities[n], push_dir)

                if speed_toward_spring < 0:
                    velocities[n] = velocities[n] - (1 + bounceLoss) * speed_toward_spring * push_dir

    for s_idx in range(len(springs)):
        i = springLinks[s_idx][0]
        j = springLinks[s_idx][1]

        update_spring_visual(springs[s_idx], i, j)

    for i in range(len(circles)):
        show_arrow(grav_force_arrows[i], circles[i].pos, last_gravity_forces[i], forceScale, maxForceArrow)
        show_arrow(normal_force_arrows[i], circles[i].pos, last_normal_forces[i], forceScale, maxForceArrow)

    update_selected_force_view()

    time = time + dt
    energy_counter = energy_counter + 1

    if energy_counter >= ENERGY_PLOT_EVERY:
        energy_counter = 0

        energies = compute_energies()
        kinetic_curve.plot(time, energies[0])
        potential_curve.plot(time, energies[1])
        total_curve.plot(time, energies[2])