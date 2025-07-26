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
powershell -Command "Invoke-WebRequest 'https://github.com/microsoft/Microsoft-MPI/releases/download/v10.1.1/msmpisetup.exe' -OutFile msmpisetup.exe"
powershell -Command "Invoke-WebRequest 'https://github.com/microsoft/Microsoft-MPI/releases/download/v10.1.1/msmpisdk.msi' -OutFile msmpisdk.msi"

start /wait msmpisetup.exe -unattend -force
start /wait msiexec /i msmpisdk.msi /quiet /norestart
del msmpisetup.exe msmpisdk.msi

echo === Checking for MPI files after installation ===
echo -- System32 MPI files --
dir C:\Windows\System32\msmpi* 2>nul || echo No MPI files in System32
echo -- Program Files MPI files --
dir "C:\Program Files\Microsoft MPI\Bin\*.*" 2>nul || echo No MPI files in Program Files
echo -- Program Files (x86) MPI files --
dir "C:\Program Files (x86)\Microsoft MPI\Bin\*.*" 2>nul || echo No MPI files in Program Files (x86)
echo -- SDK files --
dir "C:\Program Files (x86)\Microsoft SDKs\MPI\*.*" 2>nul || echo No SDK files found

echo === Setting up final environment ===
:: Add all possible MPI locations to PATH
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
set "PATH=C:\Program Files\Microsoft MPI\Bin;%PATH%"
set "PATH=C:\Program Files (x86)\Microsoft MPI\Bin;%PATH%"
set "PATH=C:\Windows\System32;%PATH%"

:: Configure development paths
set "CPATH=C:\Program Files (x86)\Microsoft SDKs\MPI\Include"
set "LIBRARY_PATH=C:\Program Files (x86)\Microsoft SDKs\MPI\Lib\x64;C:\msys64\ucrt64\lib"

echo Final verification...
where mpiexec || echo mpiexec not found
where msmpi.dll || echo msmpi.dll not found
gfortran --version
gcc --version

echo === Setup Complete ===