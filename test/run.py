import os
import sys
import optparse
import ROOT
import re

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.modules.common.countHistogramsModule import *
from PhysicsTools.NanoAODTools.postprocessing.analysis.modules.eleRECOSFProducer import *
from PhysicsTools.NanoAODTools.postprocessing.analysis.modules.eleIDSFProducer import *
from PhysicsTools.NanoAODTools.postprocessing.analysis.modules.muonScaleResProducer import *
from PhysicsTools.NanoAODTools.postprocessing.analysis.modules.muonIDISOSFProducer import *
from PhysicsTools.NanoAODTools.postprocessing.analysis.modules.VVVProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles, runsAndLumis
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import *
### main python file to run ###


def main():

  usage = 'usage: %prog [options]'
  parser = optparse.OptionParser(usage)
  parser.add_option('--year', dest='year', help='which year sample', default='2018', type='string')
  parser.add_option('-m', dest='ismc', help='to apply sf correction or not', default=True, action='store_true')
  parser.add_option('-i', '--in', dest='inputs', help='input directory with files', default=None, type='string')
  parser.add_option('-d', dest='ismc', help='to apply sf correction or not', action='store_false')
  parser.add_option('-o', '--out', dest='output', help='output directory with files', default="./", type='string')
  parser.add_option('-M', '--MODE', dest='MODE', help='MODE', default="inclusive", type='string')
  parser.add_option('--CrabCondor', '--CrabCondor', dest='CrabCondor', help='Crab Condor', default="crab", type='string')
  (opt, args) = parser.parse_args()

  PrefCorrUL16_preVFP = lambda : PrefCorr(jetroot="L1PrefiringMaps.root", jetmapname="L1prefiring_jetptvseta_UL2016preVFP", photonroot="L1PrefiringMaps.root", photonmapname="L1prefiring_photonptvseta_UL2016preVFP", branchnames=["PrefireWeight","PrefireWeight_Up", "PrefireWeight_Down"])
  PrefCorrUL16_postVFP = lambda : PrefCorr(jetroot="L1PrefiringMaps.root", jetmapname="L1prefiring_jetptvseta_UL2016postVFP", photonroot="L1PrefiringMaps.root", photonmapname="L1prefiring_photonptvseta_UL2016postVFP", branchnames=["PrefireWeight","PrefireWeight_Up", "PrefireWeight_Down"])
  PrefCorrUL17 = lambda : PrefCorr(jetroot="L1PrefiringMaps.root", jetmapname="L1prefiring_jetptvseta_UL2017BtoF", photonroot="L1PrefiringMaps.root", photonmapname="L1prefiring_photonptvseta_UL2017BtoF", branchnames=["PrefireWeight","PrefireWeight_Up", "PrefireWeight_Down"])
  
  if opt.ismc:
    if "2016" in opt.year:
#      jmeCorrections  = createJMECorrector(opt.ismc, "UL2016", opt.year[4:].upper(), "Total", "AK8PFPuppi")
#      jetmetCorrector = createJMECorrector(opt.ismc, "UL2016", jesUncert="Total", metBranchName="MET", splitJER=False, applyHEMfix=True)
      jmeCorrections  = createJMECorrector(opt.ismc, "UL2016", opt.year[4:].upper(), "All", "AK8PFPuppi")
      jetmetCorrector = createJMECorrector(opt.ismc, "UL2016", jesUncert="All", metBranchName="MET", splitJER=False, applyHEMfix=True)
    if "2017" in opt.year:
#      jmeCorrections  = createJMECorrector(opt.ismc, "UL2017", opt.year[4:].upper(), "Total","AK8PFPuppi")
#      jetmetCorrector = createJMECorrector(opt.ismc, "UL2017", jesUncert="Total", metBranchName="MET", splitJER=False, applyHEMfix=True)
      jmeCorrections  = createJMECorrector(opt.ismc, "UL2017", opt.year[4:].upper(), "All","AK8PFPuppi")
      jetmetCorrector = createJMECorrector(opt.ismc, "UL2017", jesUncert="All", metBranchName="MET", splitJER=False, applyHEMfix=True)
    if "2018" in opt.year:
#      jmeCorrections  = createJMECorrector(opt.ismc, "UL2018", opt.year[4:].upper(), "Total","AK8PFPuppi")
#      jetmetCorrector = createJMECorrector(opt.ismc, "UL2018", jesUncert="Total", metBranchName="MET", splitJER=False, applyHEMfix=True)
      jmeCorrections  = createJMECorrector(opt.ismc, "UL2018", opt.year[4:].upper(), "All","AK8PFPuppi")
      jetmetCorrector = createJMECorrector(opt.ismc, "UL2018", jesUncert="All", metBranchName="MET", splitJER=False, applyHEMfix=True)


  if opt.ismc:
    if opt.year == "2016post":
      p = PostProcessor(opt.output, opt.inputs.rstrip(",").split(","), modules=[countHistogramsModule(),puAutoWeight_2016(),PrefCorrUL16_postVFP(),muonIDISOSF2016post(),muonScaleRes2016b(),eleRECOSF2016post(),eleIDSF2016post(),jmeCorrections(),jetmetCorrector(),VVV2016()], provenance=True,fwkJobReport=True, jsonInput=runsAndLumis())
    if opt.year == "2016pre":
      p = PostProcessor(opt.output, opt.inputs.rstrip(",").split(","), modules=[countHistogramsModule(),puAutoWeight_2016(),PrefCorrUL16_preVFP() ,muonIDISOSF2016pre() ,muonScaleRes2016a(),eleRECOSF2016pre() ,eleIDSF2016pre() ,jmeCorrections(),jetmetCorrector(),VVV2016()], provenance=True,fwkJobReport=True, jsonInput=runsAndLumis())
    if opt.year == "2017":
      p = PostProcessor(opt.output, opt.inputs.rstrip(",").split(","), modules=[countHistogramsModule(),puAutoWeight_2017(),PrefCorrUL17(),        muonIDISOSF2017()    ,muonScaleRes2017() , eleRECOSF2017()    ,eleIDSF2017(),    jmeCorrections(),jetmetCorrector(),VVV2017()], provenance=True,fwkJobReport=True, jsonInput=runsAndLumis())
    if opt.year == "2018":
      p = PostProcessor(opt.output, opt.inputs.rstrip(",").split(","), modules=[countHistogramsModule(),puAutoWeight_2018(),                       muonIDISOSF2018(),    muonScaleRes2018() , eleRECOSF2018()    ,eleIDSF2018(),    jmeCorrections(),jetmetCorrector(),VVV2018()], provenance=True,fwkJobReport=True, jsonInput=runsAndLumis())
    p.run()

# Sequence for data
  if not (opt.ismc):
      year_list = ['UL2016_preVFPB','UL2016_preVFPC','UL2016_preVFPD','UL2016_preVFPE','UL2016_preVFPF','UL2016F','UL2016G','UL2016H','UL2017B','UL2017C','UL2017D','UL2017E','UL2017F','UL2018A','UL2018B','UL2018C','UL2018D']
      if opt.year in year_list : 
        jmeCorrections  = createJMECorrector(opt.ismc,  dataYear=opt.year[:6], runPeriod=opt.year[6:],  jesUncert="Total", jetType="AK8PFPuppi",)
        jetmetCorrector = createJMECorrector(opt.ismc,   dataYear=opt.year[:6], runPeriod=opt.year[6:], metBranchName="MET")
        if "2016" in opt.year:
          p = PostProcessor(opt.output, opt.inputs.rstrip(",").split(","), modules=[jetmetCorrector(),jmeCorrections(),VVV2016()], provenance=True, fwkJobReport=True, jsonInput=runsAndLumis())
        if "2017" in opt.year:
          p = PostProcessor(opt.output, opt.inputs.rstrip(",").split(","), modules=[jetmetCorrector(),jmeCorrections(),VVV2017()], provenance=True, fwkJobReport=True, jsonInput=runsAndLumis())
        if "2018" in opt.year:
          p = PostProcessor(opt.output, opt.inputs.rstrip(",").split(","), modules=[jetmetCorrector(),jmeCorrections(),VVV2018()], provenance=True, fwkJobReport=True, jsonInput=runsAndLumis())
        p.run()

if __name__ == "__main__":
    sys.exit(main())
