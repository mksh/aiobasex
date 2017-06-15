class BaseXError(Exception):
    """A base class for various BaseX-related exceptions."""


class CannotAuthenticate(BaseException):
    """Raised, when authentication."""


class QueryError(BaseXError):
    """Raised, when invalid query identified by server."""


class CannotCreateDatabase(BaseXError):
    """Raised, when there was an error creating database."""


class CannotAddResource(BaseXError):
    """Raised, when there was an error adding resource to database."""


class CannotReplaceResource(BaseXError):
    """Raised, when there was an error replacing
        existing resource at database."""
