#!/bin/bash

OPTIND=1

while getopts "h?f:i:o:s:e:x:ca:" opt; do
    case "$opt" in
    h|\?)
        echo 'parameters'
        exit 0
        ;;
    f)  INPUTFILES=$OPTARG
        # e.g. 2016, 2017, 2018
        ;;
    i)  IFILE=$OPTARG
        # e.g. WWW_dim8, WZZ_dim8, WWZ_dim8 or ZZZ_dim8
        ;;
    o)  OUTPUTFILENAMES=$OPTARG
        ;;
    a)  ADDTIONAL=$OPTARG
        ;;
    e)  EOSPATH=$OPTARG
        ;;
    x)  X509_USER_PROXYTMP=$OPTARG
        ;;
    c)  CopyToEos=1 # to copy the outfile to cmslpc eos space
        ;;
    esac
done

BASEDIR=`pwd` ; pwd ; ls -lth

export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_26/src ] ; then
  echo release CMSSW_10_6_26 already exists
else
  scram p CMSSW CMSSW_10_6_26
fi
cd CMSSW_10_6_26/src
eval `scram runtime -sh`

mv $BASEPATH/SearchSite.py .
mv $BASEPATH/ValidSite.py .
OLD_IFS="$IFS"
IFS=","
array=($INPUTFILES)
IFS="$OLD_IFS"
for INPUTFILE in ${array[@]}
do
    echo $INPUTFILE
    XRDSITE='root://cmsxrootd.fnal.gov/'
    INPUTFILENAMES=${XRDSITE}${INPUTFILE}
    echo $INPUTFILENAMES
    xrdcp $INPUTFILENAMES ${BASEDIR}
    IFS="/"
    array=($INPUTFILE)
    IFS="$OLD_IFS"
    INPUTFILELOCAL=${array[-1]}
    if [ ! -f "$BASEDIR/$INPUTFILELOCAL" ]; then
      echo $BASEDIR/$INPUTFILELOCAL "not exit"
      exit 1
    else
      echo $BASEDIR/$INPUTFILELOCAL
    fi
done

cd $CMSSW_BASE/src
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
cd PhysicsTools/NanoAODTools
cmsenv
scram b

echo "PhysicsTools/NanoAODTools dir" ; pwd ; ls -lth

cd python/postprocessing
git clone https://github.com/gqlcms/VVVun.git analysis
rm -rf $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/Condor
cd $CMSSW_BASE/src
scram b

cd $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis
source $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/init.sh

cd $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/test
echo "analysis/test dir" ; pwd ; ls -lth

OLD_IFS="$IFS"
IFS=","
array=($INPUTFILES)
IFS="$OLD_IFS"
for INPUTFILE in ${array[@]}
do
    IFS="/"
    array=($INPUTFILE)
    IFS="$OLD_IFS"
    INPUTFILELOCAL=${array[-1]}
    INPUTFILES_TMP=${INPUTFILES_TMP}${BASEDIR}/$INPUTFILELOCAL,
done

echo python run.py -i $INPUTFILES_TMP $ADDTIONAL
python run.py -i $INPUTFILES_TMP $ADDTIONAL

echo "finish run" ; echo "analysis/test dir" ; pwd ; ls -lth

# Rigorous sweeproot which checks ALL branches for ALL events.
# If GetEntry() returns -1, then there was an I/O problem, so we will delete it
python << EOL
import ROOT as r
import os
foundBad = False
try:
    f1 = r.TFile("tree.root")
    t = f1.Get("Events")
    nevts = t.GetEntries()
    for i in range(0,t.GetEntries(),1):
        if t.GetEntry(i) < 0:
            foundBad = True
            print "[RSR] found bad event %i" % i
            break
except: foundBad = True
if foundBad:
    print "[RSR] removing output file because it does not deserve to live"
    os.system("rm tree.root")
else: print "[RSR] passed the rigorous sweeproot"
EOL
mv tree.root $BASEDIR

cd $BASEDIR
ls -lth