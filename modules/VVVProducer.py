import ROOT
from ROOT import TLorentzVector
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

import math
import os
import numpy as np
from numpy import sign

def Process_0Lepton(event):
    if ( event.nFatJet < 2 ): return False
    return True

def Process_1Lepton(event):
    if ( event.nFatJet < 2 ): return False
    if ( (event.nElectron+event.nMuon) < 1 ): return False
    return True

def Process_2Lepton(event):
    if ( (event.nElectron+event.nMuon) < 2 ): return False
    return True

def Process_4Lepton(event):
    if ( (event.nElectron+event.nMuon) < 4 ): return False
    return True

def Process_inclusive(event):
    return True

class VVVProducer(Module):
  def __init__(self , year, MODE = "1Lepton" ):
    self.year = year
    self.MODE = MODE
    self.Process_Genparticles = False
    if self.MODE == "inclusive": self.function = Process_inclusive
    if self.MODE == "0Lepton": self.function = Process_0Lepton
    if self.MODE == "1Lepton": self.function = Process_1Lepton
    if self.MODE == "2Lepton": self.function = Process_2Lepton
    if self.MODE == "4Lepton": self.function = Process_4Lepton

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out   = wrappedOutputTree
    self.is_mc = bool(inputTree.GetBranch("GenJet_pt"))

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):
    # PV selection
    return (self.function)(event)

VVV2016         = lambda MODE="inclusive": VVVProducer("2016","inclusive")
VVV2016_0Lepton = lambda MODE="inclusive": VVVProducer("2016","0Lepton")
VVV2016_1Lepton = lambda MODE="inclusive": VVVProducer("2016","1Lepton")
VVV2016_2Lepton = lambda MODE="inclusive": VVVProducer("2016","2Lepton")
VVV2016_4Lepton = lambda MODE="inclusive": VVVProducer("2016","4Lepton")

VVV2017         = lambda MODE="inclusive": VVVProducer("2017","inclusive")
VVV2017_0Lepton = lambda MODE="inclusive": VVVProducer("2017","0Lepton")
VVV2017_1Lepton = lambda MODE="inclusive": VVVProducer("2017","1Lepton")
VVV2017_2Lepton = lambda MODE="inclusive": VVVProducer("2017","2Lepton")
VVV2017_4Lepton = lambda MODE="inclusive": VVVProducer("2017","4Lepton")

VVV2018         = lambda MODE="inclusive": VVVProducer("2018","inclusive")
VVV2018_0Lepton = lambda MODE="inclusive": VVVProducer("2018","0Lepton")
VVV2018_1Lepton = lambda MODE="inclusive": VVVProducer("2018","1Lepton")
VVV2018_2Lepton = lambda MODE="inclusive": VVVProducer("2018","2Lepton")
VVV2018_4Lepton = lambda MODE="inclusive": VVVProducer("2018","4Lepton")