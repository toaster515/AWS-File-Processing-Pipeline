from flask import Blueprint, request, jsonify
from app.services.file_service import handle_file_upload

file_bp = Blueprint("file_bp", __name__)

@file_bp.route("/", methods=["POST"])
def upload_file():
    """
    Upload a file and store its metadata.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
      - name: provider
        in: formData
        type: string
        required: true
        enum: ['S3', 'AZURE']
    responses:
      201:
        description: Upload successful
      400:
        description: Missing file or provider
      500:
        description: Server error
    """
    file = request.files.get("file")
    provider = request.form.get("provider")

    if not file or not provider:
        return jsonify({"error": "File and provider are required."}), 400

    try:
        result = handle_file_upload(file, provider)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
