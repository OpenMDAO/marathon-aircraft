from matplotlib import pylab as plt

from openmdao.lib.casehandlers.api import CaseDataset


cds = CaseDataset('1_pilot.bson', 'bson')


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

