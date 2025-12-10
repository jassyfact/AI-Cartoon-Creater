import base64
import os
import requests
import streamlit as st

# Title and description
st.set_page_config(page_title="AI Cartoon Creator", page_icon="🎨", layout="centered")
st.title("🎨 AI Cartoon Creator")
st.caption("Powered by Nano Banana API via Streamlit. Your key stays server-side.")

# API key handling: prefer Streamlit secrets, fall back to env var input when allowed.
api_key = st.secrets.get("NANOBANANA_API_KEY") or os.getenv("NANOBANANA_API_KEY")

if not api_key:
    st.info("Add `NANOBANANA_API_KEY` to Streamlit secrets or environment.")

with st.form("cartoon-form"):
    prompt = st.text_area(
        "Prompt",
        placeholder="A detective corgi in a neon-lit city, comic style",
        height=120,
    )
    col1, col2 = st.columns(2)
    with col1:
        size = st.selectbox("Size", ["1024x1024", "768x768", "512x512"], index=0)
    with col2:
        style = st.text_input("Style hint", value="cartoon")
    submitted = st.form_submit_button("Generate")

def call_nano_banana(prompt: str, size: str, style: str, key: str) -> str:
    """Returns an image URL or a data URI string.
    Endpoint is configurable via NANOBANANA_API_URL; defaults to /api/cartoon.
    """
    endpoint = os.getenv("NANOBANANA_API_URL", "https://nanobananaapi.ai/api/cartoon")

    resp = requests.post(
        endpoint,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"prompt": prompt, "size": size, "style": style},
        timeout=120,
    )
    if not resp.ok:
        raise RuntimeError(f"Upstream error {resp.status_code}: {resp.text}")
    data = resp.json()
    image = data.get("image_url") or data.get("image_base64")
    if not image:
        raise RuntimeError("No image returned from API")
    if image.startswith("http"):
        return image
    # Assume base64 payload
    return f"data:image/png;base64,{image}"

if submitted:
    if not prompt.strip():
        st.error("Please enter a prompt.")
    elif not api_key:
        st.error("Server is missing NANOBANANA_API_KEY. Add it to secrets.")
    else:
        with st.spinner("Generating cartoon..."):
            try:
                image_src = call_nano_banana(prompt.strip(), size, style.strip() or "cartoon", api_key)
                if image_src.startswith("http"):
                    st.image(image_src, caption="Generated cartoon", use_column_width=True)
                else:
                    # Convert data URI to displayable image
                    header, encoded = image_src.split(",", 1)
                    st.image(base64.b64decode(encoded), caption="Generated cartoon", use_column_width=True)
                st.success("Done!")
            except Exception as exc:
                st.error(str(exc))

st.markdown(
    """
**How to deploy on Streamlit Cloud**
- Add this repo to Streamlit Cloud.
- Set a secret `NANOBANANA_API_KEY` in the app settings.
- Requirements: `streamlit`, `requests`.
"""
)

