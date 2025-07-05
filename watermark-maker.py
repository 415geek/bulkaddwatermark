import streamlit as st
from PIL import Image
import io
import zipfile
import json
import os

SETTINGS_FILE = "settings.json"

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def load_settings(default_settings):
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            saved = json.load(f)
            default_settings.update(saved)
    return default_settings

def add_watermark_to_image(image, watermark, opacity=128, scale=0.2, position=(0, 0)):
    image = image.convert("RGBA")
    watermark = watermark.convert("RGBA")

    wm_width = int(image.width * scale)
    wm_height = int(watermark.height * (wm_width / watermark.width))
    watermark_resized = watermark.resize((wm_width, wm_height))

    alpha = watermark_resized.getchannel("A").point(lambda p: int(p * (opacity / 255)))
    watermark_resized.putalpha(alpha)

    pos = position

    watermarked = Image.new("RGBA", image.size)
    watermarked.paste(image, (0, 0))
    watermarked.paste(watermark_resized, pos, watermark_resized)

    return watermarked.convert("RGB")

def main():
    st.set_page_config(page_title="Batch Watermark Tool", page_icon="🖼️")
    st.title("🖼️ Batch Image Watermarking Tool Build by c8geek")

    uploaded_images = st.file_uploader("Upload Photos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
    watermark_file = st.file_uploader("Upload Watermark Logo", type=['png'])

    default_settings = {
        "opacity": 180,
        "scale": 0.15,
        "x_offset": 0,
        "y_offset": 0
    }
    settings = load_settings(default_settings)

    opacity = st.slider("Watermark Transparency (0-255)", 0, 255, settings["opacity"])
    scale = st.slider("Watermark Size (relative to image width)", 0.05, 0.5, settings["scale"], step=0.01)

    if uploaded_images and watermark_file:
        watermark = Image.open(watermark_file)

        st.subheader("🔍 Preview Watermark on an Image")
        selected_filename = st.selectbox("Select an image for preview", [f.name for f in uploaded_images])

        selected_file = next((f for f in uploaded_images if f.name == selected_filename), None)
        if selected_file:
            image = Image.open(selected_file)
            max_x = image.width
            max_y = image.height

            col1, col2 = st.columns([4, 1])
            with col1:
                x_offset = st.slider(f"Horizontal Offset (Max: {max_x})", 0, max_x, settings["x_offset"])
                y_offset = st.slider(f"Vertical Offset (Max: {max_y})", 0, max_y, settings["y_offset"])
            with col2:
                if st.button("Auto Center"):
                    x_offset = (max_x - int(image.width * scale)) // 2
                    y_offset = (max_y - int(image.height * scale * watermark.height / watermark.width)) // 2
                    st.experimental_rerun()

            result = add_watermark_to_image(image, watermark, opacity, scale, position=(x_offset, y_offset))
            st.image(result, caption="Preview of Watermarked Image", use_column_width=True)

            if st.button("Start Batch Watermarking"):
                output_zip = io.BytesIO()
                with zipfile.ZipFile(output_zip, "w") as zipf:
                    for uploaded_file in uploaded_images:
                        image = Image.open(uploaded_file)
                        result = add_watermark_to_image(
                            image, watermark, opacity, scale, position=(x_offset, y_offset)
                        )
                        img_bytes = io.BytesIO()
                        result.save(img_bytes, format="JPEG")
                        zipf.writestr(f"{uploaded_file.name}", img_bytes.getvalue())

                st.success("✅ Watermarking Complete!")
                st.download_button(
                    label="Download All Watermarked Images (ZIP)",
                    data=output_zip.getvalue(),
                    file_name="watermarked_images.zip",
                    mime="application/zip"
                )

            # Save settings after batch
            save_settings({
                "opacity": opacity,
                "scale": scale,
                "x_offset": x_offset,
                "y_offset": y_offset
            })

    else:
        st.info("Please upload both images and a watermark logo to continue.")

    # LinkedIn Button
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            """
            <a href="https://www.linkedin.com/in/lingyu-maxwell-lai" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="20" style="vertical-align:middle;">
                <span style="font-size: 16px;"> Connect on LinkedIn</span>
            </a>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
