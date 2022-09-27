from crescent.utils import any_issubclass


class A:
    ...


class B(A):
    ...


def test_any_issubclass_with_any():
    assert not any_issubclass(None, B)


def test_any_issubclass_with_cls():
    assert any_issubclass(B, A)


def test_any_issubclass_with_cls_false():
    assert not any_issubclass(A, B)
    assert not any_issubclass(object(), A)
