import streamlit as st
from PIL import Image
import os
import io
import zipfile

def add_watermark_to_image(image, watermark, opacity=128, scale=0.2, position="bottom-right"):
    image = image.convert("RGBA")
    watermark = watermark.convert("RGBA")

    # Resize watermark relative to image
    wm_width = int(image.width * scale)
    wm_height = int(watermark.height * (wm_width / watermark.width))
    watermark_resized = watermark.resize((wm_width, wm_height))

    # Apply transparency
    alpha = watermark_resized.getchannel("A").point(lambda p: int(p * (opacity / 255)))
    watermark_resized.putalpha(alpha)

    # Positioning
    if position == "bottom-right":
        pos = (image.width - wm_width - 20, image.height - wm_height - 20)
    elif position == "center":
        pos = ((image.width - wm_width) // 2, (image.height - wm_height) // 2)
    elif position == "top-left":
        pos = (20, 20)
    else:
        pos = (20, 20)

    # Paste watermark
    watermarked = Image.new("RGBA", image.size)
    watermarked.paste(image, (0, 0))
    watermarked.paste(watermark_resized, pos, watermark_resized)

    return watermarked.convert("RGB")

def main():
    st.set_page_config(page_title="Batch Watermark Tool", page_icon="🖼️")
    st.title("🖼️ Batch Image Watermarking Tool ")

    uploaded_images = st.file_uploader("Upload Photos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
    watermark_file = st.file_uploader("Upload Watermark Logo", type=['png'])

    opacity = st.slider("Watermark Transparency (0-255)", 0, 255, 180)
    scale = st.slider("Watermark Size (relative to image width)", 0.05, 0.5, 0.15, step=0.01)
    position = st.selectbox("Watermark Position", ["bottom-right", "center", "top-left"])

    if uploaded_images and watermark_file:
        watermark = Image.open(watermark_file)

        st.subheader("🔍 Preview Watermark on an Image")
        selected_filename = st.selectbox("Select an image for preview", [f.name for f in uploaded_images])

        selected_file = next((f for f in uploaded_images if f.name == selected_filename), None)
        if selected_file:
            image = Image.open(selected_file)
            result = add_watermark_to_image(image, watermark, opacity, scale, position)
            st.image(result, caption="Preview of Watermarked Image", use_column_width=True)

        st.markdown("---")

        if st.button("Start Batch Watermarking"):
            output_zip = io.BytesIO()
            with zipfile.ZipFile(output_zip, "w") as zipf:
                for uploaded_file in uploaded_images:
                    image = Image.open(uploaded_file)
                    result = add_watermark_to_image(image, watermark, opacity, scale, position)

                    # Save in-memory
                    img_bytes = io.BytesIO()
                    result.save(img_bytes, format="JPEG")
                    zipf.writestr(f"watermarked_{uploaded_file.name}", img_bytes.getvalue())

            st.success("✅ Watermarking Complete!")
            st.download_button(
                label="Download All Watermarked Images (ZIP)",
                data=output_zip.getvalue(),
                file_name="watermarked_images.zip",
                mime="application/zip"
            )
    else:
        st.info("Please upload both images and a watermark logo to continue.")

    # LinkedIn Button in Sidebar
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
