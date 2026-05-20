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

def draw_circle(evt): #circle draw command
    click_pos = evt.pos
    sphere(pos=click_pos + vec(0,0, 0.05), radius = 0.5, color = color.white)
    
scene.bind("mousedown", draw_circle)

