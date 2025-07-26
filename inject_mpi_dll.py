#!/usr/bin/env python3
"""
Inject MS-MPI DLL into Windows wheel for runtime MPI support.
Usage: python inject_mpi_dll.py <dest_dir>
"""
import sys
import zipfile
import tempfile
import shutil
import os
from pathlib import Path

def inject_msmpi_dll(dest_dir):
    """Inject msmpi.dll into the Windows wheel."""
    print("=== Injecting MS-MPI into Windows wheel ===")
    
    dest_dir = Path(dest_dir)
    wheel_files = list(dest_dir.glob('*.whl'))
    
    if not wheel_files:
        print("ERROR: No wheel file found in destination directory")
        return False
        
    wheel_file = wheel_files[0]
    print(f"Processing wheel: {wheel_file}")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 解压wheel
        with zipfile.ZipFile(wheel_file, 'r') as z:
            z.extractall(temp_path)
        
        # 创建MPI目录结构
        mpi_dir = temp_path / 'wannier_tools' / 'internal_mpi' / 'windows_amd64'
        (mpi_dir / 'bin').mkdir(parents=True, exist_ok=True)
        (mpi_dir / 'lib').mkdir(parents=True, exist_ok=True)
        (mpi_dir / 'include').mkdir(parents=True, exist_ok=True)
        
        # 查找并复制 msmpi.dll
        msmpi_dll_path = Path('C:/Windows/System32/msmpi.dll')
        if not msmpi_dll_path.exists():
            for p in [
                Path('C:/Program Files/Microsoft MPI/Bin/msmpi.dll'),
                Path('C:/Program Files (x86)/Microsoft MPI/Bin/msmpi.dll')
            ]:
                if p.exists():
                    msmpi_dll_path = p
                    break
        
        if msmpi_dll_path.exists():
            print(f"Found msmpi.dll at: {msmpi_dll_path}")
            shutil.copy2(msmpi_dll_path, mpi_dir / 'bin')
            print("Copied msmpi.dll")
        else:
            print("[ERROR] msmpi.dll not found in any standard location.")
            return False
            
        # 查找并复制 mpiexec.exe
        mpiexec_path = Path('C:/Program Files/Microsoft MPI/Bin/mpiexec.exe')
        if not mpiexec_path.exists():
            mpiexec_path = Path('C:/Program Files (x86)/Microsoft MPI/Bin/mpiexec.exe')

        if mpiexec_path.exists():
            print(f"Found mpiexec.exe at: {mpiexec_path}")
            shutil.copy2(mpiexec_path, mpi_dir / 'bin')
            print("Copied mpiexec.exe")
        else:
            print("[WARNING] mpiexec.exe not found, skipping.")
        
        # 重新打包wheel
        with zipfile.ZipFile(wheel_file, 'w', zipfile.ZIP_DEFLATED) as z:
            for file_path in temp_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_path)
                    z.write(file_path, arcname)
        
        print(f"OK - MS-MPI DLL injected into {wheel_file.name}")
        return True

def show_wheel_contents(dest_dir):
    """Display the contents of the wheel file."""
    print("=== Final wheel contents ===")
    dest_dir = Path(dest_dir)
    wheel_files = list(dest_dir.glob('*.whl'))
    
    if not wheel_files:
        print("ERROR: No wheel file found")
        return
        
    wheel_file = wheel_files[0]
    with zipfile.ZipFile(wheel_file) as z:
        total_size = 0
        for info in z.infolist():
            print(f"{info.filename:<60} {info.file_size:>10} bytes")
            total_size += info.file_size
        print(f"Total files: {len(z.infolist())}, Total size: {total_size:,} bytes")

def main():
    if len(sys.argv) != 2:
        print("Usage: python inject_mpi_dll.py <dest_dir>")
        sys.exit(1)
    
    dest_dir = sys.argv[1]
    
    # 注入MPI DLL
    success = inject_msmpi_dll(dest_dir)
    if not success:
        sys.exit(1)
    
    # 显示wheel内容
    show_wheel_contents(dest_dir)

if __name__ == "__main__":
    main() 