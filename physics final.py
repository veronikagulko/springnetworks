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
radius = 0.5
neighbors = 2

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

def spring_generator():
    # exit function if there are less than 2 circles on the screen
    if len(circles) < 2:
        return

    # clear old springs
    for spring in springs:
        spring.visible = False
        spring.delete()
    springs.clear()
    spring_pairs.clear()
    spring_rest_lengths.clear()
    
    # use set so we do not duplicate springs
    springs_pairs = set()
    
    for i in range(len(circles)):
        distances_btwn_circles = []

        for j in range(len(circles)):
            if i != j:
                distance = mag(circles[i].pos - circles[j].pos)
                distances_btwn_circles.append((distance, j))

        distances_btwn_circles.sort()

        for distance, j in distances_btwn_circles[:neighbors]:
            spring_pairs.append(tuple(sorted((i, j))))

    for i, j in spring_pairs:
        new_spring = helix(
            pos=circles[i].pos,
            axis=circles[j].pos - circles[i].pos,
            radius=0.08,
            thickness=0.03,
            color=color.yellow
        )

        springs.append(new_spring)

def draw_circle(evt):
    click_pos = evt.pos + vec(0, 0, 0.1)

    if not_overlapping_nodes(click_pos):
        new_sphere = sphere(
            pos=click_pos,
            radius=radius,
            color=color.white
        )

        circles.append(new_sphere)

        spring_generator()

    else:
        print("Circle overlaps! Not drawing.")

scene.bind("mousedown", draw_circle)

velocity = vec(0,0,0)
acceleration = -9.8
position = (1/2)* acceleration * (clock())**2

for circle in circles:
    while circle.pos > 0:
        rate(30)
        circle.pos = circle.pos + vec(0.5, 0.5, 0) * 0.1
