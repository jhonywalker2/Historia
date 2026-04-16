import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
from PIL import Image, ImageDraw
import time

st.title("Scribble Animado ✏️")

# Sidebar
with st.sidebar:
    canvas_width = st.slider("Ancho", 300, 700, 500, 50)
    canvas_height = st.slider("Alto", 200, 600, 300, 50)
    stroke_width = st.slider("Grosor", 1, 20, 5)
    jitter = st.slider("Movimiento (intensidad)", 1, 10, 3)
    speed = st.slider("Velocidad", 0.01, 0.2, 0.05)

# Canvas
canvas_result = st_canvas(
    stroke_width=stroke_width,
    stroke_color="#FFFFFF",
    background_color="#000000",
    height=canvas_height,
    width=canvas_width,
    drawing_mode="freedraw",
    key="canvas",
)

# Función scribble animada
def scribble_line(points, jitter):
    return [
        (
            x + np.random.uniform(-jitter, jitter),
            y + np.random.uniform(-jitter, jitter),
        )
        for x, y in points
    ]

# Placeholder para animación
frame = st.empty()

if canvas_result.json_data is not None:

    paths = []

    # Guardar paths originales
    for obj in canvas_result.json_data["objects"]:
        if obj["type"] == "path":
            pts = []
            for p in obj["path"]:
                if p[0] in ["M", "L"]:
                    pts.append((p[1], p[2]))
            if len(pts) > 1:
                paths.append(pts)

    # Loop de animación
    while True:
        img = Image.new("RGB", (canvas_width, canvas_height), "#000000")
        draw = ImageDraw.Draw(img)

        for pts in paths:
            for _ in range(2):  # multiplica líneas para efecto sketch
                scribbled = scribble_line(pts, jitter)
                draw.line(scribbled, fill="white", width=stroke_width)

        frame.image(img)

        time.sleep(speed)
