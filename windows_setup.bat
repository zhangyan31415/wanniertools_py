@echo off
echo === Windows Build Setup Script ===

rem 安装构建所需的 Python 包
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

echo === Setting up MinGW-compatible MPI libraries ===
set "MSMPI_INC=C:\Program Files (x86)\Microsoft SDKs\MPI\Include"
set "MSMPI_LIB64=C:\Program Files (x86)\Microsoft SDKs\MPI\Lib\x64"
set "SYSTEMROOT_DLL=C:\Windows\System32"

if not exist "%MSMPI_LIB64%\msmpi.lib" goto msmpi_lib_not_found

echo Generating libmsmpi.a for MinGW...
C:
cd C:\msys64\ucrt64\lib
copy "%MSMPI_LIB64%\msmpi.lib" . >nul
copy "%SYSTEMROOT_DLL%\msmpi.dll" . >nul
gendef msmpi.dll
dlltool -d msmpi.def -l libmsmpi.a -D msmpi.dll
del msmpi.lib msmpi.dll msmpi.def

rem Verify libmsmpi.a was created successfully
if exist C:\msys64\ucrt64\lib\libmsmpi.a (
    echo Created libmsmpi.a in C:\msys64\ucrt64\lib
    dir C:\msys64\ucrt64\lib\libmsmpi.a
) else (
    echo [ERROR] Failed to create libmsmpi.a in C:\msys64\ucrt64\lib
    echo Current directory contents:
    dir libmsmpi.a 2>nul || echo No libmsmpi.a in current directory
)
goto msmpi_lib_done

:msmpi_lib_not_found
echo [WARNING] msmpi.lib not found in expected SDK location. Cannot create MinGW-compatible MPI lib.

:msmpi_lib_done

rem Copy MPI headers to MSYS2 include path
if not exist "%MSMPI_INC%\mpi.h" goto mpi_headers_not_found

echo Copying MPI headers to C:\msys64\ucrt64\include
xcopy /E /Y "%MSMPI_INC%" C:\msys64\ucrt64\include\ >nul
rem Copy x64-specific headers to the main include directory for easier access
xcopy /Y "%MSMPI_INC%\x64\*" C:\msys64\ucrt64\include\ >nul 2>&1
  
rem Create Fortran MPI module file (mpi.mod)
echo Generating mpi.mod for GFortran...
cd C:\msys64\ucrt64\include

if exist mpi.F90 goto compile_mpi_F90
if exist mpi.f90 goto compile_mpi_f90
echo [WARNING] No Fortran MPI source file (mpi.f90/F90) found. Skipping mpi.mod generation.
goto mod_generation_done

:compile_mpi_F90
gfortran -c -cpp -fallow-invalid-boz -fno-range-check -D_WIN64 "-DINT_PTR_KIND()=8" mpi.F90
goto check_mod_result

:compile_mpi_f90
gfortran -c -cpp -fallow-invalid-boz -fno-range-check -D_WIN64 "-DINT_PTR_KIND()=8" mpi.f90

:check_mod_result
if not exist mpi.mod goto mod_not_found
copy mpi.mod ..\ >nul
echo Copied mpi.mod to C:\msys64\ucrt64\include
goto mod_generation_done

:mod_not_found
echo [ERROR] Failed to generate mpi.mod.

:mod_generation_done
del *.o *.mod 2>nul
  
:mpi_headers_done

echo === Setting up final environment ===
rem Add all possible MPI locations to PATH
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
set "PATH=C:\Program Files\Microsoft MPI\Bin;%PATH%"
set "PATH=C:\Program Files (x86)\Microsoft MPI\Bin;%PATH%"
set "PATH=C:\Windows\System32;%PATH%"

rem Configure development paths
set "CPATH=C:\msys64\ucrt64\include"
set "LIBRARY_PATH=C:\msys64\ucrt64\lib"

echo Final verification...
where mpiexec || echo mpiexec not found
where msmpi.dll || echo msmpi.dll not found
gfortran --version
gcc --version

echo === Setup Complete ===
