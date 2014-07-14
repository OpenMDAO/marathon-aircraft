from openmdao.main.api import Assembly, Component

from openmdao.lib.datatypes.api import VariableTree, Float


from wing_weight import WingWeight



class MarathonAirplane(Assembly): 



    def configure(self): 

        self.add('wing', WingWeight())

        self.add('level', AeroLevel())
        self.add('turning', AeroTurn())

        self.add('propellor_level', Propulsion())
        self.add('propellor_turning', Propulsion())

        self.add('drive_train', DriveTrain())
        self.add('engine', Human())

        self.connect('wing.geom', ['level.geom', 'turning.geom'])

        self.connect('level.drag', 'propellor_level.thrust')
        self.connect('turning.drag', 'propellor_turning.thrust')




