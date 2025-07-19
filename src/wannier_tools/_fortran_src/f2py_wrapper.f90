!> Python wrapper for WannierTools main program
!> This module provides Python interface to WannierTools calculations

module wannier_tools_wrapper
    use iso_c_binding
    implicit none
    
contains

    !> Main interface function to run WannierTools calculation
    subroutine run_wannier_tools() bind(c, name='run_wannier_tools')
        implicit none
        
        ! Call the main WannierTools subroutine
        call wannier_tools_run()
        
    end subroutine run_wannier_tools

    !> Test function to verify module is working
    subroutine test_function(result) bind(c, name='test_function')
        implicit none
        integer(c_int), intent(out) :: result
        result = 42
        print *, 'WannierTools Python wrapper test: OK'
    end subroutine test_function

end module wannier_tools_wrapper 