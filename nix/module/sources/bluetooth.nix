{
    flake.nixosModules.soundgate-bluetooth = {
        config,
        lib,
        ...
    }: let
        cfg = config.services.soundgate.sources.bluetooth;
    in {
        options.services.soundgate.sources.bluetooth = {
            enable = lib.mkEnableOption "Bluetooth source for soundgate";
        };
        config = lib.mkIf cfg.enable {
            hardware.bluetooth.enable = true;
            users.users.soundgate.extraGroups = ["bluetooth"];
        };
    };
}
