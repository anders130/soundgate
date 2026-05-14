import pytest


class FakeWpctl:
    def __init__(self, response: str | None = None) -> None:
        self.calls: list[tuple[str, ...]] = []
        self.response = response

    async def __call__(self, *args: str) -> str | None:
        self.calls.append(args)
        return self.response


@pytest.fixture
def wpctl() -> FakeWpctl:
    return FakeWpctl()
