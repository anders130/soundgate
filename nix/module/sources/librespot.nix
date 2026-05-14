{
    flake.nixosModules.soundgate-librespot = {
        config,
        lib,
        pkgs,
        ...
    }: let
        inherit (lib) mkEnableOption mkIf mkOption types;
        cfg = config.services.soundgate.sources.librespot;
        socketPath = "/run/soundgate/librespot.sock";

        onEventScript = pkgs.writeShellScript "soundgate-librespot-onevent" ''
            exec ${pkgs.python3}/bin/python3 - << 'PYEOF'
            import os, json, socket as sock
            env_map = {
                "event":       "PLAYER_EVENT",
                "name":        "NAME",
                "artists":     "ARTISTS",
                "album":       "ALBUM",
                "duration_ms": "DURATION_MS",
                "volume":      "VOLUME",
                "position_ms": "POSITION_MS",
                "track_id":    "TRACK_ID",
            }
            d = {k: os.environ.get(v, "") for k, v in env_map.items()}
            covers = os.environ.get("COVERS", "").split()
            d["cover_url"] = covers[0] if covers else os.environ.get("COVER_URL", "")
            try:
                s = sock.socket(sock.AF_UNIX, sock.SOCK_DGRAM)
                s.sendto(json.dumps(d).encode(), "${socketPath}")
            except OSError:
                pass
            PYEOF
        '';
    in {
        options.services.soundgate.sources.librespot = {
            enable = mkEnableOption "Spotify Connect source for soundgate";
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
            volumeCtrl = mkOption {
                type = types.enum ["cubic" "fixed" "linear" "log" "none"];
                default = "log";
            };
            initialVolume = mkOption {
                type = types.int;
                default = 100;
            };
            credentialsFile = mkOption {
                type = types.nullOr types.path;
                default = null;
            };
            openFirewall = mkOption {
                type = types.bool;
                default = true;
            };
        };

        config = mkIf cfg.enable {
            systemd.services.soundgate = {
                after = ["librespot.service"];
                environment.SOUNDGATE_LIBRESPOT_SOCKET = socketPath;
                serviceConfig.RuntimeDirectory = "soundgate";
            };

            users = {
                users.librespot = {
                    isSystemUser = true;
                    group = "librespot";
                    extraGroups = ["audio" "pipewire"];
                };
                groups.librespot = {};
            };

            systemd.services.librespot = {
                description = "Spotify Connect receiver (librespot)";
                wantedBy = ["multi-user.target"];
                wants = ["network-online.target"];
                after = ["network-online.target" "pipewire.service"];
                serviceConfig =
                    {
                        User = "librespot";
                        Group = "librespot";
                        ExecStart =
                            "${pkgs.librespot}/bin/librespot"
                            + " --name ${cfg.deviceName}"
                            + " --backend alsa"
                            + " --bitrate ${toString cfg.bitrate}"
                            + " --device-type ${cfg.deviceType}"
                            + " --zeroconf-port ${toString cfg.zeroconfPort}"
                            + " --volume-ctrl ${cfg.volumeCtrl}"
                            + " --initial-volume ${toString cfg.initialVolume}"
                            + " --cache /var/cache/librespot"
                            + " --onevent ${onEventScript}";
                        CacheDirectory = "librespot";
                        Restart = "on-failure";
                        RestartSec = "3s";
                        PIPEWIRE_RUNTIME_DIR = "/run/pipewire";
                    }
                    // lib.optionalAttrs (cfg.credentialsFile != null) {
                        EnvironmentFile = cfg.credentialsFile;
                    };
            };

            networking.firewall.allowedTCPPorts = mkIf cfg.openFirewall [cfg.zeroconfPort];
        };
    };
}
