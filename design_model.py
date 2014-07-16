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

        self.fuse_weight.b = 7
        self.fuse_weight.cbar = .7

        self.level.alpha = 1
        self.turning.alpha = 3
        self.fuse_weight.N_pilot = 3
        self.fuse_weight.N_propellor = 3

        solver = self.add('solver', NewtonSolver())

        #state variables
        solver.add_parameter('level.alpha', low=0, high=5, start=3)
        solver.add_parameter('turning.alpha', low=0, high=10, start=3)

        #compatibility constraints
        solver.add_constraint('(level.lift/9.81 - (wing_weight.M_tot + fuse_weight.M_tot))/2500 = 0 ')
        solver.add_constraint('(turning.lift/9.81 - (turning.load_factor * (wing_weight.M_tot + fuse_weight.M_tot)))/1200 = 0')

        #optimizer constraints
        # solver.add_constraint('((wing_weight.GM_guess - wing_weight.M_tot - fuse_weight.M_tot)/100)**2 <  0.00001')
        # solver.add_constraint('((level.lift/9.81 - (wing_weight.M_tot + fuse_weight.M_tot))/2500)**2 < .00001  ')

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

    
    ma.wing_weight.cbar = .5
    ma.level.alpha = 3
    ma.wing_weight.b = 30

    ma.fuse_weight.N_pilot = 3
    ma.fuse_weight.N_propellor = 1

    ma.run()

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

