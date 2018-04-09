from xkcdpass import xkcd_password as xp

def generate_security_key():
    '''Generates a human-friendly cryptographically secure security keys.

    Example:
        >>> mw.generate_security_key()
        'epilogue-stilt-crux-task-corset-carton'

    Returns:
        str: A security key consisting of six words delimited by dashes'''
    wordfile = xp.locate_wordfile()
    mywords = xp.generate_wordlist(wordfile=wordfile, min_length=4, max_length=8)
    return xp.generate_xkcdpassword(mywords, delimiter="-")
