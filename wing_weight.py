from openmdao.main.api import Component

from openmdao.lib.datatypes.api import Float


class WingWeight(Component): 

    GW_guess = Float(20, iotype="in", units="kg", desc="gross weight guess")

    s = Float(90, units="m**2", iotype="in", desc="wing area")
    AR = Float(20, units="unitless", iotype="in", desc="aspect ratio")

    n_ult = Float(2, iotype="in", desc="ultimate load factor")

    N_r =Float(iotype="in", desc="number of ribs")
    N_wing_sections = Float(iotype="in", desc="number of individual wing section")
    
    #outputs
    N_er =Float(iotype="out", desc="number of end ribs", units="kg")

    W_s = Float(iotype="out", desc="weight of spar", units="kg")
    W_r = Float(iotype="out", desc="weight of ribs", units="kg")
    W_er = Float(iotype="out", desc="weight of end-ribs", units="kg")
    W_le = Float(iotype="out", desc="weight of the leading edge", units="kg")
    W_te = Float(iotype="out", desc="weight of the trailing edge", units="kg")
    W_cover = Float(iotype="out", desc="weight of surface covering", units="kg")

    W_tot = Float(iotype="out", desc="total combined wing weight", units="kg")

    def execute(self): 

        self.N_er = 2*self.N_wing_panels

        self.W_tot = self.W_s + self.W_r + self.W_er + self.W_le + self.W_te + self.W_cover