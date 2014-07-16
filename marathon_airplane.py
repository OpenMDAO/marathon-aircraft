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
        #tail settings
        self.fuse_weight.b = 7
        self.fuse_weight.cbar = .7

        self.fuse_weight.N_pilot = 3
        self.fuse_weight.N_propellor = 3

        self.add('level', Aero())
        self.level.Cd_a = 3*.015

        self.add('turning', Aero())
        self.level.Cd_a = 6*.015
        self.turning.R_0 = 150 #turning radius


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




