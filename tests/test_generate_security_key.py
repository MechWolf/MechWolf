import re
from mechwolf import generate_security_key

def test_generate_security_key():
    assert re.match(r"\w*-\w*-\w*-\w*-\w*-\w*", generate_security_key())
