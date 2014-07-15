import os
from time import strftime
import numpy as np 

from openmdao.main.api import Assembly, Component

from openmdao.lib.drivers.api import COBYLAdriver, NewtonSolver

from openmdao.lib.casehandlers.api import BSONCaseRecorder


from weights import WingWeight, FuseWeight
from aero import Aero


class MarathonAirplane(Assembly): 


    def configure(self): 
        

        self.add('wing_weight', WingWeight())
        self.add('fuse_weight', FuseWeight())

        self.add('level', Aero())
        self.level.Cd_a = 3*.015

        self.add('turning', Aero())
        self.level.Cd_a = 6*.015
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


        self.wing_weight.s = 100
        self.wing_weight.AR = 30
        self.wing_weight.t_cbar = .13
        self.fuse_weight.s = 6 #tail
        self.fuse_weight.AR = 10 #tail
        self.level.alpha = 1
        self.turning.alpha = 3
        self.fuse_weight.N_pilot = 3
        self.fuse_weight.N_propellor = 3


        driver = self.add('driver', COBYLAdriver())
        driver.add_parameter('wing_weight.s', low=20, high=150)
        driver.add_parameter('wing_weight.AR', low=5, high=50)
        driver.add_objective('level.drag')
        driver.add_constraint('level.alpha < 12')
        solver = self.add('solver', NewtonSolver())

        #state variables
        solver.add_parameter('wing_weight.GM_guess', low=50, high=100)
        solver.add_parameter('level.alpha', low=0, high=5, start=3)
        solver.add_parameter('turning.alpha', low=0, high=10, start=3)
        #solver.add_parameter('wing_weight.s', low=30, high=110)

        #compatibility constraints
        solver.add_constraint('(wing_weight.GM_guess - wing_weight.M_tot - fuse_weight.M_tot)/100 = 0')
        solver.add_constraint('(level.lift/9.81 - (wing_weight.M_tot + fuse_weight.M_tot))/2500 = 0 ')
        solver.add_constraint('(turning.lift/9.81 - (turning.load_factor * (wing_weight.M_tot + fuse_weight.M_tot)))/1200 = 0')
        #solver.add_constraint('(wing_weight.s/(wing_weight.M_tot + fuse_weight.M_tot) - .27)/.3 = 0')

        #optimizer constraints
        # solver.add_constraint('((wing_weight.GM_guess - wing_weight.M_tot - fuse_weight.M_tot)/100)**2 <  0.00001')
        # solver.add_constraint('((level.lift/9.81 - (wing_weight.M_tot + fuse_weight.M_tot))/2500)**2 < .00001  ')
        # solver.add_constraint('((turning.lift/9.81 - (turning.load_factor * (wing_weight.M_tot + fuse_weight.M_tot)))/1200) < 0.00001')

        driver.workflow.add('solver')
        #solver.workflow.add(['wing_weight','fuse_weight','level','turning'])

        #data_path = os.path.join('dw_day1', 'data_%s.bson'%strftime('%Y-%m-%d_%H.%M.%S'))
        data_path = os.path.join('dw_day1', 'pilot_study.bson')
        self.recorders = [BSONCaseRecorder(data_path), ]

if __name__ == "__main__": 

    ma = MarathonAirplane()

    # for v in np.linspace(6,16,30): 
    #     ma.fuse_weight.N_pilot = 3
    #     ma.fuse_weight.N_propellor = 3
    #     ma.wing_weight.V_flight = v
    #     ma.run()

    #     print repr([ma.wing_weight.V_flight, ma.wing_weight.s, ma.wing_weight.M_tot, ma.fuse_weight.M_tot, ma.fuse_weight.M_pilots, ma.wing_weight.s, (ma.level.drag*ma.level.V*1.1), ma.level.drag*ma.level.V*1.1/(3*72)]), ","

    for i in range(1,6):
        ma.wing_weight.s = 50
        ma.level.alpha = 9
        ma.fuse_weight.N_pilot = i
        ma.fuse_weight.N_propellor = 1
        ma.run()

        print repr([ma.wing_weight.s, ma.wing_weight.AR, ma.wing_weight.b, ma.level.alpha, (ma.level.drag*ma.level.V*1.1)/ma.fuse_weight.N_pilot, ma.level.drag*ma.level.V*1.1/(ma.fuse_weight.N_pilot*72)]), ","



    #ma.driver.run_iteration()

    #print ma.wing_weight.GM_guess - (ma.wing_weight.M_tot + ma.fuse_weight.M_tot)
    #print ma.level.lift, (ma.wing_weight.W_tot + ma.fuse_weight.W_tot), ma.level.lift - (ma.wing_weight.W_tot + ma.fuse_weight.W_tot)
    #print ma.turning.lift, ma.turning.lift - (ma.turning.load_factor * (ma.wing_weight.W_tot + ma.fuse_weight.W_tot))
    # print ma.wing_weight.s/(ma.wing_weight.M_tot + ma.fuse_weight.M_tot)
    # exit()

    print "Gross Mass: ", (ma.wing_weight.M_tot + ma.fuse_weight.M_tot)
    print "level.drag:", ma.level.drag
    print "level.alpha:", ma.level.alpha
    print "turning.drag:", ma.turning.drag
    print "power req per pilot:", (ma.level.drag*ma.level.V*1.1)/ma.fuse_weight.N_pilot
    print "watts/kg:", ma.level.drag*ma.level.V*1.1/(ma.fuse_weight.N_pilot*72)
    print "wing average chord:", ma.wing_weight.cbar
