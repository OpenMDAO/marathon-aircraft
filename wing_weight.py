from openmdao.main.api import Component

from openmdao.lib.datatypes.api import Float


class WingWeight(Component): 

    GW_guess = Float(20, iotype="in", units="kg", desc="gross weight guess")

    s = Float(90, units="m**2", iotype="in", desc="wing area")
    AR = Float(20, units="unitless", iotype="in", desc="aspect ratio")

    n_ult = Float(2, iotype="in", desc="ultimate load factor")

    N_r =Float(iotype="in", desc="number of ribs")
    N_wing_sections = Float(iotype="in", desc="number of individual wing section")
	cbar = Float(iotype="in", desc="average chord")
	t_cbar = Float(iotype="in", desc="average t/c")
    
    #outputs
	N_r =Float(iotype="out", desc="number of ribs", units="kg")
    N_er =Float(iotype="out", desc="number of end ribs", units="kg")
	b     = Float(iotype="out", desc="Wing span",units="m")
	delta = Float(iotype="out", desc="average rib spacing to average chord ratio",units="unitless")
    W_s = Float(iotype="out", desc="weight of spar", units="kg")
    W_r = Float(iotype="out", desc="weight of ribs", units="kg")
    W_er = Float(iotype="out", desc="weight of end-ribs", units="kg")
    W_le = Float(iotype="out", desc="weight of the leading edge", units="kg")
    W_te = Float(iotype="out", desc="weight of the trailing edge", units="kg")
    W_cover = Float(iotype="out", desc="weight of surface covering", units="kg")

    W_tot = Float(iotype="out", desc="total combined wing weight", units="kg")

    def execute(self): 

        self.N_er = 2*self.N_wing_panels
		self.b = (self.AR*self.s)**0.5
		self.delta = self.span/self.N_r/self.cbar
		
		# Cantilevered
		self.W_s = (self.b*1.17e-1 + self.b**2*1.10e-2)*(1.0+(self.GW_guess/100.0-2.0)/4.0)
		# One wire
		#self.W_s = (self.b*3.10e-2 + self.b**2*7.56e-3)*(1.0+(self.GW_guess/100.0-2.0)/4.0)
		# two wire
		#self.W_s = (self.b*1.35e-1 + self.b**2*1.68e-3)*(1.0+(self.GW_guess/100.0-2.0)/4.0)
        
		self.W_r = self.N_r*(self.cbar**2*self.t_cbar*5.50e-2+self.cbar*1.91e-3)
		self.W_er = self.N_er*(self.cbar**2*self.t_cbar*6.62e-1+self.cbar*6.57e-3)
		slef.W_le = 0.456*(self.s**2*self.delta**(4/3)/self.b)
		self.W_te = self.b*2.77e-2
		self.W_cover = self.s*3.08e-2
		
		self.W_tot = self.W_s + self.W_r + self.W_er + self.W_le + self.W_te + self.W_cover
		
	