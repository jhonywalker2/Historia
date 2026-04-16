import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import anthropic
import base64
import io
import os

# Configuración de la página
st.set_page_config(
    page_title="Dibuja y Descubre",
    page_icon="🎨",
    layout="wide"
)

# Inicializar el cliente de Anthropic
@st.cache_resource
def get_anthropic_client():
    api_key = os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("⚠️ No se encontró la API key de Anthropic. Por favor configúrala en los secrets de Streamlit.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

client = get_anthropic_client()

# Título
st.title("🎨 Dibuja y Descubre el GIF Perfecto")
st.markdown("Dibuja algo en el canvas y la IA te mostrará un GIF relacionado")

# Crear dos columnas
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🖌️ Tu Canvas de Dibujo")
    
    with st.sidebar:
        st.subheader("⚙️ Configuración")
        
        # Dimensiones del canvas
        st.markdown("**Dimensiones del Tablero**")
        canvas_width = st.slider("Ancho", 300, 700, 500, 50)
        canvas_height = st.slider("Alto", 200, 600, 400, 50)
        
        # Herramienta de dibujo
        drawing_mode = st.selectbox(
            "Herramienta:",
            ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
        )
        
        # Grosor de línea
        stroke_width = st.slider("Grosor de línea:", 1, 30, 5)
        
        # Color de trazo
        stroke_color = st.color_picker("Color de trazo", "#FFFFFF")
        
        # Color de fondo
        bg_color = st.color_picker("Color de fondo", "#000000")
        
        # Botón de limpiar
        if st.button("🗑️ Limpiar Canvas", use_container_width=True):
            st.rerun()

    # Canvas de dibujo
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
    
    # Botón para analizar
    analyze_button = st.button("✨ Analizar mi Dibujo", type="primary", use_container_width=True)

with col2:
    st.subheader("🎭 Resultado")
    
    # Placeholder para el resultado
    result_placeholder = st.empty()
    
    if analyze_button and canvas_result.image_data is not None:
        with st.spinner("🤔 Analizando tu obra maestra..."):
            try:
                # Convertir la imagen del canvas a base64
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                
                # Convertir a RGB
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                
                # Guardar en bytes
                buffered = io.BytesIO()
                rgb_img.save(buffered, format="PNG")
                img_bytes = buffered.getvalue()
                img_base64 = base64.b64encode(img_bytes).decode()
                
                # Llamar a la API de Claude con visión
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": img_base64,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": """Analiza este dibujo y describe en 2-3 palabras clave en español lo que ves. 
                                    Responde SOLO con las palabras clave separadas por espacios, sin explicaciones adicionales.
                                    Ejemplos: "gato dormido", "casa árbol", "persona bailando", "corazón amor"
                                    Si el dibujo está vacío o no es claro, responde: "dibujo abstracto"
                                    """
                                }
                            ],
                        }
                    ],
                )
                
                # Obtener la descripción
                description = message.content[0].text.strip()
                
                # Buscar GIF usando la descripción
                gif_query = description.replace(" ", "+")
                
                # Mostrar resultado
                with result_placeholder.container():
                    st.success(f"🎯 Detecté: **{description}**")
                    
                    # Generar URL del GIF de Giphy
                    giphy_url = f"https://media.giphy.com/media/search?q={gif_query}"
                    
                    # Mostrar GIF usando embed de Giphy
                    st.markdown(f"""
                    <div style="width:100%;height:0;padding-bottom:75%;position:relative;">
                        <iframe src="https://giphy.com/embed/{get_giphy_id(description)}" 
                                width="100%" height="100%" 
                                style="position:absolute" 
                                frameBorder="0" 
                                class="giphy-embed" 
                                allowFullScreen>
                        </iframe>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.caption(f"GIF relacionado con: {description}")
                
            except Exception as e:
                result_placeholder.error(f"❌ Error al analizar: {str(e)}")
    
    elif not analyze_button:
        with result_placeholder.container():
            st.info("👆 Dibuja algo en el canvas y presiona 'Analizar mi Dibujo'")
            st.image("https://media.giphy.com/media/l0HlHFRbmaZtBRhXG/giphy.gif", 
                    caption="¡Esperando tu creatividad!")

# Función para obtener un GIF ID basado en la descripción
def get_giphy_id(description):
    # Mapeo simple de palabras clave a GIFs de Giphy
    giphy_map = {
        "gato": "JIX9t2j0ZTN9S",
        "perro": "hUo6A8z3u8mMU",
        "casa": "3o7TKQ8kAP0f9X5PoY",
        "árbol": "l0HlRnAWXxn0MhKLK",
        "corazón": "3o7abKhOpu0NwenH3O",
        "amor": "3o7abKhOpu0NwenH3O",
        "persona": "l0HlHFRbmaZtBRhXG",
        "bailando": "l0MYt5jPR6QX5pnqM",
        "carro": "3o7TKwmnDgQb5jemjK",
        "sol": "3o7TKP9ln2Dr6ze6f6",
        "luna": "3o7TKP9ln2Dr6ze6f6",
        "estrella": "3ohzdSOS8PDBZq3Ck8",
        "abstracto": "l0HlHFRbmaZtBRhXG",
    }
    
    # Buscar coincidencia
    for key, gif_id in giphy_map.items():
        if key in description.lower():
            return gif_id
    
    # GIF por defecto
    return "l0HlHFRbmaZtBRhXG"

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>Hecho con ❤️ usando Streamlit y Claude AI</p>
</div>
""", unsafe_allow_html=True)
