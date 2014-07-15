import numpy as np
from matplotlib import pylab as plt
from matplotlib.gridspec import GridSpec

from openmdao.lib.casehandlers.api import CaseDataset


cds = CaseDataset('pilot_study.bson', 'bson')


#data = cds.data.driver('driver').by_case().vars(['wing_weight.M_tot', 'fuse_weight.M_tot', 'fuse_weight.M_pilots', 'wing_weight.s']).fetch()

labels = ['wing_weight.s', 'wing_weight.M_tot', 'fuse_weight.M_tot', 'fuse_weight.M_pilots', 'wing_weight.s', 'pwr_per_pilot', 'watts_per_kg']
cantilever_data = [[31.029179006177973, 20.04597951411268, 94.87690569403432, 80.56400000000001, 31.029179006177973, 419.9342619664385, 5.8324203050894239],
[61.142916333370742, 48.502339985129737, 177.9529056940343, 161.12800000000001, 61.142916333370742, 371.20481550396238, 5.1556224375550332],
[95.413865008892074, 92.355779524158123, 261.02890569403434, 241.692, 95.413865008892074, 369.80094351322327, 5.1361242154614342],
[136.16973611295765, 160.22745027994324, 344.10490569403436, 322.25600000000003, 136.16973611295765, 515.28011387992126, 7.156668248332239]]
data = [dict(zip(labels,d)) for d in cantilever_data]

two_wire_data = [[28.707144342740921, 11.445851130931853, 94.87690569403432, 80.56400000000001, 28.707144342740921, 395.06856772072484, 5.4870634405656231],
[54.192962477796392, 22.761770149656147, 177.9529056940343, 161.12800000000001, 54.192962477796392, 333.99274662217397, 4.6387881475301942],
[80.224763829814236, 36.099849236728481, 261.02890569403434, 241.692, 80.224763829814236, 315.5830412553621, 4.383097795213363],
[106.7882176183174, 51.407011395593209, 344.10490569403436, 322.25600000000003, 106.7882176183174, 410.40199893791083, 5.7000277630265392]]

#weight fraction pie chart
the_grid = GridSpec(2, 3)

for i in range(3): 
    M_fuse_empty = data[i]['fuse_weight.M_tot'] - data[i]['fuse_weight.M_pilots']
    M_empty = data[i]['wing_weight.M_tot'] + M_fuse_empty


    ax = plt.subplot(the_grid[0, i], aspect=1)
    estimated_masses = np.array([data[i]['wing_weight.M_tot'], M_fuse_empty, M_fuse_empty-2.512*(i+1)-3.499*(i+1)])/M_empty
    labels = ['wing','pod','control surf.']
    #print M_empty, estimated_masses
    #print data[i]['wing_weight.s']
    plt.pie(estimated_masses, labels=labels, autopct='%.0f%%',)
    ax.set_title('%d Pilot'%(i+1))


plt.tight_layout()
plt.savefig('pilot_study_pie.pdf')

#total power req
plt.figure()
fig, ax = plt.subplots()
raw_data = np.array(cantilever_data)
ax.plot([1,2,3,4], raw_data[:,5],label="cantilever")
raw_data = np.array(two_wire_data)
ax.plot([1,2,3,4], raw_data[:,5],label="two-wire")
ax.legend(loc="best")

ax.set_xlabel('# of Pilots')
ax.set_ylabel('Total Watts Per Pilot')
ax.set_xticks([1,2,3])

#ax2 = plt.twinx()
#ax2.plot([1,2,3], raw_data[:,6])
#ax.set_ylabel('Watts Per kg')

plt.savefig('pilot_study_pwr_req.pdf')





