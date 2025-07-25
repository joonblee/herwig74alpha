#! /usr/bin/python
from __future__ import print_function
import yoda,glob,math,optparse
import subprocess,os
op = optparse.OptionParser(usage=__doc__)
op.add_option("-m"         , dest="plots"       , default=[], action="append")

opts, args = op.parse_args()


if(len(args)!=1) :
    print ('Must be one and only 1 name')
    quit()

name=args[0].split("-")

cmd3_weights = { 2007. : [0.5 ,4259], 1980 : [1 , 2368], 1951 : [11,5230],
                 1907.5: [17.5,5497], 1877 : [7 ,16803], 1830 : [30,8287],
                 1740. : [40  ,8728], 1640 : [40, 7299] }
wSum=0.
for key in cmd3_weights.keys() :
    wSum+= cmd3_weights[key][1]

for key in cmd3_weights.keys() :
    cmd3_weights[key][1] /= wSum 
output=""
labels={ "NonPerturbative" : "Non-Pert" ,
         "Perturbative"    : "Pert"     ,
         "Resonance"       : "Res"      }
for runType in ["NonPerturbative","Perturbative","Resonance"]:
    outhistos={}
    for fileName in glob.glob("Rivet-LowEnergy-%s-%s-*.yoda" % (name[0],runType) ):
        energy = float(fileName.split("-")[-1].strip(".yoda"))
        energyMeV = energy*1000.
        aos = yoda.read(fileName)
        for hpath,histo in aos.items():
            if("/_" in hpath or "TMP" in hpath or "RAW" in hpath) : continue
            if(len(opts.plots)>0 and hpath not in opts.plots) : continue
            if(type(histo)==yoda.core.Histo1D or
               (type(histo)==yoda.core.Scatter2D and hpath=="/BESIII_2019_I1726357/d03-x01-y01") ) :
                if( "CMD3_2019_I1770428" in hpath ) :
                    val=0.
                    for key in cmd3_weights.keys() :
                        if(abs(energyMeV-val)>abs(energyMeV-key)) :
                            val=key
                    histo.scaleW(cmd3_weights[val][1])
                    if(hpath in outhistos) :
                        outhistos[hpath] += histo
                    else :
                        outhistos[hpath] = histo
                else :
                    outhistos[hpath] = histo
                continue
            # create histo if it doesn't exist
            elif(hpath not in outhistos) :
                title=""
                path=""
                if hasattr(histo, 'title'):
                    title=histo.title()
                if hasattr(histo, 'path'):
                    path=histo.path()
                outhistos[hpath] = yoda.core.Scatter2D(path,title)
            matched = False
            for i in range(0,aos[hpath].numPoints()) :
                x = aos[hpath].points()[i].x()
                delta=1e-5
                if("KLOE_2009_I797438"   in hpath or "KLOE_2005_I655225"   in hpath or 
                   "KLOE2_2017_I1634981" in hpath or "FENICE_1994_I377833" in hpath or
                   "FENICE_1996_I426675" in hpath):
                   x=math.sqrt(x)
                   delta=1e-3
                if(abs(x-energy)<1e-3*delta or abs(x-energyMeV)<delta) :
                    duplicate = False
                    for j in range(0,outhistos[hpath].numPoints()) :
                        if(outhistos[hpath].points()[j].x()==aos[hpath].points()[i].x()) :
                            duplicate = True
                            break
                    if(not duplicate) :
                        outhistos[hpath].addPoint(aos[hpath].points()[i])
                    matched = True
                    break
            if(matched) : continue
            for i in range(0,aos[hpath].numPoints()) :
                xmin = aos[hpath].points()[i].xMin()
                xmax = aos[hpath].points()[i].xMax()
                if("KLOE_2009_I797438"   in hpath or "KLOE_2005_I655225"   in hpath or 
                   "KLOE2_2017_I1634981" in hpath or "FENICE_1994_I377833" in hpath or
                   "FENICE_1996_I426675" in hpath) :
                   xmin=math.sqrt(xmin)
                   xmax=math.sqrt(xmax)
                if((energy    > xmin and energy    < xmax) or
                   (energyMeV > xmin and energyMeV < xmax) ) :
                    duplicate = False
                    for j in range(0,outhistos[hpath].numPoints()) :
                        if(outhistos[hpath].points()[j].x()==aos[hpath].points()[i].x()) :
                            duplicate = True
                            break
                    if(not duplicate) :
                        outhistos[hpath].addPoint(aos[hpath].points()[i])
                    break
    if len(outhistos) == 0: continue
    p = subprocess.Popen(["rivet-config", "--datadir"],stdout=subprocess.PIPE)
    path=p.communicate()[0]
    if not isinstance(path, bytes) :
        path = path.encode("UTF-8").strip()
    else :
        path=path.strip().decode('utf-8')
    temp = list(outhistos.keys())
    for val in  temp :
        if type(outhistos[val]) is yoda.core.Scatter2D :
            if(outhistos[val].numPoints()==0) :
                del outhistos[val]
                continue
            analysis = val.split("/")[1]
            aos=yoda.read(os.path.join(os.path.join(os.getcwd(),path),analysis+".yoda"))
            ref = aos["/REF"+val]
            for point in ref.points() :
                matched=False
                for point2 in outhistos[val].points() :
                    if(point2.x()==point.x()) :
                        matched=True
                        break
                if(matched) : continue
                outhistos[val].addPoint(point.x(),0,point.xErrs(),(0.,0.))
        elif (type(outhistos[val]) is yoda.core.Histo1D or
              type(outhistos[val]) is yoda.core.Profile1D) :
            if(outhistos[val].numBins()==0) :
                del outhistos[val]
                continue
        else :
            print  (type(outhistos[val]) )
    
    yoda.writeYODA(outhistos,"LowEnergy-%s-%s.yoda" % (runType,args[0]))
    output+="LowEnergy-%s-%s.yoda:%s " % (runType,args[0],labels[runType])
print(output)
