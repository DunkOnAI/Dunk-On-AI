"""
Error handling utilities for roster management API.

This module provides standardized error response functions that ensure
consistent error formatting across all API endpoints.
"""

from flask import jsonify


def error_response(status_code, error_code, message, details=None):
    """
    Create a standardized error response.

    Args:
        status_code (int): HTTP status code
        error_code (str): Application-specific error code
        message (str): Human-readable error message
        details (dict, optional): Additional error details

    Returns:
        tuple: Flask JSON response with status code
    """
    payload = {
        "error": {
            "code": error_code,
            "message": message
        }
    }
    if details:
        payload["error"]["details"] = details

    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(error_code, message, details=None):
    """
    Create a 400 Bad Request error response.

    Args:
        error_code (str): Application-specific error code
        message (str): Human-readable error message
        details (dict, optional): Additional error details

    Returns:
        tuple: Flask JSON response with 400 status code
    """
    return error_response(400, error_code, message, details)


def not_found(error_code, message, details=None):
    """
    Create a 404 Not Found error response.

    Args:
        error_code (str): Application-specific error code
        message (str): Human-readable error message
        details (dict, optional): Additional error details

    Returns:
        tuple: Flask JSON response with 404 status code
    """
    return error_response(404, error_code, message, details)


def conflict(error_code, message, details=None):
    """
    Create a 409 Conflict error response.

    Args:
        error_code (str): Application-specific error code
        message (str): Human-readable error message
        details (dict, optional): Additional error details

    Returns:
        tuple: Flask JSON response with 409 status code
    """
    return error_response(409, error_code, message, details)


def unprocessable_entity(error_code, message, details=None):
    """
    Create a 422 Unprocessable Entity error response.

    Args:
        error_code (str): Application-specific error code
        message (str): Human-readable error message
        details (dict, optional): Additional error details

    Returns:
        tuple: Flask JSON response with 422 status code
    """
    return error_response(422, error_code, message, details)


def internal_server_error(error_code, message, details=None):
    """
    Create a 500 Internal Server Error response.

    Args:
        error_code (str): Application-specific error code
        message (str): Human-readable error message
        details (dict, optional): Additional error details

    Returns:
        tuple: Flask JSON response with 500 status code
    """
    return error_response(500, error_code, message, details)
