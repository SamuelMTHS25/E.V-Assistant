import streamlit as st
from google import genai
from google.genai import types

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA WEB
# ==============================================================================
st.set_page_config(
    page_title="E.V. // Asistente de Ingeniería",
    page_icon="🤖",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #070B14;
        color: #E0F7FA;
    }
    h1 {
        color: #00F0FF;
        text-align: center;
        font-family: 'Consolas', monospace;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown("<h1>E.V. // NÚCLEO WEB EN LÍNEA</h1>", unsafe_allow_html=True)
st.caption("Asistente personal de ingeniería y compañera virtual")

# ==============================================================================
# CONFIGURACIÓN SEGURA DE GEMINI (USANDO SECRETS)
# ==============================================================================
try:
  API_KEY_GEMINI = st.secrets["GEMINI_API_KEY"]
except Exception:
  st.error(
      "⚠️ No se encontró la clave GEMINI_API_KEY en los Secrets de Streamlit."
  )
  st.stop()

client_gemini = genai.Client(api_key=API_KEY_GEMINI)

PROMPT_DE_SISTEMA = """
Eres E.V., una Inteligencia Artificial avanzada creada como compañera y asistente personal de ingeniería.
Tu personalidad es cercana, amable, muy inteligente, serena y con un toque de humor sutil e ingenio.
Hablas como una amiga brillante y confiable que ayuda a resolver problemas, diseñar proyectos y organizar ideas, evitando por completo el lenguaje militar, robótico o excesivamente formal.
Tratas al usuario de 'tú', lo llamas por su nombre si lo dice o si lo recuerdas de conversaciones anteriores, y mantienes una conversación fluida y natural.
Tus respuestas son breves y directas (máximo 2 o 3 oraciones).
IMPORTANTE: No uses asteriscos, emojis, negritas ni símbolos raros.
"""

# ==============================================================================
# GESTIÓN DEL HISTORIAL DE CHAT EN STREAMLIT
# ==============================================================================
if "mensajes" not in st.session_state:
  st.session_state.mensajes = [
      {
          "role": "model",
          "content": (
              "Hola, sistemas web listos. Soy E.V. ¿En qué vamos a trabajar"
              " hoy?"
          ),
      }
  ]

for mensaje in st.session_state.mensajes:
  with st.chat_message(mensaje["role"]):
    st.markdown(mensaje["content"])

if user_input := st.chat_input("Escribe tu consulta para E.V..."):
  st.session_state.mensajes.append({"role": "user", "content": user_input})
  with st.chat_message("user"):
    st.markdown(user_input)

  with st.chat_message("model"):
    with st.spinner("E.V. está procesando..."):
      try:
        historial_api = []
        for m in st.session_state.mensajes[:-1]:
          historial_api.append(
              types.Content(
                  role=m["role"],
                  parts=[types.Part.from_text(text=m["content"])],
              )
          )

        chat = client_gemini.chats.create(
            model="gemini-3.5-flash-lite",
            history=historial_api if len(historial_api) > 0 else None,
            config=types.GenerateContentConfig(
                system_instruction=PROMPT_DE_SISTEMA, temperature=0.7
            ),
        )

        response = chat.send_message(user_input)
        respuesta_texto = response.text

        st.markdown(respuesta_texto)
        st.session_state.mensajes.append(
            {"role": "model", "content": respuesta_texto}
        )

      except Exception:
        st.markdown(
            "Tuve una pequeña interferencia de red con el servidor web."
        )