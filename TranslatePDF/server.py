import os
import fitz  # PyMuPDF
import requests
from fpdf import FPDF
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# API-ключ и Folder ID из переменных окружения
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

app = Flask(__name__)

def extract_text_from_pdf(pdf_path):
    """Извлекает текст из PDF"""
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text

def translate_text(text, target_lang="ru"):
    """Переводит текст через Yandex Translate API"""
    url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    headers = {"Authorization": f"Api-Key {YANDEX_API_KEY}"}
    body = {
        "folder_id": FOLDER_ID,
        "texts": [text],
        "targetLanguageCode": target_lang
    }
    
    response = requests.post(url, json=body, headers=headers)
    result = response.json()
    
    if "translations" in result:
        return result["translations"][0]["text"]
    else:
        return "Ошибка перевода"

def save_text_to_pdf(text, output_pdf):
    """Сохраняет переведённый текст в PDF"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(190, 10, text)
    pdf.output(output_pdf)

@app.route("/upload", methods=["POST"])
def upload_pdf():
    """Загружает и переводит PDF"""
    if "file" not in request.files:
        return jsonify({"error": "Файл не загружен"}), 400
    
    file = request.files["file"]
    pdf_path = "uploaded.pdf"
    file.save(pdf_path)

    text = extract_text_from_pdf(pdf_path)
    translated_text = translate_text(text)
    
    output_pdf = "translated.pdf"
    save_text_to_pdf(translated_text, output_pdf)
    
    return jsonify({"message": "Перевод завершён!", "download_url": "/download"}), 200

@app.route("/download", methods=["GET"])
def download_pdf():
    """Отдаёт переведённый PDF"""
    return send_file("translated.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
