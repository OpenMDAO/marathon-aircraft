import os
from time import strftime

from openmdao.main.api import Assembly, Component

from openmdao.lib.drivers.api import NewtonSolver

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


        self.wing_weight.s = 30
        self.wing_weight.AR = 30
        self.wing_weight.t_cbar = .13
        self.fuse_weight.s = 6 #tail
        self.fuse_weight.AR = 10 #tail
        self.level.alpha = 1
        self.turning.alpha = 3
        self.fuse_weight.N_pilot = 1
        self.fuse_weight.N_propellor = 1


        self.add('driver', NewtonSolver())

        #state variables
        self.driver.add_parameter('wing_weight.GM_guess', low=50, high=100)
        self.driver.add_parameter('level.alpha', low=0, high=10, start=3)
        self.driver.add_parameter('turning.alpha', low=0, high=10, start=3)
        self.driver.add_parameter('wing_weight.s', low=30, high=110)

        #compatibility constraints
        self.driver.add_constraint('(wing_weight.GM_guess - wing_weight.M_tot - fuse_weight.M_tot)/100 = 0')
        self.driver.add_constraint('(level.lift/9.81 - (wing_weight.M_tot + fuse_weight.M_tot))/2500 = 0 ')
        self.driver.add_constraint('(turning.lift/9.81 - (turning.load_factor * (wing_weight.M_tot + fuse_weight.M_tot)))/1200 = 0')
        self.driver.add_constraint('(wing_weight.s/(wing_weight.M_tot + fuse_weight.M_tot) - .3)/.3 = 0')

        self.driver.workflow.add(['wing_weight','fuse_weight','level','turning'])

        data_path = 'bug1.bson'
        self.recorders = [BSONCaseRecorder(data_path), ]

if __name__ == "__main__": 


    from openmdao.lib.casehandlers.api import CaseDataset
    ma = MarathonAirplane()

    ma.fuse_weight.N_pilot = 1
    ma.fuse_weight.N_propellor = 1
    ma.run()

    print ma.wing_weight.s

    ma.fuse_weight.N_pilot = 2
    ma.fuse_weight.N_propellor = 2
    ma.run()    

    print ma.wing_weight.s


    ma.fuse_weight.N_pilot = 3
    ma.fuse_weight.N_propellor = 3
    ma.run()  

    print ma.wing_weight.s
    #THIS IS NOT properly recording the data from the runs

    cds = CaseDataset('bug1.bson', 'bson')

    data = cds.data.by_variable().fetch()

    #I asked for all variables, so I should get all variables, but this errors
    print data['wing_weight.s']




