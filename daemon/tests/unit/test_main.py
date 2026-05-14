import inspect

from soundgate.main import main, run


def test_run_is_callable():
    assert callable(run)


def test_main_is_coroutine_function():
    assert inspect.iscoroutinefunction(main)
