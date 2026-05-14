from soundgate.adapters.sources.bluetooth import BluetoothAdapter


def test_a2dp_uuid_present_returns_true() -> None:
    adapter = BluetoothAdapter(None)
    assert adapter._has_a2dp({"UUIDs": ["0000110a-0000-1000-8000-00805f9b34fb"]})


def test_a2dp_uuid_absent_returns_false() -> None:
    adapter = BluetoothAdapter(None)
    assert not adapter._has_a2dp({"UUIDs": ["0000111e-0000-1000-8000-00805f9b34fb"]})


def test_empty_uuids_returns_false() -> None:
    adapter = BluetoothAdapter(None)
    assert not adapter._has_a2dp({"UUIDs": []})


def test_missing_uuids_returns_false() -> None:
    adapter = BluetoothAdapter(None)
    assert not adapter._has_a2dp({})


def test_uuid_case_insensitive() -> None:
    adapter = BluetoothAdapter(None)
    assert adapter._has_a2dp({"UUIDs": ["0000110A-0000-1000-8000-00805F9B34FB"]})
