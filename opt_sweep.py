import os
from time import strftime
import numpy as np 

from openmdao.main.api import Assembly, Component
from openmdao.lib.drivers.api import CaseIteratorDriver, SLSQPdriver, NewtonSolver
from openmdao.lib.casehandlers.api import BSONCaseRecorder

from weights import WingWeight, FuseWeight
from aero import Aero

from marathon_airplane import MarathonAirplane

class InitGuessHack(Component): 

    def execute(self):
        self.parent.wing_weight.b = 30

class SweepOpt(MarathonAirplane): 
    """Run across a set of parameters and re-optimize for each one""" 

    def configure(self): 

        super(SweepOpt, self).configure()

        self.add('init', InitGuessHack())

        opt = self.add('opt', SLSQPdriver())
        opt.add_parameter('wing_weight.cbar', low=.3, high=5)
        opt.add_parameter('wing_weight.b', low=5, high=100)
        opt.add_parameter('wing_weight.fos', low=2.3, high=4)
        opt.add_parameter('wing_weight.y_pod', low=0, high=15) #spanwise location of the outboard pods
        opt.add_objective('level.drag')
        opt.add_constraint('level.Cl < 1.1')
        #opt.add_constraint('wing_weight.tip_slope - .1 < 0')
        
        #IDF 
        #state variables
        opt.add_parameter('level.alpha', low=0, high=5, start=3)
        opt.add_parameter('turning.alpha', low=0, high=10, start=3)
        #compatibility constraints
        opt.add_constraint('(level.lift/9.81 - (wing_weight.M_tot + fuse_weight.M_tot))/2500 = 0 ')
        opt.add_constraint('(turning.lift/9.81 - (turning.load_factor * (wing_weight.M_tot + fuse_weight.M_tot)))/1200 = 0')

        sweep = self.add('driver', CaseIteratorDriver())
        sweep.workflow.add(['init','opt'])
        sweep.add_parameter('fuse_weight.N_pilot')


if __name__ == "__main__": 
    

    ma = SweepOpt()

    # ma.fuse_weight.N_pilot = 3
    # ma.fuse_weight.N_propellor = 1

    ma.driver.case_inputs.fuse_weight.N_pilot = [1,2,3,4]
    data_file = os.path.join('dw_day3', 'pilot_study.bson')
    ma.recorders = [BSONCaseRecorder(data_file)]

    #initial guesses
    ma.wing_weight.cbar = .5
    ma.level.alpha = 3
    ma.wing_weight.b = 30
    ma.wing_weight.y_pod = 10

    ma.run()
    

