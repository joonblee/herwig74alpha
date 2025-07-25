#! /usr/bin/python
# -*- mode: python -*-
from __future__ import print_function
import yoda,os,math,subprocess,optparse
from string import Template
# get the path for the rivet data
p = subprocess.Popen(["rivet-config", "--datadir"],stdout=subprocess.PIPE)
path=p.communicate()[0].strip().decode("UTF-8")
#Define the arguments
op = optparse.OptionParser(usage=__doc__)
op.add_option("--process"         , dest="processes"       , default=[], action="append")
op.add_option("--path"            , dest="path"            , default=path)
op.add_option("--non-perturbative", dest="nonPerturbative" , default=False, action="store_true")
op.add_option("--perturbative"    , dest="perturbative"    , default=False, action="store_true")
op.add_option("--resonance"       , dest="resonance"       , default=False, action="store_true")
op.add_option("--dest"            , dest="dest"            , default="Rivet")
op.add_option("--list"            , dest="list"            , default=False, action="store_true")
op.add_option("--plots"           , dest="plot"           , default=False, action="store_true")
opts, args = op.parse_args()
path=opts.path
thresholds = [0.7,2.*.5,2.*1.87,2.*5.28]
# the list of analyses and processes
analyses = { 'KK'           : {}, 'PiPi'         : {}, 'PPbar'     : {}, "3Pi"      : {},
             "EtaPi"        : {}, "4Pi"          : {}, "EtaEta"    : {}, "EtaOmega" : {},
             "2K1Pi"        : {}, "2K2Pi"        : {}, "4K"        : {}, "6m"       : {},
             "EtaPiPi"      : {}, "EtaPrimePiPi" : {}, "OmegaPi"   : {}, "PiGamma"  : {},
             "EtaGamma"     : {}, "PhiPi"        : {}, "OmegaPiPi" : {}, "DD"       : {},
             "BB"           : {}, "5Pi"          : {}, "LL"        : {}, "Baryon"   : {} }
# pi+pi-
analyses["PiPi"]["ALEPH_2003_I626022"   ] = ["d03-x01-y01"]
analyses["PiPi"]["BELLE_2005_I667712"   ] = ["d01-x01-y02",
                                             "d03-x01-y01","d03-x01-y02","d03-x01-y03",
                                             "d03-x01-y04","d03-x01-y05","d03-x01-y06",
                                             "d05-x01-y01","d05-x01-y02","d05-x01-y03",
                                             "d05-x01-y04","d05-x01-y05","d05-x01-y06"]
analyses["PiPi"]["BELLE_2007_I749358"   ] = ["d01-x01-y01"]
analyses["PiPi"]["CELLO_1992_I345437"   ] = ["d01-x01-y01"]
analyses["PiPi"]["CLEO_1994_I372230"    ] = ["d01-x01-y01"]
analyses["PiPi"]["MARKII_1984_I195739"  ] = ["d01-x01-y01"]
analyses["PiPi"]["MARKII_1986_I220003"  ] = ["d01-x01-y01","d01-x01-y02"]
analyses["PiPi"]["MARKII_1990_I304882"  ] = ["d01-x01-y01",
                                             "d02-x01-y01","d02-x01-y02","d02-x01-y03",
                                             "d02-x01-y04","d02-x01-y05","d02-x01-y06"]
analyses["PiPi"]["PLUTO_1984_I204487"   ] = ["d01-x01-y01"]
analyses["PiPi"]["TPC_1986_I228072"     ] = ["d01-x01-y01","d04-x01-y01"]
analyses["PiPi"]["VENUS_1995_I392360"   ] = ["d01-x01-y01"]
# pi0pi0
analyses["PiPi"]["BELLE_2009_I815978"       ] = ["d31-x01-y01","d31-x01-y02"]
analyses["PiPi"]["CRYSTAL_BALL_1982_I168793"] = ["d01-x01-y01"]
analyses["PiPi"]["CRYSTAL_BALL_1990_I294492"] = ["d01-x01-y01"]
analyses["PiPi"]["JADE_1990_I295180"        ] = ["d01-x01-y01"]
# K+K-
analyses["KK"  ]["ALEPH_2003_I626022"   ] = ["d04-x01-y01"]
analyses["KK"  ]["BELLE_2003_I629334"   ] = ["d01-x01-y01"]
analyses["KK"  ]["BELLE_2005_I667712"   ] = ["d01-x01-y01",
                                             "d04-x01-y01","d04-x01-y02","d04-x01-y03",
                                             "d04-x01-y04","d04-x01-y05","d04-x01-y06",
                                             "d06-x01-y01","d06-x01-y02","d06-x01-y03",
                                             "d06-x01-y04","d06-x01-y05","d06-x01-y06"]
analyses["KK"  ]["CLEO_1994_I372230"    ] = ["d01-x01-y01"]
analyses["KK"  ]["MARKII_1984_I195739"  ] = ["d01-x01-y01"]
analyses["KK"  ]["MARKII_1986_I220003"  ] = ["d01-x01-y01","d01-x01-y02"]
analyses["KK"  ]["TPC_1986_I228072"     ] = ["d05-x01-y01"]
# K0K0
analyses["KK"  ]["BELLE_2013_I1245023"  ] = ["d01-x01-y01","d01-x01-y02"]
# Eta Eta
analyses["EtaEta"]["BELLE_2010_I862260" ] = ["d01-x01-y01","d01-x01-y02"]
# Eta Pi
analyses["EtaPi"]["BELLE_2009_I822474" ] = ["d01-x01-y01"]
analyses["EtaPi"]["CRYSTAL_BALL_1986_I217547" ] = ["d01-x01-y01"]
# 3 pions
analyses["3Pi"]["ARGUS_1997_I420421" ] = ["d01-x01-y01","d02-x01-y01","d03-x01-y05",
                                          "d04-x01-y03","d05-x01-y01"]
analyses["3Pi"]["TASSO_1986_I228876" ] = ["d01-x01-y01"]
# 4 pions
analyses["4Pi"]["ARGUS_1989_I266416" ] = ["d01-x01-y01","d02-x01-y01",
                                          "d03-x01-y01","d04-x01-y01"]
analyses["4Pi"]["CELLO_1989_I267081" ] = ["d01-x01-y01","d02-x01-y01"]
analyses["4Pi"]["TASSO_1982_I180755" ] = ["d01-x01-y01"]
# proton antiproton
analyses["PPbar" ]["ARGUS_1989_I267759" ] = ["d02-x01-y01"]
analyses["PPbar" ]["BELLE_2005_I677625" ] = ["d01-x01-y01"]
analyses["PPbar" ]["CLEO_1994_I358510"  ] = ["d01-x01-y01"]
analyses["PPbar" ]["JADE_1986_I231554"  ] = ["d01-x01-y01"]
analyses["PPbar" ]["TASSO_1983_I191417" ] = ["d01-x01-y01"]
analyses["PPbar" ]["TPC_1987_I246557"   ] = ["d01-x01-y01"]
# other baryons
analyses["Baryon"]["BELLE_2016_I1444981"   ] = ["d01-x01-y01","d02-x01-y01"]
# K_0S K+/- pi -/+
analyses["2K1Pi"]["CELLO_1989_I266414" ] = ["d01-x01-y01"]
# K*K* and various 2K2pi states
analyses["2K2Pi"]["ARGUS_1987_I248680"] = ["d01-x01-y01","d02-x01-y01","d03-x01-y01","d04-x01-y01",
                                           "d05-x01-y01","d05-x01-y02","d05-x01-y03","d05-x01-y04","d05-x01-y05"]
analyses["2K2Pi"]["ARGUS_1988_I262713"] = ["d01-x01-y01","d02-x01-y01","d03-x01-y01","d04-x01-y01"]
analyses["2K2Pi"]["ARGUS_1994_I372451"] = ["d01-x01-y01","d02-x01-y01"]
analyses["2K2Pi"]["ARGUS_2000_I511512" ] = ["d03-x01-y01","d03-x01-y02","d03-x01-y03","d03-x01-y04",
                                            "d04-x01-y01","d04-x01-y02","d04-x01-y03","d04-x01-y04",
                                            "d05-x01-y01","d05-x01-y02","d05-x01-y03","d05-x01-y04",
                                            "d06-x01-y01","d06-x01-y02",
                                            "d07-x01-y01","d07-x01-y02","d07-x01-y03",
                                            "d08-x01-y01","d08-x01-y02","d08-x01-y03",
                                            "d09-x01-y01","d09-x01-y02",
                                            "d10-x01-y01","d10-x01-y02",
                                            "d11-x01-y01"]
# eta' pipi
analyses["EtaPrimePiPi"]["BELLE_2018_I1672149"] = ["d01-x01-y01","d02-x01-y01"]
# 6 meson final-states
analyses["6m"]["ARGUS_1996_I403304"] = [ "d01-x01-y01","d01-x01-y02","d01-x01-y03"]
analyses["6m"]["BELLE_2012_I1090664"] = ["d01-x01-y01","d01-x01-y02",
                                         "d01-x02-y01","d01-x02-y02",
                                         "d01-x03-y01","d01-x03-y02"]
analyses["6m"]["ARGUS_1987_I247567"] = ["d01-x01-y01","d02-x01-y01"]
analyses["6m"]["ARGUS_1988_I260828"] = ["d01-x01-y01"]
analyses["6m"]["ARGUS_1991_I296187"] = ["d02-x01-y01","d03-x01-y01","d05-x01-y01"]
analyses["6m"]["ARGUS_1991_I315058"] = ["d01-x01-y01","d01-x01-y02","d01-x01-y03"]
# hyperons
analyses["LL"]["BELLE_2006_I727063" ] = ["d01-x01-y01","d01-x01-y02"]
analyses["LL"]["CLEOII_1997_I439745"] = ["d01-x01-y01"]

# list the analysis if required and quit()
allProcesses=False
if "All" in opts.processes :
    allProcesses=True
    processes = sorted(list(analyses.keys()))
else :
    processes = sorted(list(set(opts.processes)))
if(opts.list) :
    for process in processes :
        print (" ".join(analyses[process]))
    quit()
if(opts.plot) :
    output=""
    for process in processes:
        for analysis in analyses[process] :
            if(analysis=="CELLO_1992_I345437") :
                for iy in range(1,22) :
                    output+= " -m/%s/%s" % (analysis,"d02-x01-y%02d"%iy)
            elif(analysis=="VENUS_1995_I392360") :
                for iy in range(1,12) :
                    output+= " -m/%s/%s" % (analysis,"d%02d-x01-y01"%iy)
            elif(analysis=="ALEPH_2003_I626022") :
                if process =="PiPi" :
                    output+= " -m/%s/%s" % (analysis,"d01-x01-y01")
                elif process =="KK" :
                    output+= " -m/%s/%s" % (analysis,"d02-x01-y01")
            elif(analysis=="BELLE_2003_I629334") :
                for ix in range(2,8) :
                    for iy in range(1,5) :
                        if(ix==8 and iy>1) : continue
                        output+= " -m/%s/%s" % (analysis,"d%02d-x01-y%02d"%(ix,iy))
            elif(analysis=="BELLE_2007_I749358") :
                for iy in range(2,100) :
                    output+= " -m/%s/%s" % (analysis,"d%02d-x01-y01"%iy)
                for iy in range(100,142) :
                    output+= " -m/%s/%s" % (analysis,"d%03d-x01-y01"%iy)
            elif(analysis=="BELLE_2010_I862260") :
                for iy in range(2,44) :
                    output+= " -m/%s/%s" % (analysis,"d%02d-x01-y01"%iy)
            elif(analysis=="BELLE_2009_I822474") :
                for iy in range(2,76) :
                    output+= " -m/%s/%s" % (analysis,"d%02d-x01-y01"%iy)
            elif(analysis=="BELLE_2013_I1245023") :
                for iy in range(2,41) :
                    for iz in range(1,4) :
                        output+= " -m/%s/%s" % (analysis,"d%02d-x01-y0%s"%(iy,iz))
            elif(analysis=="BELLE_2005_I677625") :
                for iy in range(2,7) :
                    for iz in range(1,4) :
                        if iy==6 and iz ==3 : break
                        output+= " -m/%s/%s" % (analysis,"d%02d-x01-y0%s"%(iy,iz))
            elif(analysis=="BELLE_2009_I815978") :
                for iy in range(1,31) :
                    for iz in range(1,4) :
                        if iy==30 and iz ==2 : break
                        output+= " -m/%s/%s" % (analysis,"d%02d-x01-y0%s"%(iy,iz))
            elif(analysis=="CLEO_1994_I358510") :
                for iy in range(2,4) :
                    output+= " -m/%s/%s" % (analysis,"d%02d-x01-y01"%iy)
            elif(analysis=="CLEO_1994_I358510TASSO_1983_I191417" or analysis=="CRYSTAL_BALL_1986_I217547") :
                for iy in range(1,3) :
                    output+= " -m/%s/%s" % (analysis,"d02-x01-y%02d"%iy)
            elif(analysis=="JADE_1986_I231554" or analysis=="CRYSTAL_BALL_1982_I168793") :
                output+= " -m/%s/%s" % (analysis,"d02-x01-y01")
            elif(analysis=="ARGUS_1989_I267759") :
                output+= " -m/%s/%s" % (analysis,"d01-x01-y01")
            elif(analysis=="TPC_1987_I246557") :
                for iy in range(1,3) :
                    output+= " -m/%s/%s" % (analysis,"d03-x01-y%02d"%iy)
            elif(analysis=="CRYSTAL_BALL_1990_I294492") :
                for iy in range(1,8) :
                    output+= " -m/%s/%s" % (analysis,"d02-x01-y%02d"%iy)
            for plot in analyses[process][analysis]:
                output+= " -m/%s/%s" % (analysis,plot)
    print (output)
    quit()
# mapping of process to me to use
me = { "PiPi"         : "MEgg2PiPi",
       "KK"           : "MEgg2KK"}

# get the particle masses from Herwig
particles = { "pi+" : 0., "pi0" : 0. ,"eta" : 0. ,"eta'" : 0. ,"phi" : 0. ,"omega" : 0. ,"p+" : 0. ,"K+" : 0.}
for val in particles :
    tempTxt = "get /Herwig/Particles/%s:NominalMass\nget /Herwig/Particles/%s:WidthLoCut\n" % (val,val)
    with open("temp.in",'w') as f:
        f.write(tempTxt)
    p = subprocess.Popen(["../src/Herwig", "read","temp.in"],stdout=subprocess.PIPE)
    vals = p.communicate()[0].split()
    mass = float(vals[0])-float(vals[1])
    particles[val]=mass
    os.remove("temp.in")
# minimum CMS energies for specific processes
minMass = { "PiPi"         : 2.*particles["pi+"],
            "KK"           : 2.*particles["K+"],
            "3Pi"          : 2.*particles["pi+"]+particles["pi0"],
            "4Pi"          : 2.*particles["pi+"]+2.*particles["pi0"],
            "EtaPiPi"      : particles["eta"]+2.*particles["pi+"],
            "EtaprimePiPi" : particles["eta'"]+2.*particles["pi+"],
            "EtaPhi"       : particles["phi"]+particles["eta"],
            "EtaOmega"     : particles["omega"]+particles["eta"],
            "OmegaPi"      : particles["omega"]+particles["pi0"],
            "OmegaPiPi"    : particles["omega"]+2.*particles["pi0"],
            "PhiPi"        : particles["phi"]+particles["pi0"],
            "PiGamma"      : particles["pi0"],
            "EtaGamma"     : particles["eta"],
            "PPbar"        : 2.*particles["p+"],
            "LL"           : 0.,
            "2K1Pi"        : 2.*particles["K+"]+particles["pi0"] }
# energies we need
energies={}
def nearestEnergy(en) :
    Emin=0
    delta=1e30
    anals=[]
    for val in energies :
        if(abs(val-en)<delta) :
            delta = abs(val-en)
            Emin = val
            anals=energies[val]
    return (Emin,delta,anals)

for process in processes:
    if(process not in analyses) : continue
    matrix=""
    if( process in me ) :
        matrix = me[process]
    for analysis in analyses[process] :
        aos=yoda.read(os.path.join(os.path.join(os.getcwd(),path),analysis+".yoda"))
        if(len(aos)==0) : continue
        for plot in analyses[process][analysis] :
            histo = aos["/REF/%s/%s" %(analysis,plot)]
            for point in histo.points() :
                energy = point.x()
                if(analysis=="KLOE_2009_I797438" or
                   analysis=="KLOE_2005_I655225" or
                   analysis=="KLOE2_2017_I1634981" or
                   analysis=="FENICE_1994_I377833") :
                    energy = math.sqrt(energy)
                if(energy>200) :
                    energy *= 0.001
                emin,delta,anals = nearestEnergy(energy)
                if(energy in energies) :
                    if(analysis not in energies[energy][1]) :
                        energies[energy][1].append(analysis)
                    if(matrix!="" and matrix not in energies[energy][0] and
                       minMass[process]<=energy) :
                        energies[energy][0].append(matrix)
                elif(delta<1e-7) :
                    if(analysis not in anals[1]) :
                        anals[1].append(analysis)
                    if(matrix!="" and matrix not in anals[0] and
                       minMass[process]<=energy) :
                        anals[0].append(matrix)
                else :
                    if(matrix=="") :
                        energies[energy]=[[],[analysis]]
                    elif(minMass[process]<=energy) :
                        energies[energy]=[[matrix],[analysis]]

with open("python/LowEnergy-GammaGamma-Perturbative.in", 'r') as f:
    templateText = f.read()
perturbative=Template( templateText )
with open("python/LowEnergy-GammaGamma-NonPerturbative.in", 'r') as f:
    templateText = f.read()
nonPerturbative=Template( templateText )
with open("python/LowEnergy-GammaGamma-Resonance.in", 'r') as f:
    templateText = f.read()
resonance=Template( templateText )

targets=""
for energy in sorted(energies) :
    anal=""
    for analysis in energies[energy][1]: 
        anal+= "insert /Herwig/Analysis/Rivet:Analyses 0 %s\n" %analysis
    proc=""
    matrices = energies[energy][0]
    if(allProcesses) : matrices = me.values()
    for matrix in  matrices:
        proc+="insert SubProcess:MatrixElements 0 %s\n" % matrix
    maxflavour =5
    if(energy<thresholds[1]) :
        maxflavour=2
    elif(energy<thresholds[2]) :
        maxflavour=3
    elif(energy<thresholds[3]) :
        maxflavour=4
    # input file for perturbative QCD
    if(opts.perturbative and energy> thresholds[0]) :
        process=""
        for i in range(1,maxflavour+1) :
            process+="cp MEgg2ff MEgg2qq%s\n" %i
            process+="cp gg2ffAmp gg2fqq%sAmp\n" %i
            process+="set MEgg2qq%s:Amplitude gg2fqq%sAmp\n" % (i,i)
            process+="set gg2fqq%sAmp:Process %s\n" %(i,i+10)
            process+="insert SubProcess:MatrixElements 0 MEgg2qq%s\n" % i
        inputPerturbative = perturbative.substitute({"ECMS" : "%8.6f" % energy, "ANALYSES" : anal,
                                                     "process" : process})
        with open(opts.dest+"/Rivet-LowEnergy-GammaGamma-Perturbative-%8.6f.in" % energy ,'w') as f:
            f.write(inputPerturbative)
        targets += "Rivet-LowEnergy-GammaGamma-Perturbative-%8.6f.yoda " % energy
    # input file for currents
    if(opts.nonPerturbative and proc!="") :
        inputNonPerturbative = nonPerturbative.substitute({"ECMS" : "%8.6f" % energy, "ANALYSES" : anal,
                                                           "processes" : proc})
        with open(opts.dest+"/Rivet-LowEnergy-GammaGamma-NonPerturbative-%8.6f.in" % energy ,'w') as f:
            f.write(inputNonPerturbative)
        targets += "Rivet-LowEnergy-GammaGamma-NonPerturbative-%8.6f.yoda " % energy
    # input file for resonances
    if(opts.resonance and energy>0.81) :
        inputResonance = resonance.substitute({"ECMS" : "%8.6f" % energy, "ANALYSES" : anal})
        with open(opts.dest+"/Rivet-LowEnergy-GammaGamma-Resonance-%8.6f.in" % energy ,'w') as f:
            f.write(inputResonance)
        targets += "Rivet-LowEnergy-GammaGamma-Resonance-%8.6f.yoda " % energy

print (targets)
