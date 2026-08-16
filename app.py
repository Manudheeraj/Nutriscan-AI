"""
Food Calorie & Nutrition Detector - Streamlit web interface (polished)
----------------------------------------------------------------
Run with: python -m streamlit run app.py
"""

import json
import os
import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(
    page_title="NutriScan AI",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
.main-header {
    text-align: center;
    padding: 1.5rem 0 0.5rem 0;
}
.main-header h1 {
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
    background: linear-gradient(90deg, #22c55e, #16a34a);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.main-header p {
    color: #6b7280;
    font-size: 1rem;
}
.result-card-good {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-top: 1rem;
}
.result-card-bad {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-top: 1rem;
}
.food-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #15803d;
    margin-bottom: 0.1rem;
}
.food-serving {
    color: #6b7280;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}
.not-food-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #b91c1c;
    margin-bottom: 0.3rem;
}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY environment variable is not set. Set it in your terminal before running Streamlit.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-3.7-flash")

SYSTEM_PROMPT = """You are a food identification and nutrition estimation assistant.
Given input (a text description or an image), determine if it depicts or names an
actual food or drink item.

Respond with ONLY raw JSON, no markdown fences, no preamble, matching exactly this shape:

If it IS food:
{"is_food": true, "food_name": "...", "serving_size": "...", "calories": number, "protein_g": number, "carbs_g": number, "fat_g": number}

If it is NOT food (an object, animal, person, blank image, random text, etc.):
{"is_food": false, "reason": "short explanation of what it actually is"}

Use reasonable typical estimates for a standard serving. Output nothing but the JSON object.
"""


def parse_response(text: str) -> dict:
    text = text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"is_food": False, "reason": f"Could not parse model response: {text[:200]}"}


def check_text(food_name: str) -> dict:
    response = model.generate_content([SYSTEM_PROMPT, f"Input: {food_name}"])
    return parse_response(response.text)


def check_image(image: Image.Image) -> dict:
    response = model.generate_content(
        [SYSTEM_PROMPT, "Identify this image and determine if it is food.", image])
    return parse_response(response.text)


def render_result(result: dict):
    if not result.get("is_food"):
        st.markdown(
            f"""<div class="result-card-bad">
                <div class="not-food-title">⚠️ Not food detected</div>
                <div>{result.get('reason', 'Unknown')}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""<div class="result-card-good">
                <div class="food-title">{result.get('food_name')}</div>
                <div class="food-serving">Estimated for {result.get('serving_size', 'a typical serving')}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Calories", f"{result.get('calories')}", "kcal")
        col2.metric("Protein", f"{result.get('protein_g')}", "g")
        col3.metric("Carbs", f"{result.get('carbs_g')}", "g")
        col4.metric("Fat", f"{result.get('fat_g')}", "g")


st.markdown(
    """<div class="main-header">
        <h1>🍽️ NutriScan AI</h1>
        <p>AI-powered food recognition and nutrition estimation</p>
    </div>""",
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["📝 Describe a food", "📷 Photo"])
result = None

with tab1:
    st.write("")
    with st.form(key="text_form"):
        food_text = st.text_input(
            "What did you eat?",
            placeholder="e.g. grilled chicken sandwich with fries",
            label_visibility="collapsed",
        )
        text_submitted = st.form_submit_button(
            "Analyze", type="primary", use_container_width=True)

    if text_submitted:
        if not food_text.strip():
            st.warning("Enter a food name first.")
        else:
            with st.spinner("Analyzing..."):
                result = check_text(food_text)

with tab2:
    st.write("")
    input_method = st.radio("Source", [
                            "Upload a file", "Use camera"], horizontal=True, label_visibility="collapsed")

    image_source = None
    if input_method == "Upload a file":
        uploaded = st.file_uploader("Upload a photo", type=[
                                    "jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded:
            st.image(uploaded, width=280)
            image_source = uploaded
    else:
        camera_photo = st.camera_input(
            "Take a photo", label_visibility="collapsed")
        if camera_photo:
            image_source = camera_photo

    if st.button("Analyze", key="image_btn", type="primary", use_container_width=True):
        if not image_source:
            st.warning(
                "Provide an image first, either by uploading or using the camera.")
        else:
            with st.spinner("Analyzing..."):
                result = check_image(Image.open(image_source))

if result:
    render_result(result)

st.markdown(
    """<div style="text-align:center; color:#9ca3af; font-size:0.8rem; margin-top:2.5rem;">
        Nutrition values are AI-estimated, not sourced from a verified database.
    </div>""",
    unsafe_allow_html=True,
)
