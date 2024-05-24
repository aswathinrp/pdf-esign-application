import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import io
import tempfile

def sign_pdf(pdf_file, signature_file):
    try:
        # Load PDF and Signature files
        pdf_reader = PdfReader(pdf_file)
        pdf_writer = PdfWriter()

        # Read signature image
        signature_image = Image.open(signature_file)

        # Create a temporary canvas to hold the signature
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # Convert signature image to bytes
        temp_signature = io.BytesIO()
        signature_image.save(temp_signature, format='PNG')
        temp_signature.seek(0)

        # Create a temporary file for the signature image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(temp_signature.read())
            temp_file.seek(0)

            # Get dimensions of the PDF page
            page_width, page_height = letter

            # Set the position for the signature on the right side
            signature_width = 80
            signature_height = 40
            x_position = page_width - signature_width - 50  # 50 units margin from the right edge
            y_position = 50  # 50 units from the bottom

            # Draw the signature on the canvas
            can.drawImage(temp_file.name, x_position, y_position, width=signature_width, height=signature_height)  # Adjust position and size
            can.save()

        # Move to the beginning of the StringIO buffer
        packet.seek(0)
        new_pdf = PdfReader(packet)

        # Add the "watermark" (which is the signature) on the existing page
        for i in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[i]
            page.merge_page(new_pdf.pages[0])
            pdf_writer.add_page(page)

        # Save the new PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as output_temp_file:
            pdf_writer.write(output_temp_file)
            output_temp_file_path = output_temp_file.name

        return output_temp_file_path

    except Exception as e:
        raise e

def main():
    st.title("PDF eSign Tool")
    st.write("Upload a PDF file and a signature image to eSign the document.")

    uploaded_pdf = st.file_uploader("Upload PDF File", type=['pdf'])
    uploaded_signature = st.file_uploader("Upload Signature Image", type=['png', 'jpg', 'jpeg'])

    if st.button("Sign PDF") and uploaded_pdf and uploaded_signature:
        try:
            signed_pdf_path = sign_pdf(uploaded_pdf, uploaded_signature)
            st.success("PDF signed successfully!")
            st.write("Download your signed PDF:")
            with open(signed_pdf_path, "rb") as f:
                bytes = f.read()
            st.download_button(label="Download", data=bytes, file_name="signed_document.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
