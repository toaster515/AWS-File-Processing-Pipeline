import mimetypes

def get_mime_type(file_path):
    """
    Get the MIME type of a file.
    
    Args:
        file_path (str): Path to the file.

    Returns:
        str: The MIME type of the file.
    """
    mime = mimetypes.guess_type(file_path)[0]
    if mime is None:
        mime = 'application/octet-stream'
    return mime