import os
import json
from commands import getoutput

class jdl_writter:
    def __init__(self, path, ds, filename = "submit.cmd"):
        self.path = "%s/%s/"%(path,ds)
        self.ds = ds
        self.filename = filename
        self.init_templete = '''
universe=Vanilla
RequestMemory = 2048
RequestCpus = 1
executable={TaskFolder}/{DatasetFolder}/{excutable}
transfer_executable=True
transfer_input_files={transfer_input_files}
transfer_output_files={transfer_output_files}
log={log}/$(Cluster).log
output={std_logs}/$(Cluster).$(Process).out
error={std_logs}/$(Cluster).$(Process).err
notification=Never
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
x509userproxy=x509up_u100637
+MaxRuntime={MaxRuntime}

        '''
        self.queue_templete = '''
arguments={arguments}
transfer_output_remaps={transfer_output_remaps}
queue

        '''

    # this jdl_writter also 
    # create folder and copy corresponding executable
    # create outfolder
    def init(self,replace, log, std_logs, exePath, excutable, outputPath):
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
        if not os.path.isdir("%s/%s"%(self.path, log)):
            os.makedirs("%s/%s"%(self.path, log))
        if not os.path.isdir("%s/%s"%(self.path, std_logs)):
            os.makedirs("%s/%s"%(self.path, std_logs))
        if not os.path.isdir("%s/%s"%(outputPath, replace["DatasetFolder"])):
            os.makedirs("%s/%s"%(outputPath, replace["DatasetFolder"]))

        os.system("cp %s/%s %s"%( exePath, excutable, self.path))
        with open(self.path+self.filename,"w") as fout:
            fout.write(self.init_templete.format(**replace))

    def add_queue(self,replace,):
        with open(self.path+self.filename,"a+") as fout:
            fout.write(self.queue_templete.format(**replace))

class Condor():
    def __init__(self, Filejson, samples_toRun, transfer_input_files, transfer_output_files, outputPath, YEAR, addtional, **kwargs):
        with open(Filejson,"r") as f:
            self.samples = json.loads(f.read())
        self.samples_toRun = samples_toRun
        if self.samples_toRun:
            self.samples = dict([(i,self.samples[i]) for i in self.samples_toRun])
        self.transfer_input_files  = ",".join(transfer_input_files).rstrip(",")
        self.transfer_output_files = transfer_output_files
        self.outputPath = outputPath
        self.YEAR = YEAR
        self.addtional = addtional
        self.maxnJobs = kwargs.get("maxnJobs",-1)

        self.TaskFolder = "%s/%s"%(os.getcwd(),kwargs.get("TaskFolder","tasks"))
        self.excutable = kwargs.get("excutable","exe.sh")
        self.log = kwargs.get("log","log")
        self.std_logs = "%s/%s/"%(self.log,kwargs.get("std_logs","std_logs"))
        self.MaxRuntime = kwargs.get("MaxRuntime","40000")
        self.exePath = kwargs.get("queue_templte",".")

    def arguments(self, info):
        replace = {
            "DATASET" : info["ds"],
            "INPUTFILE" : info["INPUTFILE"],
            "addtional" : info["addtional"],
            "transfer_output_files" : self.transfer_output_files,
        }
        return '"-f {INPUTFILE} -a \'{addtional}\'"'.format(**replace)

    def remaps(self, info):
        replace = {
            "transfer_output_files" : self.transfer_output_files,
            "outputPath" : self.outputPath,
            "ds" : info["ds"],
            "INPUTFILE" : info["INPUTFILE"],
            "index" : info["index"],
        }
        return '"{transfer_output_files} = {outputPath}/{ds}/out_{index}.root"'.format(**replace)

    def Create_Submit_Scripts(self):
        files=os.listdir(self.TaskFolder)
        outputfiles = self.TaskFolder.split("/")[-1]+".sh"
        with open(outputfiles,"w") as f:
            for i in files:
                i = i.replace(" ","").replace("\n","")
                f.write("condor_submit %s/%s/submit.cmd \n"%(self.TaskFolder,i))

    def Generate_Scripts(self):
        for ds in self.samples:
            self.jdl_writter = jdl_writter( self.TaskFolder, ds)
            replace = {
                "TaskFolder" : self.TaskFolder,
                "DatasetFolder" : ds,
                "excutable" : self.excutable,
                "transfer_input_files" : self.transfer_input_files,
                "transfer_output_files" : self.transfer_output_files,
                "log" : "%s/%s/%s/"%(self.TaskFolder,ds,self.log),
                "std_logs" : os.path.dirname("%s/%s/%s/"%(self.TaskFolder,ds,self.std_logs)),
                "MaxRuntime" : self.MaxRuntime,
            }
            self.jdl_writter.init(replace, self.log, self.std_logs, self.exePath, self.excutable, self.outputPath, )
            for nn,index in enumerate(self.samples[ds]):
                if ( self.maxnJobs > 0 ) & (nn > self.maxnJobs) : break
                info = {
                    "ds" : ds,
                    "INPUTFILE" : (",".join(self.samples[ds][index])).rstrip(","),
                    "YEAR" : self.YEAR,
                    "index" : index,
                    "addtional" : self.addtional(ds),
                }
                replace = {
                    "arguments" : self.arguments(info),
                    "transfer_output_remaps" : self.remaps(info),
                }
                self.jdl_writter.add_queue(replace)
            print "finish", ds
        self.Create_Submit_Scripts()


class File_json():
    def __init__(self, jsonfile, **kwargs):
        self.jsonfile = jsonfile
        self.Samples_Default = [
            "WWW",
        ]
        self.Samples = kwargs.get("Samples_ToRun",self.Samples_Default)
        self.DAS = {
            "WWW" : "/WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8/RunIISummer20UL16NanoAODAPVv2-106X_mcRun2_asymptotic_preVFP_v9-v1/NANOAODSIM",
        }
        self.Nperjobs = {
            "QCD_HT1500to2000_APV":1,
            "ST_t-channel_top_APV":1,
            "TTToHadronic_APV":1,
            "WW_APV":1,
            "WZ_APV":1,
            "ZZZ":1,
            "QCD_HT2000toInf":1,
            "ST_tW_antitop":1,
            "TTToSemiLeptonic":1,
            "WWW":2,
            "WZZ":1,
            "ZZZ_APV":1,
            "QCD_HT1000to1500":1,
            "QCD_HT2000toInf_APV":1,
            "ST_tW_antitop_APV":1,
            "TTToSemiLeptonic_APV":1,
            "WWW_APV":1,
            "WZZ_APV":1,
            "QCD_HT1000to1500_APV":1,
            "ST_t-channel_antitop":1,
            "ST_tW_top":1,
            "WJetsToQQ_HT-800toInf":1,
            "WWZ":1,
            "ZJetsToQQ_HT-800toInf":1,
            "QCD_HT1000to1500_APVv2":1,
            "ST_t-channel_antitop_APV":1,
            "ST_tW_top_APV":1,
            "WJetsToQQ_HT-800toInf_APV":1,
            "WWZ_APV":1,
            "ZZ":1,
            "QCD_HT1500to2000":1,
            "ST_t-channel_top":1,
            "TTToHadronic":1,
            "WW":1,
            "WZ":1,
            "ZZ_APV":1,
        }

    def DasFiles(self,ds):
        Files = getoutput('/cvmfs/cms.cern.ch/common/dasgoclient --query="file dataset=%s" -limit=0 '%(ds))
        Files = [i.replace("\n","").replace(" ","") for i in Files.split("\n")]
        return Files

    def Files_Splitter(self,files,Nperjobs):
        Njob = int(float(len(files))/float(Nperjobs))+1
        files_ = []
        for i in range(Njob):
            down = i*Nperjobs
            up   = (i+1)*Nperjobs
            if down >= len(files) : continue
            if up > len(files) : up = len(files)
            files_.append(files[down:up])
        return files_

    def Configer(self):
        dic = {}
        for ds in self.Samples:
            dic[ds] = {}
            files_ = self.DasFiles(self.DAS[ds])
            files_ = self.Files_Splitter(files_,self.Nperjobs[ds])
            for index,ifiles in enumerate(files_):
                dic[ds][str(index)] = ifiles
        with open(self.jsonfile,"w") as f:
            json.dump(dic,f,indent = 4)

samples_toRun = ["WWW"]
File_json_ = File_json("/mnt/ceph/connect/user/qilongguo/work/EFT_VVV/VVVun/V4/CMSSW_10_6_27/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/Condor/production/Files/1lepton.json", Samples_ToRun = samples_toRun )
File_json_.Configer()

def additional(ds):
    return " --year 2016pre -m "

Condor_ = Condor(
    "/mnt/ceph/connect/user/qilongguo/work/EFT_VVV/VVVun/V4/CMSSW_10_6_27/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/Condor/production/Files/1lepton.json", # Files.json
    samples_toRun,
    ["%s/%s"%(os.getcwd(),"x509up_u100637"),"%s/scripts/%s"%(os.getcwd(),"SearchSite.py"),"%s/scripts/%s"%(os.getcwd(),"ValidSite.py")], # transfer_input_files
    "tree.root", # transfer_output_files
    "/stash/user/qilongguo/public/ROOTFILES/VVV/1lepton/2016/nanoAODv9_corr/V1/" , # outputPath
    "2016", # YEAR
    additional, # additional argument
    excutable = "exe.sh",
    TaskFolder = "production/Task_UL2016_MC_22_2_4",
)
Condor_.Generate_Scripts()
