# soundgate

NixOS daemon that aggregates Bluetooth and Spotify Connect into a single volume and playback state, with a REST API for Home Assistant.

## Sources

- **Bluetooth** - A2DP audio + AVRCP volume sync (BlueZ D-Bus)
- **Spotify Connect** - via spotifyd, with optional bidirectional ALSA volume sync

## NixOS setup

```nix
# flake.nix
inputs.soundgate.url = "github:anders130/soundgate";
```

```nix
# configuration.nix
imports = [inputs.soundgate.nixosModules.soundgate];

services.soundgate = {
    enable = true;
    sources = {
        bluetooth.enable = true;
        spotifyd = {
            enable = true;
            deviceName = "Soundgate";
            # optional: bidirectional ALSA volume sync
            # requires running: amixer -D <alsaDevice> scontrols
            alsaVolumeSync = true;
            alsaDevice = "hw:CARD=sndrpihifiberry";
            alsaControl = "Digital";
        };
    };
};
```

## Home Assistant

Add the custom component to your HA NixOS config:

```nix
services.home-assistant.customComponents = [
    inputs.soundgate.packages.${pkgs.stdenv.hostPlatform.system}.hass-component
];
```

Point it at `http://<soundgate-host>:7676`.

## REST API

| Method | Path                 | Description                     |
| ------ | -------------------- | ------------------------------- |
| `GET`  | `/state`             | Aggregated playback state       |
| `POST` | `/volume`            | Set volume `{"level": 0.0-1.0}` |
| `POST` | `/bluetooth/connect` | Reconnect Bluetooth             |

## Development

```sh
cd daemon
pip install -e ".[dev]"
pytest
```
