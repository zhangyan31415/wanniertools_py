project('wannier-tools', 'fortran', 'c',
  version: '2.7.1',
  default_options: [
    'buildtype=release',
    'fortran_std=legacy',
    'warning_level=1'
  ]
)

# Import filesystem module
fs = import('fs')

# --- Compiler Detection ---
c_compiler = meson.get_compiler('c')

# Fortran compiler detection with better error handling
fortran_compiler = meson.get_compiler('fortran')

# Print compiler information for debugging  
message('C compiler: ' + c_compiler.get_id() + ' (' + c_compiler.cmd_array()[0] + ')')
message('Fortran compiler: ' + fortran_compiler.get_id() + ' (' + fortran_compiler.cmd_array()[0] + ')')

# Check if we're in a cross-compilation environment
if meson.is_cross_build()
  message('Cross-compilation detected')
  message('Host machine: ' + host_machine.system() + ' ' + host_machine.cpu_family())
  message('Build machine: ' + build_machine.system() + ' ' + build_machine.cpu_family())
endif

py = import('python').find_installation(pure: false)
py_dep = py.dependency()

# Simplified Fortran compiler check - if we reach here, meson already found a compiler
message('Fortran compiler successfully detected by Meson')

# --- Dependencies ---
numpy_inc = run_command(py, '-c', 'import numpy; print(numpy.get_include())', check: true).stdout().strip()
numpy_dep = declare_dependency(include_directories: numpy_inc)

# --- Fortran Source Files ---
sources = files(
  'src/wannier_tools/_fortran_src/2D_TSC.f90',
  'src/wannier_tools/_fortran_src/berrycurvature.f90',
  'src/wannier_tools/_fortran_src/berry.f90',
  'src/wannier_tools/_fortran_src/Boltz_transport_anomalous.f90',
  'src/wannier_tools/_fortran_src/dos.f90',
  'src/wannier_tools/_fortran_src/effective_mass.f90',
  'src/wannier_tools/_fortran_src/eigen.f90',
  'src/wannier_tools/_fortran_src/ekb_ribbon.f90',
  'src/wannier_tools/_fortran_src/ek_bulk.f90',
  'src/wannier_tools/_fortran_src/ek_bulk_polar.f90',
  'src/wannier_tools/_fortran_src/ek_ribbon.f90',
  'src/wannier_tools/_fortran_src/ek_slab.f90',
  'src/wannier_tools/_fortran_src/element_table.f90',
  'src/wannier_tools/_fortran_src/fermiarc.f90',
  'src/wannier_tools/_fortran_src/fermisurface.f90',
  'src/wannier_tools/_fortran_src/findnodes.f90',
  'src/wannier_tools/_fortran_src/ham_bulk.f90',
  'src/wannier_tools/_fortran_src/ham_qlayer2qlayer.f90',
  'src/wannier_tools/_fortran_src/ham_ribbon_b.f90',
  'src/wannier_tools/_fortran_src/ham_ribbon.f90',
  'src/wannier_tools/_fortran_src/ham_slab.f90',
  'src/wannier_tools/_fortran_src/inverse.f90',
  'src/wannier_tools/_fortran_src/lanczos_sparse.f90',
  'src/wannier_tools/_fortran_src/landau_level.f90',
  'src/wannier_tools/_fortran_src/landau_level_sparse.f90',
  'src/wannier_tools/_fortran_src/main.f90',
  'src/wannier_tools/_fortran_src/math_lib.f90',
  'src/wannier_tools/_fortran_src/mat_mul.f90',
  'src/wannier_tools/_fortran_src/mgmres.f90',
  'src/wannier_tools/_fortran_src/module.f90',
  'src/wannier_tools/_fortran_src/optic.f90',
  'src/wannier_tools/_fortran_src/orbital_momenta.f90',
  'src/wannier_tools/_fortran_src/proteus.f90',
  'src/wannier_tools/_fortran_src/psi.f90',
  'src/wannier_tools/_fortran_src/rand.f90',
  'src/wannier_tools/_fortran_src/readHmnR.f90',
  'src/wannier_tools/_fortran_src/readinput.f90',
  'src/wannier_tools/_fortran_src/runtime_mpi.f90',
  'src/wannier_tools/_fortran_src/sigma.f90',
  'src/wannier_tools/_fortran_src/sigma_OHE.f90',
  'src/wannier_tools/_fortran_src/sparse.f90',
  'src/wannier_tools/_fortran_src/stop_sub.f90',
  'src/wannier_tools/_fortran_src/surfgreen.f90',
  'src/wannier_tools/_fortran_src/surfstat.f90',
  'src/wannier_tools/_fortran_src/symmetry.f90',
  'src/wannier_tools/_fortran_src/unfolding.f90',
  'src/wannier_tools/_fortran_src/wanniercenter_adaptive.f90',
  'src/wannier_tools/_fortran_src/wanniercenter.f90',
  'src/wannier_tools/_fortran_src/wt_aux.f90'
)

# --- Library Discovery ---
# Find NumPy library directory
numpy_lib_dir = run_command(py, '-c', 'import numpy, os; print(os.path.join(os.path.dirname(numpy.__file__), "core", "lib"))', check: true).stdout().strip()

# Basic link arguments
link_args = [
  '-L' + numpy_lib_dir,
]

# Try to link npymath if available
npymath_check = run_command(py, '-c', '''
import numpy, os, glob
lib_dir = os.path.join(os.path.dirname(numpy.__file__), "core", "lib") 
files = glob.glob(os.path.join(lib_dir, "libnpymath*"))
print("yes" if files else "no")
''', check: false).stdout().strip()

if npymath_check == 'yes'
  link_args += ['-lnpymath']
endif

# ---- Use meson dependency() for automatic library detection -------------------------
# Try to find MPI dependency
# On Windows, use MSYS2 gfortran-compatible MPI to avoid ABI issues
if build_machine.system() == 'windows'
  message('Windows detected: using MSYS2 gfortran-compatible MPI for ABI compatibility')
  message('Reason: Official MS-MPI uses Intel Fortran ABI, incompatible with gfortran')
  message('Solution: MSYS2 mingw-w64-x86_64-msmpi provides gfortran-compatible libraries')
  
  # Force check for MSYS2 MPI installation
  msys2_mpi_inc = 'C:/msys64/mingw64/include'
  msys2_mpi_lib = 'C:/msys64/mingw64/lib'
  
  # Verify MSYS2 gfortran-compatible MPI is installed
  mpi_h_exists = run_command('python', '-c', 
    'import os; exit(0 if os.path.exists(r"' + msys2_mpi_inc + '/mpi.h") else 1)', 
    check: false).returncode() == 0
  mpi_lib_exists = run_command('python', '-c', 
    'import os; exit(0 if os.path.exists(r"' + msys2_mpi_lib + '/libmsmpi.dll.a") else 1)', 
    check: false).returncode() == 0
    
  if mpi_h_exists and mpi_lib_exists
    message('[OK] MSYS2 gfortran-compatible MPI found')
    message('   Headers: ' + msys2_mpi_inc + '/mpi.h')
    message('   Library: ' + msys2_mpi_lib + '/libmsmpi.dll.a')
    
    # Create MPI dependency with explicit MSYS2 paths
            mpi_dep = declare_dependency(
      include_directories: include_directories(msys2_mpi_inc),
      dependencies: [
        c_compiler.find_library('msmpi', dirs: msys2_mpi_lib, required: true)
      ],
      compile_args: ['-DHAVE_MPI']
    )
    message('[OK] Hybrid gfortran+MS-MPI compatibility configured successfully')
    message('   Build: gfortran + MSYS2 libs (ABI consistent)')
    message('   Runtime: Official MS-MPI mpiexec.exe (from separate installation)')
  else
    error('MSYS2 gfortran-compatible MPI not found!\n' +
          'Required: pacman -S mingw-w64-x86_64-msmpi\n' + 
          'This package provides gfortran-compatible MPI libraries to avoid ABI mismatch.')
  endif
else
  # Linux/macOS: use standard MPI detection
  mpi_dep = dependency('mpi', language: 'fortran', required: false)
endif

# Try to find libraries using meson's dependency system
# For wheels/manylinux builds, disable system library detection to avoid conflicts
disable_system_libs = run_command('python', '-c', 'import os; print(os.environ.get("CIBUILDWHEEL", "false"))', check: false).stdout().strip()
if disable_system_libs == '1'
  # In cibuildwheel environment, use manual linking only
  blas_dep = dependency('', required: false)  # Force not found
  lapack_dep = dependency('', required: false)  # Force not found
  arpack_dep = dependency('', required: false)  # Force not found to avoid system conflicts
  message('cibuildwheel detected: using manual library linking only')
else
  # Normal build environment, use meson detection
blas_dep = dependency('blas', required: false)
lapack_dep = dependency('lapack', required: false) 
arpack_dep = dependency('arpack', required: false)
endif

math_deps = []

if mpi_dep.found()
  message('Found MPI via dependency()')
  math_deps += [mpi_dep]
else
  message('MPI not found, building in serial mode.')
endif

if blas_dep.found()
  message('Found BLAS via dependency()')
  math_deps += [blas_dep]
else
  message('BLAS not found via dependency(), will try platform-specific manual linking')
  if build_machine.system() == 'darwin'
    message('macOS: Using Accelerate framework for BLAS')
    link_args += ['-framework', 'Accelerate']
  elif build_machine.system() == 'linux'
    message('Linux: Using OpenBLAS with explicit paths for manylinux')
    # For manylinux builds, use explicit library paths
    link_args += ['-L/usr/lib64', '-L/usr/local/lib64', '-L/usr/local/lib', '-lopenblas']
  elif build_machine.system() == 'windows'
    message('Windows: Configuring single-threaded OpenBLAS from MSYS2 for MPI compatibility')
    # Add MSYS2 library and include paths
    link_args += ['-LC:/msys64/mingw64/lib', '-lopenblas']
    # Ensure DLL search path includes MSYS2 bin directory
    message('Windows: Adding MSYS2 bin to library search path for DLL discovery')
    # Add compile flags to ensure single-threaded operation for MPI compatibility
    message('Windows: Configuring OpenBLAS for single-threaded mode to prevent MPI conflicts')
  endif
endif

if lapack_dep.found()
  message('Found LAPACK via dependency()')
  math_deps += [lapack_dep]
else
  message('LAPACK not found via dependency(), checking platform-specific options') 
  if build_machine.system() == 'darwin'
    message('macOS: LAPACK included in Accelerate framework')
    # Already linked via Accelerate framework above
  elif build_machine.system() == 'windows'
    message('Windows: LAPACK included in OpenBLAS')
    # OpenBLAS includes LAPACK functionality, no separate linking needed
  else
    message('Linux: LAPACK linking disabled to avoid conflicts')
    # Don't add -llapack to avoid conflicts on Linux
  endif
endif

if arpack_dep.found()
  message('Found ARPACK via dependency()')
  math_deps += [arpack_dep]
else
  message('ARPACK not found via dependency() - skipping ARPACK linking')
  message('Note: Some advanced features may not be available without ARPACK')
  # Don't add -larpack if we can't find it
endif

# For Windows, add additional system libraries and ensure consistent toolchain
if build_machine.system() == 'windows'
  if fortran_compiler.get_id().startswith('gcc')
    message('Windows: Using MinGW/GCC toolchain with enhanced DLL support')
    # Add runtime libraries with explicit paths for better DLL discovery
    link_args += ['-LC:/msys64/mingw64/bin', '-LC:/msys64/mingw64/lib']
    link_args += ['-lgfortran', '-lquadmath', '-lm', '-lwinpthread']
    
    # Add runtime DLL search paths
    link_args += ['-Wl,--enable-auto-import']
    link_args += ['-Wl,--enable-runtime-pseudo-reloc']
    
    message('Windows: Added MinGW runtime libraries and DLL search paths')
    
    # Ensure we use MinGW linker, not MSVC
    if c_compiler.get_id() != 'gcc'
      warning('Windows: C compiler is not GCC, this may cause linking issues')
      warning('Consider setting CC=gcc and CXX=g++ for consistent toolchain')
    endif
  endif
endif

# -------------------------------------------------------------------------------

# --- Build Targets ---
# Add f2py wrapper to the main library sources
all_sources = sources + files('src/wannier_tools/_fortran_src/f2py_wrapper.f90')

# Set fortran compiler arguments
fortran_args = []

if fortran_compiler.get_id().startswith('intel')
  if build_machine.system() == 'windows'
    fortran_args += ['/fpp']
  else
    fortran_args += ['-fpp']
  endif
else
  fortran_args += ['-cpp', '-fallow-argument-mismatch']
endif

# Add MPI preprocessor definition if MPI is found
# For wheels/packaging builds, we use runtime MPI detection only
runtime_mpi_only = run_command('python', '-c', 'import os; print(os.environ.get("WANNIERTOOLS_RUNTIME_MPI_ONLY", "false"))', check: false).stdout().strip()
is_wheel_build = run_command('python', '-c', 'import os; print(os.environ.get("CIBUILDWHEEL", "false"))', check: false).stdout().strip()

# Force runtime MPI detection only when explicitly requested
if runtime_mpi_only == 'true'
  message('Building with runtime-only MPI detection (explicitly requested)')
elif mpi_dep.found() and host_machine.system() != 'windows'
  # Only enable compile-time MPI on Linux and macOS
  fortran_args += ['-DMPI']
  if is_wheel_build == '1'
    message('Building wheel with compile-time MPI support (bundled OpenMPI)')
  else
    message('Building with compile-time MPI support')
  endif
elif host_machine.system() == 'windows'
  message('Building with runtime-only MPI detection (Windows - not implemented yet)')
else
  message('Building with runtime-only MPI detection (no MPI found)')
endif

if build_machine.system() == 'windows' and fortran_compiler.get_id().startswith('intel')
  mpi_lib_dir = 'C:/Program Files (x86)/Intel/oneAPI/mpi/latest/lib/'
  link_args += ['-LIBPATH:' + mpi_lib_dir, 'impi.lib']
endif 

wt_lib = static_library('wt', all_sources,
  fortran_args: fortran_args,
  dependencies: mpi_dep.found() ? [mpi_dep] : [],
  install: false
)

# 先找出 numpy.f2py 的源码目录
f2py_src_dir = run_command(py, '-c',
  'import os, numpy.f2py; print(os.path.join(os.path.dirname(numpy.f2py.__file__), "src"))'
).stdout().strip()

# 把 fortranobject.c 和它的头文件都列进来
f2py_rt_c = files(join_paths(f2py_src_dir, 'fortranobject.c'))

# （可选）如果有头文件要手动指 include path：
f2py_rt_inc = include_directories(f2py_src_dir)

# 你原来的 f2py_wrappers custom_target 会生成 C 包装器
f2py_generated = custom_target(
  'f2py_wrappers',
  input: 'src/wannier_tools/_fortran_src/f2py_wrapper.f90',
  output: ['wannier_tools_extmodule.c', 'wannier_tools_ext-f2pywrappers2.f90'],
  command: [py, '-m', 'numpy.f2py', '-m', 'wannier_tools_ext', '@INPUT@']
)

f2py_c = f2py_generated[0]
f2py_f90 = f2py_generated[1]


f2py_incdir = run_command(py, '-c', 'import numpy.f2py; print(numpy.f2py.get_include())', check: true).stdout().strip()

# 最终把 fortranobject.c 和生成的 C 包装器一起编译
py.extension_module(
  'wannier_tools_ext',
  sources: [
    f2py_c,
    f2py_f90,
    f2py_rt_c
  ],
  dependencies: [py_dep, numpy_dep] + math_deps,  # 添加数学库依赖
  c_args: ['-I' + f2py_incdir],    # 已有的 NumPy include
  include_directories: f2py_rt_inc, # 把 fortranobject.c 的目录也加进来
  link_with: [wt_lib],
  link_args: link_args,
  install: true,
  install_dir: py.get_install_dir() / 'wannier_tools',
  install_tag: 'extension'   # Add install tag to ensure it is installed by meson-python
)

# Install Python package files
py.install_sources([
  'src/wannier_tools/__init__.py',
  'src/wannier_tools/cli.py',
  'src/wannier_tools/__main__.py',
  'src/wannier_tools/check_deps.py',
],
  subdir: 'wannier_tools'
)

# Install internal_mpi files (including placeholder and any MPI files created during CI)
internal_mpi_files = files(
  'src/wannier_tools/internal_mpi/__init__.py',
  'src/wannier_tools/internal_mpi/.placeholder',
)
py.install_sources(internal_mpi_files, subdir: 'wannier_tools/internal_mpi', preserve_path: false)

# Install examples and other data
install_subdir('examples', install_dir: py.get_install_dir() / 'wannier_tools', strip_directory: false) 