from flask import jsonify


def success_response(data=None, message=None, status_code=200):
    """
    Standard success response format
    """
    response = {
        'success': True
    }

    if message:
        response['message'] = message

    if data is not None:
        response['data'] = data

    return jsonify(response), status_code


def error_response(message, status_code=400, errors=None):
    """
    Standard error response format
    """
    response = {
        'success': False,
        'error': message
    }

    if errors:
        response['errors'] = errors

    return jsonify(response), status_code


def paginated_response(items, page, per_page, total, schema=None):
    """
    Standard paginated response format
    """
    if schema:
        items_data = schema.dump(items, many=True)
    else:
        items_data = items

    return jsonify({
        'success': True,
        'data': items_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }), 200
