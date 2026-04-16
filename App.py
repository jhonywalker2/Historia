import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
from PIL import Image, ImageDraw

st.title("Tablero estilo Scribble")

with st.sidebar:
    st.subheader("Propiedades del Tablero")

    canvas_width = st.slider("Ancho del tablero", 300, 700, 500, 50)
    canvas_height = st.slider("Alto del tablero", 200, 600, 300, 50)

    drawing_mode = st.selectbox(
        "Herramienta de Dibujo:",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
    )

    stroke_width = st.slider("Selecciona el ancho de línea:", 1, 30, 15)
    stroke_color = st.color_picker("Color de trazo", "#FFFFFF")
    bg_color = st.color_picker("Color de fondo", "#000000")

# Canvas original
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=canvas_height,
    width=canvas_width,
    drawing_mode=drawing_mode,
    key=f"canvas_{canvas_width}_{canvas_height}",
)

# Función para efecto scribble
def scribble_line(points, jitter=2):
    new_points = []
    for x, y in points:
        new_x = x + np.random.uniform(-jitter, jitter)
        new_y = y + np.random.uniform(-jitter, jitter)
        new_points.append((new_x, new_y))
    return new_points

# Procesar dibujo
if canvas_result.json_data is not None:
    img = Image.new("RGB", (canvas_width, canvas_height), bg_color)
    draw = ImageDraw.Draw(img)

    for obj in canvas_result.json_data["objects"]:
        if obj["type"] == "path":
            path = obj["path"]

            # extraer puntos
            points = []
            for p in path:
                if p[0] in ["L", "M"]:
                    points.append((p[1], p[2]))

            # aplicar efecto scribble
            scribbled = scribble_line(points, jitter=3)

            # dibujar línea deformada
            if len(scribbled) > 1:
                draw.line(scribbled, fill=stroke_color, width=stroke_width)

    st.subheader("Resultado Scribble")
    st.image(img)
