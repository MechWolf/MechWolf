import re
from mechwolf import generate_security_key, validate_security_key

def test_validate_security_key():
    # invalid format
    assert not validate_security_key("test")

    # not valid words
    assert not validate_security_key("a-a-a-a-a-a")

    # too many words
    assert not validate_security_key("epilogue-stilt-crux-task-corset-carton-carton")

    # valid words but wrong case
    assert not validate_security_key("EPILOGUE-STILT-CRUX-TASK-CORSET-CARTON")

    # valid key works
    assert validate_security_key("epilogue-stilt-crux-task-corset-carton")

def test_generate_security_key():
    assert validate_security_key(generate_security_key())
