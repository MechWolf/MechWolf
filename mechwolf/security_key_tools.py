from xkcdpass import xkcd_password as xp
import re

def generate_security_key():
    '''Generates a human-friendly cryptographically secure security keys.

    Returns:
        str: A security key consisting of six words delimited by dashes

    Example:
        >>> mw.generate_security_key()
        'epilogue-stilt-crux-task-corset-carton'
    '''
    wordfile = xp.locate_wordfile()
    word_list = xp.generate_wordlist(wordfile=wordfile, min_length=4, max_length=8)
    return xp.generate_xkcdpassword(word_list, delimiter="-")

def validate_security_key(security_key):
    '''Checks that a MechWolf security key is valid.

    Args:
        security_key (str): The security key to validate.

    Returns:
        bool: Whether the security key is valid.

    Example:
        >>> mw.validate_security_key('epilogue-stilt-crux-task-corset-carton')
        True
        >>> mw.validate_security_key("not-A-valid-k3y")
        False
    '''
    # check the format
    if not re.match(r"\w*-\w*-\w*-\w*-\w*-\w*", security_key):
        return False

    wordfile = xp.locate_wordfile()
    word_list = set(xp.generate_wordlist(wordfile=wordfile, min_length=4, max_length=8))

    # check that the words in the security key are valid
    for word in security_key.split("-"):
        if word not in word_list:
            return False

    # check number of words
    if len(security_key.split("-")) != 6:
        return False

    return True
