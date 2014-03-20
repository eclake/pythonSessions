# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Ipython notebook example
# 
# In this example I include info on:
# 
# * when you might want to use a dictionary
# * the numpy equivalent to the idl where
# * some more plotting
# * some more input/output tricks
# 
# ##What's so good about using ipython notebooks?
# 
# Here is a place you can do your research/development storing notes+plots+code all in one place.  Google 'ipython notebook' to find out about all the useful features like outputting the code to a .py file.

# <codecell>

#First a line of code that allows you to place your plots in the notebook
%pylab inline

# <markdowncell>

# One of the most useful things to do is obviously to read in data tables.  You can read them in into a dictionary like structure so that you can access your columns with the names already defined in the file - the file looks something like this:
# 
# \#magIn r50in magMeas r50meas r50SE
#         
#         ...data...
# 
# This file holds some properties for a set of simulated single Sersic profiles: the total magnitude and half-light radius of the profiles (magIn, r50in) and the measured properties using one measure (magMeas, r50meas) as well as the measured half-light radius using SExtractor (r50SE).  If the measurements have failed they are set to a value of -1.  The size measurements are all in pixels.

# <codecell>

import pylab #remember with this import you are importing it into the namespace pylab, 
             #hence the call pylab.genfromtxt rather than genfromtxt

data=pylab.genfromtxt('someData.txt', dtype=None, names=True)

#google genfromtxt to set the data types and names for each column manually in the genfromtxt call.
#With dtype=None it will guess what variable type to assign each column.

# <codecell>

#This means that you can access your data with the column name, like this
print data['r50SE'][:10]

# <markdowncell>

# So, how well has each measurement technique done at measuring the sizes?

# <markdowncell>

# ###Comparing size estimates

# <codecell>

#figure()

#first you want to be careful to only plot the objects for which the measurement has worked
goodIdxSE=np.all([data['r50SE'] >= 0], axis=0) #produces an array of booleans the same length as data['r50SE']
                                               #but when using this to index the array only the 'true's get used.
                                               #axis=0 defines the dimension along which you are looking.

pylab.scatter(data['r50in'][goodIdxSE],data['r50SE'][goodIdxSE])
pylab.plot([-10,10],[-10,10],c='r',linewidth=2)

ax=plt.gca() #making an axis object
ax.set_xlim(0,8)
ax.set_ylim(0,8)

pylab.xlabel('input r$_{50}$',fontsize=15)
pylab.ylabel('SExtractor r$_{50}$',fontsize=15)

pylab.savefig('/Users/efcl/Documents/papers/LBG_morphology_evolution/plots/testing.ps',orientation='landscape')

# <codecell>

figure()

#first you want to be careful to only plot the objects for which the measurement has worked
goodIdxMeas=np.all([data['r50meas'] >= 0], axis=0) 

pylab.scatter(data['r50in'][goodIdxMeas],data['r50meas'][goodIdxMeas])
pylab.plot([-10,10],[-10,10],c='r',linewidth=2)

ax=plt.gca() #making an axis object
ax.set_xlim(0,8)
ax.set_ylim(0,8)

pylab.xlabel('input r$_{50}$',fontsize=15)
pylab.ylabel('CoG-based r$_{50}$',fontsize=15)

# <markdowncell>

# There are certainly some differences between how the two different measurement techniques are working.
# 
# * Larger scatter using the CoG-based technique
# * Maybe CoG-based technique doing better at measuring sizes of large object?
# 
# Could the difference in scatter be at all dependent on the brightness of the profile - i.e. are the differences mainly S/N effects?

# <markdowncell>

# ###Size estimates as a function of input magnitude

# <codecell>

figure()

#You can choose the colours of the points based on html colour codes.
#Check out this website: http://html-color-codes.info
pylab.scatter(data['magIn'][goodIdxMeas],data['r50in'][goodIdxMeas]-data['r50meas'][goodIdxMeas],c='#DA81F5',linewidths=0,label='CoG',\
    alpha=0.5)
pylab.scatter(data['magIn'][goodIdxSE],data['r50in'][goodIdxSE]-data['r50SE'][goodIdxSE],c='#04B4AE',linewidths=0,label='SE',alpha=0.5)

ax=plt.gca() #making an axis object
#ax.set_xlim(0,8)
#ax.set_ylim(0,8)

pylab.xlabel('input magnitude',fontsize=15)
pylab.ylabel('r$_{50}$in - measured r$_{50}$',fontsize=15)
pylab.legend()

# <markdowncell>

# It certainly does have a dependence on the brightness of the profile.  Here I care about the measured distribution of sizes, so does one of the measurements bias the mean of the distribution more than the other?

# <markdowncell>

# ###Size distribution

# <codecell>

#Going to define some magnitude bins to split the sample into
magBins=np.arange(np.min(data['magIn']),np.max(data['magIn'])) #10 mag bins
magBinDelta=0.5

from collections import defaultdict
#defaultdict allows you to populate a dictionary with a certain type of variable
#every time.  If the key doesn't exist yet, it will create an entry with
#that type of variable.  Here, we always want to store lists.

magBinDict=defaultdict(list)
for bin in magBins:
    indices=np.all([data['magIn'] > bin - magBinDelta, data['magIn'] <= bin + magBinDelta],axis=0)
    magBinDict[bin]=indices

# <codecell>

distributionMeanDict={'r50in':defaultdict(float), \
                      'r50meas':defaultdict(float), \
                      'r50SE':defaultdict(float)}

plottingDict={'r50in':{'color':'green','label':'input'}, \
              'r50meas':{'color':'blue','label':'CoG'}, \
              'r50SE':{'color':'red','label':'SE'}}

#note, just because the output histograms might be in ascending magnitude order, that will not necessarily
#always be the case because standard dictionaries do not retain any standard order.  The do not remember
#what order things are added, although one of the options in collections does!
for bin in magBins:
    if len(data['magIn'][magBinDict[bin]]) > 0:
        figure()
        for key in plottingDict:
            n, bins, patches = plt.hist(data[key][magBinDict[bin]],10, color=plottingDict[key]['color'], \
                                        label=plottingDict[key]['label'], histtype='step', linewidth=2)
                                        #histtype='step' is an unfilled line plot, default type is bar
            distributionMeanDict[key][bin]=np.mean(data[key][magBinDict[bin]])
        pylab.title(str(bin)+' magnitude bin')
        pylab.xlabel('size')
        pylab.legend()

# <markdowncell>

# OK, the histograms are a little ugly and could be plotted better but I'll summarise the bias to the distribution with the measured mean values.

# <codecell>

figure()

for key in plottingDict:
    pylab.scatter(distributionMeanDict[key].keys(), distributionMeanDict[key].values(), c=plottingDict[key]['color'], \
                  label=plottingDict[key]['label'], s=40) #marker size 40 (default 20)
    
pylab.legend()
pylab.xlabel('mag in')
pylab.ylabel('mean size')

# <markdowncell>

# Let's write the mean values to a file!

# <codecell>

f = open('meanSize_mag.txt','w')

outputStr='#mag '
for key in distributionMeanDict:
    outputStr=outputStr+key+' '
f.write(outputStr+'\n')

for mag in distributionMeanDict['r50in'].keys():
    outputStr=str(mag)+' '
    for key in distributionMeanDict:
        if mag in distributionMeanDict[key].keys():
            outputStr=outputStr+' '+str(distributionMeanDict[key][mag])
        else:
            outputStr=outputStr+' -1 '
    outputStr=outputStr+'\n'
    f.write(outputStr)
    
f.close()

# <codecell>


