{inputs, ...}: {
    flake.nixosModules.soundgate = {
        config,
        lib,
        pkgs,
        ...
    }: let
        inherit (lib) getExe mkEnableOption mkIf mkOption types;
        cfg = config.services.soundgate;
    in {
        imports = [
            inputs.self.nixosModules.soundgate-bluetooth
            inputs.self.nixosModules.soundgate-spotifyd
            inputs.self.nixosModules.soundgate-hass
        ];

        options.services.soundgate = {
            enable = mkEnableOption "Soundgate multi-source audio aggregator";
            package = mkOption {
                type = types.package;
                default = inputs.self.packages.${pkgs.stdenv.hostPlatform.system}.default;
            };
            httpPort = mkOption {
                type = types.port;
                default = 7676;
            };
            openFirewall = mkOption {
                type = types.bool;
                default = false;
            };
            inactivityTimeout = mkOption {
                type = types.int;
                default = 10;
                description = "Seconds before a playing source with no event is considered inactive.";
            };
            pipewireSink = mkOption {
                type = types.str;
                default = "@DEFAULT_SINK@";
            };
            controlPipewireVolume = mkOption {
                type = types.bool;
                default = true;
                description = "Whether soundgate sets PipeWire volume directly. Set to false when an external system (e.g. Home Assistant syncing to a speaker) controls the physical volume — keeps PipeWire at 100% to avoid double-attenuation.";
            };
        };

        config = mkIf cfg.enable {
            users = {
                users.soundgate = {
                    isSystemUser = true;
                    group = "soundgate";
                    extraGroups = ["audio" "pipewire"];
                };
                groups.soundgate = {};
            };
            systemd.services.soundgate = {
                description = "Soundgate audio aggregator";
                wantedBy = ["multi-user.target"];
                after = ["network.target" "pipewire.service"];
                environment = {
                    SOUNDGATE_HTTP_PORT = toString cfg.httpPort;
                    SOUNDGATE_INACTIVITY_TIMEOUT = toString cfg.inactivityTimeout;
                    SOUNDGATE_PIPEWIRE_SINK = cfg.pipewireSink;
                    SOUNDGATE_CONTROL_PIPEWIRE_VOLUME =
                        if cfg.controlPipewireVolume
                        then "1"
                        else "0";
                    SOUNDGATE_CACHE_DIR = "/var/cache/soundgate";
                    PIPEWIRE_RUNTIME_DIR = "/run/pipewire";
                };
                serviceConfig = {
                    ExecStart = getExe cfg.package;
                    User = "soundgate";
                    Group = "soundgate";
                    CacheDirectory = "soundgate";
                    CacheDirectoryMode = "0750";
                    Restart = "on-failure";
                    RestartSec = "3s";
                };
            };
            networking.firewall.allowedTCPPorts = mkIf cfg.openFirewall [cfg.httpPort];
        };
    };
}
