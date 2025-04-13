from flask import Blueprint, request, jsonify
from app.services.metadata_service import handle_metadata_upload, get_record_by_id

record_bp = Blueprint("record_bp", __name__)

@record_bp.route("/", methods=["POST"])
def create_record():
    """
    Create a new file record and store its metadata.
    ---
    consumes:
      - applicaiton/json
    parameters:
      - name: metadata
        in: body
        description: Metadata for the file record
        type: json
        required: true
    responses:
      201:
        description: Record created successfully
      400:
        description: Missing metadata
      500:
        description: Server error
    """
    metadata = request.get_json()

    if not metadata:
        return jsonify({"error": "metadata is required."}), 400

    try:
        result = handle_metadata_upload(metadata)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@record_bp.route("/<uuid:record_id>", methods=["GET"])
def get_record(record_id):
    """
    Get a file record by its ID.
    ---
    parameters:
      - name: record_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Record found
      404:
        description: Record not found
      500:
        description: Server error
    """
    record = get_record_by_id(record_id)
    if not record:
        return jsonify({"error": "Record not found."}), 404
    else:
        return jsonify(record), 200