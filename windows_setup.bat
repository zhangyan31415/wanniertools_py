@echo off
echo === Windows Build Setup Script ===

rem 安装构建所需的 Python 包
pip install delvewheel ninja -q

echo === Checking for existing MPI files before installation ===
dir C:\Windows\System32\*mpi*.dll 2>nul || echo No MPI DLLs in System32
dir "C:\Program Files\Microsoft MPI\Bin\*.dll" 2>nul || echo No MPI DLLs in Program Files
dir "C:\Program Files (x86)\Microsoft MPI\Bin\*.dll" 2>nul || echo No MPI DLLs in Program Files (x86)

echo === Installing MSYS2 UCRT64 toolchain with MPI ===
C:\msys64\usr\bin\pacman.exe -Syu --noconfirm
C:\msys64\usr\bin\pacman.exe -S --noconfirm mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-gcc-fortran mingw-w64-ucrt-x86_64-openblas mingw-w64-ucrt-x86_64-arpack mingw-w64-ucrt-x86_64-mpi

echo === Setting up MSYS2 PATH ===
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
echo Verifying MSYS2 compilers...
gfortran --version
gcc --version

echo === MSYS2 MPI Installation Complete ===
echo Verifying MSYS2 MPI installation...
C:\msys64\ucrt64\bin\mpiexec --version || echo MPI not found
echo Checking MPI libraries...
dir C:\msys64\ucrt64\lib\*mpi* || echo No MPI libraries found

echo === Checking MSYS2 MPI files ===
echo -- MSYS2 MPI binaries --
dir C:\msys64\ucrt64\bin\mpi* 2>nul || echo No MPI binaries in MSYS2
echo -- MSYS2 MPI libraries --
dir C:\msys64\ucrt64\lib\*mpi* 2>nul || echo No MPI libraries in MSYS2
echo -- MSYS2 MPI headers --
dir C:\msys64\ucrt64\include\mpi* 2>nul || echo No MPI headers in MSYS2

echo === Setting up final environment ===
rem Add MSYS2 paths to environment
set "PATH=C:\msys64\ucrt64\bin;%PATH%"

rem Configure development paths for MSYS2 MPI
set "CPATH=C:\msys64\ucrt64\include"
set "LIBRARY_PATH=C:\msys64\ucrt64\lib"

echo Final verification...
C:\msys64\ucrt64\bin\mpiexec --version || echo mpiexec not found
gfortran --version
gcc --version

echo === Setup Complete ===
