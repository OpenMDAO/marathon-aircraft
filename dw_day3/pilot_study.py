import numpy as np

from matplotlib import pyplot as plt, rcParams
from openmdao.lib.casehandlers.api import CaseDataset
cds = CaseDataset('pilot_study.bson', 'bson')

#ask for the variables you care about
var_names = ['wing_weight.b', 'wing_weight.cbar', 'wing_weight.s', 'wing_weight.AR', 
'wing_weight.tip_slope', 'wing_weight.M_tot', 'fuse_weight.M_tot', 'fuse_weight.N_pilot', 'fuse_weight.M_pilot', 
'level.Cl', 'level.alpha', 'level.Re', 'level.drag', 'turning.drag','fuse_weight.V_flight'
]
#Note why aren't level.V, wing_weight.V_flight in the data set? 

#note, should not have to do this, but the query for constant values seems broken. 
V_flight = cds.simulation_info['constants']['fuse_weight.V_flight'] 
M_pilot = cds.simulation_info['constants']['fuse_weight.M_pilot']
data = cds.data.driver('driver').vars(var_names).by_variable().fetch()



#wing size charts
rcParams['font.size'] = 15 #font size on all plots
fig, ax = plt.subplots()
ax.plot(data['fuse_weight.N_pilot'],data['wing_weight.b'], c='b', lw=5)
ax.set_title('Wing Size vs # of Pilots')
ax.set_xlabel('# of Pilots')
ax.set_ylabel('Span (m)', color='b')
for tl in ax.get_yticklabels():
    tl.set_color('b')
ax.set_xticks([1,2,3,4])

ax2 = ax.twinx()
ax2.plot(data['fuse_weight.N_pilot'],data['wing_weight.cbar'], c='g', lw=5)
ax2.set_ylabel('Chord (m)', color='g')

for tl in ax2.get_yticklabels():
    tl.set_color('g')

plt.savefig('wing_size.pdf')

#power plots
fig, ax = plt.subplots()
drag = np.array(data['level.drag'])
N_pilot = np.array(data['fuse_weight.N_pilot'])
watts_per_kg = drag*V_flight*1.2/(N_pilot*M_pilot)
watts_per_pilot = drag*V_flight*1.2/N_pilot

ax.plot(N_pilot, watts_per_kg, c='b', lw=5)
ax.set_title('Power vs # of Pilots')
ax.set_xlabel('# of Pilots')
ax.set_ylabel(r'watts per kg-pilot')
ax.set_xticks([1,2,3,4])
ax.set_ylim(2.5,4.5)

ax2 = ax.twinx()
ax2.plot(N_pilot, watts_per_pilot, c='b', lw=5)
ax2.set_ylabel(r'watts per pilot')
ax2.set_ylim(2.5*M_pilot,4.5*M_pilot)

plt.savefig('pilot_power.pdf')

#Empty Mass
#(ma.wing_weight.M_tot + ma.fuse_weight.M_tot) - (ma.fuse_weight.N_pilot*ma.fuse_weight.M_pilot)
M_wing = np.array(data['wing_weight.M_tot'])
M_fuse = np.array(data['fuse_weight.M_tot'])
fig, ax = plt.subplots()
ax.plot(N_pilot, M_wing + M_fuse - (N_pilot*M_pilot), c='b', lw=5)
ax.set_title('Empty Mass vs # of Pilots')
ax.set_xlabel('# of Pilots')
ax.set_ylabel(r'Empty Weight (kg)')
ax.set_xticks([1,2,3,4])

plt.savefig('empty_weight.pdf')


fig, ax = plt.subplots()
ax.plot(N_pilot, data['wing_weight.tip_slope'], c='b', lw=5)
ax.set_xticks([1,2,3,4])

# print data['wing_weight.b']
# print data['wing_weight.cbar']
plt.show()





