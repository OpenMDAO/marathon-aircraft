import numpy as np
from scipy.integrate import quad

from openmdao.main.api import Component

from openmdao.lib.datatypes.api import Float, Int


class WingWeight(Component): 

    #GM_guess = Float(30, iotype="in", units="kg", desc="gross weight guess")
    cbar = Float(.5, iotype="in", desc="average chord", units="m")
    b = Float(30,iotype="in", desc="Wing span",units="m")

    V_flight = Float(11.72, units="m/s", iotype="in", desc="design flight speed")
    V_gust = Float(2.8, units="m/s", iotype="in", desc="design wind gust speeds")

    N_wing_sections = Int(iotype="in", desc="number of individual wing section")
    t_cbar = Float(.13, iotype="in", desc="average t/c")
    
    M_pod = Float(72.4+8.164, iotype="in", desc="weight of each pilot pod", units="kg") 
    y_pod = Float(10, iotype="in", desc="weight of each pilot pod", units="m") 
    fos   = Float(2.3, iotype="in", desc="Factor of safety of spar", units="unitless") 

    #outputs
    AR = Float(units="unitless", iotype="out", desc="aspect ratio")
    s = Float(units="m**2", iotype="in", desc="wing area")
    tbar = Float(iotype="out", desc="average thickness", units="m")
    n_ult = Float(iotype="out", desc="ultimate load factor")
    N_r = Int(iotype="out", desc="number of ribs")
    N_er = Int (iotype="out", desc="number of end ribs")
    delta = Float(iotype="out", desc="average rib spacing to average chord ratio",units="unitless")
    M_s = Float(iotype="out", desc="mass of spar", units="kg")
    M_r = Float(iotype="out", desc="mass of ribs", units="kg")
    M_er = Float(iotype="out", desc="mass of end-ribs", units="kg")
    M_le = Float(iotype="out", desc="mass of the leading edge", units="kg")
    M_te = Float(iotype="out", desc="mass of the trailing edge", units="kg")
    M_cover = Float(iotype="out", desc="mass of surface covering for control surfaces", units="kg")
    M_shearweb = Float(iotype="out", desc="mass of the shear web for the spar", units="kg")


    M_tot = Float(iotype="out", desc="total combined wing weight", units="kg")
    tip_deflection = Float(iotype="out", desc="deflection at the tip", units="m")
    tip_slope = Float(iotype="out", desc="change in deflection w.r.t span at the tip", units="unitless")

    def execute(self): 

        self.n_ult = (self.V_flight+self.V_gust)**2/self.V_flight**2

        self.N_er = 2*self.N_wing_sections
        #self.b = (self.AR*self.s)**0.5
        self.s = self.b*self.cbar
        self.AR = self.b**2/self.s
        #self.cbar = self.s/self.b
        self.tbar = self.t_cbar*self.cbar
        self.N_r = int(np.floor(self.b*3.28)) # 1 every foot
        self.delta = self.b/self.N_r/self.cbar
        
        # Deadalus Empirical Cantilevered
        # self.M_s = (self.b*1.17e-1 + self.b**2*1.10e-2)*(1.0+(self.n_ult*self.GM_guess/100.0-2.0)/4.0)
        # One wire
        #self.M_s = (self.b*3.10e-2 + self.b**2*7.56e-3)*(1.0+(self.n_ult*self.GM_guess/100.0-2.0)/4.0)
        # two wire
        #self.M_s = (self.b*1.35e-1 + self.b**2*1.68e-3)*(1.0+(self.n_ult*self.GM_guess/100.0-2.0)/4.0)
        
        w_pc = self.M_pod*9.81
        w_ps = 0*self.M_pod*9.81
        l1 = self.y_pod
        l2 = self.b /2 - l1

        p_wing = (w_pc/2 + w_ps)/(l1+l2)
        rho = 1580.6 #NCT301,HS40 carbon
        sig_max = 1.0204e9/self.fos #NCT301,HS40 carbon with FOS applied (deadalus was ~2.3)
        E = 2.3028e11 #NCT301, HS40 carbon

        # these are constants defined to make calcs easier
        a1 = -p_wing
        b1 = w_pc/2
        a2 = -p_wing
        b2 = w_ps
        d2 = -a2*l2-b2
        d1 = -a1*l1-b1+d2
        e2 = -a2/2*l2**2-(b2+d2)*l2
        e1 = -a1/2*l1**2-(b1+d1)*l1+e2

        #def m1(y):
        #    return a1/2*y**2+(b1+d1)*y+e1

        #def m2(y):
        #    return a2/2*y**2+(b2+d2)*y+e2
    
        def m1int(y):
            return a1/6*y**3+(b1+d1)/2*y**2+e1*y
        
        def m2int(y):
            return a2/6*y**3+(b2+d2)/2*y**2+e2*y

        self.M_s = 4*rho/(self.tbar*sig_max)*(np.abs(m1int(self.y_pod)-m1int(0))+np.abs(m2int(l2)-m2int(0)))
        self.tip_deflection = sig_max*(self.b/2)**2/(E*self.tbar)
        self.tip_slope = 2*sig_max*(self.b/2)/(E*self.tbar)

        # Deadalus estimates
        self.M_r = self.N_r*(self.cbar**2*self.t_cbar*5.50e-2+self.cbar*1.91e-3)
        self.M_er = self.N_er*(self.cbar**2*self.t_cbar*6.62e-1+self.cbar*6.57e-3)
        #self.M_le = 0.456*(self.s**2*self.delta**(4/3)/self.b)
        #self.M_te = self.b*2.77e-2
        
        # Muscular skin estimate with DAE11 airfoil
        self.M_cover = self.s*2.061*0.212 # muscular skin estimate with DAE11 airfoil
        self.M_shearweb = self.b*self.tbar*0.550
        
        self.M_tot = (self.M_s + self.M_r + self.M_er + self.M_cover + self.M_shearweb)


class FuseWeight(WingWeight):

    V_flight = Float(11.72, units="m/s", iotype="in", desc="design flight speed")
    V_gust = Float(2.8, units="m/s", iotype="in", desc="design wind gust speeds")
    rho = Float(1.1, iotype="in", units="kg/m**3", desc="density of air")

    L_tailboom = Float(3.2, iotype="in", desc="length of tailboom")

    N_pilot = Int(3, iotype="in", desc="number of pilots")
    N_propellor = Int(3,iotype="in", desc="number of pilots")
    N_pod = Int(3, iotype="in", desc="number of fared pods")

    M_pilot = Float(72.4+8.164, iotype="in", desc="weight per pilot") #8.164 kg of stuff per pilot
    M_propellor  = Float(2.512, iotype="in", desc="weight per propellor")
    M_pod  = Float(3.499, iotype="in", desc="weight per pilot pod")

    q_max = Float(iotype="out", desc="manoeuvring speed dynamic pressure")
    M_tailboom = Float(iotype="out", desc="weight of tailboom", units="kg")
    M_pilots = Float(iotype="out", desc="weight of pilots", units="kg")
    
    def execute(self):

        self.s = self.b*self.cbar
        self.AR = self.b**2/self.s

        self.q = .5*self.rho*(self.V_flight+self.V_gust)
        self.b = (self.AR*self.s)**0.5
        self.cbar = self.s/self.b
        self.N_r = int(np.floor(self.b*3.28)) # 1 every foot
        self.delta = self.b/self.N_r/self.cbar

        self.M_s = (self.b*4.15e-2 + self.b**2*3.91e-3)*(1.0+((self.q_max*self.s)/78.5-1.0)/2.0)
        
        self.M_r = self.N_r*(self.cbar**2*self.t_cbar*1.16e-1+self.cbar*4.01e-3)
        self.M_le = 0.174*(self.s**2*self.delta**(4/3)/self.b)
        self.M_cover = self.s*1.93e-2
        
        self.M_tailboom = (self.L_tailboom*1.14e-1+self.L_tailboom**2*1.96e-2)*(1.0+((self.q_max*self.s)/78.5-1.0)/2.0)
        self.M_pilots = self.N_pilot*self.M_pilot
        self.M_tot = (self.M_s + self.M_r + self.M_le + self.M_cover + self.M_tailboom + \
                     self.M_pilots + self.N_pod*self.M_pod  + self.N_propellor*self.M_propellor)


if __name__ == "__main__": 
    import numpy as np
    from matplotlib import pyplot as plt

    w_pc = 70*9.81
    w_ps = 70*9.81
    fos = 2
    l1 = 5
    l2 = 55
    p_wing = (w_pc/2 + w_ps)/(l1+l2)
    rho = 1580.6 #NCT301,HS40 carbon
    t = 0.7*0.14
    sig_max = 1.0204e9/fos #NCT301,HS40 carbon with FOS applied

    # these are constants defined to make calcs easier
    a1 = -p_wing
    b1 = w_pc/2
    a2 = -p_wing
    b2 = w_ps
    d2 = -a2*l2-b2
    d1 = -a1*l1-b1+d2
    e2 = -a2/2*l2**2-(b2+d2)*l2
    e1 = -a1/2*l1**2-(b1+d1)*l1+e2

    def m1(y):
        return a1/2*y**2+(b1+d1)*y+e1

    def m2(y):
        return a2/2*y**2+(b2+d2)*y+e2
    
    def m1int(y):
        return a1/6*y**3+(b1+d1)/2*y**2+e1*y
        
    def m2int(y):
        return a2/6*y**3+(b2+d2)/2*y**2+e2*y
        
    sparmass = 2*rho/(t*sig_max)*(m1int(l1)-m1int(0)+m2int(l2)-m2int(0))
    repr(sparmass)
        
    Y = np.linspace(0,l1,50)
    M = m1(Y)
    plt.plot(Y,M)

    Y = np.linspace(0,l2,50)
    M = m2(Y)
    plt.plot(l1+Y,M)

    plt.show()
    #y = 0 -> l1
    #y = 0 -> l2
    