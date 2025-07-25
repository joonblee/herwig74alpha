#! /usr/bin/python
from __future__ import print_function
import yoda,os,math,subprocess,optparse
from string import Template
import numpy
import matplotlib.pyplot as plt
from scipy.integrate import quad 
import datetime
import lhapdf
p = lhapdf.mkPDF("CT14lo",0)

htmlTemplate=Template("""
<html>
<head>
<title>Tests of Onium Cross Sections</title>
<style>
      html { font-family: sans-serif; }
      img { border: 0; }
      a { text-decoration: none; font-weight: bold; }
    </style>
            <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
          tex2jax: {inlineMath: [["$$","$$"]]}
        });
        </script>
        <script type="text/javascript" async
          src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
        </script>
        </head>
<body>
<section id="OniumTests">
<h1>Tests of Onium Cross Sections</h1>
${plots}
</section>

<footer style="clear:both; margin-top:3em; padding-top:3em">
${time}
</footer>

</body>
</html>""")
plotTemplate=Template("""
<div class="plot" id="plot_${id}" style="float:left; font-size:smaller; font-weight:bold;">
  <a href="#MC_Simple_Onium-${id}">&#9875;</a> ${id}:<br/>
  <a name="MC_Simple_Onium-${id}"><a href="${id}.pdf">
    <img src="${id}.png">
  </a></a>
</div>""")
# various test functions

s = 13e3**2
GeV2nb=.389379304e6

R02=0.560236
M=2.9804
aS=0.248943

def dSigmady1S0(y) :
    A = numpy.pi**2*aS**2*R02/3./M**5*GeV2nb
    x1 = M/numpy.sqrt(s)*numpy.exp(y)
    x2 = M/numpy.sqrt(s)*numpy.exp(-y)
    return p.xfxQ(21,x1,M)*p.xfxQ(21,x2,M)*A

def dSigmady3P0(y) :
    A = 12.*numpy.pi**2*aS**2*R02/M**7*GeV2nb
    x1 = M/numpy.sqrt(s)*numpy.exp(y)
    x2 = M/numpy.sqrt(s)*numpy.exp(-y)
    return p.xfxQ(21,x1,M)*p.xfxQ(21,x2,M)*A

def dSigmady3P2(y) :
    A = 16.*numpy.pi**2*aS**2*R02/M**7*GeV2nb
    x1 = M/numpy.sqrt(s)*numpy.exp(y)
    x2 = M/numpy.sqrt(s)*numpy.exp(-y)
    return p.xfxQ(21,x1,M)*p.xfxQ(21,x2,M)*A

def dSigmady1D2(y) :
    A = 80.*numpy.pi**2*aS**2*R02/3./M**9*GeV2nb
    x1 = M/numpy.sqrt(s)*numpy.exp(y)
    x2 = M/numpy.sqrt(s)*numpy.exp(-y)
    return p.xfxQ(21,x1,M)*p.xfxQ(21,x2,M)*A

# latex for plots
latexName = {441  : "\\eta_c", 443    : "J/\\psi", 100441 : "\\eta_c(2S)", 100443 : "\psi(2S)",
           
             10443 : "h_c", 10441: "\\chi_{c0}", 20443: "\\chi_{c1}",  445: "\\chi_{c2}",

             30443 : "\\psi(3770)" , 20445 : "\\psi_2(1D)", 447 : "\\psi_3(1D)", 100445: "\\chi_{c2}(2P)",
           
             551  : "\\eta_b", 553 : "\\Upsilon" , 100551 : "\\eta_b(2S)", 100553 : "\\Upsilon(2S)", 200551 : "\\eta_b(3S)", 200553 : "\\Upsilon(3S)", 300553 : "\\Upsilon(4S)",
           
             10553 : "h_b", 10551: "\\chi_{b0}", 20553: "\\chi_{b1}",  555: "\\chi_{b2}",
           
             110553 : "h_b(2P)", 110551: "\\chi_{b0}(2P)", 120553: "\\chi_{b1}(2P)",  100555: "\\chi_{b2}(2P)",
             210553 : "h_b(3P)", 210551: "\\chi_{b0}(3P)", 220553: "\\chi_{b1}(3P)",  200555: "\\chi_{b2}(3P)",

             10555 : "\\eta_{b2}", 30553 : "\\Upsilon_1(1D)", 20555 : "\\Upsilon_2(1D)", 557 : "\\Upsilon_3(1D)",
           
             541 : "B_c^+", 543 : "B_c^{*+}", 10541 : "B_{c0}^{*+}", 545 : "B_{c2}^{*+}",
             100541 : "B_c(2S)^+", 100543 : "B_c(2S)^{*+}", 10543 : "B_{c1}^+", 20543 : "B_{c1}^{\\prime+}",
             30543 : "B_c(1D)^{*+}", 547 : "B_{c3}(1D)^{*+}", 20545 : "B_{c2}(H)^{+}", 10545 : "B_{c2}(L)^+",
              4403 : "(cc)_1", 5503 : "(bb)_1", 5401 : "(bc)_0", 5403 : "(bc)_1"  }
# cross section tests
testParameters  = {"eta_c_1S" : [   441,"ccbar","1S",0.560236,2.9804 ,0.248943,dSigmady1S0,"MEgg2EtaC1S" ],
                   "eta_c_2S" : [100441,"ccbar","2S",0.6966  ,3.638  ,0.232538,dSigmady1S0,"MEgg2EtaC2S" ],
                   "eta_b_1S" : [   551,"bbbar","1S",1.8**3  ,9.397  ,0.180058,dSigmady1S0,"MEgg2EtaB1S" ],
                   "eta_b_2S" : [100551,"bbbar","2S",2.8974  ,9.996  ,0.177496,dSigmady1S0,"MEgg2EtaB2S" ],
                   "eta_b_3S" : [200551,"bbbar","3S",2.2496  ,10.337 ,0.176137,dSigmady1S0,"MEgg2EtaB3S" ],
                   "eta_b2_1D": [ 10555,"bbbar","1D",0.8394  ,10.158 ,0.176842,dSigmady1D2,"MEgg2EtaB21D"],
                   "chi_c0_1P": [ 10441,"ccbar","1P",0.1296  ,3.41476,0.237512,dSigmady3P0,"MEgg2ChiC01P"],
                   "chi_b0_1P": [ 10551,"bbbar","1P",1.6057  ,9.85944,0.17806 ,dSigmady3P0,"MEgg2ChiB01P"],
                   "chi_b0_2P": [110551,"bbbar","2P",1.8240  ,10.2325,0.176546,dSigmady3P0,"MEgg2ChiB02P"],
                   "chi_b0_3P": [210551,"bbbar","3P",1.9804  ,10.5007,0.175507,dSigmady3P0,"MEgg2ChiB03P"],
                   "chi_c2_1P": [   445,"ccbar","1P",0.1296  ,3.5562 ,0.2343  ,dSigmady3P2,"MEgg2ChiC21P"],
                   "chi_c2_2P": [100445,"ccbar","2P",0.1767  ,3.929  ,0.226766,dSigmady3P2,"MEgg2ChiC22P"],
                   "chi_b2_1P": [   555,"bbbar","1P",1.6057  ,9.91221,0.177841,dSigmady3P2,"MEgg2ChiB21P"],
                   "chi_b2_2P": [100555,"bbbar","2P",1.8240  ,10.2686,0.176404,dSigmady3P2,"MEgg2ChiB22P"],
                   "chi_b2_3P": [200555,"bbbar","3P",1.9804  ,10.5264,0.175409,dSigmady3P2,"MEgg2ChiB23P"],

}

# options
op = optparse.OptionParser(usage=__doc__)
op.add_option("--generate-input-files", dest="infiles", default=False, action="store_true")
op.add_option("--analyse", dest="analyse", default=False, action="store_true")
op.add_option("--fast", dest="fast", default=False, action="store_true")
opts, args = op.parse_args()
# get template and write the file
with open(os.path.join("Rivet/Templates/Hadron.in"), 'r') as f:
    templateText = f.read()
template = Template( templateText )
# if we are generating the inputfiles
if opts.infiles :
    targets=""
    # now loop over the examples
    for (key,val) in testParameters.items() :
        # substs for the input file
        parameters={"parameterFile" : "insert /Herwig/Analysis/RivetAnalysis:Analyses 0 MC_Hadron_Onium",
                    "bscheme"       : "",
                    "shower"        : "do /Herwig/OniumParameters:SetWaveFunction %s %s %s" %(val[1],val[2],val[3]), 
                    "process"       : """
set /Herwig/Generators/EventGenerator:EventHandler:LuminosityFunction:Energy 13000.0
set /Herwig/Generators/EventGenerator:EventHandler:HadronizationHandler NULL
set /Herwig/Generators/EventGenerator:EventHandler:CascadeHandler NULL
set /Herwig/Generators/EventGenerator:EventHandler:DecayHandler NULL
set /Herwig/Analysis/Basics:CheckQuark 0
set /Herwig/Generators/EventGenerator:EventHandler:Cuts:MHatMin 2.0
set /Herwig/Generators/EventGenerator:EventHandler:Cuts:X1Min 1e-8
set /Herwig/Generators/EventGenerator:EventHandler:Cuts:X2Min 1e-8
insert SubProcess:MatrixElements[0] %s
""" % val[7],
                    "collider" : "PPCollider.in",
                    "runname"  : "Onium-%s"%key}
        with open(os.path.join("Rivet","Onium-%s.in"%key), 'w') as f:
            f.write( template.substitute(parameters) )
        targets += "Onium-%s.yoda " % key
    print(targets)
# if we are doing the analysis
if opts.analyse :
    if not os.path.isdir("Onium-Sigma"):
        os.mkdir("Onium-Sigma")
    plots=""
    # loop over the tests
    for (key,val) in testParameters.items() :
        R02 = val[3]
        M   = val[4]
        aS  = val[5]
        # plot title
        lName = latexName[val[0]]
        plt.title("Differential Cross section w.r.t rapidity for $gg\\to %s$"%lName)
        # analytic line
        ymax = numpy.log(math.sqrt(s)/M)-0.001
        ys = numpy.linspace(-ymax,ymax,1000)
        sig=[]
        for y in ys :
            sig.append(val[6](y))
        plt.plot(ys,sig,label="analytic ",color="black")
        aos   = yoda.read("Onium-%s.yoda" % key)
        histo = aos["/MC_Hadron_Onium/h_y_%s" % val[0]]
        x  = []
        dx = []
        y1 = []
        dy1= []
        chisq = 0.
        ndof  = 0
        for hbin in histo.bins() :
            x  .append(hbin.xMid()      )
            dx .append(0.5*hbin.xWidth())
            y1 .append(hbin.height()   /1000.)
            dy1.append(hbin.heightErr()/1000.)
            if(dy1[-1]>0. and x[-1]>0.01 and x[-1]<0.99) :
                if(opts.fast) :
                    fval = val[6](hbin.xMid())
                else :
                    fval = quad(val[6],hbin.xMin(),hbin.xMax())[0]/hbin.xWidth()
                chisq += ((fval-y1[-1])/dy1[-1])**2
                ndof+=1.
        if(ndof!=0) : chisq/=ndof
        plt.errorbar(x,y1,yerr=dy1,xerr=dx,linestyle="none",fmt="none",
                     label="Hw 7",color="red")
        plt.xlabel("$y_{%s}$" % lName)
        plt.ylabel("$d\\sigma/dy_{%s}$ [nb]" % lName)
        plt.legend(title="$\\chi^2/N=%.2f$"%chisq)
        plt.xlim([-ymax,ymax])
        plt.ylim(ymin=0)
        plots+=plotTemplate.substitute({"id" : key})
        # now for the total cross section
        sigmaTotal=quad(val[6],-ymax,ymax)
        dat = open("Onium-%s.out" % key)
        line =dat.readline()
        while line :
            line=line.strip()
            if "Total" in line and "attempted" in line :
                line=line.split()[-1].split("e")
                power=float(line[1])
                line=line[0].strip(")").split("(")
                value=float(line[0])
                error=float(line[1])
                line=line[0].split(".")
                if len(line)==2 :
                    error *= 10**(-float(len(line[1])))
                value *= 10**power
                error *= 10**power
                break
            line=dat.readline()
        sMax = max(sig)
        
        chisq = (sigmaTotal[0]-value)**2/(sigmaTotal[1]**2+error**2)
        frac = (sigmaTotal[0]-value)/(sigmaTotal[0]+value)
        plt.text(0.,0.15*sMax,"Total Cross Section = $%.2f\\times10^{%s}$ nb"%(sigmaTotal[0]/10**power,int(power)),horizontalalignment='center')
        plt.text(0.,0.10*sMax,"Fractional Difference = %.2f per mille"%(frac*1000),horizontalalignment='center')
        plt.text(0.,0.05*sMax,"$\\chi^2 = %.2f$"%(chisq),horizontalalignment='center')
        plt.savefig("Onium-Sigma/%s.pdf" %key)
        plt.savefig("Onium-Sigma/%s.png" %key)
        plt.clf()
        
    with open(os.path.join("Onium-Sigma","index.html"), 'w') as f:
        f.write( htmlTemplate.substitute( {"plots" : plots,
                                           "time"  :'<p>Generated at %s</p>' % datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")  }) )
