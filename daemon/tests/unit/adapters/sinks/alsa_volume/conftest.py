import pytest


class FakeAmixer:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, int]] = []

    async def __call__(self, device: str, control: str, percent: int) -> None:
        self.calls.append((device, control, percent))


@pytest.fixture
def amixer() -> FakeAmixer:
    return FakeAmixer()
