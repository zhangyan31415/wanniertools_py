subroutine stop_wannier_tools(exit_code, message)
    use iso_c_binding
    implicit none
    integer(c_int), intent(in) :: exit_code
    character(kind=c_char, len=*), intent(in) :: message
    
    write(*,*) 'FATAL ERROR:', message
    call exit(exit_code)
end subroutine stop_wannier_tools 