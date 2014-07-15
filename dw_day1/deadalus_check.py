import numpy as np
from matplotlib import pylab as plt

from openmdao.lib.casehandlers.api import CaseDataset


cds = CaseDataset('deadalus_check.bson', 'bson')


data = cds.data.by_case().fetch()[-1]

#weight fraction pie chart


W_fuse_empty = data['fuse_weight.M_tot'] - data['fuse_weight.M_pilots']
W_empty = data['wing_weight.M_tot'] + W_fuse_empty

print "Wing Mass (kg): ", data['wing_weight.M_tot']
# print "  M_s:", data['wing_weight.M_s']
# print "  M_r:", data['wing_weight.M_r']
# print "  M_er:", data['wing_weight.M_er']
# print "  M_le:", data['wing_weight.M_le']
# print "  M_te:", data['wing_weight.M_te']
# print "  M_cover:", data['wing_weight.M_cover']


print "Fuse Mass (kg): ", W_fuse_empty
# print "  M_s:", data['fuse_weight.M_s']
# print "  M_r:", data['fuse_weight.M_r']
# print "  M_le:", data['fuse_weight.M_le']
# print "  M_cover:", data['fuse_weight.M_cover']
# print "  M_tailboom:", data['fuse_weight.M_tailboom']
# print "  M_propellor:", 2.512*3
# print "  M_pod:", 3.499*1

print 

print "Empty Mass (kg): ", W_empty
print "    wing: {:.2%}".format(data['wing_weight.M_tot']/W_empty)
print "    fuse {:.2%}".format(W_fuse_empty/W_empty)


W_gross = data['wing_weight.M_tot'] + data['fuse_weight.M_tot']

print "Gross Mass (kg): ", W_gross
print "    wing: {:.2%}".format(data['wing_weight.M_tot']/W_gross)
print "    fuse {:.2%}".format(data['fuse_weight.M_tot']/W_gross)

fig,ax = plt.subplots()

x = np.array([0,1,2])
labels = ['wing','pod','control surf.']
deadalus_masses = np.array([18985.4, 10926.8, 537.8+623.3])/31073
ax.bar(x, deadalus_masses, color='b', width=.35)
ax.set_title('Sizing Model Validation')


estimated_masses = np.array([data['wing_weight.M_tot'], W_fuse_empty, W_fuse_empty-2.512*3-3.499*1])/W_empty
plt.bar(x+.35, estimated_masses, color='g', width=.35)

#ax.set_aspect('equal')
ax.set_xticks(x+.35)
ax.set_xticklabels(labels)


plt.tight_layout()
plt.savefig('deadalus_check.pdf')

