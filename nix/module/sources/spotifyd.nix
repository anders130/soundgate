{inputs, ...}: {
    flake.nixosModules.soundgate-spotifyd = {
        config,
        lib,
        pkgs,
        ...
    }: let
        inherit (lib) mkEnableOption mkIf mkOption types;
        cfg = config.services.soundgate.sources.spotifyd;

        socketPath = "/run/soundgate/spotifyd.sock";

        onEventScript = pkgs.writeShellScript "soundgate-spotifyd-onevent" ''
            exec ${pkgs.python3}/bin/python3 - << 'PYEOF'
            import os, json, socket as sock
            env_map = {
                "event":       "PLAYER_EVENT",
                "name":        "TRACK_NAME",
                "artists":     "TRACK_ARTIST",
                "album":       "TRACK_ALBUM",
                "duration_ms": "TRACK_DURATION",
                "volume":      "VOLUME",
                "position_ms": "POSITION_MS",
                "track_id":    "TRACK_ID",
                "cover_url":   "TRACK_COVER",
            }
            d = {k: os.environ.get(v, "") for k, v in env_map.items()}
            try:
                s = sock.socket(sock.AF_UNIX, sock.SOCK_DGRAM)
                s.sendto(json.dumps(d).encode(), "${socketPath}")
            except OSError:
                pass
            PYEOF
        '';
    in {
        options.services.soundgate.sources.spotifyd = {
            enable = mkEnableOption "Spotify Connect source for soundgate via spotifyd";
            deviceName = mkOption {
                type = types.str;
                default = "Soundgate";
            };
            bitrate = mkOption {
                type = types.enum [96 160 320];
                default = 320;
            };
            deviceType = mkOption {
                type = types.str;
                default = "speaker";
            };
            zeroconfPort = mkOption {
                type = types.port;
                default = 57621;
            };
            backend = mkOption {
                type = types.str;
                default = "alsa";
                description = "spotifyd audio backend. Use 'alsa' for system services; 'pulseaudio' requires PulseAudio/PipeWire socket access.";
            };
            openFirewall = mkOption {
                type = types.bool;
                default = true;
            };
            alsaVolumeSync = mkOption {
                type = types.bool;
                default = false;
                description = ''
                    Use a patched spotifyd fork with bidirectional ALSA volume sync.
                    When enabled, soundgate writes ALSA mixer volume on every volume change
                    so spotifyd's monitor picks it up and pushes it to the Spotify session.
                '';
            };
            alsaControl = mkOption {
                type = types.str;
                default = "Master";
                description = "ALSA mixer control name (the volume knob). Run 'amixer -D <alsaDevice> scontrols' to list options.";
            };
            alsaDevice = mkOption {
                type = types.str;
                default = "default";
                description = "ALSA mixer device spotifyd opens for volume control (spotifyd 'mixer' key). Use e.g. 'hw:CARD=sndrpihifiberry'. Run 'amixer scontrols' for available devices.";
            };
            extraSettings = mkOption {
                type = types.attrs;
                default = {};
                description = ''
                    Extra settings merged into services.spotifyd.settings.global.
                    Use this for credentials, e.g. { username = "foo"; password_cmd = "cat /run/secrets/spotify-password"; }.
                '';
            };
        };

        config = mkIf cfg.enable {
            nixpkgs.overlays = lib.optionals cfg.alsaVolumeSync [
                (_: _: {
                    spotifyd = inputs.self.packages.${pkgs.stdenv.hostPlatform.system}.spotifyd-patched;
                })
            ];

            services.spotifyd = {
                enable = true;
                settings.global =
                    {
                        device_name = cfg.deviceName;
                        bitrate = cfg.bitrate;
                        device_type = cfg.deviceType;
                        zeroconf_port = cfg.zeroconfPort;
                        backend = cfg.backend;
                        onevent = onEventScript;
                        use_mpris = false;
                    }
                    // lib.optionalAttrs cfg.alsaVolumeSync {
                        volume_controller = "alsa_linear";
                        mixer = cfg.alsaDevice;
                        control = cfg.alsaControl;
                    }
                    // cfg.extraSettings;
            };

            systemd.services.soundgate = {
                after = ["spotifyd.service"];
                environment =
                    {
                        SOUNDGATE_SPOTIFYD_SOCKET = socketPath;
                    }
                    // lib.optionalAttrs cfg.alsaVolumeSync {
                        SOUNDGATE_ALSA_VOLUME_SYNC_CONTROL = cfg.alsaControl;
                        SOUNDGATE_ALSA_VOLUME_SYNC_DEVICE = cfg.alsaDevice;
                    };
                path = lib.mkIf cfg.alsaVolumeSync [pkgs.alsa-utils];
                serviceConfig.RuntimeDirectory = "soundgate";
            };

            systemd.services.spotifyd = {
                environment.PIPEWIRE_RUNTIME_DIR = "/run/pipewire";
                serviceConfig.SupplementaryGroups = lib.mkForce ["audio" "pipewire"];
            };

            networking.firewall.allowedTCPPorts = mkIf cfg.openFirewall [cfg.zeroconfPort];
            networking.firewall.allowedUDPPorts = mkIf cfg.openFirewall [cfg.zeroconfPort];
        };
    };
}
