import os
import shutil
import uuid
from flask import Flask, request, jsonify, send_file
from PyPDF2 import PdfReader, PdfWriter
from wand.image import Image as WandImage
from PIL import Image as PILImage
from werkzeug.utils import secure_filename
from flask import abort

app = Flask(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# === UTILITIES ===

@app.errorhandler(413)
def too_large(e):
    return "File is too large. Maximum allowed size is 32 MB.", 413

def extract_first_page(input_pdf_path, output_pdf_path):
    try:
        reader = PdfReader(input_pdf_path)
        if not reader.pages:
            raise ValueError("PDF has no pages.")
        writer = PdfWriter()
        writer.add_page(reader.pages[0])
        with open(output_pdf_path, "wb") as f:
            writer.write(f)
    except Exception as e:
        raise RuntimeError(f"Failed to extract first page from PDF: {str(e)}")


def pdf_to_png(pdf_path, png_path):
    try:
        with WandImage(filename=pdf_path, resolution=300) as img:
            img.compression_quality = 99
            img.format = 'png'
            img.save(filename=png_path)
    except Exception as e:
        if 'not allowed by the security policy' in str(e):
            raise RuntimeError(
                "ImageMagick security policy blocks reading PDF. "
                "You may need to edit /etc/ImageMagick*/policy.xml to allow PDF."
            )
        raise RuntimeError(f"Failed to convert PDF to PNG: {str(e)}")


def scale_image(input_path, output_path, scale_factor):
    try:
        with PILImage.open(input_path) as img:
            img = img.convert("RGBA")
            new_width = max(1, int(img.width * scale_factor))
            new_height = max(1, int(img.height * scale_factor))
            img = img.resize((new_width, new_height), PILImage.LANCZOS)
            img.save(output_path)
    except Exception as e:
        raise RuntimeError(f"Failed to scale image: {str(e)}")


# === ROUTE ===

@app.route('/thumbnail', methods=['POST'])
def thumbnail():
    request_id = str(uuid.uuid4())
    work_dir = os.path.join(UPLOAD_DIR, request_id)
    os.makedirs(work_dir, exist_ok=True)

    try:
        # 1️⃣ Validate and save uploaded PDF
        if 'file' not in request.files or request.files['file'].filename.strip() == '':
            return jsonify({"error": "Missing PDF file. Provide 'file' in form-data."}), 400

        uploaded_file = request.files['file']
        original_filename = secure_filename(uploaded_file.filename)
        if not original_filename.lower().endswith('.pdf'):
            return jsonify({"error": "Uploaded file must have .pdf extension."}), 400

        input_pdf_path = os.path.join(work_dir, "input.pdf")
        uploaded_file.save(input_pdf_path)

        if os.path.getsize(input_pdf_path) == 0:
            return jsonify({"error": "Uploaded PDF file is empty."}), 400

        # 2️⃣ Validate scale
        if 'scale' not in request.form:
            return jsonify({"error": "Missing 'scale' parameter in form-data."}), 400

        scale_raw = request.form['scale'].strip()
        try:
            scale = float(scale_raw)
        except ValueError:
            return jsonify({"error": "Scale must be a decimal number."}), 400

        if scale <= 0 or scale > 10:
            return jsonify({"error": "Scale must be >0 and <=10."}), 400

        # 3️⃣ Define default output filename
        base_name, _ = os.path.splitext(original_filename)
        output_filename = f"{base_name}_scale-{scale}.png"

        # 4️⃣ Process PDF
        first_page_pdf_path = os.path.join(work_dir, "first_page.pdf")
        extract_first_page(input_pdf_path, first_page_pdf_path)

        original_png_path = os.path.join(work_dir, "original.png")
        pdf_to_png(first_page_pdf_path, original_png_path)

        scaled_png_path = os.path.join(work_dir, output_filename)
        scale_image(original_png_path, scaled_png_path, scale)

        # 5️⃣ Serve the file
        return send_file(
            scaled_png_path,
            mimetype='image/png',
            as_attachment=True,
            download_name=output_filename
        )

    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {str(e)}"}), 500
    finally:
        try:
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir)
        except Exception as cleanup_error:
            app.logger.error(f"Failed to cleanup work dir {work_dir}: {str(cleanup_error)}")


# === ENTRY POINT ===

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
