# Linux OpenMPI Runtime Directory

This directory contains OpenMPI runtime files for Linux x86_64 platform.

Files in this directory are populated during the CI build process:
- `bin/mpirun` - MPI launcher executable
- `bin/orterun` - OpenRTE launcher (if available)
- `lib/libmpi.so*` - OpenMPI core libraries
- `lib/libopen-pal.so*` - OpenPAL libraries
- `lib/libopen-rte.so*` - OpenRTE libraries
- `share/` - OpenMPI configuration and help files

These files enable MPI parallel execution on Linux systems without requiring
users to install OpenMPI separately. 