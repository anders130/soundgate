{
    perSystem = {pkgs, ...}: {
        packages.spotifyd-patched = pkgs.spotifyd.overrideAttrs (old: {
            patches = (old.patches or []) ++ [./patches/spotifyd-alsa-volume-sync.patch];
        });
    };
}
