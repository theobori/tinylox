{
  lib,
  buildPythonPackage,
  setuptools,
}:
buildPythonPackage {
  pname = "tinylox";
  version = "0.1.0";
  pyproject = true;

  src = ./.;

  nativeBuildInputs = [ setuptools ];

  pythonImportsCheck = [ "tinylox" ];

  meta = {
    description = "Tiny Lox Tree-Walk interpreter";
    homepage = "https://github.com/theobori/tinylox";
    license = lib.licenses.mit;
    mainProgram = "tinylox";
  };
}
