"""
Constants for roster management API endpoints.

This module defines roster constraints, valid values, and error codes
used throughout the roster management system.
"""

# Roster constraints
MAX_ROSTER_SIZE = 15
MAX_STARTERS = 5
MIN_ROSTER_SIZE = 0

# Valid role values
VALID_ROLES = ['starter', 'bench']
DEFAULT_ROLE = 'bench'


# Error codes for standardized error responses
class ErrorCodes:
    """Standard error codes for API responses."""

    # User errors
    USER_NOT_FOUND = 'USER_NOT_FOUND'

    # Player errors
    PLAYER_NOT_FOUND = 'PLAYER_NOT_FOUND'
    PLAYER_NOT_ON_ROSTER = 'PLAYER_NOT_ON_ROSTER'
    PLAYER_ALREADY_ON_ROSTER = 'PLAYER_ALREADY_ON_ROSTER'

    # Roster constraint errors
    ROSTER_FULL = 'ROSTER_FULL'
    STARTERS_FULL = 'STARTERS_FULL'

    # Request validation errors
    INVALID_ROLE = 'INVALID_ROLE'
    INVALID_REQUEST = 'INVALID_REQUEST'
    MISSING_REQUIRED_FIELD = 'MISSING_REQUIRED_FIELD'
    CONFIRMATION_REQUIRED = 'CONFIRMATION_REQUIRED'

    # Database errors
    DATABASE_ERROR = 'DATABASE_ERROR'
