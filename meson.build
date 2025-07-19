project('wannier-tools', 'fortran', 'c',
  version: '2.7.1',
  default_options: [
    'buildtype=release',
    'fortran_std=legacy',
    'warning_level=1'
  ]
)

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
# On Windows, try Intel MPI first, then Microsoft MPI
if build_machine.system() == 'windows'
  mpi_dep = dependency('', required: false)  # Initialize as not found
  
  # First try Intel MPI (I_MPI_ROOT environment variable or FC compiler)
  impi_root = run_command('python', '-c', 
    'import os; print(os.environ.get("I_MPI_ROOT", os.environ.get("CONDA_PREFIX", "")))', 
    check: false).stdout().strip()
  
  # Also check if FC is set to Intel MPI compiler
  fc_compiler = run_command('python', '-c', 
    'import os; fc = os.environ.get("FC", ""); print(fc if "mpii" in fc.lower() else "")', 
    check: false).stdout().strip()
  
  if impi_root != '' or fc_compiler != ''
    if fc_compiler != ''
      message('Found Intel MPI Fortran compiler: ' + fc_compiler)
      # Extract MPI root from compiler path
      impi_root = run_command('python', '-c', 
        'import os; fc = r"' + fc_compiler + '"; print(os.path.dirname(os.path.dirname(fc)) if fc else "")', 
        check: false).stdout().strip()
    endif
    
    message('Checking for Intel MPI at: ' + impi_root)
    # Check for Intel MPI in conda environment
    impi_inc_paths = [
      join_paths(impi_root, 'Library', 'include'),
      join_paths(impi_root, 'include'),
      join_paths(impi_root, 'inc')
    ]
    impi_lib_paths = [
      join_paths(impi_root, 'Library', 'lib'),
      join_paths(impi_root, 'Library', 'lib', 'release'),
      join_paths(impi_root, 'lib'),
      join_paths(impi_root, 'lib', 'release')
    ]
    
    # Try to find Intel MPI headers and libraries
    foreach inc_path : impi_inc_paths
      mpi_h_check = run_command('python', '-c', 
        'import os; print("yes" if os.path.exists(r"' + join_paths(inc_path, 'mpi.h') + '") else "no")', 
        check: false).stdout().strip()
      if mpi_h_check == 'yes'
        message('Found Intel MPI headers at: ' + inc_path)
        foreach lib_path : impi_lib_paths
          lib_dir_check = run_command('python', '-c', 
            'import os; print("yes" if os.path.exists(r"' + lib_path + '") else "no")', 
            check: false).stdout().strip()
          if lib_dir_check == 'yes'
            message('Found Intel MPI lib directory at: ' + lib_path)
            # For Intel MPI on Windows, try different library names
            impi_libs = ['-limpi', '-lmpi', '-limpicxx']
            mpi_dep = declare_dependency(
              include_directories: include_directories(inc_path),
              link_args: ['-L' + lib_path] + impi_libs
            )
            message('Successfully configured Intel MPI dependency')
            break
          endif
        endforeach
        if mpi_dep.found()
          break
        endif
      endif
    endforeach
    
    # If headers/libs not found but we have the compiler, try generic approach
    if not mpi_dep.found() and fc_compiler != ''
      message('Intel MPI compiler found but libs not detected, using compiler wrapper approach')
      mpi_dep = declare_dependency()  # Let the compiler wrapper handle everything
    endif
  endif
  
  # If Intel MPI not found, try Microsoft MPI
  if not mpi_dep.found()
    msmpi_dir = run_command('python', '-c', 
      'import os; print(os.environ.get("MSMPI_BIN", ""))', 
      check: false).stdout().strip()
    
    if msmpi_dir != ''
      message('Found Microsoft MPI at: ' + msmpi_dir)
      # Create a custom MPI dependency for MS-MPI
      msmpi_inc = run_command('python', '-c',
        'import os; msmpi_bin = os.environ.get("MSMPI_BIN", ""); print(os.path.join(os.path.dirname(msmpi_bin), "Include") if msmpi_bin else "")',
        check: false).stdout().strip()
      msmpi_lib = run_command('python', '-c', 
        'import os; msmpi_bin = os.environ.get("MSMPI_BIN", ""); print(os.path.join(os.path.dirname(msmpi_bin), "Lib", "x64") if msmpi_bin else "")',
        check: false).stdout().strip()
      
      if msmpi_inc != '' and msmpi_lib != ''
        mpi_dep = declare_dependency(
          include_directories: include_directories(msmpi_inc),
          dependencies: c_compiler.find_library('msmpi', dirs: msmpi_lib, required: false)
        )
        if mpi_dep.found()
          message('Successfully configured Microsoft MPI dependency')
        endif
      endif
    endif
  endif
  
  # Generic fallback
  if not mpi_dep.found()
    message('Trying generic MPI detection for Windows')
    mpi_dep = dependency('mpi', language: 'fortran', required: false)
  endif
else
  # Linux/macOS: use standard MPI detection
  mpi_dep = dependency('mpi', language: 'fortran', required: false)
endif

# Try to find libraries using meson's dependency system
blas_dep = dependency('blas', required: false)
lapack_dep = dependency('lapack', required: false) 
arpack_dep = dependency('arpack', required: false)

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
    message('Linux: Trying openblas')
    link_args += ['-lopenblas']
  elif build_machine.system() == 'windows'
    message('Windows: Trying standard BLAS/LAPACK libraries')
    # Use standard BLAS/LAPACK libraries available in MinGW
    link_args += ['-lblas', '-llapack']
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
    message('Windows: LAPACK already linked with BLAS above')
    # Already added -llapack in BLAS fallback section
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
    message('Windows: Using MinGW/GCC toolchain')
    link_args += ['-lgfortran', '-lquadmath', '-lm']
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
if mpi_dep.found()
  fortran_args += ['-DMPI']
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

# Install examples and other data
install_subdir('examples', install_dir: py.get_install_dir() / 'wannier_tools', strip_directory: false) 