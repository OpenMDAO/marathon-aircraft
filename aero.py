from numpy import pi
import numpy as np
from scipy.interpolate import interp1d

from openmdao.main.api import Component

from openmdao.lib.datatypes.api import Float


#DEA11 Airfoil drag polar data taken from Deadauls paper

Cl = [0,      .662,   .735,   .771,   .874,   1.02,  1.27,  1.37,  1.47,  1.54,  1.56,  1.58,  1.59, 1.59]
Cd = [.0012, .0112, .0103, .00928, .00939, .00965, .0102, .0107, .0114, .0130, .0145, .0160, .0179, .0196]
Cd_interp = interp1d(Cl, Cd, bounds_error=False)

class Aero(Component): 

    s = Float(90, units="m**2", iotype="in", desc="wing area")
    AR = Float(20, units="unitless", iotype="in", desc="aspect ratio")
    e = Float(.97, units="unitless", iotype="in", desc="span efficiency factor")
    V = Float(11.72 , units="m/s", iotype="in", desc="flight speed")
    R_0 = Float(float("inf"), units="m", iotype="in", desc="turning radius")
    rho = Float(1.1, iotype="in", units="kg/m**3", desc="density of air")

    alpha = Float(2, units="deg", iotype="in", desc="angle of attack")

    Cd_a = Float(.001, units="unitless", iotype="in", desc="parasitic drag coefficient * area")

    Cl = Float(iotype="out", units="unitless", desc="Lift Coefficient")
    Cd_prof = Float(iotype="out", units="unitless", desc="profile Drag Coefficient")
    Cd_i = Float(iotype="out", units="unitless", desc="induced Drag Coefficient")
    
    lift = Float(iotype="out", units="N", desc="Total lift")
    drag = Float(iotype="out", units="N", desc="Total drag")
    load_factor = Float(iotype="out", units="unitless", desc="load factor")

    def execute(self): 

        self.Cl = 2*pi*self.alpha*pi/180.
        self.Cd = Cd_interp(self.Cl)

        self.Cd_i = self.Cl**2 / (pi*self.e*self.AR)
        Cd_tot = self.Cd + self.Cd_i 

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


