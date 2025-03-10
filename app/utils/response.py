from flask import jsonify


def create_response(data=None, message="Success", status_code=200, status=True, pagination=None):
    response = {
        "status": status,
        "status_code": status_code,
        "message": message
    }

    # Always include data field in the response
    if data is not None or status:
        response["data"] = data if data is not None else []

    # Add pagination metadata if provided
    if pagination:
        response["pagination"] = pagination

    return jsonify(response), status_code
