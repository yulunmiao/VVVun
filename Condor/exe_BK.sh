#!/bin/bash

DATASET=$1
INPUTFILES=$2
ADDTIONAL=$3
INPUTFILEAREA=http://stash.osgconnect.net/+qilongguo/gKK/private_NanoAOD/V1/

BASEDIR=`pwd`

OLD_IFS="$IFS"
IFS=","
array=($INPUTFILES)
IFS="$OLD_IFS"
for INPUTFILE in ${array[@]}
do
    echo $INPUTFILE
    echo wget --tries=3 --no-check-certificate $INPUTFILEAREA/$DATASET/$INPUTFILE
    wget --tries=3 --no-check-certificate $INPUTFILEAREA/$DATASET/$INPUTFILE
    if [ ! -f "$BASEDIR/$INPUTFILE" ]; then
      echo $BASEDIR/$INPUTFILE "not exit"
      exit 1
    else
      echo $BASEDIR/$INPUTFILE
    fi
done

echo "base dir"
pwd
ls -lth

export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_26/src ] ; then
  echo release CMSSW_10_6_26 already exists
else
  scram p CMSSW CMSSW_10_6_26
fi
cd CMSSW_10_6_26/src
eval `scram runtime -sh`

cd $CMSSW_BASE/src
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
cd PhysicsTools/NanoAODTools
cmsenv
scram b

echo "PhysicsTools/NanoAODTools dir"
pwd
ls -lth

cd python/postprocessing
git clone https://github.com/gqlcms/XWWNano.git analysis
cd $CMSSW_BASE/src
scram b

cd $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis
echo "analysis dir"
pwd
ls -lth
source $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/init.sh

cd $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/test
echo "analysis/test dir"
pwd
ls -lth

OLD_IFS="$IFS"
IFS=","
array=($INPUTFILES)
IFS="$OLD_IFS"
for INPUTFILE in ${array[@]}
do
    INPUTFILES_TMP=${INPUTFILES_TMP}${BASEDIR}/$INPUTFILE,
done

echo python run.py -i $INPUTFILES_TMP $ADDTIONAL
python run.py -i $INPUTFILES_TMP $ADDTIONAL

echo "finish run"
echo "analysis/test dir"
pwd
ls -lth

mv tree.root $BASEDIR

cd $BASEDIR
ls -lth

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





mv $BASEPATH/SearchSite.py .
mv $BASEPATH/ValidSite.py .

python SearchSite.py $INPUTFILENAMES
cat test_ValidSite.log
XRDSITE=`cat ValidSite.txt`
INPUTFILENAMES=${XRDSITE}${INPUTFILENAMES}
echo $INPUTFILENAMES
xrdcp $INPUTFILENAMES .
LOCALInputFile=`cat Localfile.txt`
echo $LOCALInputFile

cmsDriver.py mc2016 \
-n -1 \
--mc \
--eventcontent NANOAODSIM \
--datatier NANOAODSIM \
--conditions 106X_mcRun2_asymptotic_v17 \
--step NANO \
--nThreads 1 \
--era Run2_2016,run2_nanoAOD_106Xv2 \
--customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC \
--filein file:$LOCALInputFile \
--fileout file:$OUTPUTFILENAMES \
--no_exec

cmsRun mc2016_NANO.py

pwd
ls -lth

# Rigorous sweeproot which checks ALL branches for ALL events.
# If GetEntry() returns -1, then there was an I/O problem, so we will delete it
python << EOL
import ROOT as r
import os
foundBad = False
try:
    f1 = r.TFile("$OUTPUTFILENAMES")
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
    os.system("rm $OUTPUTFILENAMES")
else: print "[RSR] passed the rigorous sweeproot"
EOL

mv $OUTPUTFILENAMES $BASEPATH
echo $BASEPATH
ls -lth $BASEPATH

cd $BASEPATH

rm -rf CMSSW_10_6_20

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_20/src ] ; then
  echo release CMSSW_10_6_26 already exists
else
  scram p CMSSW CMSSW_10_6_26
fi
cd CMSSW_10_6_26/src
eval `scram runtime -sh`

cd $CMSSW_BASE/src
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
cd PhysicsTools/NanoAODTools
eval `scram runtime -sh`
scram b -j 16

echo "PhysicsTools/NanoAODTools dir"
pwd
ls -lth

cd python/postprocessing
git clone https://github.com/gqlcms/XWWNano.git analysis
rm -rf $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/test/crab_auto
rm -rf $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/Makeplots
rm -rf $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/Powheg
rm -rf $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/TransferTree
cd $CMSSW_BASE/src
scram b -j 16

cd $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis
echo "analysis dir"
pwd
ls -lth
source $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/init.sh

cd $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/test
echo "analysis/test dir"
pwd
ls -lth

echo python run_1LeptonSF.py -m -i $BASEPATH/$OUTPUTFILENAMES -o ./ --year $YEAR -M 1Lepton_SF
python run_1LeptonSF.py -m -i $BASEPATH/$OUTPUTFILENAMES -o ./ --year $YEAR -M 1Lepton_SF


echo "finish run"
echo "analysis/test dir"
pwd
ls -lth

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

mv tree.root $BASEPATH

cd $BASEPATH
ls -lth




/home/gql/tutorial/lib/WVV-aQGC-study/FrameWork/Nanotool/Code/v3

rm -r data
rm -r modules
rm -r others
rm -r scripts
rm -r test/crab_auto/

data
modules
others
scripts
test

cp -r /home/gql/tutorial/lib/WVV-aQGC-study/FrameWork/Nanotool/Code/v3/$1 .

cp /mnt/ceph/connect/user/qilongguo/work/EFT_VVV/VVVun/V4/CMSSW_10_6_27/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/Condor/x509up_u100637 .
cp /mnt/ceph/connect/user/qilongguo/work/EFT_VVV/VVVun/V4/CMSSW_10_6_27/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/Condor/scripts/SearchSite.py .
cp /mnt/ceph/connect/user/qilongguo/work/EFT_VVV/VVVun/V4/CMSSW_10_6_27/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/Condor/scripts/ValidSite.py .
cp /mnt/ceph/connect/user/qilongguo/work/EFT_VVV/VVVun/V4/CMSSW_10_6_27/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/Condor/exe.sh .
sh exe.sh -f /store/mc/RunIISummer20UL16NanoAODAPVv2/WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_preVFP_v9-v1/30000/3C951515-FF1A-B447-8B3C-26489E39F5D4.root -a ' --year 2016pre -m ' > debug 2>&1

