{
    perSystem = {pkgs, ...}: {
        packages.hass-component = pkgs.python3Packages.buildPythonPackage {
            pname = "soundgate-hass-component";
            version = "0.1.0";
            src = ../hass;
            format = "other";
            installPhase = ''
                mkdir -p $out/${pkgs.python3.sitePackages}/custom_components
                cp -r custom_components/soundgate $out/${pkgs.python3.sitePackages}/custom_components/
            '';
            passthru = {
                isHomeAssistantComponent = true;
                domain = "soundgate";
            };
        };
    };
}
