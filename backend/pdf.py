from flask import Flask, request, jsonify, send_file
from fpdf import FPDF
import tempfile

app = Flask(__name__)

class TextPDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 16)
        self.cell(0, 10, "Generated Description", ln=True, align="C")

    def add_text(self, text):
        self.set_font("Arial", '', 12)
        self.ln(10)
        self.multi_cell(0, 10, text)

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not isinstance(text, str) or not text.strip():
            return jsonify({"error": "Invalid or empty text input"}), 400

        pdf = TextPDF()
        pdf.add_page()
        pdf.add_text(text)

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp.name)

        return send_file(temp.name, as_attachment=True, download_name="generated_text.pdf")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=7000, debug=True)

