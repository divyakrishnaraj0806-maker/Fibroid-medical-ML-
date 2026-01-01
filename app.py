import streamlit as st
import numpy as np
import joblib

# ---------- load model ----------
# For now we assume you trained a model on these 11 features in this order:
# [age, heavy_bleeding_level, pain_pattern,
#  family_history, bleed_between, period_length_cat,
#  post_menopause_bleed, abdominal_swelling,
#  anemia_symptoms, urinary_frequency, constipation]

model = joblib.load("model.pkl")

st.set_page_config(page_title="Fibroid / Uterine Risk Checker", layout="wide")
st.title("🩺 Uterine Fibroid / Cancer Risk Checker")
st.markdown(
    "This tool is for **awareness only**. It cannot give a diagnosis, "
    "but helps women decide when to see a doctor earlier."
)

# ---------- sidebar inputs ----------
st.sidebar.header("Enter your details")

age = st.sidebar.slider("Age (years)", 18, 70, 35)

# 1) Heavy menstrual bleeding (3 levels)
heavy_bleeding_option = st.sidebar.selectbox(
    "Menstrual bleeding pattern",
    [
        "Normal (pads last several hours, no large clots)",
        "Moderately heavy (pads last ~2–3 hours, small clots)",
        "Very heavy (pads/cloth soaked in 1–2 hours or large clots)"
    ]
)
if heavy_bleeding_option.startswith("Normal"):
    heavy_bleeding_level = 0
elif heavy_bleeding_option.startswith("Moderately"):
    heavy_bleeding_level = 1
else:
    heavy_bleeding_level = 2

# 2) Pain pattern
pain_pattern_option = st.sidebar.selectbox(
    "Pelvic / lower abdominal pain",
    [
        "No pain",
        "Pain mainly during periods",
        "Pain most days of the month"
    ]
)
if pain_pattern_option == "No pain":
    pain_pattern = 0
elif pain_pattern_option == "Pain mainly during periods":
    pain_pattern = 1
else:
    pain_pattern = 2

# 3) Family history
family_history = 1 if st.sidebar.selectbox(
    "Family history of fibroids / uterine cancer?",
    ["No", "Yes"]
) == "Yes" else 0

# 4) Bleeding between periods
bleed_between = 1 if st.sidebar.selectbox(
    "Bleeding / spotting between periods?",
    ["No", "Yes"]
) == "Yes" else 0

# 5) Period length (days of bleeding)
period_len_option = st.sidebar.selectbox(
    "Number of days of bleeding in each period",
    ["1–3 days", "4–7 days", "More than 7 days"]
)
if period_len_option == "1–3 days":
    period_length_cat = 0
elif period_len_option == "4–7 days":
    period_length_cat = 1
else:
    period_length_cat = 2

# 6) Postmenopausal bleeding (only meaningful if age >= 45)
post_menopause_bleed = 0
if age >= 45:
    post_menopause_bleed = 1 if st.sidebar.selectbox(
        "Bleeding after periods have stopped for ≥1 year?",
        ["No", "Yes"]
    ) == "Yes" else 0

# 7) Abdominal swelling / mass
abdominal_swelling = 1 if st.sidebar.selectbox(
    "Lower belly looks bigger or feels like a lump?",
    ["No", "Yes"]
) == "Yes" else 0

# 8) Anemia symptoms
anemia_symptoms = 1 if st.sidebar.selectbox(
    "Very tired, dizzy, or breathless with light work?",
    ["No", "Yes"]
) == "Yes" else 0

# 9) Urinary frequency
urinary_frequency = 1 if st.sidebar.selectbox(
    "Need to pass urine very often (or at night)?",
    ["No", "Yes"]
) == "Yes" else 0

# 10) Constipation
constipation = 1 if st.sidebar.selectbox(
    "Frequent constipation or difficulty passing stool?",
    ["No", "Yes"]
) == "Yes" else 0

# ---------- risk computation ----------
if st.sidebar.button("Check Risk", use_container_width=True):
    # Prepare input in same order as training
    x = np.array([[
        age,
        heavy_bleeding_level,
        pain_pattern,
        family_history,
        bleed_between,
        period_length_cat,
        post_menopause_bleed,
        abdominal_swelling,
        anemia_symptoms,
        urinary_frequency,
        constipation
    ]])

    # If you trained a model:
    try:
        prob = model.predict_proba(x)[0][1] * 100
    except Exception:
        # Fallback simple rule‑based risk if model not ready
        prob = 0
        # simple scoring: you can tweak these weights
        score = 0
        score += heavy_bleeding_level * 2
        score += pain_pattern
        score += family_history * 2
        score += bleed_between * 3
        score += (period_length_cat == 2) * 3
        score += post_menopause_bleed * 5
        score += abdominal_swelling * 3
        score += anemia_symptoms * 3
        score += urinary_frequency
        score += constipation

        # map score (0–20+) to 0–100%
        prob = min(100, score * 5)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Estimated risk score", f"{prob:.0f}%")
    with col2:
        if prob >= 70:
            st.error("HIGH RISK – Please see a gynecologist as soon as possible.")
        elif prob >= 40:
            st.warning("MODERATE RISK – Book a gynecology check‑up in the next few weeks.")
        else:
            st.success("LOWER RISK – Still consider regular yearly check‑ups.")

st.markdown("---")
st.info(
    "This app is an educational decision‑support tool. It cannot replace a "
    "professional medical examination, ultrasound, or biopsy."
)
