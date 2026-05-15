import os
import sys
import subprocess

def main():
    # Base Nuitka command
    # --standalone: Creates a folder with the executable and all dependencies
    # --onefile: (Optional) Change to --onefile if you want a single executable file instead of a folder
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone", 
        "--disable-console",           # Equivalent to console=False
        "--enable-plugin=pyqt5",       # Replaces collect_data_files/submodules for PyQt5
        "--include-package=pynput",    # Equivalent to hiddenimports
        "--include-package=pygame",    # Equivalent to hiddenimports
        "--output-dir=build_out",      # Where to put the final build
    ]

    # 1. Collect Data Files (Equivalent to `datas = []` logic)
    if os.path.exists('img'):
        cmd.append('--include-data-dir=img=img')
    if os.path.exists('skins'):
        cmd.append('--include-data-dir=skins=skins')
    if os.path.exists('sounds'):
        cmd.append('--include-data-dir=sounds=sounds')
    if os.path.exists('bongo.ini'):
        cmd.append('--include-data-file=bongo.ini=bongo.ini')

    # 2. Add Icons
    icon_path = 'img/cat-rest.png'
    if os.path.exists(icon_path):
        if sys.platform == 'win32':
            # Nuitka can automatically convert PNG to ICO on Windows if imageio is installed
            cmd.append(f'--windows-icon-from-ico={icon_path}')
        elif sys.platform == 'darwin':
            cmd.append(f'--macos-app-icon={icon_path}')

    # 3. macOS App Bundle Specifics
    if sys.platform == 'darwin':
        cmd.extend([
            '--macos-create-app-bundle',
            '--macos-app-name=BongoCat',
            '--macos-bundle-identifier=com.luinbytes.bongocat',
            # Nuitka automatically handles high res and background flags based on plugins
        ])

    # 4. Entry Point
    cmd.append('bongo_cat/main.py')

    # Run the build process
    print("Executing Nuitka build...")
    print(" ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild completed successfully!")
    except subprocess.CalledProcessError:
        print("\nBuild failed. Check the Nuitka output above for errors.")

if __name__ == "__main__":
    main()
