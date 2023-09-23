import re
import base64

def rfc_1123_str(s: str):
    '''
    Transforms a string into an RFC 1123 Compliant string.
    '''
    return re.sub("[^0-9a-zA-Z]", "-", s).lower()

def valid_display_string(s: str):
    '''
    Returns True on valid match, false on invalid match.
    The string can:
      - start / end with alphanumeric character
      - contain one [" ", "-", "_"] between alphanumeric characters
    '''
    pattern = re.compile("^[a-zA-Z0-9]+([-_  ][a-zA-Z0-9]+)*$")
    return pattern.match(s)

def valid_url(s: str):
    '''
    Returns True on valid url match, false on invalid url match.
    - Hostames with ports are allowed
    - paths are allowed
    - must be http or https protocol
    '''
    pattern = re.compile("^(https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z0-9]{2,}(\.[a-zA-Z0-9]{2,})(\.[a-zA-Z0-9]{2,})?([:][0-9]{1,5})?[\/]?([a-zA-Z0-9]{1,})?$")
    return pattern.match(s)

def valid_docker_image(s: str):
    '''
    Returns True on valid docker image match, false on invalid docker image match
    '''
    pattern = re.compile("^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])([\/][a-z0-9]{1,})*([:][a-z0-9-]{1,})?$")
    return pattern.match(s)

def base64_encode(s: str):
    '''
    Returns Base64 encoded String
    '''
    encoded_bytes = base64.b64encode(s.encode("utf-8"))
    encoded_str = str(encoded_bytes, "utf-8")
    return encoded_str