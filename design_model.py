import os
from time import strftime
import numpy as np 

from openmdao.main.api import Assembly, Component

from openmdao.lib.drivers.api import SLSQPdriver, NewtonSolver

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
        self.connect('fuse_weight.V_flight', ['wing_weight.V_flight','level.V', 'turning.V']) #flight speed

        #design Variables: 
        self.connect('wing_weight.cbar',['level.cbar','turning.cbar'])

        #multidisciplinary connection
        self.connect('fuse_weight.M_tot', 'wing_weight.M_pod')
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


 

        solver = self.add('solver', NewtonSolver())

        #state variables
        #solver.add_parameter('wing_weight.GM_guess', low=50, high=100)
        solver.add_parameter('level.alpha', low=0, high=5, start=3)
        solver.add_parameter('turning.alpha', low=0, high=10, start=3)
        #solver.add_parameter('wing_weight.s', low=30, high=110)

        #compatibility constraints
        #solver.add_constraint('(wing_weight.GM_guess - wing_weight.M_tot - fuse_weight.M_tot)/100 = 0')
        solver.add_constraint('(level.lift/9.81 - (wing_weight.M_tot + fuse_weight.M_tot))/2500 = 0 ')
        solver.add_constraint('(turning.lift/9.81 - (turning.load_factor * (wing_weight.M_tot + fuse_weight.M_tot)))/1200 = 0')
        #solver.add_constraint('(wing_weight.s/(wing_weight.M_tot + fuse_weight.M_tot) - .27)/.3 = 0')

        #optimizer constraints
        # solver.add_constraint('((wing_weight.GM_guess - wing_weight.M_tot - fuse_weight.M_tot)/100)**2 <  0.00001')
        # solver.add_constraint('((level.lift/9.81 - (wing_weight.M_tot + fuse_weight.M_tot))/2500)**2 < .00001  ')
        # solver.add_constraint('((turning.lift/9.81 - (turning.load_factor * (wing_weight.M_tot + fuse_weight.M_tot)))/1200) < 0.00001')

        opt = self.add('driver', SLSQPdriver())
        opt.add_parameter('wing_weight.cbar', low=.3, high=5)
        opt.add_parameter('wing_weight.b', low=5, high=100)
        opt.add_objective('level.drag')
        opt.add_constraint('level.Cl < 1.1')
        opt.add_constraint('(wing_weight.tip_deflection - 10)/30 < 0')
        opt.workflow.add('solver')


        #data_path = os.path.join('dw_day1', 'data_%s.bson'%strftime('%Y-%m-%d_%H.%M.%S'))
        data_path = os.path.join('dw_day1', 'ar_study.bson')
        self.recorders = [BSONCaseRecorder(data_path), ]

if __name__ == "__main__": 

    ma = MarathonAirplane()

    # for v in np.linspace(6,16,30): 
    #     ma.fuse_weight.N_pilot = 3
    #     ma.fuse_weight.N_propellor = 3
    #     ma.fuse_weight.V_flight = v
    #     ma.run()

    
    ma.wing_weight.cbar = .5
    ma.level.alpha = 3
    ma.wing_weight.b = 30

    ma.fuse_weight.N_pilot = 2
    ma.fuse_weight.N_propellor = 1

    ma.run()

    # for s in np.linspace(12,40,10): 
    #     #print ar 
    #     ma.wing_weight.s = s
    #     ma.run()

    #     #print repr([ma.wing_weight.AR, ma.wing_weight.b, ma.wing_weight.tbar, ma.wing_weight.M_tot, ma.wing_weight.M_s+ma.wing_weight.M_shearweb, (ma.level.drag*ma.level.V*1.2)/ma.fuse_weight.N_pilot]), ","
    #     print repr([ma.wing_weight.s, ma.wing_weight.b, ma.level.Cl , (ma.level.drag*ma.level.V*1.2)/ma.fuse_weight.N_pilot]), ","



    #ma.driver.run_iteration()

    #print ma.wing_weight.GM_guess - (ma.wing_weight.M_tot + ma.fuse_weight.M_tot)
    #print ma.level.lift, (ma.wing_weight.W_tot + ma.fuse_weight.W_tot), ma.level.lift - (ma.wing_weight.W_tot + ma.fuse_weight.W_tot)
    #print ma.turning.lift, ma.turning.lift - (ma.turning.load_factor * (ma.wing_weight.W_tot + ma.fuse_weight.W_tot))
    # print ma.wing_weight.s/(ma.wing_weight.M_tot + ma.fuse_weight.M_tot)
    # exit()

    print "Wing Span:", ma.wing_weight.b
    print "Wing Chord:", ma.wing_weight.cbar
    print "Wing Area: ", ma.wing_weight.s
    print "Wing AR: ", ma.wing_weight.AR
    print 
    print "tip deflection", ma.wing_weight.tip_deflection
    print "tip slope", ma.wing_weight.tip_slope
    print "Gross Mass: ", (ma.wing_weight.M_tot + ma.fuse_weight.M_tot)
    print "Empty Mass: ", (ma.wing_weight.M_tot + ma.fuse_weight.M_tot) - (ma.fuse_weight.N_pilot*ma.fuse_weight.M_pilot)
    print "level.Cl:", ma.level.Cl
    print "level.alpha:", ma.level.alpha
    print "level.Re", ma.level.Re

    print "tot power req per pilot:", (ma.level.drag*ma.level.V*1.1)/ma.fuse_weight.N_pilot
    print "watts/kg:", ma.level.drag*ma.level.V*1.1/(ma.fuse_weight.N_pilot*72)

    print "level.drag:", ma.level.drag
    print "turning.drag:", ma.turning.drag

