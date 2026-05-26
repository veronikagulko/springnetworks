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

#click_surface = box(pos=vec(0, 0, 0), size=vec(20, 20, 0.01), color=color.black)

# delete default light sources
scene.lights = []

# custom light sources
light1 = local_light(pos=vector(5, 5, 5), color=color.red)
light2 = local_light(pos=vector(5, 5, -5), color=color.cyan)

# global variables
run = True
radius = 0.5
neighbors = 2
gravity = vec(0, -3, 0)
dt = 0.01
damping = 0.995


circles = []
velocities = []
circle_positions = []


springs = []
spring_pairs = []
spring_rest_lengths = []


def clear_action(b):
    for circle in circles:
        circle.visible = False
        circle.delete()

    for spring in springs:
        spring.visible = False
        spring.delete()

    circles.clear()
    velocities.clear()
    springs.clear()
    spring_pairs.clear()
    spring_rest_lengths.clear()

button(bind=clear_action, text="Clear Screen")

def not_overlapping_nodes(new_pos):
    for circle in circles:
        if mag(circle.pos - new_pos) < radius * 2:
            return False
    return True

def draw_circle(evt):
    click_pos = evt.pos + vec(0, 0, 0.1)

    if not_overlapping_nodes(click_pos):
        new_sphere = sphere(
            pos=click_pos,
            radius=radius,
            color=color.white
        )

        circles.append(new_sphere)
        velocities.append(vec(0, 0, 0))



    else:
        print("Circle overlaps! Not drawing.")

scene.bind("mousedown", draw_circle)

while run:
    rate(60)
    if len(circles) == 0:
        continue

    acceleration = []
    for i in range(len(circles)):
        acceleration.append(gravity)

    for i in range(len(circles)):
        velocities[i] = velocities[i] + acceleration[i] * dt
        velocities[i] = velocities[i] * damping
        if circles[i].pos.y < -4:
            circles[i].pos = circles[i].pos
        else:
            circles[i].pos = circles[i].pos + velocities[i] * dt