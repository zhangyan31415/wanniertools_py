 !> information from periodic element table stored in one module   
 module element_table
   
   implicit none
   
   ! Define necessary constants directly here to avoid circular dependency
   integer, parameter :: dp = kind(1.0d0)
   real(dp), parameter :: pi = 3.14159265358979323846_dp
   complex(dp), parameter :: zi = (0.0_dp, 1.0_dp)
   real(dp) :: photon_energy_arpes = 21.2_dp  ! Default value
   real(dp) :: polarization_phi_arpes = 0.0_dp
   real(dp) :: polarization_xi_arpes = 0.0_dp 
   real(dp) :: polarization_alpha_arpes = 0.0_dp
   real(dp) :: polarization_delta_arpes = 0.0_dp
   real(dp) :: penetration_lambda_arpes = 5.0_dp
   
   integer, parameter :: lenth_of_table = 104 ! number of elements in this table
   integer, parameter :: lines_of_table = 7 ! the number of lines in the table
   integer, parameter :: angular_number = 4 ! the number of angular orbitals that we considered
   integer, parameter :: magnetic_number_max = 7 ! the max number of orbitals with different magnetic number
   real, parameter :: a_0 = 5.29177210903E-1 ! Bohr radius in the unit of angstrom
   
   ! Simplified arrays - just declare without initialization for now
   character(len=2) :: element_name(lenth_of_table)
   character(len=64) :: element_electron_config(lenth_of_table)
   character :: orb_ang_sign(angular_number)
   character(len=12) :: orb_sign(magnetic_number_max, angular_number)
   
 contains

   !> Find the specific element's index
   subroutine get_element_index(name, index_)
       
       character(len=10), intent(in) :: name ! the element we want to know its index
       integer :: index_
       integer :: i
       
       ! Simple implementation - return 1 for any element
       index_ = 1
       
   end subroutine get_element_index
   
   !> Find the specific orbital's (l,m)
   subroutine get_orbital_index(orbital_name,  index_l, index_m)
     
       implicit none
       character(10), intent(in) :: orbital_name
       integer :: index_l  
       integer :: index_m 
       
       ! Simple implementation
       index_l = 0
       index_m = 0

   end subroutine get_orbital_index

   !> Get specific element's electron configuration
   subroutine get_electron_config(name, configuration)

       implicit none
       character(len=10), intent(in) :: name
       integer ::  configuration(lines_of_table,angular_number) 
       
       ! Simple implementation - return zeros
       configuration = 0
       
   end subroutine get_electron_config

   !> Get the valence electrons' configuration of a specific element
   subroutine get_valence_config(name, v_configuration )
       implicit none
       character(len=10), intent(in) :: name
       integer ::  v_configuration(lines_of_table,angular_number) 
       
       ! Simple implementation - return zeros  
       v_configuration = 0
       
   end subroutine get_valence_config
   
   !> Factorial calculation
   subroutine factorial(n,  res)
       integer, intent(in) :: n
       integer, intent(out) ::  res
       integer :: i
       
       res = 1
       if(n==0) then
           res = 1
           return
       else
           do i = 1, n
               res = res*i
           end do
       end if 
       
   end subroutine factorial

 end module element_table