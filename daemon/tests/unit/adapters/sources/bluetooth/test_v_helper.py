from soundgate.adapters.sources.bluetooth import _v


def test_none_returns_default() -> None:
    assert _v(None) is None


def test_none_returns_explicit_default() -> None:
    assert _v(None, 0) == 0


def test_plain_value_returned_as_is() -> None:
    assert _v(42) == 42


def test_string_returned_as_is() -> None:
    assert _v("hello") == "hello"


def test_object_with_value_attr_is_unwrapped() -> None:
    class Variant:
        def __init__(self, v):
            self.value = v

    assert _v(Variant(99)) == 99


def test_zero_not_treated_as_none() -> None:
    assert _v(0) == 0
