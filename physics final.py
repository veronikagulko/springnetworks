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


# button for clear screen
def clear_action(b):
    for obj in scene.objects:
        obj.visible = False
        obj.delete()
        
button(bind=clear_action, text="Clear Screen")



circle_positions = []

def draw_circle(evt):
    click_pos = evt.pos
    sphere(pos=click_pos + vec(0,0, 0.05), radius = 0.5, color = color.white)
    circle_positions.append(click_pos)


    
scene.bind("mousedown", draw_circle)

