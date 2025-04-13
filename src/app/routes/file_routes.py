import json
from flask import Blueprint, request, jsonify
from app.services.file_service import handle_file_upload, handle_file_download
from app.services.metadata_service import handle_metadata_upload
from app.services.process_service import handle_process_request
from app.utils import mime_utility

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
      - name: metadata
        in: formData
        type: json
        required: true
    responses:
      201:
        description: Upload successful
      400:
        description: Missing file or provider
      500:
        description: Server error
    """
    file = request.files.get("file")
    metadata = request.form.get("metadata")

    if not file or not metadata:
        return jsonify({"error": "File and metadata are required."}), 400
    
    try:
        file_result = handle_file_upload(file)
        mime_type = mime_utility.get_mime_type(file_result["object_key"])
        metadata = json.loads(metadata)
        metadata["mime_type"] = mime_type

        record_result = handle_metadata_upload(metadata)
        result = {"file": file_result, "record": record_result}

        # Check if processing is required
        # Must indicate true and provide process_params in metadata
        if "process" in metadata and str(metadata["process"]).lower() == "true" and "process_params" in metadata and metadata["process_params"]:
            process_result = handle_process_request(record_result["id"], file_result["object_key"], file_result["bucket"], metadata)
            result["processing"] = process_result

        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@file_bp.route("/<string:object_key>", methods=["GET"])
def download_file(object_key):
    """
    Download a file from S3.
    ---
    parameters:
      - name: object_key
        in: path
        type: string
        required: true
    responses:
      200:
        description: File downloaded successfully
      404:
        description: File not found
      500:
        description: Server error
    """
    try:
        file_path = handle_file_download(object_key)
        return jsonify({"file_path": file_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
