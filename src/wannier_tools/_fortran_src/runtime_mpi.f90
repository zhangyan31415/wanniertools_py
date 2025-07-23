!> Runtime MPI detection module
!> This module attempts to detect and initialize MPI at runtime
!> without requiring compile-time MPI dependencies

module runtime_mpi
    use para, only: dp
    implicit none
    
    ! MPI status variables
    logical :: mpi_available = .false.
    logical :: mpi_initialized = .false.
    integer :: ierr = 0
    integer :: cpuid = 0
    integer :: num_cpu = 1
    
    ! MPI constants (will be ignored if MPI not available)
    integer, parameter :: mpi_integer = 4
    integer, parameter :: mpi_double_precision = 8
    integer, parameter :: mpi_double_complex = 16
    integer, parameter :: mpi_sum = 1
    integer, parameter :: mpi_comm_world = 0
    
contains

    !> Try to initialize MPI at runtime
    subroutine try_init_mpi()
        implicit none
        
        ! Check if we're running under MPI
        call check_mpi_environment()
        
        if (mpi_available) then
            ! Try to initialize MPI
            call attempt_mpi_init()
        else
            ! No MPI environment detected, use serial mode
            cpuid = 0
            num_cpu = 1
            mpi_initialized = .false.
        endif
        
    end subroutine try_init_mpi
    
    !> Check if MPI environment is available
    subroutine check_mpi_environment()
        implicit none
        character(len=256) :: env_var
        integer :: status
        
        ! Check for common MPI environment variables (MPICH on Linux, OpenMPI on macOS)
        call get_environment_variable('PMI_RANK', env_var, status)
        if (len_trim(env_var) > 0) then
            mpi_available = .true.
            return
        endif
        
        call get_environment_variable('OMPI_COMM_WORLD_RANK', env_var, status)
        if (len_trim(env_var) > 0) then
            mpi_available = .true.
            return
        endif
        
        call get_environment_variable('MPI_LOCALRANKID', env_var, status)
        if (len_trim(env_var) > 0) then
            mpi_available = .true.
            return
        endif
        ! Custom launcher support (Windows fallback)
        call get_environment_variable('WT_RANK', env_var, status)
        if (len_trim(env_var) > 0) then
            mpi_available = .true.
            return
        endif
        
        ! If no MPI environment variables found, assume serial
        mpi_available = .false.
        
    end subroutine check_mpi_environment
    
    !> Attempt to initialize MPI
    subroutine attempt_mpi_init()
        implicit none
        
        ! This will only work if MPI libraries are available at runtime
        ! We'll use a simple approach: try to call MPI functions
        
        ! Try to initialize MPI - this might fail if MPI libs not available
        call safe_mpi_init()
        
        if (mpi_initialized) then
            call safe_mpi_comm_rank()
            call safe_mpi_comm_size()
        else
            ! Fall back to serial mode
            cpuid = 0
            num_cpu = 1
        endif
        
    end subroutine attempt_mpi_init
    
    !> Safe MPI init that won't crash if MPI not available
    subroutine safe_mpi_init()
        implicit none
        
        if (mpi_available) then
            ! Try to call real MPI_Init - this will work if running under mpirun
            call try_mpi_init_real()
        else
            ierr = 1
            mpi_initialized = .false.
        endif
        
    end subroutine safe_mpi_init
    
    !> Try to detect MPI environment without calling MPI functions
    subroutine try_mpi_init_real()
        implicit none
        
        ! For manylinux compatibility, we can't call actual MPI functions
        ! Instead, we rely purely on environment variables set by mpirun/mpiexec
        
        if (mpi_available) then
            ! Assume MPI is successfully "initialized" if environment is detected
            ierr = 0
            mpi_initialized = .true.
            
            ! Get rank and size from environment variables
            call get_rank_from_env()
            call get_size_from_env()
        else
            ierr = 1
            mpi_initialized = .false.
        endif
        
    end subroutine try_mpi_init_real
    
    !> Get MPI rank from environment variables
    subroutine get_rank_from_env()
        implicit none
        character(len=32) :: rank_str
        integer :: status
        
        ! Try different MPI implementation environment variables (MPICH/OpenMPI)
        call get_environment_variable('PMI_RANK', rank_str, status)
        if (len_trim(rank_str) > 0) then
            read(rank_str, *, iostat=status) cpuid
            if (status == 0) return
        endif
        
        call get_environment_variable('OMPI_COMM_WORLD_RANK', rank_str, status)
        if (len_trim(rank_str) > 0) then
            read(rank_str, *, iostat=status) cpuid
            if (status == 0) return
        endif
        
        call get_environment_variable('MV2_COMM_WORLD_RANK', rank_str, status)
        if (len_trim(rank_str) > 0) then
            read(rank_str, *, iostat=status) cpuid
            if (status == 0) return
        endif

        call get_environment_variable('WT_RANK', rank_str, status)
        if (len_trim(rank_str) > 0) then
            read(rank_str, *, iostat=status) cpuid
            if (status == 0) return
        endif
        
        ! Default to 0 if can't determine
        cpuid = 0
        
    end subroutine get_rank_from_env
    
    !> Get MPI size from environment variables
    subroutine get_size_from_env()
        implicit none
        character(len=32) :: size_str
        integer :: status
        
        ! Try different MPI implementation environment variables (MPICH/OpenMPI)
        call get_environment_variable('PMI_SIZE', size_str, status)
        if (len_trim(size_str) > 0) then
            read(size_str, *, iostat=status) num_cpu
            if (status == 0) return
        endif
        
        call get_environment_variable('OMPI_COMM_WORLD_SIZE', size_str, status)
        if (len_trim(size_str) > 0) then
            read(size_str, *, iostat=status) num_cpu
            if (status == 0) return
        endif
        
        call get_environment_variable('MV2_COMM_WORLD_SIZE', size_str, status)
        if (len_trim(size_str) > 0) then
            read(size_str, *, iostat=status) num_cpu
            if (status == 0) return
        endif

        call get_environment_variable('WT_SIZE', size_str, status)
        if (len_trim(size_str) > 0) then
            read(size_str, *, iostat=status) num_cpu
            if (status == 0) return
        endif
        
        ! Default to 1 if can't determine
        num_cpu = 1
        
    end subroutine get_size_from_env
    
    !> Safe MPI rank detection - now redundant since we get rank in try_mpi_init_real
    subroutine safe_mpi_comm_rank()
        implicit none
        character(len=32) :: rank_str
        integer :: status
        
        if (.not. mpi_initialized) return
        
        ! If MPI was successfully initialized, rank should already be set
        ! But try environment variables as fallback (MPICH/OpenMPI)
        if (cpuid == 0) then
            call get_environment_variable('PMI_RANK', rank_str, status)
            if (status == 0) then
                read(rank_str, *, iostat=status) cpuid
                if (status == 0) return
            endif
            
            call get_environment_variable('OMPI_COMM_WORLD_RANK', rank_str, status)
            if (status == 0) then
                read(rank_str, *, iostat=status) cpuid
                if (status == 0) return
            endif
        endif
        
    end subroutine safe_mpi_comm_rank
    
    !> Safe MPI size detection - now redundant since we get size in try_mpi_init_real
    subroutine safe_mpi_comm_size()
        implicit none
        character(len=32) :: size_str
        integer :: status
        
        if (.not. mpi_initialized) return
        
        ! If MPI was successfully initialized, size should already be set
        ! But try environment variables as fallback (MPICH/OpenMPI)
        if (num_cpu == 1) then
            call get_environment_variable('PMI_SIZE', size_str, status)
            if (status == 0) then
                read(size_str, *, iostat=status) num_cpu
                if (status == 0) return
            endif
            
            call get_environment_variable('OMPI_COMM_WORLD_SIZE', size_str, status)
            if (status == 0) then
                read(size_str, *, iostat=status) num_cpu
                if (status == 0) return
            endif
        endif
        
    end subroutine safe_mpi_comm_size
    
    !> Finalize MPI if it was initialized
    subroutine try_finalize_mpi()
        implicit none
        
        if (mpi_initialized) then
            ! For manylinux compatibility, we don't call actual MPI_Finalize
            ! Just mark as not initialized
            mpi_initialized = .false.
            ierr = 0
        endif
        
    end subroutine try_finalize_mpi
    
    subroutine runtime_allreduce_real(local_array, global_array, dims)
        implicit none
        integer, intent(in) :: dims(2)
        real(dp), intent(in) :: local_array(dims(1), dims(2))
        real(dp), intent(out) :: global_array(dims(1), dims(2))
        
        ! Local variables
        real(dp), allocatable :: temp_array(:,:)
        character(len=20) :: rank_file
        integer :: other_rank, ios
        logical :: file_exists
        
        if (num_cpu <= 1) then
            global_array = local_array
            return
        endif
        
        ! Each process writes its results
        write(rank_file, '(a,i0,a)') 'rank_', cpuid, '.dat'
        open(unit=500+cpuid, file=rank_file, form='unformatted')
        write(500+cpuid) local_array
        close(500+cpuid)
        
        call sleep(1) ! Simple barrier
        
        if (cpuid == 0) then
            global_array = local_array
            allocate(temp_array(dims(1), dims(2)))
            
            do other_rank = 1, num_cpu - 1
                write(rank_file, '(a,i0,a)') 'rank_', other_rank, '.dat'
                inquire(file=rank_file, exist=file_exists)
                if (file_exists) then
                    open(unit=600, file=rank_file, form='unformatted', iostat=ios)
                    if (ios == 0) then
                        read(600) temp_array
                        close(600)
                        global_array = global_array + temp_array
                    endif
                endif
            enddo
            
            deallocate(temp_array)
            
            open(unit=700, file='final_result.dat', form='unformatted')
            write(700) global_array
            close(700)
            
            do other_rank = 0, num_cpu - 1
                write(rank_file, '(a,i0,a)') 'rank_', other_rank, '.dat'
                open(unit=800, file=rank_file, iostat=ios)
                if (ios == 0) close(unit=800, status='delete')
            enddo
        else
            do while (.true.)
                inquire(file='final_result.dat', exist=file_exists)
                if (file_exists) exit
                call sleep(1)
            enddo
            
            open(unit=700, file='final_result.dat', form='unformatted', iostat=ios)
            if (ios == 0) then
                read(700) global_array
                close(700)
            else
                global_array = local_array
            endif
        endif
        
        if (cpuid == 0) then
            call sleep(1)
            open(unit=700, file='final_result.dat', iostat=ios)
            if (ios == 0) close(unit=700, status='delete')
        endif
        
    end subroutine runtime_allreduce_real
    
end module runtime_mpi 