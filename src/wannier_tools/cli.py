#!/usr/bin/env python3
"""
WannierTools Command Line Interface

This script provides a command-line interface to WannierTools.
It can be used as a standalone executable.
"""

import argparse
import sys
import os
import subprocess
import shutil
import platform
from pathlib import Path

from . import run, create_sample_input

def main():
    """Main command line interface"""
    parser = argparse.ArgumentParser(
        description="WannierTools Python Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wt-py                    # Run with default wt.in
  wt-py -i input.in        # Run with custom input file
  wt-py -o output.log      # Redirect output to file
  wt-py --sample           # Create sample input file
  wt-py -i input.in -o out.log  # Custom input and output

Note: For parallel computation, make sure MPI is installed:
  macOS: brew install open-mpi
  Ubuntu: sudo apt install libopenmpi-dev
  Then use: mpirun -np N wt-py
        """
    )
    
    parser.add_argument(
        '-i', '--input', 
        default='wt.in',
        help='Input file path (default: wt.in)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: print to console)'
    )
    
    parser.add_argument(
        '-n', '--np',
        type=int,
        default=1,
        help='Number of processes for parallel run (default: 1)'
    )

    # internal flag used to stop recursive spawning
    parser.add_argument('--no-spawn', action='store_true', help=argparse.SUPPRESS)
    
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Create a sample wt.in input file and exit'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='WannierTools Python Interface 2.7.1'
    )
    
    args = parser.parse_args()
    
    if args.sample:
        create_sample_input()
        print("Sample input file created. You can now edit wt.in and run the calculation.")
        return 0
    
    # Parallel execution wrapper -------------------------------------------------
    if not args.no_spawn and args.np > 1:
        # Try to locate bundled mpirun first
        sysname = platform.system().lower()
        machine = platform.machine().lower()

        if sysname.startswith('linux'):
            plat_dir = 'linux_x86_64'
        elif sysname == 'darwin':
            plat_dir = 'macos_arm64'
        elif sysname == 'windows':
            plat_dir = 'windows_amd64'
        else:
            plat_dir = None

        mpirun_exe = None
        if plat_dir:
            pkg_root = Path(__file__).resolve().parent
            if sysname == 'windows':
                # Windows uses mpiexec.exe
                candidate = pkg_root / 'internal_mpi' / plat_dir / 'bin' / 'mpiexec.exe'
            else:
                # Linux/macOS use mpirun
                candidate = pkg_root / 'internal_mpi' / plat_dir / 'bin' / 'mpirun'
            
            print(f"[DEBUG] Looking for bundled MPI at: {candidate}")
            if candidate.is_file():
                mpirun_exe = str(candidate)
                print(f"[DEBUG] Found bundled MPI: {mpirun_exe}")
            else:
                print(f"[DEBUG] Bundled MPI not found. Checking directory contents...")
                mpi_dir = pkg_root / 'internal_mpi'
                if mpi_dir.exists():
                    print(f"[DEBUG] internal_mpi directory exists: {list(mpi_dir.iterdir())}")
                    if (mpi_dir / plat_dir).exists():
                        print(f"[DEBUG] Platform directory exists: {list((mpi_dir / plat_dir).iterdir())}")
                        bin_dir = mpi_dir / plat_dir / 'bin'
                        if bin_dir.exists():
                            print(f"[DEBUG] Bin directory exists: {list(bin_dir.iterdir())}")
                        else:
                            print(f"[DEBUG] Bin directory does not exist: {bin_dir}")
                    else:
                        print(f"[DEBUG] Platform directory does not exist: {mpi_dir / plat_dir}")
                else:
                    print(f"[DEBUG] internal_mpi directory does not exist: {mpi_dir}")

        # Fallback to system mpirun/mpiexec if bundled is not found
        if mpirun_exe is None:
            if sysname == 'windows':
                mpirun_exe = shutil.which('mpiexec.exe') or shutil.which('mpiexec')
            else:
                mpirun_exe = shutil.which('mpirun') or shutil.which('mpiexec')

        # On Linux/macOS, if an mpirun is found, use it
        if mpirun_exe is not None:
            new_cmd = [mpirun_exe, '-np', str(args.np), sys.executable, '-m', 'wannier_tools.cli', '--no-spawn']

            # propagate user-visible CLI args (except -n/--np)
            for flag, val in (('-i', args.input), ('-o', args.output)):
                if val is not None:
                    new_cmd.extend([flag, val])
            if args.sample:
                new_cmd.append('--sample')

            # Set up environment for bundled MPI
            env = os.environ.copy()
            if plat_dir:
                is_bundled = False
                # Check if we are using a bundled MPI executable
                if sysname == 'windows':
                    # In TOML strings, backslashes are escaped, but pathlib handles it.
                    # Here we construct path with forward slashes for string matching consistency.
                    bundled_path_str = (Path('internal_mpi') / plat_dir / 'bin' / 'mpiexec.exe').as_posix()
                    if mpirun_exe.replace('\\', '/').endswith(bundled_path_str):
                        is_bundled = True
                else:
                    bundled_path_str = (Path('internal_mpi') / plat_dir / 'bin' / 'mpirun').as_posix()
                    if mpirun_exe.replace('\\', '/').endswith(bundled_path_str):
                        is_bundled = True

                if is_bundled:
                    pkg_root = Path(__file__).resolve().parent
                    mpi_root = pkg_root / 'internal_mpi' / plat_dir
                    
                    if sysname == 'windows':
                        # Add bundled bin to PATH for DLLs like msmpi.dll
                        env['PATH'] = f"{str(mpi_root / 'bin')};{env.get('PATH', '')}"
                        print(f"[INFO] Using bundled MS-MPI. Added to PATH: {mpi_root / 'bin'}")
                    else:
                        # Set OpenMPI environment variables for Linux/macOS
                        env['OPAL_PREFIX'] = str(mpi_root)
                        env['OPAL_PKGDATADIR'] = str(mpi_root / 'share' / 'openmpi')
                        env['OPAL_DATADIR'] = str(mpi_root / 'share')
                        
                        # Update library path
                        lib_path = str(mpi_root / 'lib')
                        if sysname.startswith('linux'):
                            env['LD_LIBRARY_PATH'] = f"{lib_path}:{env.get('LD_LIBRARY_PATH', '')}"
                        elif sysname == 'darwin':
                            env['DYLD_LIBRARY_PATH'] = f"{lib_path}:{env.get('DYLD_LIBRARY_PATH', '')}"

            try:
                # Use subprocess.run for cross-platform compatibility
                result = subprocess.run(new_cmd, env=env)
                sys.exit(result.returncode)
            except (FileNotFoundError, PermissionError) as e:
                print(f"[ERROR] Failed to execute {new_cmd[0]}: {e}")
                sys.exit(1)
        
        # Fallback for all systems if no mpirun/mpiexec was found
        else:
            print(f"[ERROR] Requested np > 1 on {sysname} but no mpirun/mpiexec found (bundled or system).\n"
                  "Falling back to serial execution.")


    # Run WannierTools (serial or already-spawned)
    return run(input_file=args.input, output_file=args.output)

if __name__ == '__main__':
    sys.exit(main()) 