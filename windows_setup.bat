@echo off
echo === Windows Build Setup Script ===

pip install delvewheel ninja -q

echo === Checking for existing MPI files before installation ===
dir C:\Windows\System32\*mpi*.dll 2>nul || echo No MPI DLLs in System32
dir "C:\Program Files\Microsoft MPI\Bin\*.dll" 2>nul || echo No MPI DLLs in Program Files
dir "C:\Program Files (x86)\Microsoft MPI\Bin\*.dll" 2>nul || echo No MPI DLLs in Program Files (x86)

echo === Installing MSYS2 UCRT64 toolchain ===
C:\msys64\usr\bin\pacman.exe -Syu --noconfirm
C:\msys64\usr\bin\pacman.exe -S --noconfirm mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-gcc-fortran mingw-w64-ucrt-x86_64-openblas mingw-w64-ucrt-x86_64-arpack

echo === Setting up MSYS2 PATH ===
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
echo Verifying MSYS2 compilers...
gfortran --version
gcc --version

echo === Installing Microsoft MPI ===
powershell -Command "Invoke-WebRequest 'https://download.microsoft.com/download/a/5/2/a5207ca5-1203-491a-8fb8-906fd68ae623/msmpisetup.exe' -OutFile msmpisetup.exe"
powershell -Command "Invoke-WebRequest 'https://download.microsoft.com/download/a/5/2/a5207ca5-1203-491a-8fb8-906fd68ae623/msmpisdk.msi' -OutFile msmpisdk.msi"

start /wait msmpisetup.exe -unattend
start /wait msiexec /i msmpisdk.msi /quiet /norestart
del msmpisetup.exe msmpisdk.msi

echo === Checking for MPI files after installation ===
dir C:\Windows\System32\*mpi*.dll 2>nul || echo No MPI DLLs in System32
dir "C:\Program Files\Microsoft MPI\Bin\*.dll" 2>nul || echo No MPI DLLs in Program Files
dir "C:\Program Files (x86)\Microsoft MPI\Bin\*.dll" 2>nul || echo No MPI DLLs in Program Files (x86)
where mpiexec 2>nul || echo mpiexec not found in PATH

echo === Setting up final environment ===
set "PATH=C:\msys64\ucrt64\bin;C:\Program Files\Microsoft MPI\Bin;%PATH%"
set "CPATH=C:\Program Files (x86)\Microsoft SDKs\MPI\Include"
set "LIBRARY_PATH=C:\Program Files (x86)\Microsoft SDKs\MPI\Lib\x64;C:\msys64\ucrt64\lib"

echo Final verification...
gfortran --version
gcc --version

echo === Setup Complete === 