{
    flake.nixosModules.soundgate-hass = {
        config,
        lib,
        ...
    }: let
        inherit (lib) mkEnableOption mkIf mkOption types;
        cfg = config.services.soundgate.integrations.hass;
    in {
        options.services.soundgate.integrations.hass = {
            enable = mkEnableOption "Home Assistant custom component deployment";
            customComponentsDir = mkOption {
                type = types.path;
                default = "/var/lib/hass/custom_components";
            };
        };

        config = mkIf cfg.enable {
            systemd.services.home-assistant.preStart = lib.mkAfter ''
                mkdir -p ${cfg.customComponentsDir}
                rm -rf   ${cfg.customComponentsDir}/soundgate
                cp -r --no-preserve=mode \
                    ${../../../hass/custom_components/soundgate} \
                    ${cfg.customComponentsDir}/soundgate
            '';
        };
    };
}
