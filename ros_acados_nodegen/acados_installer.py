import argparse
import os
import sys
import subprocess
from pathlib import Path

ACADOS_REPO = "https://github.com/acados/acados.git"

def run(cmd, cwd=None, check=True):
    print(f"==> {cmd}")
    subprocess.run(cmd, cwd=cwd, check=check, shell=isinstance(cmd, str))

def check_cmd(name):
    return subprocess.call(["which", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def write_exports(acados_dir: Path, rc_file: Path):
    lines = [
        "",
        "# --- acados environment variables (added by ros_acados_nodegen) ---",
        f'export ACADOS_SOURCE_DIR="{acados_dir}"',
        'export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$ACADOS_SOURCE_DIR/lib"',
    ]
    with rc_file.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Appended ACADOS env to {rc_file}. Source it or open a new shell.")
    
def check_exports(rc_file: Path):
    return rc_file.exists() and any("ACADOS_SOURCE_DIR" in line for line in rc_file.read_text().splitlines())

def install_acados(prefix: Path, with_openmp: bool, with_osqp: bool, 
                   with_qpoases: bool, export_env: bool):
    # Basic checks
    for dep in ["git", "cmake", "make"]:
        if not check_cmd(dep):
            print(f"ERROR: '{dep}' not found. Please install it first.", file=sys.stderr)
            sys.exit(1)

    # --- Load acados modules ---
    acados_dir = prefix
    build_dir = acados_dir / "build"
    acados_dir.parent.mkdir(parents=True, exist_ok=True)
    if not acados_dir.exists():
        print(f"Cloning acados into {acados_dir} ...")
        run(["git", "clone", ACADOS_REPO, str(acados_dir)])
        run(["git", "submodule", "update", "--init", "--recursive"], cwd=acados_dir)
    else:
        print(f"acados directory already exists: {acados_dir}")

    # --- Build acados ---
    build_dir.mkdir(parents=True, exist_ok=True)
    cmake_flags = [
        f"-DACADOS_WITH_OPENMP={'ON' if with_openmp else 'OFF'}",
        f"-DACADOS_WITH_OSQP={'ON' if with_osqp else 'OFF'}",
        f"-DACADOS_WITH_QPOASES={'ON' if with_qpoases else 'OFF'}",
        f"-DACADOS_PYTHON='ON'",
    ]
    jobs = os.cpu_count() or 2
    if not build_dir.exists():
        print("Configuring with CMake ...")
        run(["cmake", "..", *cmake_flags], cwd=build_dir)
        print(f"Building and installing acados (-j{jobs}) ...")
        run(["make", f"-j{jobs}"], cwd=build_dir)
        run(["make", "install"], cwd=build_dir)

    # --- Install acados template in pip ---
    python = Path(sys.executable)
    pip = str(python.parent / "pip")
    print("Installing Python interface (acados_template) ...")
    template_dir = acados_dir / "interfaces" / "acados_template"
    run([pip, "install", "."], cwd=template_dir)

    # --- Update shell rc file ---
    shell = (os.environ.get("SHELL") or "")
    rc = Path.home() / (".bashrc" if "bash" in shell else ".zshrc" if "zsh" in shell else ".bashrc")
    if export_env and not check_exports(rc):
        write_exports(acados_dir, rc)

    print("acados installation finished.")
    print(f"ACADOS_SOURCE_DIR={acados_dir}")

def main():
    p = argparse.ArgumentParser(description="Install acados (clone, build, install) without shell script.")
    p.add_argument("--prefix", type=Path, default=Path.home() / "acados", help="Install directory (default: ~/acados)")
    p.add_argument("--omp", action="store_true", help="Enable OpenMP")
    p.add_argument("--osqp", action="store_true", help="Enable OSQP")
    p.add_argument("--qpoases", action="store_true", help="Enable qpOASES")
    p.add_argument("-e", "--export", action="store_true", help="Append ACADOS env to your shell rc file")
    args = p.parse_args()

    install_acados(
        prefix=args.prefix,
        with_openmp=args.omp,
        with_osqp=args.osqp,
        with_qpoases=args.qpoases,
        export_env=args.export
    )

if __name__ == "__main__":
    main()