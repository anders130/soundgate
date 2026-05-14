{
    perSystem = {
        pkgs,
        self',
        ...
    }: let
        pythonPkgs = pkgs.python313Packages;
        devDeps = with pythonPkgs; [
            pytest
            pytest-asyncio
            black
            isort
            httpx
            dbus-fast
            aioresponses
        ];
        src = ../daemon;
        package = self'.packages.default;
        pyproject = {
            build-system = {
                requires = ["hatchling"];
                build-backend = "hatchling.build";
            };
            project = {
                name = "soundgate";
                version = "0.1.0";
                dependencies = ["aiohttp"];
                requires-python = ">=3.13";
                scripts.soundgate = "soundgate.main:run";
            };
            tool.hatch.build.targets.wheel.packages = ["src/soundgate"];
            tool.pytest.ini_options = {
                asyncio_mode = "auto";
                testpaths = ["tests"];
                pythonpath = ["src"];
            };
            tool.isort.profile = "black";
        };
    in {
        packages.default = pythonPkgs.buildPythonPackage {
            inherit src;
            pname = "soundgate";
            version = "0.1.0";
            format = "pyproject";
            build-system = [pythonPkgs.hatchling];
            dependencies = with pythonPkgs; [
                fastapi
                uvicorn
                dbus-fast
                aiohttp
            ];
            prePatch = ''
                cat ${pkgs.writers.writeTOML "pyproject.toml" pyproject} > pyproject.toml
            '';
        };

        devShells.default = pkgs.mkShell {
            inputsFrom = [package];
            buildInputs = devDeps;
            shellHook = ''
                cat ${pkgs.writers.writeTOML "pyproject.toml" pyproject} > daemon/pyproject.toml
                echo "__version__ = \"${package.version}\"" > daemon/src/soundgate/__init__.py
            '';
        };

        formatter = pkgs.writeShellApplication {
            name = "format";
            runtimeInputs = devDeps;
            text = ''
                black daemon/
                isort daemon/ --profile black
            '';
        };

        checks = let
            checkDeps = {
                inherit src;
                buildInputs = [package] ++ devDeps;
            };
        in {
            tests = pkgs.runCommand "soundgate-tests" checkDeps ''
                cp -r $src test-src
                chmod -R u+w test-src
                cd test-src
                pytest -p no:cacheprovider
                touch $out
            '';
            format = pkgs.runCommand "soundgate-format" checkDeps ''
                black --check $src
                isort $src --check --diff --known-local-folder soundgate --profile black
                touch $out
            '';
        };
    };
}
