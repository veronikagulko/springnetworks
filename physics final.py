from vpython import *

#Web VPython 3.2

scene = canvas(
    title="Click to Draw Circles",
    width=800,
    height=600,
    background=color.black
)

scene.range = 5
scene.center = vec(0, 0, 0)

click_surface = box(
    pos=vec(0, 0, 0),
    size=vec(20, 20, 0.01),
    color=color.black
)

# delete light source
scene.lights = []
# custom light source
my_light = local_light(pos=vector(5, 5, 5), color=color.red)
my_light = local_light(pos=vector(5, 5, -5), color=color.cyan)

#global variables for the nodes
radius = 0.5

# button for clear screen
def clear_action(b):
    for obj in scene.objects:
        obj.visible = False
        obj.delete()
    circles.clear()
    circle_positions.clear()
        
button(bind=clear_action, text="Clear Screen")

# this stores the positions of circles previosuly made and checks if 
circle_positions = []
circles = []

def not_overlapping_nodes(new_pos):
    for old_pos in circle_positions:
        if mag(old_pos - new_pos) < radius * 2:
            return False
    return True

def draw_circle(evt):
    click_pos = evt.pos + vec(0, 0, 0.05)
    if not_overlapping_nodes(click_pos):
        new_sphere = sphere(pos=click_pos + vec(0,0, 0.05), radius = radius, color = color.white)
        circle_positions.append(click_pos)
        circles.append(new_sphere)
    else:
        print("Circle overlaps! Not drawing.")


    
scene.bind("mousedown", draw_circle)