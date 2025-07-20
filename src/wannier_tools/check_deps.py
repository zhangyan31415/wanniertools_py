#!/usr/bin/env python3
"""
Dependency checker for WannierTools compilation and runtime
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def check_command(cmd, description):
    """Check if a command exists"""
    try:
        path = shutil.which(cmd)
        if path:
            print(f"[OK] {description}: {path}")
            return True
        else:
            print(f"[FAIL] {description}: Not found")
            return False
    except Exception as e:
        print(f"[FAIL] {description}: Error checking - {e}")
        return False

def check_conda_gfortran():
    """Check if gfortran is available in conda environment"""
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if not conda_prefix:
        return False
    
    # List of possible Fortran compiler names (Windows and Unix)
    fortran_compilers = [
        'gfortran',                           # Standard Linux/macOS
        'x86_64-w64-mingw32-gfortran.exe',   # Windows conda gfortran_win-64
        'x86_64-w64-mingw32-gfortran',       # Windows conda without .exe
        'i686-w64-mingw32-gfortran.exe',     # 32-bit Windows
        'i686-w64-mingw32-gfortran',         # 32-bit Windows without .exe
        'gfortran.exe',                      # Windows native
    ]
    
    # Check for gfortran in conda environment bin directory
    bin_dir = os.path.join(conda_prefix, 'bin')
    if os.name == 'nt':  # Windows
        # Also check Scripts directory on Windows
        bin_dirs = [bin_dir, os.path.join(conda_prefix, 'Scripts')]
    else:
        bin_dirs = [bin_dir]
    
    for bin_path in bin_dirs:
        if not os.path.exists(bin_path):
            continue
            
        for compiler in fortran_compilers:
            compiler_path = os.path.join(bin_path, compiler)
            if os.path.exists(compiler_path):
                print(f"[OK] gfortran in conda environment: {compiler_path}")
                return True
    
    # Also check with shutil.which for any of these compilers
    for compiler in fortran_compilers:
        path = shutil.which(compiler)
        if path and path.startswith(conda_prefix):
            print(f"[OK] gfortran in conda environment: {path}")
            return True
    
    return False

def check_fortran_compiler():
    """Check Fortran compiler with conda priority"""
    conda_prefix = os.environ.get('CONDA_PREFIX')
    
    if conda_prefix:
        # In conda environment - prioritize conda gfortran
        if check_conda_gfortran():
            return True
        
        # Check for system gfortran as fallback but warn
        system_gfortran = shutil.which('gfortran')
        if system_gfortran and not system_gfortran.startswith(conda_prefix):
            print(f"[WARN] Found system gfortran: {system_gfortran}")
            print("   Recommend installing conda gfortran: mamba install gfortran")
            return True
        
        print("[FAIL] No gfortran found in conda environment")
        return False
    else:
        # System installation - check for any gfortran
        compilers = ['gfortran', 'ifort', 'flang']
        for compiler in compilers:
            if check_command(compiler, f"Fortran compiler ({compiler})"):
                return True
        return False

def check_python_packages():
    """Check required Python packages"""
    required_packages = ['numpy', 'ninja']
    missing = []
    
    for pkg in required_packages:
        try:
            __import__(pkg)
            print(f"[OK] Python package {pkg}: Installed")
        except ImportError:
            print(f"[FAIL] Python package {pkg}: Not installed")
            missing.append(pkg)
    
    return len(missing) == 0, missing

def check_system_libraries():
    """Check for system libraries"""
    conda_prefix = os.environ.get('CONDA_PREFIX', '/usr')
    lib_paths = [
        f"{conda_prefix}/lib",
        "/usr/lib",
        "/usr/local/lib",
        "/opt/homebrew/lib"  # macOS
    ]
    
    libraries_found = {
        'openblas': False,
        'arpack': False,
        'blas': False,
        'lapack': False
    }
    
    for lib_path in lib_paths:
        if not os.path.exists(lib_path):
            continue
            
        try:
            files = os.listdir(lib_path)
            for file in files:
                if 'openblas' in file.lower() and ('.so' in file or '.dylib' in file):
                    libraries_found['openblas'] = True
                if 'arpack' in file.lower() and ('.so' in file or '.dylib' in file):
                    libraries_found['arpack'] = True
                if file.startswith('libblas') and ('.so' in file or '.dylib' in file):
                    libraries_found['blas'] = True
                if file.startswith('liblapack') and ('.so' in file or '.dylib' in file):
                    libraries_found['lapack'] = True
        except PermissionError:
            continue
    
    for lib, found in libraries_found.items():
        status = "[OK]" if found else "[FAIL]"
        print(f"{status} Library {lib}: {'Found' if found else 'Not found'}")
    
    return all(libraries_found.values())

def install_missing_dependencies():
    """Try to install missing dependencies automatically"""
    print("\n[INFO] Attempting to install missing dependencies...")
    
    # Check if we're in a conda/mamba environment
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if conda_prefix:
        # Use mamba/conda to install system dependencies
        conda_cmd = 'mamba' if shutil.which('mamba') else 'conda'
        if shutil.which(conda_cmd):
            print(f"[INFO] Using {conda_cmd} to install system dependencies...")
            try:
                # Install gfortran if missing
                if not check_conda_gfortran():
                    print("[INFO] Installing gfortran in conda environment...")
                    subprocess.run([conda_cmd, 'install', '-y', 'gfortran'], check=True)
                    print("[OK] Installed gfortran")
                
                # Also ensure we have BLAS/LAPACK/ARPACK
                subprocess.run([
                    conda_cmd, 'install', '-y', 
                    'openblas', 'arpack', 'ninja'
                ], check=True)
                print("[OK] Successfully installed dependencies with conda/mamba")
                return True
            except subprocess.CalledProcessError:
                print("[FAIL] Failed to install with conda/mamba")
                return False
    
    # Fallback to pip for Python packages
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'ninja'
        ], check=True)
        print("[OK] Installed Python build dependencies")
    except subprocess.CalledProcessError:
        print("[FAIL] Failed to install Python dependencies")
        return False
    
    return False

def print_installation_instructions():
    """Print installation instructions for missing dependencies"""
    print("\n" + "="*60)
    print("INSTALLATION INSTRUCTIONS")
    print("="*60)
    
    conda_prefix = os.environ.get('CONDA_PREFIX')
    
    if conda_prefix:
        print("\n[CONDA] For conda/mamba environment (Recommended):")
        print("mamba install gfortran openblas arpack ninja")
        print("# or")
        print("conda install gfortran openblas arpack ninja")
    
    print("\n[PIP] For Python packages:")
    print("pip install ninja")
    
    print("\n[SYSTEM] For system dependencies:")
    print("\n--- Conda/Mamba (Recommended) ---")
    print("mamba install gfortran openblas arpack")
    print("# or")
    print("conda install gfortran openblas arpack")
    
    print("\n--- Ubuntu/Debian ---")
    print("sudo apt update")
    print("sudo apt install gfortran libopenblas-dev libarpack2-dev")
    
    print("\n--- CentOS/RHEL/Fedora ---")
    print("sudo yum install gcc-gfortran openblas-devel arpack-devel")
    print("# or for newer versions:")
    print("sudo dnf install gcc-gfortran openblas-devel arpack-devel")
    
    print("\n--- macOS (with Homebrew) ---")
    print("brew install gcc openblas arpack")

def main():
    """Main dependency checking function"""
    print("Checking WannierTools dependencies...")
    print("="*60)
    
    all_good = True
    missing_critical = []
    
    # Check Fortran compiler
    if not check_fortran_compiler():
        all_good = False
        missing_critical.append("Fortran compiler (conda gfortran recommended)")
    
    # Check Python packages
    packages_ok, missing_packages = check_python_packages()
    if not packages_ok:
        all_good = False
        missing_critical.extend(missing_packages)
    
    # Check system libraries
    if not check_system_libraries():
        all_good = False
        missing_critical.append("BLAS/LAPACK/ARPACK libraries")
    
    print("\n" + "="*60)
    
    if all_good:
        print("[OK] All dependencies are satisfied!")
        return True
    else:
        print("[WARN] Some dependencies are missing:")
        for item in missing_critical:
            print(f"   - {item}")
        
        # Try automatic installation
        if os.environ.get('CONDA_PREFIX'):
            print("\n[INFO] Attempting automatic installation...")
            if install_missing_dependencies():
                print("[OK] Dependencies installed successfully!")
                return True
        
        print_installation_instructions()
        print("\n[NOTE] After installing dependencies, run 'wt-check-deps' again to verify.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 