#! /usr/bin/python
# -*- mode: python -*-
from __future__ import print_function
import logging,sys,os
from string import Template
from HerwigInputs import *
import sys
if sys.version_info[:3] < (2,4,0):
    print ("rivet scripts require Python version >= 2.4.0... exiting")
    sys.exit(1)

if __name__ == "__main__":
    import logging
    from optparse import OptionParser, OptionGroup
    parser = OptionParser(usage="%prog name [...]")


simulation=""

numberOfAddedProcesses=0
def addProcess(thefactory,theProcess,Oas,Oew,scale,mergedlegs,NLOprocesses):
    global numberOfAddedProcesses
    global simulation
    numberOfAddedProcesses+=1
    res ="set "+thefactory+":OrderInAlphaS "+Oas+"\n"
    res+="set "+thefactory+":OrderInAlphaEW "+Oew+"\n"
    res+="do "+thefactory+":Process "+theProcess+" "
    if ( mergedlegs != 0 ):
      if simulation!="Merging":
          print ("simulation is not Merging, trying to add merged legs.")
          sys.exit(1)
      res+="["
      for j in range(mergedlegs):
        res+=" j "
      res+="]"
    res+="\n"
    if (NLOprocesses!=0):
       if simulation!="Merging":
          print ("simulation is not Merging, trying to add NLOProcesses.")
          sys.exit(1)
       res+="set MergingFactory:NLOProcesses %s \n" % NLOprocesses
    if ( scale != "" ):
      res+="set "+thefactory+":ScaleChoice /Herwig/MatrixElements/Matchbox/Scales/"+scale+"\n"
    return res

addedBRReweighter=False
def addBRReweighter():
  global addedBRReweighter
  if(addedBRReweighter):
    logging.error("Can only add BRReweighter once.")
    sys.exit(1)
  res="create Herwig::BranchingRatioReweighter /Herwig/Generators/BRReweighter\n"
  res+="insert /Herwig/Generators/EventGenerator:EventHandler:PostHadronizationHandlers 0 /Herwig/Generators/BRReweighter\n"
  addedBRReweighter=True
  return res

selecteddecaymode=False
def selectDecayMode(particle,decaymodes):
  global selecteddecaymode
  res="do /Herwig/Particles/"+particle+":SelectDecayModes"
  for decay in decaymodes:
    res+=" /Herwig/Particles/"+particle+"/"+decay
  res+="\n"
  selecteddecaymode=True
  return res

ME_Upsilon = """\
create Herwig::MEee2VectorMeson /Herwig/MatrixElements/MEUpsilon HwMELepton.so
set /Herwig/MatrixElements/MEUpsilon:VectorMeson /Herwig/Particles/Upsilon(4S)
set /Herwig/MatrixElements/MEUpsilon:Coupling 96.72794
""" + insert_ME("MEUpsilon")

(opts, args) = parser.parse_args()
## Check args
if len(args) != 1:
    logging.error("Must specify at least input file")
    sys.exit(1)

name = args[0]
print (name)
# work out name and type of the collider
(collider,have_hadronic_collider) = identifyCollider(name)

# workout the type of simulation
(simulation,templateName,parameterName,parameters)=identifySimulation(name,collider,have_hadronic_collider)

if simulation=="Merging" :
    thefactory="MergingFactory"
else :
    thefactory="Factory"
        
# settings for four flavour scheme
fourFlavour="""
read Matchbox/FourFlavourScheme.in
{bjetgroup}
set /Herwig/Cuts/MatchboxJetMatcher:Group bjet
""".format(bjetgroup=particlegroup(thefactory,'bjet','b','bbar','c', 'cbar',
                                   's','sbar','d','dbar','u','ubar','g'))

# work out the process and parameters
process=StringBuilder()

# DIS
if(collider=="DIS") :
    if(simulation=="") :
        if "NoME" in name :
            process = StringBuilder("set /Herwig/Shower/ShowerHandler:HardEmission None")
            parameterName=parameterName.replace("NoME-","")
            parameterName=parameterName.replace("DIS-" ,"")
        if "CC" in parameterName :
            process += insert_ME("MEDISCC")
        else :
            process += insert_ME("MEDISNC")
    elif(simulation=="Powheg") :
        if "CC" in parameterName :
            process = StringBuilder(insert_ME("PowhegMEDISCC"))
        else :
            process = StringBuilder(insert_ME("PowhegMEDISNC"))
    elif(simulation=="Matchbox" ) :
        if "CC" in name :
            if "e-" in parameterName :
                process = StringBuilder(addProcess(thefactory,"e- p -> nu_e j","0","2","",0,0))
            else :
                process = StringBuilder(addProcess(thefactory,"e+ p -> nu_ebar j","0","2","",0,0))
        else :
            if "e-" in parameterName :
                process = StringBuilder(addProcess(thefactory,"e- p -> e- j","0","2","",0,0))
            else :
                process = StringBuilder(addProcess(thefactory,"e+ p -> e+ j","0","2","",0,0))
    elif(simulation=="Merging" ) :
        if "CC" in name :
            if "e-" in parameterName :
                process = StringBuilder(addProcess(thefactory,"e- p -> e- j","0","2","",2,2))
            else :
                process = StringBuilder(addProcess(thefactory,"e+ p -> e+ j","0","2","",2,2))
        else :
            if "e-" in parameterName :
                process = StringBuilder(addProcess(thefactory,"e- p -> nu_e j","0","2","",2,2))
            else :
                process = StringBuilder(addProcess(thefactory,"e+ p -> nu_ebar j","0","2","",2,2))
    Q2Min=1.
    Q2Max=1000000.
    if "VeryLow" in name :
        Q2Max=20.
        parameterName=parameterName.replace("-VeryLowQ2","")
    elif "Low" in name :
        Q2Min=20.
        Q2Max=100.
        parameterName=parameterName.replace("-LowQ2","")
    elif "Med" in name :
        Q2Min=100.
        Q2Max=1000.
        parameterName=parameterName.replace("-MedQ2","")
    elif "High" in name :
        Q2Min=1000.
        parameterName=parameterName.replace("-HighQ2","")
    if "CC" in name :
        process+="set /Herwig/Cuts/ChargedCurrentCut:MaxQ2 2%s\nset /Herwig/Cuts/ChargedCurrentCut:MinQ2 %s\n" %(Q2Max,Q2Min)
    else :
        process+="set /Herwig/Cuts/NeutralCurrentCut:MaxQ2 2%s\nset /Herwig/Cuts/NeutralCurrentCut:MinQ2 %s\n" %(Q2Max,Q2Min)
# EE
elif(collider=="EE") :
    if(simulation=="") :
        if "gg" in parameterName :
            process = StringBuilder("create Herwig::MEee2Higgs2SM /Herwig/MatrixElements/MEee2Higgs2SM\n")
            process+=insert_ME("MEee2Higgs2SM","Gluon","Allowed")
        elif "LL" in parameterName :
            process = StringBuilder(insert_ME("MEee2gZ2ll"))
            process += "set /Herwig/MatrixElements/MEee2gZ2ll:Allowed Charged\n"
        elif "WW" in parameterName : 
            process = StringBuilder(insert_ME("MEee2VV"))
            process += "set /Herwig/MatrixElements/MEee2VV:Process WW\n"
        else :
            process  = StringBuilder(insert_ME("MEee2gZ2qq"))
            try :
                ecms = float(parameterName)
                if(ecms<=3.75) :
                    process+= "set /Herwig/MatrixElements/MEee2gZ2qq:MaximumFlavour 3\n"
                elif(ecms<=10.6) :
                    process+= "set /Herwig/MatrixElements/MEee2gZ2qq:MaximumFlavour 4\n"
            except :
                pass
    elif(simulation=="Powheg") :
        if "LL" in parameterName :
            process = StringBuilder(insert_ME("PowhegMEee2gZ2ll"))
            process += "set /Herwig/MatrixElements/PowhegMEee2gZ2ll:Allowed Charged\n"
        else :
            process = StringBuilder(insert_ME("PowhegMEee2gZ2qq"))
            try :
                ecms = float(parameterName)
                if(ecms<=3.75) :
                    process+= "set /Herwig/MatrixElements/PowhegMEee2gZ2qq:MaximumFlavour 3\n"
                elif(ecms<=10.6) :
                    process+= "set /Herwig/MatrixElements/PowhegMEee2gZ2qq:MaximumFlavour 4\n"
            except :
                pass
    elif(simulation=="Matchbox" ) :
        try :
            ecms = float(parameterName)
            if(ecms<=3.75) :
                process = StringBuilder(addProcess(thefactory,"e- e+ -> u ubar","0","2","",0,0))
                process+=addProcess(thefactory,"e- e+ -> d dbar","0","2","",0,0)
                process+=addProcess(thefactory,"e- e+ -> s sbar","0","2","",0,0)
            elif(ecms<=10.6) :
                process = StringBuilder(addProcess(thefactory,"e- e+ -> u ubar","0","2","",0,0))
                process+=addProcess(thefactory,"e- e+ -> d dbar","0","2","",0,0)
                process+=addProcess(thefactory,"e- e+ -> c cbar","0","2","",0,0)
                process+=addProcess(thefactory,"e- e+ -> s sbar","0","2","",0,0)
            else :
                process = StringBuilder(addProcess(thefactory,"e- e+ -> j j","0","2","",0,0))
        except:
            process = StringBuilder(addProcess(thefactory,"e- e+ -> j j","0","2","",0,0))
    elif(simulation=="Merging" ) :
        try :
            ecms = float(parameterName)
            if(ecms<=10.1) :
                process = StringBuilder(addProcess(thefactory,"e- e+ -> j j","0","2","",2,2))
                process+="read Matchbox/FourFlavourScheme.in"
            else :
                process = StringBuilder(addProcess(thefactory,"e- e+ -> j j","0","2","",2,2))
        except:
            process = StringBuilder(addProcess(thefactory,"e- e+ -> j j","0","2","",2,2))
# EE-Gamma
elif(collider=="EE-Gamma") :
    if(simulation=="") :
        if("mumu" in parameterName) :
            process = StringBuilder(insert_ME("MEgg2ff","Muon"))
            process +="set /Herwig/Cuts/Cuts:MHatMin 3.\n"
        elif( "tautau" in parameterName) :
            process = StringBuilder(insert_ME("MEgg2ff","Tau"))
            process +="set /Herwig/Cuts/Cuts:MHatMin 3.\n"
        elif( "Jets" in parameterName) :
            if("Direct" in parameterName ) :
                process = StringBuilder(insert_ME("MEgg2ff","Quarks"))
            elif("Single-Resolved" in parameterName ) :
                process = StringBuilder(insert_ME("MEGammaP2Jets",None,"Process","SubProcess"))
                process+= insert_ME("MEGammaP2Jets",None,"Process","SubProcess2")
            else :
                process = StringBuilder(insert_ME("MEQCD2to2"))
            process+="insert /Herwig/Cuts/Cuts:OneCuts[0] /Herwig/Cuts/JetKtCut"
            process+="set  /Herwig/Cuts/JetKtCut:MinKT 3."
        elif ("pi0"  in parameterName or "Eta" in parameterName or "EtaPrime" in parameterName or
              "EtaC" in parameterName):
            if "EtaC" in parameterName :
                mename="EtaC1S"
            elif "pi0" in parameterName :
                mename="pi0"
            elif "EtaPrime" in parameterName :
                mename="etaPrime"
            elif "Eta" in parameterName :
                mename="eta"
            process = StringBuilder(insert_ME("MEff2ff%s" % mename) )
            if "10.58" in parameterName: 
                process+="cp /Herwig/MatrixElements/MEff2ff%s /Herwig/MatrixElements/MEff2ff%s2" % (mename,mename)
                process+= insert_ME("MEff2ff%s2" % mename)
                process+="cp /Herwig/MatrixElements/MEff2ff%s /Herwig/MatrixElements/MEff2ff%s3" % (mename,mename)
                process+= insert_ME("MEff2ff%s3" % mename)
                process+="set /Herwig/MatrixElements/MEff2ff%s:Q2_1Min 0.  " % mename
                process+="set /Herwig/MatrixElements/MEff2ff%s:Q2_1Max 1.  " % mename
                process+="set /Herwig/MatrixElements/MEff2ff%s:Q2_2Min 1.  " % mename
                process+="set /Herwig/MatrixElements/MEff2ff%s:Q2_2Max 1e10" % mename
                process+="set /Herwig/MatrixElements/MEff2ff%s2:Q2_2Min 0.  " % mename
                process+="set /Herwig/MatrixElements/MEff2ff%s2:Q2_2Max 1.  " % mename
                process+="set /Herwig/MatrixElements/MEff2ff%s2:Q2_1Min 1.  " % mename
                process+="set /Herwig/MatrixElements/MEff2ff%s2:Q2_1Max 1e10" % mename
                process+="set /Herwig/MatrixElements/MEff2ff%s3:Q2_2Min 1.  " % mename
                process+="set /Herwig/MatrixElements/MEff2ff%s3:Q2_2Max 1e10" % mename
                process+="set /Herwig/MatrixElements/MEff2ff%s3:Q2_1Min 1.  " % mename
                process+="set /Herwig/MatrixElements/MEff2ff%s3:Q2_1Max 1e10" % mename
        elif "ChiC0_2P" in parameterName :
            process = StringBuilder(insert_ME("MEff2ffChiC02P"))
        elif "ChiC2_2P" in parameterName :
            process = StringBuilder(insert_ME("MEff2ffChiC22P"))
        elif "ChiC2" in parameterName :
            process = StringBuilder(insert_ME("MEff2ffChiC21P"))
        elif "Onium" in parameterName :
            process = StringBuilder(insert_ME("MEff2ffEtaC1S") )
            process+= insert_ME("MEff2ffEtaC2S" )
            process+= insert_ME("MEff2ffChiC01P")
            process+= insert_ME("MEff2ffChiC21P")
            process+= insert_ME("MEff2ffChiC22P")
            process+= insert_ME("MEff2ffEtaB1S" )
            process+= insert_ME("MEff2ffEtaB2S" )
            process+= insert_ME("MEff2ffChiB01P")
            process+= insert_ME("MEff2ffChiB21P")
            process+= insert_ME("MEff2ffChiB02P")
            process+= insert_ME("MEff2ffChiB22P")
            process+= insert_ME("MEff2ffChiB03P")
            process+= insert_ME("MEff2ffChiB23P")
            process+= insert_ME("MEff2ffEtaB21D")
        else :
            print ("process not supported for Gamma Gamma processes at EE")
            quit()
    else :
        print ("Only internal matrix elements currently supported for Gamma Gamma processes at EE")
        quit()
elif(collider=="GammaGamma") :
    if(simulation=="") :
        if("mumu" in parameterName) :
            process = StringBuilder(insert_ME("MEgg2ff"))
            process +="set /Herwig/MatrixElements/gg2ffAmp:Process Muon\n"
            process +="set /Herwig/Cuts/Cuts:MHatMin 3.\n"
        else :
            print ("process not supported for Gamma Gamma processes at EE")
            quit()
    else :
        print ("Only internal matrix elements currently supported for Gamma Gamma processes at EE")
        quit()
# TVT
elif(collider=="TVT") :
    process = StringBuilder("set /Herwig/Generators/EventGenerator:EventHandler:BeamB /Herwig/Particles/pbar-\n")
    ecms=1960.
    if "Run-II" in parameterName :  ecms = 1960.0
    elif "Run-I" in parameterName : ecms = 1800.0
    elif "900" in parameterName :   ecms = 900.0
    elif "630" in parameterName :   ecms = 630.0
    elif "300" in parameterName :   ecms = 300.0
    process+=collider_lumi(ecms)
    if(simulation=="") :
        if "PromptPhoton" in parameterName :
            process+=insert_ME("MEGammaJet")
            process+="set /Herwig/Cuts/PhotonKtCut:MinKT 15.\n"
        elif "DiPhoton-GammaGamma" in parameterName :
            process+=insert_ME("MEGammaGamma")
            process+="set /Herwig/Cuts/PhotonKtCut:MinKT 5.\n"
            parameterName=parameterName.replace("-GammaGamma","")
        elif "DiPhoton-GammaJet" in parameterName :
            process+=insert_ME("MEGammaJet")
            process+="set /Herwig/Cuts/PhotonKtCut:MinKT 5.\n"
            parameterName=parameterName.replace("-GammaJet","")
        elif "UE" in parameterName :
            if "Dipole" in parameters["shower"]:
                process+="read snippets/MB-DipoleShower.in\n"
            else:
                process+="read snippets/MB.in\n"
            process+="read snippets/Diffraction.in\n"
                
            process += "set /Herwig/Decays/DecayHandler:LifeTimeOption 0\n"
            process += "set /Herwig/Decays/DecayHandler:MaxLifeTime 10*mm\n"
        elif "Jets" in parameterName :
            process+=insert_ME("MEQCD2to2")
            process+="set /Herwig/UnderlyingEvent/MPIHandler:IdenticalToUE 0\n"
            if "DiJets" in name :
                process +=jet_kt_cut( 30.)
                cuts=[100.,300.,600.,900.,ecms]
                for i in range(1,len(cuts)) :
                    tstring = "-DiJets-%s"%i
                    if tstring in parameterName :
                        process+=mhat_cut(cuts[i-1],cuts[i])
                        parameterName=parameterName.replace(tstring,"-DiJets")
            else :
                if "Run" in parameterName :
                    cuts=[5.,20.,40.,80.,160.,320.]
                elif "300" in parameterName :
                    cuts=[5.,]
                elif "630" in parameterName :
                    cuts=[5.,20.,40.]
                elif "900" in parameterName :
                    cuts=[5.,]
                cuts.append(ecms)
                for i in range(1,len(cuts)) :
                    tstring = "-Jets-%s"%i
                    if tstring in parameterName :
                        process+=jet_kt_cut(cuts[i-1],cuts[i])
                        parameterName=parameterName.replace(tstring,"-Jets")
        elif "Run-I-WZ" in parameterName :
            process+=insert_ME("MEqq2W2ff","Electron")
            process+=insert_ME("MEqq2gZ2ff","Electron")
        elif "Run-II-W" in parameterName or "Run-I-W" in parameterName :
            process+=insert_ME("MEqq2W2ff","Electron")
        elif "Run-II-Z-e" in parameterName or "Run-I-Z" in parameterName :
            process +=insert_ME("MEqq2gZ2ff","Electron")
        elif "Run-II-Z-LowMass-mu" in parameterName :
            process +=insert_ME("MEqq2gZ2ff","Muon")
            process+=addLeptonPairCut("25","70")
        elif "Run-II-Z-HighMass-mu" in parameterName :
            process +=insert_ME("MEqq2gZ2ff","Muon")
            process+=addLeptonPairCut("150","600")
        elif "Run-II-Z-mu" in parameterName :
            process +=insert_ME("MEqq2gZ2ff","Muon")
    elif(simulation=="Powheg") :
        if "Run-I-WZ" in parameterName :
            process+=insert_ME("PowhegMEqq2W2ff","Electron")
            process+=insert_ME("PowhegMEqq2gZ2ff","Electron")
        elif "Run-II-W" in parameterName or "Run-I-W" in parameterName :
            process+=insert_ME("PowhegMEqq2W2ff","Electron")
        elif "Run-II-Z-e" in parameterName or "Run-I-Z" in parameterName :
            process+=insert_ME("PowhegMEqq2gZ2ff","Electron")
        elif "Run-II-Z-LowMass-mu" in parameterName :
            process+=insert_ME("PowhegMEqq2gZ2ff","Muon")
            process+=addLeptonPairCut("25","70")
        elif "Run-II-Z-HighMass-mu" in parameterName :
            process+=insert_ME("PowhegMEqq2gZ2ff","Muon")
            process+=addLeptonPairCut("150","600")
        elif "Run-II-Z-mu" in parameterName :
            process+=insert_ME("PowhegMEqq2gZ2ff","Muon")
        elif "DiPhoton-GammaGamma" in parameterName :
            process+=insert_ME("MEGammaGammaPowheg","GammaGamma")
            process+=insert_ME("MEGammaGamma","gg")
            process+="set /Herwig/Cuts/PhotonKtCut:MinKT 5.\n"
            process+=jet_kt_cut(5.)
            parameterName=parameterName.replace("-GammaGamma","")
        elif "DiPhoton-GammaJet" in parameterName :
            process+=insert_ME("MEGammaGammaPowheg","VJet")
            process+="set /Herwig/Cuts/PhotonKtCut:MinKT 5.\n"
            process+=jet_kt_cut(5.)
            parameterName=parameterName.replace("-GammaJet","")
    elif(simulation=="Matchbox" or simulation=="Merging" ) :
        if "Jets" in parameterName :
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p p -> j j","2","0","MaxJetPtScale",0,0)
            elif(simulation=="Merging"):
                process+=addProcess(thefactory,"p p -> j j","2","0","MaxJetPtScale",1,0)
            if "DiJets" in parameterName :
                process+=addFirstJet("30")+addSecondJet("25")
                cuts=[100.,300.,600.,900.,ecms]
                for i in range(1,len(cuts)) :
                    tstring = "-DiJets-%s"%i
                    if tstring in parameterName :
                        process+=addJetPairCut(cuts[i-1],cuts[i])
                        parameterName=parameterName.replace(tstring,"-DiJets")
            else :
                if "Run" in parameterName :
                    cuts=[5.,20.,40.,80.,160.,320.]
                elif "300" in parameterName :
                    cuts=[5.,]
                elif "630" in parameterName :
                    cuts=[5.,20.,40.]
                elif "900" in parameterName :
                    cuts=[5.,]
                cuts.append(ecms)
                for i in range(1,len(cuts)) :
                    tstring = "-Jets-%s"%i
                    if tstring in parameterName :
                        process+=addFirstJet(cuts[i-1],cuts[i])
                        parameterName=parameterName.replace(tstring,"-Jets")
        elif "Run-I-WZ" in parameterName :
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p pbar e+ e-","0","2","LeptonPairMassScale",0,0)
                process+=addProcess(thefactory,"p pbar e+ nu","0","2","LeptonPairMassScale",0,0)
                process+=addProcess(thefactory,"p pbar e- nu","0","2","LeptonPairMassScale",0,0)
            elif(simulation=="Merging"):
                process+=particlegroup(thefactory,'epm','e+','e-')
                process+=particlegroup(thefactory,'epmnu','e+','e-','nu_e','nu_ebar')
                process+=addProcess(thefactory,"p pbar epm epmnu","0","2","LeptonPairMassScale",2,2)
            process+=addLeptonPairCut("60","120")
        elif "Run-II-W" in parameterName or "Run-I-W" in parameterName :
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p pbar e+ nu","0","2","LeptonPairMassScale",0,0)
                process+=addProcess(thefactory,"p pbar e- nu","0","2","LeptonPairMassScale",0,0)
            elif(simulation=="Merging"):
                process+=particlegroup(thefactory,'epm','e+','e-')
                process+=addProcess(thefactory,"p pbar epm nu","0","2","LeptonPairMassScale",2,2)
            process+=addLeptonPairCut("60","120")
        elif "Run-II-Z-e" in parameterName or "Run-I-Z" in parameterName :
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p pbar e+ e-","0","2","LeptonPairMassScale",0,0)
            elif(simulation=="Merging"):
                process+=addProcess(thefactory,"p pbar e+ e-","0","2","LeptonPairMassScale",2,2)
            process+=addLeptonPairCut("60","120")
        elif "Run-II-Z-LowMass-mu" in parameterName :
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p pbar mu+ mu-","0","2","LeptonPairMassScale",0,0)
            elif(simulation=="Merging"):
                process+=addProcess(thefactory,"p pbar mu+ mu-","0","2","LeptonPairMassScale",2,2)
            process+=addLeptonPairCut("25","70")
        elif "Run-II-Z-HighMass-mu" in parameterName :
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p pbar mu+ mu-","0","2","LeptonPairMassScale",0,0)
            elif(simulation=="Merging"):
                process+=addProcess(thefactory,"p pbar mu+ mu-","0","2","LeptonPairMassScale",2,2)
            process+=addLeptonPairCut("150","600")
        elif "Run-II-Z-mu" in parameterName :
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p pbar mu+ mu-","0","2","LeptonPairMassScale",0,0)
            elif(simulation=="Merging"):
                process+=addProcess(thefactory,"p pbar mu+ mu-","0","2","LeptonPairMassScale",2,2)
            process+=addLeptonPairCut("60","120")
# Star
elif(collider=="Star" ) :
    process = StringBuilder("set /Herwig/Decays/DecayHandler:LifeTimeOption 0\n")
    process+= "set /Herwig/Decays/DecayHandler:MaxLifeTime 10*mm\n"
    process+= "set /Herwig/Generators/EventGenerator:EventHandler:BeamB /Herwig/Particles/p+\n"
    process+= collider_lumi(200.0)
    process+= "set /Herwig/Cuts/Cuts:X2Min 0.01\n"
    if(simulation=="") :
        if "UE" in parameterName :
            if "Dipole" in parameters["shower"]:
                process+="read snippets/MB-DipoleShower.in\n"
            else:
                process+="read snippets/MB.in\n"    
            process+="read snippets/Diffraction.in\n"
            
            
        else :
            process+=insert_ME("MEQCD2to2")
            process+="set /Herwig/UnderlyingEvent/MPIHandler:IdenticalToUE 0\n"
            if "Jets-1" in parameterName :   process+=jet_kt_cut(2.)
            elif "Jets-2" in parameterName : process+=jet_kt_cut(5.)
            elif "Jets-3" in parameterName : process+=jet_kt_cut(20.)
            elif "Jets-4" in parameterName : process+=jet_kt_cut(25.)
    else :
        logging.error("Star not supported for %s " % simulation)
        sys.exit(1)
# ISR and SppS
elif ( collider=="ISR" or collider =="SppS" or collider == "SPS" or collider == "Fermilab" ) :
    process = StringBuilder("set /Herwig/Decays/DecayHandler:LifeTimeOption 0\n")
    process+="set /Herwig/Decays/DecayHandler:MaxLifeTime 10*mm\n"
    if(collider=="SppS") :
        process = StringBuilder("set /Herwig/Generators/EventGenerator:EventHandler:BeamB /Herwig/Particles/pbar-\n")
    if    "17.4" in parameterName : process+=collider_lumi( 17.4)
    elif  "27.4" in parameterName : process+=collider_lumi( 27.4)
    elif  "30"   in parameterName : process+=collider_lumi( 30.4)
    elif  "38.8" in parameterName : process+=collider_lumi( 38.8)
    elif  "44"   in parameterName : process+=collider_lumi( 44.4)
    elif  "53"   in parameterName : process+=collider_lumi( 53.0)
    elif  "62"   in parameterName : process+=collider_lumi( 62.2)
    elif  "63"   in parameterName : process+=collider_lumi( 63.0)
    elif "200"   in parameterName : process+=collider_lumi(200.0)
    elif "500"   in parameterName : process+=collider_lumi(500.0)
    elif "546"   in parameterName : process+=collider_lumi(546.0)
    elif "900"   in parameterName : process+=collider_lumi(900.0)
    if "UE" in parameterName :
        if(simulation=="") :
            if "Dipole" in parameters["shower"]:
                process+="read snippets/MB-DipoleShower.in\n"
            else:
                process+="read snippets/MB.in\n"
                process+="read snippets/Diffraction.in\n"
        else :
            logging.error(" SppS and ISR not supported for %s " % simulation)
            sys.exit(1)
    elif "Z-mu" in parameterName :
        if simulation == "" :
            process+=insert_ME("MEqq2gZ2ff","Muon")
            process+=mhat_minm_maxm(2,2,20)
        elif simulation == "Powheg" :
            process+=insert_ME("PowhegMEqq2gZ2ff","Muon")
            process+=mhat_minm_maxm(2,2,20)
        elif(simulation=="Matchbox"):
            process+=addProcess(thefactory,"p p mu+ mu-","0","2","LeptonPairMassScale",0,0)
            process+=addLeptonPairCut("2","20")
        elif(simulation=="Merging"):
            process+=addProcess(thefactory,"p p mu+ mu-","0","2","LeptonPairMassScale",2,2)
            process+=addLeptonPairCut("2","20")
        else :
            logging.error(" SppS and ISR not supported for %s " % simulation)
            sys.exit(1)
    else :
        logging.error(" Process not supported for SppS and ISR %s " % parameterName )
        sys.exit(1)
        
# LHC
elif(collider=="LHC") :
    ecms=7000.0
    if   parameterName.startswith("7-")   : ecms = 7000.0
    elif parameterName.startswith("8-")   : ecms = 8000.0
    elif parameterName.startswith("13-")  : ecms = 13000.0
    elif parameterName.startswith("900")  : ecms = 900.0
    elif parameterName.startswith("2360") : ecms = 2360.0
    elif parameterName.startswith("2760") : ecms = 2760.0
    elif parameterName.startswith("5-")   : ecms = 5000.0
    else                                  : ecms = 7000.0
    process = StringBuilder(collider_lumi(ecms))
    if(simulation=="") :
        if "VBF" in parameterName :
            process+=insert_ME("MEPP2HiggsVBF")
            if "GammaGamma" in parameterName :
               process+=selectDecayMode("h0",["h0->gamma,gamma;"])
               addedBRReweighter = True
            elif "WW" in parameterName :
               process+=selectDecayMode("h0",["h0->W+,W-;"])
               addedBRReweighter = True
            elif "ZZ" in parameterName :
               process+=selectDecayMode("h0",["h0->Z0,Z0;"])
               addedBRReweighter = True
            elif "8-" not in parameterName :
                process+=selectDecayMode("h0",["h0->tau-,tau+;"])
                addedBRReweighter = True
                process+="set /Herwig/Particles/tau-:Stable Stable\n"
                
        elif "ggHJet" in parameterName :
            process+=selectDecayMode("h0",["h0->tau-,tau+;"])
            addedBRReweighter = True
            process+="set /Herwig/Particles/tau-:Stable Stable\n"
            process+=insert_ME("MEHiggsJet")
            process+=jet_kt_cut(20.)
        elif "ggH" in parameterName :
            process+=insert_ME("MEHiggs")
            process+=insert_ME("MEHiggsJet","qqbar")
            process+=jet_kt_cut(0.0)
            if "GammaGamma" in parameterName :
               process+=selectDecayMode("h0",["h0->gamma,gamma;"])
               addedBRReweighter = True
            elif "WW" in parameterName :
               process+=selectDecayMode("h0",["h0->W+,W-;"])
               addedBRReweighter = True
            elif "ZZ" in parameterName :
               process+=selectDecayMode("h0",["h0->Z0,Z0;"])
               addedBRReweighter = True
            elif "8-" not in parameterName :
                process+=selectDecayMode("h0",["h0->tau-,tau+;"])
                addedBRReweighter = True
                process+="set /Herwig/Particles/tau-:Stable Stable\n"
                
        elif "PromptPhoton" in parameterName :
            process+=insert_ME("MEGammaJet")
            if "PromptPhoton-1" in parameterName :
                process+="set /Herwig/Cuts/PhotonKtCut:MinKT 5.\n"
                process+="set /Herwig/Cuts/PhotonKtCut:MaxKT 25.\n"
                parameterName=parameterName.replace("-1","")
            elif "PromptPhoton-2" in parameterName :
                process+="set /Herwig/Cuts/PhotonKtCut:MinKT 25.\n"
                process+="set /Herwig/Cuts/PhotonKtCut:MaxKT 80.\n"
                parameterName=parameterName.replace("-2","")
            elif "PromptPhoton-3" in parameterName :
                process+="set /Herwig/Cuts/PhotonKtCut:MinKT 80.\n"
                process+="set /Herwig/Cuts/PhotonKtCut:MaxKT 150.\n"
                parameterName=parameterName.replace("-3","")
            elif "PromptPhoton-4" in parameterName :
                process+="set /Herwig/Cuts/PhotonKtCut:MinKT 150.\n"
                process+="set /Herwig/Cuts/PhotonKtCut:MaxKT 500.\n"
                parameterName=parameterName.replace("-4","")
            elif "PromptPhoton-5" in parameterName :
                process+="set /Herwig/Cuts/PhotonKtCut:MinKT 500.\n"
                parameterName=parameterName.replace("-5","")
        elif "DiPhoton-GammaGamma" in parameterName :
            process+=insert_ME("MEGammaGamma")
            process+="set /Herwig/Cuts/PhotonKtCut:MinKT 5.\n"
            parameterName=parameterName.replace("-GammaGamma","")
        elif "DiPhoton-GammaJet" in parameterName :
            process+=insert_ME("MEGammaJet")
            process+="set /Herwig/Cuts/PhotonKtCut:MinKT 5.\n"
            parameterName=parameterName.replace("-GammaJet","")
        elif "8-WH" in parameterName :
            process+=insert_ME("MEPP2WH")
            process+=jet_kt_cut(0.0)
            if "GammaGamma" in parameterName :
               process+=selectDecayMode("h0",["h0->gamma,gamma;"])
               addedBRReweighter = True
            elif "WW" in parameterName :
               process+=selectDecayMode("h0",["h0->W+,W-;"])
               addedBRReweighter = True
            elif "ZZ" in parameterName :
               process+=selectDecayMode("h0",["h0->Z0,Z0;"])
               addedBRReweighter = True
        elif "8-ZH" in parameterName :
            process+=insert_ME("MEPP2ZH")
            process+=jet_kt_cut(0.0)
            if "GammaGamma" in parameterName :
               process+=selectDecayMode("h0",["h0->gamma,gamma;"])
               addedBRReweighter = True
            elif "WW" in parameterName :
               process+=selectDecayMode("h0",["h0->W+,W-;"])
               addedBRReweighter = True
            elif "ZZ" in parameterName :
               process+=selectDecayMode("h0",["h0->Z0,Z0;"])
               addedBRReweighter = True
        elif "WH" in parameterName :
            process+=selectDecayMode("h0",["h0->b,bbar;"])
            process+=selectDecayMode("W+",["W+->nu_e,e+;",
                                           "W+->nu_mu,mu+;"])
            addedBRReweighter = True
            process+=insert_ME("MEPP2WH")
            process+=jet_kt_cut(0.0)
        elif "ZH" in parameterName :
            process+=selectDecayMode("h0",["h0->b,bbar;"])
            process+=selectDecayMode("Z0",["Z0->e-,e+;",
                                           "Z0->mu-,mu+;"])
            addedBRReweighter = True
            process+=insert_ME("MEPP2ZH")
            process+=jet_kt_cut(0.0)
        elif "UE"  in parameterName or "Cent" in parameterName :
            if "Dipole" in parameters["shower"]:
                process+="read snippets/MB-DipoleShower.in\n"
            else:
                process+="set /Herwig/Shower/ShowerHandler:IntrinsicPtGaussian 2.2*GeV\n"                
                process+="read snippets/MB.in\n"
            process+="read snippets/Diffraction.in\n"
            if "Long" in parameterName :
                process += "set /Herwig/Decays/DecayHandler:MaxLifeTime 100*mm\n"
        elif "8-DiJets" in parameterName or "7-DiJets" in parameterName or "13-DiJets" in parameterName :
            process+=insert_ME("MEQCD2to2")
            process+="set MEQCD2to2:MaximumFlavour 5\n"
            process+="set /Herwig/UnderlyingEvent/MPIHandler:IdenticalToUE 0\n"
            if "13-DiJets" not in parameterName :
                if "-A" in parameterName :
                    process+=jet_kt_cut(45.)
                    process+="set /Herwig/Cuts/JetKtCut:MinEta -3.\n"
                    process+="set /Herwig/Cuts/JetKtCut:MaxEta  3.\n"
                elif "-B" in parameterName :
                    process+=jet_kt_cut(20.)
                    process+="set /Herwig/Cuts/JetKtCut:MinEta -2.7\n"
                    process+="set /Herwig/Cuts/JetKtCut:MaxEta  2.7\n"
                elif "-C" in parameterName :
                    process+=jet_kt_cut(20.)
                    process+="set /Herwig/Cuts/JetKtCut:MinEta -4.8\n"
                    process+="set /Herwig/Cuts/JetKtCut:MaxEta  4.8\n"
            else :
                if "-A" in parameterName :
                    process+=jet_kt_cut(60.)
                    process+="set /Herwig/Cuts/JetKtCut:MinEta -3.\n"
                    process+="set /Herwig/Cuts/JetKtCut:MaxEta  3.\n"
                elif "-B" in parameterName :
                    process+=jet_kt_cut(180.)
                    process+="set /Herwig/Cuts/JetKtCut:MinEta -3.\n"
                    process+="set /Herwig/Cuts/JetKtCut:MaxEta  3.\n"
                
            if "DiJets-1" in parameterName   : process+=mhat_cut(90.)
            elif "DiJets-2" in parameterName : process+=mhat_cut(200.)
            elif "DiJets-3" in parameterName : process+=mhat_cut(450.)
            elif "DiJets-4" in parameterName : process+=mhat_cut(750.)
            elif "DiJets-5" in parameterName : process+=mhat_cut(950.)
            elif "DiJets-6" in parameterName : process+=mhat_cut(1550.)
            elif "DiJets-7" in parameterName : process+=mhat_cut(2150.)
            elif "DiJets-8" in parameterName : process+=mhat_cut(2750.)
            elif "DiJets-9" in parameterName : process+=mhat_cut(3750.)
            elif "DiJets-10" in parameterName : process+=mhat_cut(4750.)
            elif "DiJets-11" in parameterName : process+=mhat_cut(5750.)
        elif(      "7-Jets" in parameterName 
               or  "8-Jets" in parameterName 
               or "13-Jets" in parameterName 
               or "2760-Jets" in parameterName 
            ) :
            process+=insert_ME("MEQCD2to2")
            process+="set MEQCD2to2:MaximumFlavour 5\n"
            process+="set /Herwig/UnderlyingEvent/MPIHandler:IdenticalToUE 0\n"
            if "Jets-10" in parameterName  : process+=jet_kt_cut(1800.)
            elif "Jets-0" in parameterName : process+=jet_kt_cut(5.)
            elif "Jets-1" in parameterName : process+=jet_kt_cut(10.)
            elif "Jets-2" in parameterName : process+=jet_kt_cut(20.)
            elif "Jets-3" in parameterName : process+=jet_kt_cut(40.)
            elif "Jets-4" in parameterName : process+=jet_kt_cut(70.)
            elif "Jets-5" in parameterName : process+=jet_kt_cut(150.)
            elif "Jets-6" in parameterName : process+=jet_kt_cut(200.)
            elif "Jets-7" in parameterName : process+=jet_kt_cut(300.)
            elif "Jets-8" in parameterName : process+=jet_kt_cut(500.)
            elif "Jets-9" in parameterName : process+=jet_kt_cut(800.)
        elif( "-Charm" in parameterName  or "-Bottom" in parameterName ) :
            
            if("8-Bottom" in parameterName) :
                addBRReweighter()
                process+=selectDecayMode("Jpsi",["Jpsi->mu-,mu+;"])
                
            if "Bottom" in parameterName :
                process+="cp MEHeavyQuark MEBottom\n" 
                process+="set MEBottom:QuarkType Bottom\n"
                process+=insert_ME("MEBottom")
            else : 
                process+="cp MEHeavyQuark MECharm\n" 
                process+="set MECharm:QuarkType Charm\n"
                process+=insert_ME("MECharm")
            process+="set /Herwig/UnderlyingEvent/MPIHandler:IdenticalToUE 0\n"
            if "-0" in parameterName :
                if "Bottom" in parameterName :
                    process+="set MEBottom:Process Pair\n"
                    process+=jet_kt_cut(0.)
                else :
                    process+=jet_kt_cut(1.)
            elif "-1" in parameterName : process+=jet_kt_cut(5.)
            elif "-2" in parameterName : process+=jet_kt_cut(15.)
            elif "-3" in parameterName : process+=jet_kt_cut(20.)
            elif "-4" in parameterName : process+=jet_kt_cut(50.)
            elif "-5" in parameterName : process+=jet_kt_cut(80.)
            elif "-6" in parameterName : process+=jet_kt_cut(110.)
            elif "-7" in parameterName : process+=jet_kt_cut(30.)+mhat_cut(90.)
            elif "-8" in parameterName : process+=jet_kt_cut(30.)+mhat_cut(340.)
            elif "-9" in parameterName : process+=jet_kt_cut(30.)+mhat_cut(500.)
        elif "Top-L" in parameterName :
            process+="set MEHeavyQuark:QuarkType Top\n"
            process+=insert_ME("MEHeavyQuark")
            process+=selectDecayMode("t",["t->nu_e,e+,b;",
                                          "t->nu_mu,mu+,b;"])
            process+=addBRReweighter()
            
        elif "Top-SL" in parameterName :
            process+="set MEHeavyQuark:QuarkType Top\n"
            process+=insert_ME("MEHeavyQuark")
            process+="set /Herwig/Particles/t:Synchronized Not_synchronized\n"
            process+="set /Herwig/Particles/tbar:Synchronized Not_synchronized\n"
            process+=selectDecayMode("t",["t->nu_e,e+,b;","t->nu_mu,mu+,b;"])
            process+=selectDecayMode("tbar",["tbar->b,bbar,cbar;",
                                             "tbar->bbar,cbar,d;",
                                             "tbar->bbar,cbar,s;",
                                             "tbar->bbar,s,ubar;",
                                             "tbar->bbar,ubar,d;"])
            process+=addBRReweighter()
            
        elif "Top-All" in parameterName :
            process+="set MEHeavyQuark:QuarkType Top\n"
            process+=insert_ME("MEHeavyQuark")
        elif "WZ" in parameterName :
            process+=insert_ME("MEPP2VV","WZ")
            process+=selectDecayMode("W+",["W+->nu_e,e+;",
                                           "W+->nu_mu,mu+;"])
            process+=selectDecayMode("W-",["W-->nu_ebar,e-;",
                                           "W-->nu_mubar,mu-;"])
            process+=selectDecayMode("Z0",["Z0->e-,e+;",
                                           "Z0->mu-,mu+;"])
            addedBRReweighter = True
            
        elif "WW-emu" in parameterName :
            process+=insert_ME("MEPP2VV","WW")
            process+="set /Herwig/Particles/W+:Synchronized 0\n"
            process+="set /Herwig/Particles/W-:Synchronized 0\n"
            process+=selectDecayMode("W+",["W+->nu_e,e+;"])
            process+=selectDecayMode("W-",["W-->nu_mubar,mu-;"])
            addedBRReweighter = True
            
        elif "WW-ll" in parameterName :
            process+=insert_ME("MEPP2VV","WW")
            process+=selectDecayMode("W+",["W+->nu_e,e+;","W+->nu_mu,mu+;","W+->nu_tau,tau+;"])
            addedBRReweighter = True
            
        elif "ZZ-ll" in parameterName :
            process+=insert_ME("MEPP2VV","ZZ")
            process+=selectDecayMode("Z0",["Z0->e-,e+;",
                                           "Z0->mu-,mu+;",
                                           "Z0->tau-,tau+;"])
            addedBRReweighter = True

        elif "ZZ-lv" in parameterName :
            process+=insert_ME("MEPP2VV","ZZ")
            process+=selectDecayMode("Z0",["Z0->e-,e+;",
                                           "Z0->mu-,mu+;",
                                           "Z0->tau-,tau+;",
                                           "Z0->nu_e,nu_ebar;",
                                           "Z0->nu_mu,nu_mubar;",
                                           "Z0->nu_tau,nu_taubar;"])
            addedBRReweighter = True
        elif "W-e" in parameterName :
            process+=insert_ME("MEqq2W2ff","Electron")
        elif "W-mu" in parameterName :
            process+=insert_ME("MEqq2W2ff","Muon")
        elif "Z-e" in parameterName or "Z-mu" in parameterName :
            if "Z-e" in parameterName:
                process+=insert_ME("MEqq2gZ2ff","Electron")
            else :
                process+=insert_ME("MEqq2gZ2ff","Muon")
            mcuts=[10,35,75,110,400,ecms]
            for i in range(1,6) :
                tstring = "-Mass%s"%i
                if tstring in parameterName :
                    process+=mhat_minm_maxm(mcuts[i-1],mcuts[i-1],mcuts[i])
                    parameterName=parameterName.replace(tstring,"")
        elif "Z-nu" in parameterName :
            process+=insert_ME("MEqq2gZ2ff","Neutrinos")
        elif "W-Jet" in parameterName :
            process+=insert_ME("MEWJet","Electron","WDecay")
            if "W-Jet-1-e" in parameterName :
                process+="set /Herwig/Cuts/WBosonKtCut:MinKT 100.0*GeV\n"
                parameterName=parameterName.replace("W-Jet-1-e","W-Jet-e")
            elif "W-Jet-2-e" in parameterName :
                process+="set /Herwig/Cuts/WBosonKtCut:MinKT 190.0*GeV\n"
                parameterName=parameterName.replace("W-Jet-2-e","W-Jet-e")
            elif "W-Jet-3-e" in parameterName :
                process+="set /Herwig/Cuts/WBosonKtCut:MinKT 270.0*GeV\n"
                parameterName=parameterName.replace("W-Jet-3-e","W-Jet-e")
        elif "Z-Jet" in parameterName :
            if "-e" in parameterName :
                process+=insert_ME("MEZJet","Electron","ZDecay")
                if "Z-Jet-0-e" in parameterName :
                    process+="set /Herwig/Cuts/ZBosonKtCut:MinKT 35.0*GeV\n"
                    parameterName=parameterName.replace("Z-Jet-0-e","Z-Jet-e")
                elif "Z-Jet-1-e" in parameterName :
                    process+="set /Herwig/Cuts/ZBosonKtCut:MinKT 100.0*GeV\n"
                    parameterName=parameterName.replace("Z-Jet-1-e","Z-Jet-e")
                elif "Z-Jet-2-e" in parameterName :
                    process+="set /Herwig/Cuts/ZBosonKtCut:MinKT 190.0*GeV\n"
                    parameterName=parameterName.replace("Z-Jet-2-e","Z-Jet-e")
                elif "Z-Jet-3-e" in parameterName :
                    process+="set /Herwig/Cuts/ZBosonKtCut:MinKT 270.0*GeV\n"
                    parameterName=parameterName.replace("Z-Jet-3-e","Z-Jet-e")
            else :
                process+=insert_ME("MEZJet","Muon","ZDecay")
                process+="set /Herwig/Cuts/ZBosonKtCut:MinKT 35.0*GeV\n"
                parameterName=parameterName.replace("Z-Jet-0-mu","Z-Jet-mu")
        elif "WGamma" in parameterName :
            process+=insert_ME("MEPP2VGamma","1")
            process+="set MEPP2VGamma:MassOption 1"
            process+="set /Herwig/Cuts/PhotonKtCut:MinKT 10.\n"
            
            
            if "-e" in parameterName :
                process+=selectDecayMode("W+",["W+->nu_e,e+;"])
                addedBRReweighter=True
            else :
                process+=selectDecayMode("W+",["W+->nu_mu,mu+;"])
                addedBRReweighter=True
        elif "ZGamma" in parameterName :
            process+=insert_ME("MEPP2VGamma","2")
            process+="set /Herwig/Cuts/PhotonKtCut:MinKT 10.\n"
            if "-e" in parameterName :
                process+=selectDecayMode("Z0",["Z0->e-,e+;"])
                addedBRReweighter=True
            else :
                process+=selectDecayMode("Z0",["Z0->mu-,mu+;"])
                addedBRReweighter=True
        else :
            logging.error(" Process %s not supported for internal matrix elements" % name)
            sys.exit(1)
    elif(simulation=="Powheg") :
        if "VBF" in parameterName :
            process+=insert_ME("PowhegMEPP2HiggsVBF")
            if "GammaGamma" in parameterName :
               process+=selectDecayMode("h0",["h0->gamma,gamma;"])
               addedBRReweighter = True
            elif "WW" in parameterName :
               process+=selectDecayMode("h0",["h0->W+,W-;"])
               addedBRReweighter = True
            elif "ZZ" in parameterName :
               process+=selectDecayMode("h0",["h0->Z0,Z0;"])
               addedBRReweighter = True
            elif "8-" not in parameterName :
                process+=selectDecayMode("h0",["h0->tau-,tau+;"])
                addedBRReweighter = True
                process+="set /Herwig/Particles/tau-:Stable Stable\n"
            
        elif "ggHJet" in parameterName :
            logging.error(" Process %s not supported for POWHEG matrix elements" % name)
            sys.exit(1)
        elif "ggH" in parameterName :
            process+=insert_ME("PowhegMEHiggs")
            if "GammaGamma" in parameterName :
               process+=selectDecayMode("h0",["h0->gamma,gamma;"])
               addedBRReweighter = True
            elif "WW" in parameterName :
               process+=selectDecayMode("h0",["h0->W+,W-;"])
               addedBRReweighter = True
            elif "ZZ" in parameterName :
               process+=selectDecayMode("h0",["h0->Z0,Z0;"])
               addedBRReweighter = True
            elif "8-" not in parameterName :
                process+=selectDecayMode("h0",["h0->tau-,tau+;"])
                addedBRReweighter = True
                process+="set /Herwig/Particles/tau-:Stable Stable\n"
        elif "8-WH" in parameterName :
            process+=insert_ME("PowhegMEPP2WH")
            process+=jet_kt_cut(0.0)
            if "GammaGamma" in parameterName :
               process+=selectDecayMode("h0",["h0->gamma,gamma;"])
               addedBRReweighter = True
            elif "WW" in parameterName :
               process+=selectDecayMode("h0",["h0->W+,W-;"])
               addedBRReweighter = True
            elif "ZZ" in parameterName :
               process+=selectDecayMode("h0",["h0->Z0,Z0;"])
               addedBRReweighter = True
        elif "8-ZH" in parameterName :
            process+=insert_ME("PowhegMEPP2ZH")
            process+=jet_kt_cut(0.0)
            if "GammaGamma" in parameterName :
               process+=selectDecayMode("h0",["h0->gamma,gamma;"])
               addedBRReweighter = True
            elif "WW" in parameterName :
               process+=selectDecayMode("h0",["h0->W+,W-;"])
               addedBRReweighter = True
            elif "ZZ" in parameterName :
               process+=selectDecayMode("h0",["h0->Z0,Z0;"])
               addedBRReweighter = True
        elif "WH" in parameterName :
            process+=selectDecayMode("h0",["h0->b,bbar;"])
            process+=selectDecayMode("W+",["W+->nu_e,e+;",
                                           "W+->nu_mu,mu+;"])
            addedBRReweighter = True
            process+=insert_ME("PowhegMEPP2WH")
            process+=jet_kt_cut(0.0)
        elif "ZH" in parameterName :
            process+=selectDecayMode("h0",["h0->b,bbar;"])
            process+=selectDecayMode("Z0",["Z0->e-,e+;",
                                           "Z0->mu-,mu+;"])
            addedBRReweighter = True
            process+=insert_ME("PowhegMEPP2ZH")
            process+=jet_kt_cut(0.0)
        elif "UE" in parameterName :
            logging.error(" Process %s not supported for powheg matrix elements" % name)
            sys.exit(1)
        elif "WZ" in parameterName :
            process+="create Herwig::HwDecayHandler /Herwig/NewPhysics/DecayHandler\n"
            process+="set /Herwig/NewPhysics/DecayHandler:NewStep No\n"
            process+="set /Herwig/Shower/ShowerHandler:SplitHardProcess No\n";
            process+="set /Herwig/Decays/ZDecayer:PhotonGenerator NULL\n";
            process+="set /Herwig/Decays/WDecayer:PhotonGenerator NULL\n";
            process+="insert /Herwig/NewPhysics/DecayHandler:Excluded 0 /Herwig/Particles/tau-\n"
            process+="insert /Herwig/NewPhysics/DecayHandler:Excluded 1 /Herwig/Particles/tau+\n"
            process+="insert /Herwig/Generators/EventGenerator:EventHandler:PreCascadeHandlers 0 /Herwig/NewPhysics/DecayHandler\n"
            process+=insert_ME("PowhegMEPP2VV","WZ")
            process+=selectDecayMode("W+",["W+->nu_e,e+;",
                                           "W+->nu_mu,mu+;"])
            process+=selectDecayMode("W-",["W-->nu_ebar,e-;",
                                           "W-->nu_mubar,mu-;"])
            process+=selectDecayMode("Z0",["Z0->e-,e+;",
                                           "Z0->mu-,mu+;"])
            addedBRReweighter = True
            
        elif "WW-emu" in parameterName :
            process+="create Herwig::HwDecayHandler /Herwig/NewPhysics/DecayHandler\n"
            process+="set /Herwig/NewPhysics/DecayHandler:NewStep No\n"
            process+="set /Herwig/Shower/ShowerHandler:SplitHardProcess No\n";
            process+="set /Herwig/Decays/ZDecayer:PhotonGenerator NULL\n";
            process+="set /Herwig/Decays/WDecayer:PhotonGenerator NULL\n";
            process+="insert /Herwig/NewPhysics/DecayHandler:Excluded 0 /Herwig/Particles/tau-\n"
            process+="insert /Herwig/NewPhysics/DecayHandler:Excluded 1 /Herwig/Particles/tau+\n"
            process+="insert /Herwig/Generators/EventGenerator:EventHandler:PreCascadeHandlers 0 /Herwig/NewPhysics/DecayHandler\n"
            process+=insert_ME("PowhegMEPP2VV","WW")
            process+="set /Herwig/Particles/W+:Synchronized 0\n"
            process+="set /Herwig/Particles/W-:Synchronized 0\n"
            process+=selectDecayMode("W+",["W+->nu_e,e+;"])
            process+=selectDecayMode("W-",["W-->nu_mubar,mu-;"])
            addedBRReweighter = True
            
        elif "WW-ll" in parameterName :
            process+="create Herwig::HwDecayHandler /Herwig/NewPhysics/DecayHandler\n"
            process+="set /Herwig/NewPhysics/DecayHandler:NewStep No\n"
            process+="set /Herwig/Shower/ShowerHandler:SplitHardProcess No\n";
            process+="set /Herwig/Decays/ZDecayer:PhotonGenerator NULL\n";
            process+="set /Herwig/Decays/WDecayer:PhotonGenerator NULL\n";
            process+="insert /Herwig/NewPhysics/DecayHandler:Excluded 0 /Herwig/Particles/tau-\n"
            process+="insert /Herwig/NewPhysics/DecayHandler:Excluded 1 /Herwig/Particles/tau+\n"
            process+="insert /Herwig/Generators/EventGenerator:EventHandler:PreCascadeHandlers 0 /Herwig/NewPhysics/DecayHandler\n"
            process+=insert_ME("PowhegMEPP2VV","WW")
            process+=selectDecayMode("W+",["W+->nu_e,e+;",
                                           "W+->nu_mu,mu+;",
                                           "W+->nu_tau,tau+;"])
            addedBRReweighter = True
            
        elif "ZZ-ll" in parameterName :
            process+="create Herwig::HwDecayHandler /Herwig/NewPhysics/DecayHandler\n"
            process+="set /Herwig/NewPhysics/DecayHandler:NewStep No\n"
            process+="set /Herwig/Shower/ShowerHandler:SplitHardProcess No\n";
            process+="set /Herwig/Decays/ZDecayer:PhotonGenerator NULL\n";
            process+="set /Herwig/Decays/WDecayer:PhotonGenerator NULL\n";
            process+="insert /Herwig/NewPhysics/DecayHandler:Excluded 0 /Herwig/Particles/tau-\n"
            process+="insert /Herwig/NewPhysics/DecayHandler:Excluded 1 /Herwig/Particles/tau+\n"
            process+="insert /Herwig/Generators/EventGenerator:EventHandler:PreCascadeHandlers 0 /Herwig/NewPhysics/DecayHandler\n"
            process+=insert_ME("PowhegMEPP2VV","ZZ")
            process+=selectDecayMode("Z0",["Z0->e-,e+;",
                                           "Z0->mu-,mu+;",
                                           "Z0->tau-,tau+;"])
            addedBRReweighter = True
            
        elif "ZZ-lv" in parameterName :
            process+="create Herwig::HwDecayHandler /Herwig/NewPhysics/DecayHandler\n"
            process+="set /Herwig/NewPhysics/DecayHandler:NewStep No\n"
            process+="set /Herwig/Shower/ShowerHandler:SplitHardProcess No\n";
            process+="set /Herwig/Decays/ZDecayer:PhotonGenerator NULL\n";
            process+="set /Herwig/Decays/WDecayer:PhotonGenerator NULL\n";
            process+="insert /Herwig/NewPhysics/DecayHandler:Excluded 0 /Herwig/Particles/tau-\n"
            process+="insert /Herwig/NewPhysics/DecayHandler:Excluded 1 /Herwig/Particles/tau+\n"
            process+="insert /Herwig/Generators/EventGenerator:EventHandler:PreCascadeHandlers 0 /Herwig/NewPhysics/DecayHandler\n"
            process+=insert_ME("PowhegMEPP2VV","ZZ")
            process+=selectDecayMode("Z0",["Z0->e-,e+;",
                                           "Z0->mu-,mu+;",
                                           "Z0->tau-,tau+;",
                                           "Z0->nu_e,nu_ebar;",
                                           "Z0->nu_mu,nu_mubar;",
                                           "Z0->nu_tau,nu_taubar;"])
            addedBRReweighter = True
        elif "W-e" in parameterName :
            process+=insert_ME("PowhegMEqq2W2ff","Electron")
        elif "W-mu" in parameterName :
            process+=insert_ME("PowhegMEqq2W2ff","Muon")
        elif "Z-e" in parameterName or "Z-mu" in parameterName :
            if "Z-e" in parameterName:
                process+=insert_ME("PowhegMEqq2gZ2ff","Electron")
            else :
                process+=insert_ME("PowhegMEqq2gZ2ff","Muon")
            mcuts=[10,35,75,110,400,ecms]
            for i in range(1,6) :
                tstring = "-Mass%s"%i
                if tstring in parameterName :
                    process+=mhat_minm_maxm(mcuts[i-1],mcuts[i-1],mcuts[i])
                    parameterName=parameterName.replace(tstring,"")
        elif "Z-nu" in parameterName :
            process+=insert_ME("PowhegMEqq2gZ2ff","Neutrinos")
        elif "DiPhoton-GammaGamma" in parameterName :
            process+=insert_ME("MEGammaGammaPowheg","GammaGamma")
            process+=insert_ME("MEGammaGamma","gg")
            process+="set /Herwig/Cuts/PhotonKtCut:MinKT 5.\n"
            process+=jet_kt_cut(5.)
            parameterName=parameterName.replace("-GammaGamma","")
        elif "DiPhoton-GammaJet" in parameterName :
            process+=insert_ME("MEGammaGammaPowheg","VJet")
            process+="set /Herwig/Cuts/PhotonKtCut:MinKT 5.\n"
            process+=jet_kt_cut(5.)
            parameterName=parameterName.replace("-GammaJet","")
        else :
            logging.error(" Process %s not supported for internal POWHEG matrix elements" % name)
            sys.exit(1)
            
    elif( simulation=="Matchbox" or simulation=="Merging" ) :
        if "VBF" in parameterName :
            parameters["nlo"] = "read Matchbox/VBFNLO.in\n"
            if(simulation=="Merging"):
                process+="cd /Herwig/Merging/\n"
            process+="insert "+thefactory+":DiagramGenerator:RestrictLines 0 /Herwig/Particles/Z0\n"
            process+="insert "+thefactory+":DiagramGenerator:RestrictLines 0 /Herwig/Particles/W+\n"
            process+="insert "+thefactory+":DiagramGenerator:RestrictLines 0 /Herwig/Particles/W-\n"
            process+="insert "+thefactory+":DiagramGenerator:RestrictLines 0 /Herwig/Particles/gamma\n"
            process+="do "+thefactory+":DiagramGenerator:TimeLikeRange 0 0\n"
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p p h0 j j","0","3","FixedScale",0,0)
            elif(simulation=="Merging"):
                process+=addProcess(thefactory,"p p h0 j j","0","3","FixedScale",1,1)
            process+=setHardProcessWidthToZero(["h0"])
            process+="set /Herwig/MatrixElements/Matchbox/Scales/FixedScale:FixedScale 125.7\n"
            if "GammaGamma" in parameterName :
               process+=selectDecayMode("h0",["h0->gamma,gamma;"])
               process+=addBRReweighter()
            elif "WW" in parameterName :
               process+=selectDecayMode("h0",["h0->W+,W-;"])
               process+=addBRReweighter()
            elif "ZZ" in parameterName :
               process+=selectDecayMode("h0",["h0->Z0,Z0;"])
               process+=addBRReweighter()
            elif "8-" not in parameterName :
                process+=selectDecayMode("h0",["h0->tau-,tau+;"])
                process+=addBRReweighter()
                process+="set /Herwig/Particles/tau-:Stable Stable\n"
        elif "ggHJet" in parameterName :
            if(simulation=="Merging"):
               logging.warning("ggHJet not explicitly tested for %s " % simulation)
               sys.exit(0)
            parameters["nlo"] = "read Matchbox/MadGraph-GoSam.in\nread Matchbox/HiggsEffective.in\n"
            process+=selectDecayMode("h0",["h0->tau-,tau+;"])
            process+=addBRReweighter()
            process+="set /Herwig/Particles/tau-:Stable Stable\n"
            process+=setHardProcessWidthToZero(["h0"])
            process+=addProcess(thefactory,"p p h0 j","3","1","FixedScale",0,0)
            process+=addFirstJet("20")
            process+="set "+thefactory+":ScaleChoice /Herwig/MatrixElements/Matchbox/Scales/FixedScale\n"
            process+="set /Herwig/MatrixElements/Matchbox/Scales/FixedScale:FixedScale 125.7\n"
        elif "ggH" in parameterName :
            parameters["nlo"] = "read Matchbox/MadGraph-GoSam.in\nread Matchbox/HiggsEffective.in\n"
            if(simulation=="Merging"):
                process+= "cd /Herwig/MatrixElements/Matchbox/Amplitudes\nset OpenLoops:HiggsEff Yes\nset MadGraph:Model heft\n"
                process+="cd /Herwig/Merging/\n"
            process+=setHardProcessWidthToZero(["h0"])
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p p h0","2","1","FixedScale",0,0)
            elif(simulation=="Merging"):
                process+=addProcess(thefactory,"p p h0","2","1","FixedScale",2,2)
            process+="set /Herwig/MatrixElements/Matchbox/Scales/FixedScale:FixedScale 125.7\n"
            if "GammaGamma" in parameterName :
               process+=selectDecayMode("h0",["h0->gamma,gamma;"])
               process+=addBRReweighter()
            elif "WW" in parameterName :
               process+=selectDecayMode("h0",["h0->W+,W-;"])
               process+=addBRReweighter()
            elif "ZZ" in parameterName :
               process+=selectDecayMode("h0",["h0->Z0,Z0;"])
               process+=addBRReweighter()
            elif "8-" not in parameterName :
                process+=selectDecayMode("h0",["h0->tau-,tau+;"])
                process+=addBRReweighter()
                process+="set /Herwig/Particles/tau-:Stable Stable\n"
        elif "8-WH" in parameterName :
            if(simulation=="Merging"):
              logging.warning("8-WH not explicitly tested for %s " % simulation)
              sys.exit(0)
            process+=setHardProcessWidthToZero(["h0","W+","W-"])
            process+=addProcess(thefactory,"p p W+ h0","0","2","FixedScale",0,0)
            process+=addProcess(thefactory,"p p W- h0","0","2","FixedScale",0,0)
            process+="set /Herwig/MatrixElements/Matchbox/Scales/FixedScale:FixedScale 125.7\n"
            if "GammaGamma" in parameterName :
               process+=selectDecayMode("h0",["h0->gamma,gamma;"])
               process+=addBRReweighter()
            elif "WW" in parameterName :
               process+=selectDecayMode("h0",["h0->W+,W-;"])
               process+=addBRReweighter()
            elif "ZZ" in parameterName :
               process+=selectDecayMode("h0",["h0->Z0,Z0;"])
               process+=addBRReweighter()
               
        elif "8-ZH" in parameterName :
            if(simulation=="Merging"):
              logging.warning("8-ZH not explicitly tested for %s " % simulation)
              sys.exit(0)
            process+=setHardProcessWidthToZero(["h0","Z0"])
            process+=addProcess(thefactory,"p p Z0 h0","0","2","FixedScale",0,0)
            process+="set /Herwig/MatrixElements/Matchbox/Scales/FixedScale:FixedScale 125.7\n"
            if "GammaGamma" in parameterName :
               process+=selectDecayMode("h0",["h0->gamma,gamma;"])
               process+=addBRReweighter()
            elif "WW" in parameterName :
               process+=selectDecayMode("h0",["h0->W+,W-;"])
               process+=addBRReweighter()
            elif "ZZ" in parameterName :
               process+=selectDecayMode("h0",["h0->Z0,Z0;"])
               process+=addBRReweighter()
               
        elif "WH" in parameterName :
            if(simulation=="Merging"):
              logging.warning("WH not explicitly tested for %s " % simulation)
              sys.exit(0)
            process+=selectDecayMode("h0",["h0->b,bbar;"])
            process+=addBRReweighter()
            process+=setHardProcessWidthToZero(["h0"])
            process+=addProcess(thefactory,"p p e+ nu h0","0","3","LeptonPairMassScale",0,0)
            process+=addProcess(thefactory,"p p e- nu h0","0","3","LeptonPairMassScale",0,0)
            process+=addProcess(thefactory,"p p mu+ nu h0","0","3","LeptonPairMassScale",0,0)
            process+=addProcess(thefactory,"p p mu- nu h0","0","3","LeptonPairMassScale",0,0)
            process+=addLeptonPairCut("60","120")
        elif "ZH" in parameterName :
            if(simulation=="Merging"):
              logging.warning("ZH not explicitly tested for %s " % simulation)
              sys.exit(0)
            process+=selectDecayMode("h0",["h0->b,bbar;"])
            process+=addBRReweighter()
            process+=setHardProcessWidthToZero(["h0"])
            process+=addProcess(thefactory,"p p e+ e- h0","0","3","LeptonPairMassScale",0,0)
            process+=addProcess(thefactory,"p p mu+ mu- h0","0","3","LeptonPairMassScale",0,0)
            process+=addLeptonPairCut("60","120")
        elif "UE" in parameterName :
            logging.error(" Process %s not supported for Matchbox matrix elements" % name)
            sys.exit(1)
        elif "8-DiJets" in parameterName or "7-DiJets" in parameterName or "13-DiJets" in parameterName :
            if(simulation=="Matchbox"):
              process+=addProcess(thefactory,"p p j j","2","0","MaxJetPtScale",0,0)
            elif(simulation=="Merging"):
              process+=addProcess(thefactory,"p p j j","2","0","MaxJetPtScale",1,1)
            process+="set /Herwig/UnderlyingEvent/MPIHandler:IdenticalToUE 0\n"
            if "13-DiJets" not in parameterName :
                if "-A" in parameterName :
                    process+=addFirstJet("45")
                    process+=addSecondJet("25")
                    process+="set /Herwig/Cuts/FirstJet:YRange  -3. 3.\n"
                    process+="set /Herwig/Cuts/SecondJet:YRange -3. 3.\n"
                elif "-B" in parameterName :
                    process+=addFirstJet("20")
                    process+=addSecondJet("15")
                    process+="set /Herwig/Cuts/FirstJet:YRange  -2.7 2.7\n"
                    process+="set /Herwig/Cuts/SecondJet:YRange -2.7 2.7\n"
                elif "-C" in parameterName :
                    process+=addFirstJet("20")
                    process+=addSecondJet("15")
                    process+="set /Herwig/Cuts/FirstJet:YRange  -4.8 4.8\n"
                    process+="set /Herwig/Cuts/SecondJet:YRange -4.8 4.8\n"
                else :
                    logging.error("Exit 00001")
                    sys.exit(1)
            else :
                if "-A" in parameterName :
                    process+= addFirstJet("75.")
                    process+=addSecondJet("60.")
                    process+="set /Herwig/Cuts/JetKtCut:MinEta -3.\n"
                    process+="set /Herwig/Cuts/JetKtCut:MaxEta  3.\n"
                elif "-B" in parameterName :
                    process+= addFirstJet("220.")
                    process+=addSecondJet("180.")
                    process+="set /Herwig/Cuts/JetKtCut:MinEta -3.\n"
                    process+="set /Herwig/Cuts/JetKtCut:MaxEta  3.\n"
                else :
                    logging.error("Exit 00001")
                    sys.exit(1)

                    
            if "DiJets-1" in parameterName   : process+=addJetPairCut("90")
            elif "DiJets-2" in parameterName : process+=addJetPairCut("200")
            elif "DiJets-3" in parameterName : process+=addJetPairCut("450")
            elif "DiJets-4" in parameterName : process+=addJetPairCut("750")
            elif "DiJets-5" in parameterName : process+=addJetPairCut("950")
            elif "DiJets-6" in parameterName : process+=addJetPairCut("1550")
            elif "DiJets-7" in parameterName : process+=addJetPairCut("2150")
            elif "DiJets-8" in parameterName : process+=addJetPairCut("2750")
            elif "DiJets-9" in parameterName : process+=mhat_cut(3750.)
            elif "DiJets-10" in parameterName : process+=mhat_cut(4750.)
            elif "DiJets-11" in parameterName : process+=mhat_cut(5750.)
            else :
                logging.error("Exit 00002")
                sys.exit(1)


        elif(      "7-Jets" in parameterName 
               or  "8-Jets" in parameterName 
               or "13-Jets" in parameterName 
               or "2760-Jets" in parameterName 
            ) :
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p p j j","2","0","MaxJetPtScale",0,0)
            elif(simulation=="Merging"):
                process+=addProcess(thefactory,"p p j j","2","0","MaxJetPtScale",1,1)
            process+="set /Herwig/UnderlyingEvent/MPIHandler:IdenticalToUE 0\n"
            if "Jets-10" in parameterName  : process+=addFirstJet("1800")
            elif "Jets-0" in parameterName : process+=addFirstJet("5")
            elif "Jets-1" in parameterName : process+=addFirstJet("10")
            elif "Jets-2" in parameterName : process+=addFirstJet("20")
            elif "Jets-3" in parameterName : process+=addFirstJet("40")
            elif "Jets-4" in parameterName : process+=addFirstJet("70")
            elif "Jets-5" in parameterName : process+=addFirstJet("150")
            elif "Jets-6" in parameterName : process+=addFirstJet("200")
            elif "Jets-7" in parameterName : process+=addFirstJet("300")
            elif "Jets-8" in parameterName : process+=addFirstJet("500")
            elif "Jets-9" in parameterName : process+=addFirstJet("800")
            else :
                logging.error("Exit 00003")
                sys.exit(1)
        elif(     "-Charm" in parameterName or "-Bottom" in parameterName) :
            parameters["bscheme"]=fourFlavour
            process+="set /Herwig/Particles/b:HardProcessMass 4.2*GeV\n"
            process+="set /Herwig/Particles/bbar:HardProcessMass 4.2*GeV\n"
            
            if("8-Bottom" in parameterName) :
                addBRReweighter()
                process+=selectDecayMode("Jpsi",["Jpsi->mu-,mu+;"])
            
            if "Bottom" in parameterName :
                if(simulation=="Matchbox"):
                    process+=addProcess(thefactory,"p p b bbar","2","0","MaxJetPtScale",0,0)
                elif(simulation=="Merging"):
                    process+=addProcess(thefactory,"p p b bbar","2","0","MaxJetPtScale",1,0)
            else:
                if(simulation=="Matchbox"):
                    process+=addProcess(thefactory,"p p c cbar","2","0","MaxJetPtScale",0,0)
                elif(simulation=="Merging"):
                    process+=addProcess(thefactory,"p p c cbar","2","0","MaxJetPtScale",1,0)

            process+="set /Herwig/UnderlyingEvent/MPIHandler:IdenticalToUE 0\n"
            if "-0" in parameterName   : process+=addFirstJet("0")
            elif "-1" in parameterName : process+=addFirstJet("5")
            elif "-2" in parameterName : process+=addFirstJet("15")
            elif "-3" in parameterName : process+=addFirstJet("20")
            elif "-4" in parameterName : process+=addFirstJet("50")
            elif "-5" in parameterName : process+=addFirstJet("80")
            elif "-6" in parameterName : process+=addFirstJet("110")
            elif "-7" in parameterName :
                process+=addFirstJet("30")
                process+=addSecondJet("25")
                process+=addJetPairCut("90")
            elif "-8" in parameterName :
                process+=addFirstJet("30")
                process+=addSecondJet("25")
                process+=addJetPairCut("340")
            elif "-9" in parameterName :
                process+=addFirstJet("30")
                process+=addSecondJet("25")
                process+=addJetPairCut("500")
            else :
                logging.error("Exit 00004")
                sys.exit(1)
                  
        elif "Top-L" in parameterName :
            process+=setHardProcessWidthToZero(["t","tbar"])
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p p t tbar","2","0","TopPairMTScale",0,0)
            elif(simulation=="Merging"):
                process+=addProcess(thefactory,"p p t tbar","2","0","TopPairMTScale",2,2)
            process+=selectDecayMode("t",["t->nu_e,e+,b;",
                                          "t->nu_mu,mu+,b;"])
            process+=addBRReweighter()
            
        elif "Top-SL" in parameterName :
            process+=setHardProcessWidthToZero(["t","tbar"])
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p p t tbar","2","0","TopPairMTScale",0,0)
            elif(simulation=="Merging"):
                process+=addProcess(thefactory,"p p t tbar","2","0","TopPairMTScale",2,2)
            process+="set /Herwig/Particles/t:Synchronized Not_synchronized\n"
            process+="set /Herwig/Particles/tbar:Synchronized Not_synchronized\n"
            process+=selectDecayMode("t",["t->nu_e,e+,b;",
                                          "t->nu_mu,mu+,b;"])
            process+=selectDecayMode("tbar",["tbar->b,bbar,cbar;",
                                             "tbar->bbar,cbar,d;",
                                             "tbar->bbar,cbar,s;",
                                             "tbar->bbar,s,ubar;",
                                             "tbar->bbar,ubar,d;"])
            process+=addBRReweighter()
            
        elif "Top-All" in parameterName :
            process+=setHardProcessWidthToZero(["t","tbar"])
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p p t tbar","2","0","TopPairMTScale",0,0)
            elif(simulation=="Merging"):
                process+=addProcess(thefactory,"p p t tbar","2","0","TopPairMTScale",2,2)
        elif "WZ" in parameterName :
            if(simulation=="Merging"):
              logging.warning("WZ not explicitly tested for %s " % simulation)
              sys.exit(0)
            process+=setHardProcessWidthToZero(["W+","W-","Z0"])
            process+=addProcess(thefactory,"p p W+ Z0","0","2","FixedScale",0,0)
            process+=addProcess(thefactory,"p p W- Z0","0","2","FixedScale",0,0)
            process+="set /Herwig/MatrixElements/Matchbox/Scales/FixedScale:FixedScale 171.6*GeV\n\n"
            process+=selectDecayMode("W+",["W+->nu_e,e+;",
                                           "W+->nu_mu,mu+;"])
            process+=selectDecayMode("W-",["W-->nu_ebar,e-;",
                                           "W-->nu_mubar,mu-;"])
            process+=selectDecayMode("Z0",["Z0->e-,e+;",
                                           "Z0->mu-,mu+;"])
            process+=addBRReweighter()
            process+=addLeptonPairCut("60","120")
        elif "WW-emu" in parameterName :
            if(simulation=="Merging"):
              logging.warning("WW-emu not explicitly tested for %s " % simulation)
              sys.exit(0)
            
            process+=setHardProcessWidthToZero(["W+","W-","Z0"])
            process+=addProcess(thefactory,"p p W+ W-","0","2","FixedScale",0,0)
            process+="set /Herwig/MatrixElements/Matchbox/Scales/FixedScale:FixedScale 160.8*GeV\n"
            process+="set /Herwig/Particles/W+:Synchronized 0\n"
            process+="set /Herwig/Particles/W-:Synchronized 0\n"
            process+=selectDecayMode("W+",["W+->nu_e,e+;"])
            process+=selectDecayMode("W-",["W-->nu_mubar,mu-;"])
            process+=addBRReweighter()
            parameters["bscheme"] = "read Matchbox/FourFlavourScheme.in\n"
            
            process+=addLeptonPairCut("60","120")
        elif "WW-ll" in parameterName :
            if(simulation=="Merging"):
              logging.warning("WW-ll not explicitly tested for %s " % simulation)
              sys.exit(0)
            process+=setHardProcessWidthToZero(["W+","W-","Z0"])
            process+=addProcess(thefactory,"p p W+ W-","0","2","FixedScale",0,0)
            process+="set /Herwig/MatrixElements/Matchbox/Scales/FixedScale:FixedScale 160.8*GeV\n"
            process+=selectDecayMode("W+",["W+->nu_e,e+;",
                                           "W+->nu_mu,mu+;",
                                           "W+->nu_tau,tau+;"])
            process+=addBRReweighter()
            process+=addLeptonPairCut("60","120")
            parameters["bscheme"] = "read Matchbox/FourFlavourScheme.in\n"

        elif "ZZ-ll" in parameterName :
            if(simulation=="Merging"):
              logging.warning("ZZ-ll not explicitly tested for %s " % simulation)
              sys.exit(0)
            process+=setHardProcessWidthToZero(["W+","W-","Z0"])
            process+=addProcess(thefactory,"p p Z0 Z0","0","2","FixedScale",0,0)
            process+="set /Herwig/MatrixElements/Matchbox/Scales/FixedScale:FixedScale 182.2*GeV\n"
            process+=selectDecayMode("Z0",["Z0->e-,e+;",
                                           "Z0->mu-,mu+;",
                                           "Z0->tau-,tau+;"])
            process+=addBRReweighter()
            process+=addLeptonPairCut("60","120")
        elif "ZZ-lv" in parameterName :
            if(simulation=="Merging"):
              logging.warning("ZZ-lv not explicitly tested for %s " % simulation)
              sys.exit(0)
            process+=setHardProcessWidthToZero(["W+","W-","Z0"])
            process+=addProcess(thefactory,"p p Z0 Z0","0","2","FixedScale",0,0)
            process+="set /Herwig/MatrixElements/Matchbox/Scales/FixedScale:FixedScale 182.2*GeV\n"
            process+=selectDecayMode("Z0",["Z0->e-,e+;",
                                           "Z0->mu-,mu+;",
                                           "Z0->tau-,tau+;",
                                           "Z0->nu_e,nu_ebar;",
                                           "Z0->nu_mu,nu_mubar;",
                                           "Z0->nu_tau,nu_taubar;"])
            process+=addBRReweighter()
            process+=addLeptonPairCut("60","120")
        elif "W-e" in parameterName :
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p p e+ nu","0","2","LeptonPairMassScale",0,0)
                process+=addProcess(thefactory,"p p e- nu","0","2","LeptonPairMassScale",0,0)
            elif(simulation=="Merging"):
                process+=particlegroup(thefactory,'epm','e+','e-')
                process+=addProcess(thefactory,"p p epm nu","0","2","LeptonPairMassScale",2,2)
            process+=addLeptonPairCut("60","120")

        elif "W-mu" in parameterName :
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p p mu+ nu","0","2","LeptonPairMassScale",0,0)
                process+=addProcess(thefactory,"p p mu- nu","0","2","LeptonPairMassScale",0,0)
            elif(simulation=="Merging"):
                process+=particlegroup(thefactory,'mupm','mu+','mu-')
                process+=addProcess(thefactory,"p p mupm nu","0","2","LeptonPairMassScale",2,2)
            process+=addLeptonPairCut("60","120")
        elif "Z-e" in parameterName or "Z-mu" in parameterName :
            if "Z-e" in parameterName :
                if(simulation=="Matchbox"):
                    process+=addProcess(thefactory,"p p e+ e-","0","2","LeptonPairMassScale",0,0)
                elif(simulation=="Merging"):
                    process+=addProcess(thefactory,"p p e+ e-","0","2","LeptonPairMassScale",2,2)
            elif "Z-mu" in parameterName :
                if(simulation=="Matchbox"):
                    process+=addProcess(thefactory,"p p mu+ mu-","0","2","LeptonPairMassScale",0,0)
                elif(simulation=="Merging"):
                    process+=addProcess(thefactory,"p p mu+ mu-","0","2","LeptonPairMassScale",2,2)
            mcuts=[10,35,75,110,400,ecms]
            for i in range(1,6) :
                tstring = "-Mass%s"%i
                if tstring in parameterName :
                    process+=addLeptonPairCut(mcuts[i-1],mcuts[i])
                    parameterName=parameterName.replace(tstring,"")
        elif "Z-nu" in parameterName :
            if(simulation=="Matchbox"):
                process+=addProcess(thefactory,"p p nu nu","0","2","LeptonPairMassScale",0,0)
            elif(simulation=="Merging"):
                process+=addProcess(thefactory,"p p nu nu","0","2","LeptonPairMassScale",2,2)
        elif "Z-jj" in parameterName :
            if(simulation=="Merging"):
              logging.warning("Z-jj not explicitly tested for %s " % simulation)
              sys.exit(0)
            process+=addProcess(thefactory,"p p e+ e- j j","2","2","LeptonPairMassScale",0,0)
            process+=addFirstJet("40")
            process+=addSecondJet("30")
            process+=addLeptonPairCut("60","120")
        elif "W-Jet" in parameterName :
            if(simulation=="Merging"):
              logging.warning("W-Jet not explicitly tested for %s " % simulation)
              sys.exit(0)
            
            process+=addProcess(thefactory,"p p e+ nu j","1","2","HTScale",0,0)
            process+=addProcess(thefactory,"p p e- nu j","1","2","HTScale",0,0)
            
            process+=addLeptonPairCut("60","120")
            if "W-Jet-1-e" in parameterName :
                process+=addFirstJet("100")
                parameterName=parameterName.replace("W-Jet-1-e","W-Jet-e")
            elif "W-Jet-2-e" in parameterName :
                process+=addFirstJet("190")
                parameterName=parameterName.replace("W-Jet-2-e","W-Jet-e")
            elif "W-Jet-3-e" in parameterName :
                process+=addFirstJet("270")
                parameterName=parameterName.replace("W-Jet-3-e","W-Jet-e")
            else :
                logging.error("Exit 00005")
                sys.exit(1)
        elif "Z-Jet" in parameterName :
            if(simulation=="Merging"):
              logging.warning("Z-Jet not explicitly tested for %s " % simulation)
              sys.exit(0)
            
            
            if "-e" in parameterName :
                process+=addProcess(thefactory,"p p e+ e- j","1","2","HTScale",0,0)
                if "Z-Jet-0-e" in parameterName :
                    process+=addFirstJet("35")
                    parameterName=parameterName.replace("Z-Jet-0-e","Z-Jet-e")
                elif "Z-Jet-1-e" in parameterName :
                    process+=addFirstJet("100")
                    parameterName=parameterName.replace("Z-Jet-1-e","Z-Jet-e")
                elif "Z-Jet-2-e" in parameterName :
                    process+=addFirstJet("190")
                    parameterName=parameterName.replace("Z-Jet-2-e","Z-Jet-e")
                elif "Z-Jet-3-e" in parameterName :
                    process+=addFirstJet("270")
                    parameterName=parameterName.replace("Z-Jet-3-e","Z-Jet-e")
                else :
                    logging.error("Exit 00006")
                    sys.exit(1)
            else :
                process+=addProcess(thefactory,"p p mu+ mu- j","1","2","HTScale",0,0)
                process+=addFirstJet("35")
                parameterName=parameterName.replace("Z-Jet-0-mu","Z-Jet-mu")
            process+=addLeptonPairCut("60","120")
        elif "Z-bb" in parameterName :
            if(simulation=="Merging"):
              logging.warning("Z-bb not explicitly tested for %s " % simulation)
              sys.exit(0)
            parameters["bscheme"]=fourFlavour
            process+="set /Herwig/Particles/b:HardProcessMass 4.2*GeV\nset /Herwig/Particles/bbar:HardProcessMass 4.2*GeV\n"
            process+=addProcess(thefactory,"p p e+ e- b bbar","2","2","FixedScale",0,0)
            process+=addLeptonPairCut("66","116")
            process+=addFirstJet("18")
            process+=addSecondJet("15")
            process+=addLeptonPairCut("60","120")
        elif "Z-b" in parameterName :
            if(simulation=="Merging"):
              logging.warning("Z-b not explicitly tested for %s " % simulation)
              sys.exit(0)
            process+=particlegroup(thefactory,'bjet','b','bbar')
            process+=addProcess(thefactory,"p p e+ e- bjet","1","2","FixedScale",0,0)
            process+="set /Herwig/MatrixElements/Matchbox/Scales/FixedScale:FixedScale 91.2*GeV\n"
            process+=addLeptonPairCut("60","120")
            process+=addFirstJet("15")
        elif "W-b" in parameterName :
            if(simulation=="Merging"):
              logging.warning("W-b not explicitly tested for %s " % simulation)
              sys.exit(0)
            parameters["bscheme"]=fourFlavour
            process += "set /Herwig/Particles/b:HardProcessMass 4.2*GeV\nset /Herwig/Particles/bbar:HardProcessMass 4.2*GeV\n"
            process+=addProcess(thefactory,"p p e-  nu b bbar","2","2","FixedScale",0,0)
            process+=addProcess(thefactory,"p p mu+ nu b bbar","2","2","FixedScale",0,0)
            process += "set /Herwig/MatrixElements/Matchbox/Scales/FixedScale:FixedScale 80.4*GeV\n"
            process+=addFirstJet("30")
            process+=addLeptonPairCut("60","120")
        else :
            logging.error(" Process %s not supported for Matchbox matrix elements" % name)
            sys.exit(1)
# LHC-GammaGamma
elif(collider=="LHC-GammaGamma" ) :
    if   "-7-" in parameterName : process = StringBuilder(collider_lumi(7000.0))
    elif "-8-" in parameterName : process = StringBuilder(collider_lumi(8000.0))
    else :                        process = StringBuilder(collider_lumi(7000.0))
    if(simulation=="") :
        if "7" in parameterName : process += insert_ME("MEgg2ff","Muon")
        else :
            logging.error(" Process %s not supported for default matrix elements" % name)
            sys.exit(1)
    else :
        logging.error("LHC-GammaGamma not supported for %s " % simulation)
        sys.exit(1)

if "EHS" in name :
    pFile = os.path.join(collider,"{c}-{pn}.in".format(c="EHS", pn=parameterName))
else :
    pFile = os.path.join(collider,"{c}-{pn}.in".format(c=collider, pn=parameterName))
with open(os.path.join("Rivet",pFile), 'r') as f:
    parameters['parameterFile'] = f.read()
    
parameters['runname'] = 'Rivet-%s' % name
parameters['process'] = str(process)
if have_hadronic_collider :
    if "EHS" in name :
        parameters['collider'] = "PPCollider.in\nread snippets/FixedTarget-PP.in"
    else :
        parameters['collider'] = "PPCollider.in"

#check if selecteddecaymode and addedBRReweighter is consistent

if selecteddecaymode and not addedBRReweighter:
    logging.error("Decaymode was selected but no BRReweighter was added.")
    sys.exit(1)

if addedBRReweighter and not selecteddecaymode:
    logging.error("BRReweighter was added but no Decaymode was selected.")
    sys.exit(1)

# check that we only add one process if in merging mode:

if numberOfAddedProcesses > 1 and simulation =="Merging":
    logging.error("In Merging only one process is allowed at the moment. See ticket #403.")
    sys.exit(1)

# Check if a process was added for Merging or Matchbox:

if numberOfAddedProcesses == 0 and (simulation =="Merging" or simulation =="Matchbox"):
    logging.error("No process was selected.")
    sys.exit(1)

# get template and write the file
with open(os.path.join("Rivet/Templates",templateName), 'r') as f:
    templateText = f.read()

template = Template( templateText )

with open(os.path.join("Rivet",name+".in"), 'w') as f:
        f.write( template.substitute(parameters) )
