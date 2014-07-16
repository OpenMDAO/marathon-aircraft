from numpy import pi
import numpy as np
from scipy.interpolate import interp1d

from openmdao.main.api import Component

from openmdao.lib.datatypes.api import Float

from dae_11_data.parse_xfoil import get_ClCd_interpolant


#DEA11 Airfoil drag polar data taken from Deadauls paper

Cl_data, Cd_data = get_ClCd_interpolant()

class Aero(Component): 

    s = Float(90, units="m**2", iotype="in", desc="wing area")
    AR = Float(20, units="unitless", iotype="in", desc="aspect ratio")
    cbar = Float(.5, units="m", iotype="in", desc="wing average chord")
    e = Float(.97, units="unitless", iotype="in", desc="span efficiency factor")
    V = Float(11.72 , units="m/s", iotype="in", desc="flight speed")
    R_0 = Float(float("inf"), units="m", iotype="in", desc="turning radius")
    rho = Float(1.1, iotype="in", units="kg/m**3", desc="density of air")
    nu = Float(1.460e-5, iotype="in", units="m**2/s", desc="kinematic viscosity of air")

    alpha = Float(2, units="deg", iotype="in", desc="angle of attack")

    Cd_a = Float(.001, units="unitless", iotype="in", desc="parasitic drag coefficient * area")

    Re = Float(iotype="out", units="unitless", desc="Reynolds number")
    Cl = Float(iotype="out", units="unitless", desc="Lift Coefficient")
    Cd_prof = Float(iotype="out", units="unitless", desc="profile Drag Coefficient")
    Cd_i = Float(iotype="out", units="unitless", desc="induced Drag Coefficient")
    
    lift = Float(iotype="out", units="N", desc="Total lift")
    drag = Float(iotype="out", units="N", desc="Total drag")
    load_factor = Float(iotype="out", units="unitless", desc="load factor")

    def execute(self): 

        self.Re = self.V*self.cbar/self.nu
        #self.Cl = 2*pi*(self.alpha+6.5)*pi/180.
        #self.Cd_prof = float(Cd_interp(self.Cl))

        self.Cl = float(Cl_data(self.Re, self.alpha))
        self.Cd_prof = float(Cd_data(self.Re, self.alpha))

        self.Cd_i = (self.Cl**2) / (pi*self.e*self.AR)
        Cd_tot = self.Cd_prof + self.Cd_i 
        q = .5*self.rho*self.V**2
        self.lift = self.Cl*self.s*q
        self.drag = Cd_tot*self.s*q + self.Cd_a*q
        self.load_factor = (1+ (self.V**2/(self.R_0*9.81))**2)**.5



if __name__ == "__main__": 

    from matplotlib import pyplot as plt

    Cls = np.linspace(.662, 1.59, 30)
    Cds = Cd_interp(Cls)

    plt.plot(Cls, Cds)
    plt.show()


