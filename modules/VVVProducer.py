import ROOT
from ROOT import TLorentzVector
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

import math
import os
import numpy as np
from numpy import sign

def Process_1Lepton_2fatJets(event):
    if ( event.nFatJet < 2 ): return False
    if ( (event.nElectron+event.nMuon) < 1 ): return False
    return True

class VVVProducer(Module):
  def __init__(self , year, MODE = "1Lepton" ):
    self.year = year
    self.MODE = MODE
    self.Process_Genparticles = False
    if self.MODE == "1Lepton":
        self.function = Process_1Lepton_2fatJets

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    self.is_mc = bool(inputTree.GetBranch("GenJet_pt"))

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):

    # PV selection

    return (self.function)(event)


VVV2016 = lambda MODE="inclusive": VVVProducer("2016",MODE)
VVV2017 = lambda MODE="inclusive": VVVProducer("2017",MODE)
VVV2018 = lambda MODE="inclusive": VVVProducer("2018",MODE)