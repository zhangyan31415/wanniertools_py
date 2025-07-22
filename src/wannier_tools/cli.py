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
        else:
            plat_dir = None

        mpirun_exe = None
        if plat_dir:
            pkg_root = Path(__file__).resolve().parent
            candidate = pkg_root / 'internal_mpi' / plat_dir / 'bin' / 'mpirun'
            if candidate.is_file():
                mpirun_exe = str(candidate)

        # Fallback to system mpirun if bundled is not found (Linux/macOS only)
        if mpirun_exe is None and sysname != 'windows':
            mpirun_exe = shutil.which('mpirun') or shutil.which('mpiexec')

        # On Linux/macOS, if an mpirun is found, use it
        if mpirun_exe is not None and sysname != 'windows':
            new_cmd = [mpirun_exe, '-np', str(args.np), sys.executable, '-m', 'wannier_tools.cli', '--no-spawn']

            # propagate user-visible CLI args (except -n/--np)
            for flag, val in (('-i', args.input), ('-o', args.output)):
                if val is not None:
                    new_cmd.extend([flag, val])
            if args.sample:
                new_cmd.append('--sample')

            os.execvpe(new_cmd[0], new_cmd, os.environ)
            # exec replaces current process; no return
        
        # Windows fallback: use multiprocessing
        elif sysname == 'windows':
            print("[INFO] No mpirun found on Windows, using multiprocessing fallback")
            import multiprocessing as mp
            
            def run_with_rank(rank, input_file, output_file):
                """Run WannierTools with specific rank"""
                env = os.environ.copy()
                env['WT_RANK'] = str(rank)
                env['WT_SIZE'] = str(args.np)
                print(f"[INFO] Starting process {rank}/{args.np}")
                return run(input_file=input_file, output_file=output_file)
            
            # Start processes
            processes = []
            for rank in range(args.np):
                p = mp.Process(target=run_with_rank, args=(rank, args.input, args.output))
                p.start()
                processes.append(p)
            
            # Wait for all processes
            for p in processes:
                p.join()
            
            return 0
        
        # Fallback for Linux/macOS if no mpirun was found
        else:
            print(f"[ERROR] Requested np > 1 on {sysname} but no mpirun/mpiexec found (bundled or system).\n"
                  "Falling back to serial execution.")


    # Run WannierTools (serial or already-spawned)
    return run(input_file=args.input, output_file=args.output)

if __name__ == '__main__':
    sys.exit(main()) 