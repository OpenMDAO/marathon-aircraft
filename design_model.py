from openmdao.main.api import Assembly, Component

from openmdao.lib.drivers.api import NewtonSolver


from weights import WingWeight, FuseWeight
from aero import Aero


class MarathonAirplane(Assembly): 


    def configure(self): 

        self.add('wing_weight', WingWeight())
        self.add('fuse_weight', FuseWeight())

        self.add('level', Aero())
        self.level.Cd_a = 3*.015

        self.add('turning', Aero())
        self.turning.R_0 = 92 #turning radius


        # self.add('propellor_level', Propulsion())
        # self.add('propellor_turning', Propulsion())

        # self.add('drive_train', DriveTrain())
        # self.add('engine', Human())

        #Global Variables
        self.connect('level.Cd_a', 'turning.Cd_a')
        self.connect('fuse_weight.rho', ['level.rho', 'turning.rho']) #air density 
        self.connect('wing_weight.V_flight', ['fuse_weight.V_flight','level.V', 'turning.V']) #flight speed

        #design Variables: 
        self.connect('wing_weight.s', ['level.s', 'turning.s'])
        self.connect('wing_weight.AR', ['level.AR', 'turning.AR'])


        self.wing_weight.s = 90
        self.wing_weight.AR = 40
        self.fuse_weight.s = 6 #tail
        self.fuse_weight.AR = 10 #tail
        self.level.alpha = 1
        self.turning.alpha = 3


        self.add('driver', NewtonSolver())

        #state variables
        self.driver.add_parameter('wing_weight.GW_guess', low=50, high=100, start=60)
        self.driver.add_parameter('level.alpha', low=0, high=10, start=3)
        self.driver.add_parameter('turning.alpha', low=0, high=10, start=3)

        #compatibility constraints
        self.driver.add_constraint('(wing_weight.GW_guess - wing_weight.W_tot - fuse_weight.W_tot)/3500 = 0')
        self.driver.add_constraint('(level.lift - (wing_weight.W_tot + fuse_weight.W_tot))/2500 = 0 ')
        self.driver.add_constraint('(turning.lift - (turning.load_factor * (wing_weight.W_tot + fuse_weight.W_tot)))/1200 = 0')

        self.driver.workflow.add(['wing_weight','fuse_weight','level','turning'])

        

if __name__ == "__main__": 

    ma = MarathonAirplane()

    ma.run()

    #ma.driver.run_iteration()

    print ma.wing_weight.GW_guess - (ma.wing_weight.W_tot + ma.fuse_weight.W_tot)
    print ma.level.lift, (ma.wing_weight.W_tot + ma.fuse_weight.W_tot), ma.level.lift - (ma.wing_weight.W_tot + ma.fuse_weight.W_tot)
    print ma.turning.lift, ma.turning.lift - (ma.turning.load_factor * (ma.wing_weight.W_tot + ma.fuse_weight.W_tot))

    #exit()

    print "Gross Weight: ", (ma.wing_weight.W_tot + ma.fuse_weight.W_tot)/9.81
    print "Empty Weight: ", (ma.wing_weight.W_tot + ma.fuse_weight.W_tot)/9.81 - 
    print "level.drag:", ma.level.drag
    print "level.alpha:", ma.level.alpha
    print "turning.drag:", ma.turning.drag
    print "power req:", ma.level.drag*ma.level.V*1.1
    print "watts/kg:", ma.level.drag*ma.level.V*1.1/(3*72)
