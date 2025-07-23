"""
WannierTools Python Wrapper
"""
import os
import sys
from pathlib import Path
import platform

# ------------------------------------------------------------------
# Make bundled OpenMPI shared libraries discoverable before we import
# the compiled Fortran extension (which links to libmpi).
# ------------------------------------------------------------------

def _inject_internal_mpi_libs():
    sysname = platform.system().lower()
    if sysname.startswith('linux'):
        plat_dir = 'linux_x86_64'
        lib_env = 'LD_LIBRARY_PATH'
    elif sysname == 'darwin':
        plat_dir = 'macos_arm64'
        lib_env = 'DYLD_LIBRARY_PATH'
    else:
        return  # Windows: runtime_mpi, nothing to inject


    pkg_root = Path(__file__).resolve().parent
    mpi_lib_dir = pkg_root / 'internal_mpi' / plat_dir / 'lib'
    if mpi_lib_dir.is_dir():
        os.environ[lib_env] = f"{mpi_lib_dir}:{os.environ.get(lib_env,'')}"


_inject_internal_mpi_libs()

import subprocess  # after env vars set

# Version of the package
__version__ = "2.7.1"

def run(input_file="wt.in", output_file=None):
    """
    Run the WannierTools main program using the compiled Fortran extension.

    Parameters:
    input_file (str): Path to the WannierTools input file (default: "wt.in").
    output_file (str or None): If set, redirect stdout/stderr to this file.
    """
    # Check if we're running under MPI by looking at environment variables
    # This works without requiring mpi4py
    mpi_rank = os.environ.get('OMPI_COMM_WORLD_RANK')  # OpenMPI
    if mpi_rank is None:
        mpi_rank = os.environ.get('PMI_RANK')  # Intel MPI, MPICH
    if mpi_rank is None:
        mpi_rank = os.environ.get('SLURM_PROCID')  # SLURM
    
    # Only output messages from the main process (rank 0)
    is_main_process = (mpi_rank is None or int(mpi_rank) == 0)
    
    try:
        from . import wannier_tools_ext
        if is_main_process:
            print("Successfully loaded wannier_tools_ext extension module.")
    except ImportError as e:
        if is_main_process:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!! FATAL: Could not import the compiled Fortran extension module.")
            print(f"!!! Error details: {e}")
            print("!!! Please ensure the package was compiled correctly.")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return

    original_cwd = os.getcwd()
    input_dir = os.path.dirname(os.path.abspath(input_file))
    if not input_dir:
        input_dir = '.'

    if is_main_process:
        print(f"Changing working directory to: {input_dir}")
    os.chdir(input_dir)

    try:
        if output_file:
            with open(output_file, 'w') as f, open('/dev/null', 'r') as devnull:
                old_stdout, old_stderr, old_stdin = sys.stdout, sys.stderr, sys.stdin
                sys.stdout, sys.stderr, sys.stdin = f, f, devnull
                try:
                    if is_main_process:
                        print("Calling the Fortran `run_wannier_tools` subroutine...")
                    wannier_tools_ext.wannier_tools_wrapper.run_wannier_tools()
                    if is_main_process:
                        print("Fortran subroutine finished.")
                finally:
                    sys.stdout, sys.stderr, sys.stdin = old_stdout, old_stderr, old_stdin
        else:
            if is_main_process:
                print("Calling the Fortran `run_wannier_tools` subroutine...")
            wannier_tools_ext.wannier_tools_wrapper.run_wannier_tools()
            if is_main_process:
                print("Fortran subroutine finished.")
    except Exception as e:
        if is_main_process:
            error_msg = str(e).lower()
            if 'mpi' in error_msg or 'comm_f2c' in error_msg or 'mpi_init' in error_msg:
                print("=" * 60)
                print("MPI Error Detected!")
                print("=" * 60)
                print(f"Error details: {e}")
                print("\nThis error typically occurs when:")
                print("1. MPI is not properly installed on your system")
                print("2. The program is called directly instead of via mpirun/mpiexec")
                print("\nTo fix this issue:")
                print("📦 Install MPI:")
                print("   macOS:        brew install open-mpi")
                print("   Ubuntu:       sudo apt install libopenmpi-dev")
                print("   CentOS/RHEL:  sudo yum install openmpi-devel")
                print("   Conda:        conda install openmpi")
                print("\n🚀 For parallel execution, use:")
                print("   mpirun -np <N> wt-py")
                print("   (where <N> is the number of processes)")
                print("\n💡 For single-core execution:")
                print("   Just run: wt-py")
                print("   (MPI should still be installed for the runtime)")
                print("=" * 60)
            else:
            print(f"An error occurred during the Fortran execution: {e}")
    finally:
        if is_main_process:
            print(f"Restoring original working directory: {original_cwd}")
        os.chdir(original_cwd)

def create_sample_input():
    """
    Create a sample wt.in input file for testing.
    """
    sample_input = """&TB_FILE
Hrfile = 'wannier90_hr.dat'
Package = 'VASP'             
/

&CONTROL
BulkBand_calc         = T
BulkFS_calc           = F  
BulkGap_cube_calc     = F
BulkGap_plane_calc    = F
SlabBand_calc         = F
WireBand_calc         = F
SlabSS_calc           = F
SlabArc_calc          = F
SlabSpintexture_calc  = F
wanniercenter_calc    = F
/

&SYSTEM
NSLAB = 10               
NSLAB1= 4                
NSLAB2= 4                
NumOccupied = 18         
SOC = 1                  
E_FERMI = 4.4195         
/

&PARAMETERS
Eta_Arc = 0.001     
E_arc = 0.0         
OmegaNum = 100      
OmegaMin = -0.6     
OmegaMax =  0.5     
Nk1 = 101            
Nk2 = 101            
Nk3 = 101            
NP = 2               
Gap_threshold = 0.01 
/

LATTICE
Angstrom
-2.069  -3.583614  0.000000     
 2.069  -3.583614  0.000000     
 0.000   2.389075  9.546667     

ATOM_POSITIONS
5                               
Direct                          
Bi 0.3990    0.3990    0.6970
Bi 0.6010    0.6010    0.3030
Te 0     0     0.5
Te 0.2060    0.2060    0.1180
Te 0.7940    0.7940    0.8820

PROJECTORS
3 3 3 3 3
Bi pz px py
Bi pz px py  
Te pz px py
Te pz px py
Te pz px py

SURFACE            
 1  0  0
 0  1  0

KPATH_BULK
4              
G 0.00000 0.00000 0.0000 Z 0.00000 0.00000 0.5000
Z 0.00000 0.00000 0.5000 F 0.50000 0.50000 0.0000  
F 0.50000 0.50000 0.0000 G 0.00000 0.00000 0.0000
G 0.00000 0.00000 0.0000 L 0.50000 0.00000 0.0000

KPATH_SLAB
2              
K 0.33 0.67 G 0.0 0.0  
G 0.0 0.0 M 0.5 0.5

KPLANE_SLAB
-0.1 -0.1      
 0.1  0.1      

KPLANE_BULK
-0.50 -0.50      
 0.50  0.50      

KCUBE_BULK
-0.50 -0.50 -0.50      
 0.50  0.50  0.50      
"""
    
    with open("wt.in", "w") as f:
        f.write(sample_input)
    
    print("Sample input file 'wt.in' created.")
    print("You can edit this file according to your needs and then run wannier_tools.run()")

# Lazy import of cli module to avoid circular imports
def __getattr__(name):
    if name == 'cli':
        import importlib
        cli_module = importlib.import_module('.cli', package=__name__)
        globals()['cli'] = cli_module  # Cache it
        return cli_module
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = ['run', 'create_sample_input', 'cli'] 