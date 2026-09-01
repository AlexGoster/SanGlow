import os
import sys
import platform
import shutil
from pathlib import Path

import PyInstaller.__main__


def build(arch: str = "auto") -> None:
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    icon_path = project_root / "assets" / "icon.ico"
    manifest_path = project_root / "assets" / "app.manifest"

    if arch == "auto":
        arch = "x64" if platform.machine().endswith("64") else "x86"

    suffix = f"-{arch}"
    dist_name = f"SanGlow{suffix}"

    args = [
        str(src_dir / "main.py"),
        f"--name={dist_name}",
        "--onedir",
        "--noconsole",
        "--noconfirm",
        "--clean",
        f"--distpath={project_root / 'dist'}",
        f"--workpath={project_root / 'build'}",
        f"--specpath={project_root}",
        "--add-data=config;config",
        "--add-data=assets;assets",
        "--hidden-import=pygame",
        "--hidden-import=spotipy",
        "--hidden-import=sqlalchemy",
        "--hidden-import=jwt",
        "--hidden-import=cryptography",
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--collect-submodules=PyQt6",
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "--exclude-module=pandas",
        "--exclude-module=PIL",
        "--exclude-module=test",
        "--exclude-module=unittest",
        "--exclude-module=xmlrpc",
        "--exclude-module=pydoc",
        "--exclude-module=doctest",
        "--version-file=version_info.txt",
    ]

    if icon_path.exists():
        args.append(f"--icon={icon_path}")

    if manifest_path.exists():
        args.append(f"--manifest={manifest_path}")

    print(f"Building SanGlow ({arch})...")
    PyInstaller.__main__.run(args)

    dist_dir = project_root / "dist" / dist_name
    if dist_dir.exists():
        print(f"Build complete: {dist_dir}")
    else:
        print("Build failed!", file=sys.stderr)
        sys.exit(1)

    return dist_name


def build_all() -> None:
    build("x64")
    build("x86")


def create_portable_zip(dist_name: str) -> str:
    project_root = Path(__file__).parent
    zip_path = project_root / f"{dist_name}.zip"
    dist_dir = project_root / "dist" / dist_name

    if zip_path.exists():
        zip_path.unlink()

    shutil.make_archive(str(project_root / dist_name), 'zip', dist_dir)
    print(f"Portable zip: {zip_path}")
    return str(zip_path)


def create_installer(arch: str = "auto") -> str:
    project_root = Path(__file__).parent

    if arch == "auto":
        arch = "x64" if platform.machine().endswith("64") else "x86"

    dist_name = f"SanGlow-{arch}"
    dist_dir = project_root / "dist" / dist_name

    if not dist_dir.exists():
        print(f"Build {arch} first!", file=sys.stderr)
        sys.exit(1)

    print(f"Creating installer for {arch}...")

    iscc = None
    for p in [
        r"C:\Users\Lenovo\AppData\Local\Programs\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]:
        if os.path.exists(p):
            iscc = p
            break

    if not iscc:
        print("Inno Setup not found!", file=sys.stderr)
        return ""

    target = project_root / "dist" / "SanGlow"
    if target.exists():
        if target.is_symlink():
            target.unlink()
        else:
            shutil.rmtree(target)
    shutil.copytree(str(dist_dir.resolve()), str(target))

    try:
        import subprocess
        result = subprocess.run(
            [iscc, "/DArchitecture=" + arch, str(project_root / "installer.iss")],
            cwd=str(project_root),
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            installer_path = project_root / "installer_output" / "sanglow_setup.exe"
            renamed = project_root / "installer_output" / f"sanglow_setup_{arch}.exe"
            if installer_path.exists():
                installer_path.rename(renamed)
                print(f"Installer: {renamed}")
                return str(renamed)
        else:
            print(f"Installer failed: {result.stderr}", file=sys.stderr)
    finally:
        if target.exists():
            if target.is_symlink():
                target.unlink()
            else:
                shutil.rmtree(target)
    return ""


def clean() -> None:
    for d in ["build", "dist", "installer_output"]:
        p = Path(__file__).parent / d
        if p.exists():
            shutil.rmtree(p)
            print(f"Removed {p}")
    for f in Path(__file__).parent.glob("*.spec"):
        f.unlink()
        print(f"Removed {f}")


if __name__ == "__main__":
    if "--clean" in sys.argv:
        clean()
    elif "--all" in sys.argv:
        build_all()
    elif "--zip" in sys.argv:
        arch = "x64"
        for a in sys.argv:
            if a in ("x64", "x86"):
                arch = a
        dist_name = build(arch)
        create_portable_zip(dist_name)
    elif "--installer" in sys.argv:
        arch = "x64"
        for a in sys.argv:
            if a in ("x64", "x86"):
                arch = a
        build(arch)
        create_installer(arch)
    else:
        arch = "x64"
        for a in sys.argv:
            if a in ("x64", "x86"):
                arch = a
        build(arch)
