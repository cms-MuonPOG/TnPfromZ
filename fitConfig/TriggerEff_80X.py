import FWCore.ParameterSet.Config as cms
import os
import sys
args = sys.argv[1:]
if (sys.argv[0] == "cmsRun"): args =sys.argv[2:]
scenario = "data_all"
if len(args) > 0: scenario = args[0]
print "Will run scenario ", scenario 

### USAGE:
###    cmsRun TriggerEff.py <scenario> [ <id> [ <binning1> ... <binningN> ] ]
###    ex> cmsRun TriggerEff.py mc IsoMu20_from_Tight2012
### scenarios:
###   - data_all (default)  
###   - signal_mc

### newly added variable on top of default TnP tree by using "AddBranch.py":
### [IsoMu24_OR_IsoTkMu24]: IsoMu24 == 1 or IsoTkMu24 == 1
### [Mu50_OR_TkMu50]: Mu50 == 1 or HLT_TkMu50 == 1
### [pair_dPhi]: abs(tag_phi - phi) if abs(tag_phi - phi) < 3.1415926535 else 2*3.1415926535 - abs(tag_phi - phi);tag_eta;eta;phi;tag_phi
### [pair_dPhiPrimeDeg]: pair_dPhi*(180/3.1415926535) if ((tag_eta > 0.9 and eta > 0.9) or (tag_eta < -0.9 and eta < -0.9)) else 999;pair_dPhi;tag_eta;eta;phi;tag_phi

def Add_AdditionalBranches( _PassingProbe, _ProbeCondition):
    if _PassingProbe == "IsoMu24_OR_IsoTkMu24":
        Template.Categories.IsoMu24_OR_IsoTkMu24 = cms.vstring("IsoMu24_OR_IsoTkMu24", "dummy[pass=1,fail=0]")
        Template.Categories.Tight2012 = cms.vstring("Tight2012", "dummy[pass=1,fail=0]")
        Template.Variables.combRelIsoPF04dBeta = cms.vstring("pf relative isolation", "0", "999", "")
        Template.Variables.pair_dPhiPrimeDeg = cms.vstring("pair_dPhiPrimeDeg", "0", "9999", "")

    elif _PassingProbe == "Mu50_OR_TkMu50":
        Template.Categories.Mu50_OR_TkMu50 = cms.vstring("Mu50_OR_TkMu50", "dummy[pass=1,fail=0]")
        Template.Categories.HighPt = cms.vstring("HighPt", "dummy[pass=1,fail=0]")
        Template.Variables.relTkIso = cms.vstring("Relative Tracker Isolation", "0", "999", "")
        Template.Variables.pair_dPhiPrimeDeg = cms.vstring("pair_dPhiPrimeDeg", "0", "9999", "")


def FindTnPTreeName( List_TnPTree, _PassingProbe, _ProbeCondition ):
    if _PassingProbe == "IsoMu24_OR_IsoTkMu24":
        List_TnPTree.append( "TnPTree_Run2016BCDEF_MuonPOG_TrigSF_Mu24_addBranch_final.root" )
        List_TnPTree.append( "TnPTree_Madgraph_Moriond17_MuonPOG_TrigSF_Mu24_addBranch_final_addWeight.root" )

    elif _PassingProbe == "Mu50_OR_TkMu50":
        List_TnPTree.append( "TnPTree_Run2016BCDEF_MuonPOG_TrigSF_Mu50_addBranch_final.root" )
        List_TnPTree.append( "TnPTree_Madgraph_Moriond17_MuonPOG_TrigSF_Mu50_addBranch_final_addWeight.root" ) 

    else:
        print "No corresponding tree!"
        sys.exit()


PassingProbe = ""
ProbeCondition = ""
if "_from_" in args[1]:
    PassingProbe = args[1].split("_from_")[0]
    ProbeCondition = args[1].split("_from_")[1]
else:
    PassingProbe = args[1]
    ProbeCondition = "None"

print "PassingProbe: " + PassingProbe
print "On top of " + ProbeCondition

version = "v20170202_1st_ComputeSF_ForMoriond17_RunBtoF";

BaseLocation = ""
TnPLocation = ""
hostName = os.environ['HOSTNAME']
if hostName.endswith('sdfarm.kr'): # -- KISTI -- #
    TnPLocation = "/cms/home/kplee/scratch/TagProbeTrees/MuonPOG_80X";
else:
    TnPLocation = "/home/kplee/data1/TagProbe/MuonPOG_80X";

BaseLocation = TnPLocation + "/" + version;

# Type = os.getcwd().split("/")[-2] # -- Dir name -- #
Type = "None"

List_TnPTree = [] # -- structure: [Data tree, MC tree] -- #
FindTnPTreeName( List_TnPTree, PassingProbe, ProbeCondition )

Ntuple_Data = cms.vstring( "file:"+BaseLocation+"/"+List_TnPTree[0] )
Ntuple_MC = cms.vstring( "file:"+BaseLocation+"/"+List_TnPTree[1] )

print "+" * 100;
print "Type: " + Type
print "Data Location: ", Ntuple_Data
print "MC location: ", Ntuple_MC
print "+" * 100;

process = cms.Process("TagProbe")

process.load('FWCore.MessageService.MessageLogger_cfi')

process.source = cms.Source("EmptySource")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )

Template = cms.EDAnalyzer("TagProbeFitTreeAnalyzer",
    NumCPU = cms.uint32(1),
    SaveWorkspace = cms.bool(False),

    Variables = cms.PSet(
        mass = cms.vstring("Tag-muon Mass", "70", "130", "GeV/c^{2}"),
        pt = cms.vstring("muon p_{T}", "0", "1000", "GeV/c"),
        phi = cms.vstring("muon #phi", "-3.14", "3.14", ""),
        tag_pt = cms.vstring("tag muon p_{T}", "0", "1000", "GeV/c"),
        eta    = cms.vstring("muon #eta", "-2.5", "2.5", ""),
        abseta = cms.vstring("muon |#eta|", "0", "2.5", ""),
        tag_abseta = cms.vstring("tag muon |#eta|", "0", "2.5", ""),
        tag_nVertices = cms.vstring("Number of vertices", "0", "999", ""),

        pair_deltaR = cms.vstring("pair_deltaR", "0", "999", ""),
        
    ),

    Categories = cms.PSet(
        tag_IsoMu24 = cms.vstring("tag_IsoMu24", "dummy[pass=1,fail=0]"),
    ),

    Expressions = cms.PSet(

    ),

    Cuts = cms.PSet(

    ),

    PDFs = cms.PSet(
        voigtPlusExpo = cms.vstring(
            "Voigtian::signal(mass, mean[90,80,100], width[2.495], sigma[3,1,20])",
            "Exponential::backgroundPass(mass, lp[0,-5,5])",
            "Exponential::backgroundFail(mass, lf[0,-5,5])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusExpo = cms.vstring(
            "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
            "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,2,10])",
            "SUM::signal(vFrac[0.8,0,1]*signal1, signal2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        # -- PDF Sets for the case of failing on error calculation by MINOS -- #
        vpvPlusExpo2 = cms.vstring(
            "Voigtian::signal1(mass, mean1[91,86,96], width[2.495], sigma1[2,1,5])",
            "Voigtian::signal2(mass, mean2[91,81,101], width,        sigma2[6,3,10])",
            "SUM::signal(vFrac[0.8,0,1]*signal1, signal2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        # -- Separate signal model of passing probe and failing probe -- #
        vpvPlusExpo3 = cms.vstring(
            "Voigtian::signalPass1(mass, meanPass1[91,84,98], width[2.495], sigmaPass1[2.5,1,6])",
            "Voigtian::signalPass2(mass, meanPass2[91,81,101], width,        sigmaPass2[5,1,10])",
            "SUM::signalPass(vFracPass[0.8,0,1]*signalPass1, signalPass2)",
            "Voigtian::signalFail1(mass, meanFail1[91,84,98], width[2.495], sigmaFail1[2.5,1,6])",
            "Voigtian::signalFail2(mass, meanFail2[91,81,101], width,        sigmaFail2[5,1,10])",
            "SUM::signalFail(vFracFail[0.8,0,1]*signalFail1, signalFail2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        # -- PDF Sets for the case of failing on error calculation by MINOS -- #
        vpvPlusExpo4 = cms.vstring(
            "Voigtian::signalPass1(mass, meanPass1[91,86,96], width[2.495], sigmaPass1[2.5,1,5])",
            "Voigtian::signalPass2(mass, meanPass2[91,78,104], width,        sigmaPass2[5,1,8])",
            "SUM::signalPass(vFracPass[0.7,0,1]*signalPass1, signalPass2)",
            "Voigtian::signalFail1(mass, meanFail1[91,86,96], width[2.495], sigmaFail1[2.5,1,5])",
            "Voigtian::signalFail2(mass, meanFail2[91,82,100], width,        sigmaFail2[5,1,10])",
            "SUM::signalFail(vFracFail[0.7,0,1]*signalFail1, signalFail2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),

        # -- PDF Sets for the case of failing on error calculation by MINOS -- #
        vpvPlusExpo5 = cms.vstring(
            "Voigtian::signalPass1(mass, meanPass1[91.1,86.3,96.1], width[2.495], sigmaPass1[2.52,1.4,5.1])",
            "Voigtian::signalPass2(mass, meanPass2[91.2,78.4,104.5], width,        sigmaPass2[5.12,1.3,8.2])",
            "SUM::signalPass(vFracPass[0.7,0,1]*signalPass1, signalPass2)",
            "Voigtian::signalFail1(mass, meanFail1[91.3,86.1,96.3], width[2.495], sigmaFail1[2.4,1,5.3])",
            "Voigtian::signalFail2(mass, meanFail2[91.2,82.5,100.5], width,        sigmaFail2[5.2,1,10.1])",
            "SUM::signalFail(vFracFail[0.7,0,1]*signalFail1, signalFail2)",
            "Exponential::backgroundPass(mass, lp[-0.11,-1.3,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.12,-1.2,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        
        vpvPlusExpoMin70 = cms.vstring(
            "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
            "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
            "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0.7,1]",
            "signalFractionInPassing[0.9]"
        )
    ),

    binnedFit = cms.bool(True),
    binsForFit = cms.uint32(40),
    saveDistributionsPlot = cms.bool(False),

    Efficiencies = cms.PSet(), # will be filled later
)

Add_AdditionalBranches( PassingProbe, ProbeCondition )

# print Template.Categories

PtMin = 9999
List_Pt22 = ["IsoMu20_OR_IsoTkMu20", "IsoMu20", "IsoTkMu20", "L1_IsoMu20", "L2_IsoMu20", "L3_IsoMu20", "IsoF_IsoMu20", "TkMuF_IsoTkMu20", "IsoF_IsoTkMu20", "Tight2012", "RelTrkIso_010", "L3_IsoMu20_OR_TkMuF_IsoTkMu20"]
List_Pt24 = ["IsoMu22_OR_IsoTkMu22"]
List_Pt26 = ["IsoMu24_OR_IsoTkMu24", "IsoMu24", "IsoTkMu24", "L2_IsoMu24", "L3_IsoMu24", "IsoF_IsoMu24", "TkMuF_IsoTkMu24", "IsoF_IsoTkMu24", "L3_IsoMu24_OR_TkMuF_IsoTkMu24", "IsoF_IsoMu24_OR_IsoF_IsoTkMu24"]
List_Pt29 = ["IsoMu27", "IsoTkMu27", "IsoMu27_OR_IsoTkMu27"]
List_Pt47 = ["Mu45_eta2p1", "L1_Mu45_eta2p1", "L2_Mu45_eta2p1"]
List_Pt52 = ["Mu50", "HLT_TkMu50", "Mu50_OR_TkMu50", "L1_Mu50", "L2_Mu50"]
if PassingProbe in List_Pt22: PtMin = 22
elif PassingProbe in List_Pt24: PtMin = 24
elif PassingProbe in List_Pt26: PtMin = 26
elif PassingProbe in List_Pt29: PtMin = 29
elif PassingProbe in List_Pt47: PtMin = 47
elif PassingProbe in List_Pt52: PtMin = 52

EtaMax = 2.4
List_eta2p1 = ["Mu45_eta2p1", "L1_Mu45_eta2p1", "L2_Mu45_eta2p1"]
if PassingProbe in List_eta2p1: 
    EtaMax = 2.1

PT_ETA_BINS = cms.PSet(
                        pt     = cms.vdouble( 0, 9999 ), # -- Will be set later -- #
                        abseta = cms.vdouble(0.0, 0.9, 1.2, 2.1, 2.4),
                        # abseta = cms.vdouble(0.0, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4),

                        # tag_IsoMu20 = cms.vstring("pass"),
                        # tag_pt =  cms.vdouble(22,9999)
                        tag_IsoMu24 = cms.vstring("pass"),
                        tag_pt =  cms.vdouble(26,9999),

)

if PassingProbe in List_Pt22: PT_ETA_BINS.pt = cms.vdouble( 22, 25, 30, 40, 50, 60, 120, 200, 500 )
elif PassingProbe in List_Pt24: PT_ETA_BINS.pt = cms.vdouble( 24, 30, 40, 50, 60, 120, 200, 500 ) 
elif PassingProbe in List_Pt26: PT_ETA_BINS.pt = cms.vdouble( 26, 30, 40, 50, 60, 120, 200, 500 ) 
elif PassingProbe in List_Pt29: PT_ETA_BINS.pt = cms.vdouble( 29, 40, 50, 60, 120, 200, 500 ) 
elif PassingProbe in List_Pt47: PT_ETA_BINS.pt = cms.vdouble( 47, 50, 60, 120, 200, 500 )
elif PassingProbe in List_Pt52: PT_ETA_BINS.pt = cms.vdouble( 52, 55, 60, 80, 120, 200, 300, 400, 800 )
# elif PassingProbe in List_Pt52: PT_ETA_BINS.pt = cms.vdouble( 53, 100, 200, 700 )

if EtaMax == 2.1: PT_ETA_BINS.abseta = cms.vdouble(0.0, 0.9, 1.2, 2.1)


PT_BINS = cms.PSet(
                        pt     = cms.vdouble( 0, 9999 ), #Will be set later

                        abseta = cms.vdouble(0.0, EtaMax),
                        # tag_IsoMu20 = cms.vstring("pass"),
                        # tag_pt =  cms.vdouble(22,9999),
                        tag_IsoMu24 = cms.vstring("pass"),
                        tag_pt =  cms.vdouble(26,9999),
                        tag_abseta =  cms.vdouble(0, 2.4),
)
List_Binning_TurnOn_16 = ["L1SingleMu16"]
List_Binning_TurnOn_18 = ["L1_IsoMu20"]
List_Binning_TurnOn_20 = ["IsoMu20_OR_IsoTkMu20", "IsoMu20", "IsoTkMu20", "L2_IsoMu20", "L3_IsoMu20", "IsoF_IsoMu20", "TkMuF_IsoTkMu20", "IsoF_IsoTkMu20", "L2_Mu45_eta2p1", "L2_Mu50", "L3_IsoMu20_OR_TkMuF_IsoTkMu20"]
List_Binning_TurnOn_22 = ["IsoMu22_OR_IsoTkMu22", "L1_Mu45_eta2p1", "L1_Mu50", "L1_IsoMu24"]
List_Binning_TurnOn_24 = ["IsoMu24_OR_IsoTkMu24", "IsoMu24", "IsoTkMu24", "L2_IsoMu24", "L3_IsoMu24", "IsoF_IsoMu24", "TkMuF_IsoTkMu24", "IsoF_IsoTkMu24", "L3_IsoMu24_OR_TkMuF_IsoTkMu24", "IsoF_IsoMu24_OR_IsoF_IsoTkMu24"]
List_Binning_TurnOn_26 = []
List_Binning_TurnOn_27 = ["IsoMu27_OR_IsoTkMu27", "IsoMu27", "IsoTkMu27"]
List_Binning_TurnOn_45 = ["Mu45_eta2p1"]
List_Binning_TurnOn_50 = ["Mu50", "HLT_TkMu50", "Mu50_OR_TkMu50"]
List_Binning_NoTurnOn = ["Tight2012", "RelTrkIso_010"]


if PassingProbe in List_Binning_TurnOn_16:
    PT_BINS.pt = cms.vdouble( 0, 10, 14, 16, 18, 20, 25, 30, 40, 50, 60, 80, 120, 200, 500 )
elif PassingProbe in List_Binning_TurnOn_18:
    PT_BINS.pt = cms.vdouble( 0, 10, 16, 18, 20, 22, 25, 30, 40, 50, 60, 80, 120, 200, 500 )
elif PassingProbe in List_Binning_TurnOn_20:
    PT_BINS.pt = cms.vdouble( 0, 10, 15, 18, 20, 22, 25, 30, 40, 50, 60, 80, 120, 200, 500 )
elif PassingProbe in List_Binning_TurnOn_22:
    PT_BINS.pt = cms.vdouble( 0, 10, 15, 20, 22, 24, 26, 30, 40, 50, 60, 80, 120, 200, 500 )
elif PassingProbe in List_Binning_TurnOn_24:
    PT_BINS.pt = cms.vdouble( 0, 10, 15, 18, 22, 24, 26, 30, 40, 50, 60, 80, 120, 200, 500 )
elif PassingProbe in List_Binning_TurnOn_26:
    PT_BINS.pt = cms.vdouble( 0, 10, 15, 20, 24, 26, 28, 30, 40, 50, 60, 80, 120, 200, 500 )
elif PassingProbe in List_Binning_TurnOn_27:
    PT_BINS.pt = cms.vdouble( 0, 15, 23, 25, 27, 29, 31, 40, 50, 60, 80, 120, 200, 500 )
elif PassingProbe in List_Binning_TurnOn_45:
    PT_BINS.pt = cms.vdouble( 0, 10, 15, 20, 25, 30, 40, 43, 45, 47, 50, 60, 80, 120, 200, 500 )
elif PassingProbe in List_Binning_TurnOn_50:
    PT_BINS.pt = cms.vdouble( 0, 10, 15, 20, 25, 30, 40, 45, 48, 50, 52, 55, 60, 80, 120, 200, 300, 400, 800 )
    # PT_BINS.pt = cms.vdouble( 0, 10, 15, 20, 25, 30, 40, 45, 48, 50, 53, 100, 200, 700 )
elif PassingProbe in List_Binning_NoTurnOn:
    PT_BINS.pt = cms.vdouble( 22, 25, 30, 40, 50, 60, 80, 120, 200, 500 )


ETA_BINS = cms.PSet(
					eta = cms.vdouble(-2.4, -2.1, -1.6, -1.2, -0.9, -0.3, -0.2, 0, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4),

                    pt     = cms.vdouble( PtMin, 9999 ),
                    # tag_IsoMu20 = cms.vstring("pass"),
                    # tag_pt =  cms.vdouble(22,9999),
                    tag_IsoMu24 = cms.vstring("pass"),
                    tag_pt =  cms.vdouble(26,9999),
                    tag_abseta =  cms.vdouble(0, 2.4),
                       )
if EtaMax == 2.1: ETA_BINS.eta = cms.vdouble(-2.1, -1.6, -1.2, -0.9, -0.3, -0.2, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1)

phi = 3.141592
degree15 = phi / 12;
PHI_BINS = cms.PSet(
                    phi     = cms.vdouble( (-1)*degree15*12, (-1)*degree15*11, (-1)*degree15*9, (-1)*degree15*7, (-1)*degree15*5, (-1)*degree15*3, (-1)*degree15*1, degree15*1, degree15*3, degree15*5, degree15*7, degree15*9, degree15*11, degree15*12),
                    
                    pt     = cms.vdouble( PtMin, 9999 ),
                    abseta = cms.vdouble(0.0, EtaMax),
                    # tag_IsoMu20 = cms.vstring("pass"),
                    # tag_pt =  cms.vdouble(22,9999),
                    tag_IsoMu24 = cms.vstring("pass"),
                    tag_pt =  cms.vdouble(26,9999),
                    tag_abseta =  cms.vdouble(0, 2.4),
                    )

VTX_BINS  = cms.PSet(
	tag_nVertices = cms.vdouble(2.5, 4.5, 6.5, 8.5, 10.5, 12.5, 14.5, 16.5, 18.5, 20.5, 
                                22.5, 24.5, 26.5, 28.5, 30.5, 32.5, 34.5, 36.5, 38.5, 40.5,
                                42.5, 44.5, 46.5, 48.5, 50.5),

    pt     = cms.vdouble(  PtMin, 9999 ),
    abseta = cms.vdouble(  0.0, EtaMax),
    # tag_IsoMu20 = cms.vstring("pass"),
    # tag_pt =  cms.vdouble(22,9999),
    tag_IsoMu24 = cms.vstring("pass"),
    tag_pt =  cms.vdouble(26,9999),
    tag_abseta =  cms.vdouble(0, 2.4),
)


process.TnP_MuonID = Template.clone(
    InputFileNames = cms.vstring(),
    InputTreeName = cms.string("fitter_tree"),
    InputDirectoryName = cms.string("tpTree"),
    OutputFileName = cms.string("TnP_MuonTrigger_%s.root" % scenario),
    Efficiencies = cms.PSet(),
)

#Add the variables for PU reweighting
if "_weight" in scenario:
    process.TnP_MuonID.WeightVariable = cms.string("weight")
    process.TnP_MuonID.Variables.weight = cms.vstring("weight","-10000","10000","")

if scenario=="data_25ns":
    process.TnP_MuonID.InputFileNames = Ntuple_Data

if "mc" in scenario:
    process.TnP_MuonID.InputFileNames = Ntuple_MC

#IDS = [ "IsoMu20","Mu20","L2fL1sMu16L1f0L2Filtered10Q","IsoTkMu20","L1sMu16"]
IDS = [args[1]] #here the id is taken from the arguments provided to cmsRun 
# ALLBINS = [ ("pt",PT_BINS), ("eta",ETA_BINS), ("vtx",VTX_BINS), ("pteta",PT_ETA_BINS) ]
# ALLBINS = [ ("pt",PT_BINS), ("eta",ETA_BINS), ("phi",PHI_BINS), ("vtx",VTX_BINS), ("pteta",PT_ETA_BINS) ]
# ALLBINS = [ ("pt",PT_BINS), ("eta",ETA_BINS), ("vtx",VTX_BINS), ("InstLumi",InstLumi_BINS) ]
# ALLBINS = [ ("pt",PT_BINS), ("eta",ETA_BINS), ("phi",PHI_BINS), ("vtx",VTX_BINS) ]
# ALLBINS = [ ("eta",ETA_BINS) ]
# ALLBINS = [ ("eta",ETA_BINS), ("vtx",VTX_BINS) ]
# ALLBINS = [ ("vtx",VTX_BINS) ]
# ALLBINS = [ ("eta",ETA_BINS), ("vtx",VTX_BINS), ("phi",PHI_BINS) ]
# ALLBINS = [ ("pt",PT_BINS), ("eta",ETA_BINS), ("phi",PHI_BINS), ("vtx",VTX_BINS), ("pteta",PT_ETA_BINS) ]
ALLBINS = [ ("pteta",PT_ETA_BINS) ]

# ALLBINS = [("pteta",PT_ETA_BINS)]
# ALLBINS = [("run", RUN_BINS)]
# ALLBINS = [("pt",PT_BINS), ("eta",ETA_BINS), ("phi",PHI_BINS), ("InstLumi",InstLumi_BINS), ("bx",BX_BINS) ]
# ALLBINS = [("InstLumi",InstLumi_BINS)]

if len(args) > 1 and args[1] not in IDS: IDS += [ args[1] ]
for ID in IDS:
    print "now doing ",ID
    if len(args) > 1 and ID != args[1]: continue
    for X,B in ALLBINS:
        if len(args) > 2 and X not in args[2:]: continue
        #Add the information about ID and binning into the outputFileName
        module = process.TnP_MuonID.clone(OutputFileName = cms.string("TnP_MuonTrigger_%s_%s_%s.root" % (scenario, ID, X)))
        
        shape = "vpvPlusExpo"
        if X == "pteta": shape = "vpvPlusExpo3"

        #DEN: Binning
        DEN = B.clone(); num = ID; numstate = "pass"

        # -- dR condition between tag & probe muons for all binning (larger than 0.3) -- #
        DEN.pair_deltaR = cms.vdouble(0.3, 999)

        # -- pair not critical: both on MC and data -- #
        DEN.pair_dPhiPrimeDeg = cms.vdouble( 70, 9999 )            

        if "_from_" in ID:
            parts = ID.split("_from_")
            num = parts[0]
            # add Additional ID conditions to the binning ... 
            # ex> cmsRun TriggerEff.py mc IsoMu20_and_Tight2012_from_SIP4_and_PFIso25 => SIP4 and PFIso25 info. is added to the binning definition
            for D in parts[1].split("_and_"):
                if D == "dBeta_015": DEN.combRelIsoPF04dBeta = cms.vdouble(0, 0.15)
                elif D == "dBeta_025": DEN.combRelIsoPF04dBeta = cms.vdouble(0, 0.25)
            	elif D == "RelTrkIso_010": DEN.relTkIso = cms.vdouble(0, 0.10)

                # Set D as the variable of DEN ... DEN.D = cms.vstring("pass")
                else: setattr(DEN, D, cms.vstring("pass"))

        print "#" * 100
        print "Binning variable: ", X
        print "Binning: ", DEN
        print "PDF: ", shape

        # numString: EfficiencyCategoryState variable. 
        # ex> cmsRun TriggerEff.py mc IsoMu20_and_Tight2012_from_SIP4_and_PFIso25 => numString = cms.vstring("IsoMu20", "pass", "Tight2012", "pass")
        numString = cms.vstring()
        for N in num.split("_and_"):
            numString += [N, "pass"]

        print "Passing probe condition: ", numString
        print "#" * 100
        print "\n"
        
        #Set Efficiency
        setattr(module.Efficiencies, ID+"_"+X, cms.PSet(
            EfficiencyCategoryAndState = numString,
            UnbinnedVariables = cms.vstring("mass"),
            BinnedVariables = DEN,
            BinToPDFmap = cms.vstring(shape)
        ))

        if scenario.find("mc") != -1:
            # setattr(module.Efficiencies, ID+"_"+X+"_mcTrue", cms.PSet(
            #     EfficiencyCategoryAndState = numString,
            #     UnbinnedVariables = cms.vstring("mass"),
            #     BinnedVariables = DEN.clone(mcTrue = cms.vstring("true"))
            # ))
            if "_weight" in scenario:
                getattr(module.Efficiencies, ID+"_"+X          ).UnbinnedVariables.append("weight")
                # getattr(module.Efficiencies, ID+"_"+X+"_mcTrue").UnbinnedVariables.append("weight")

        setattr(process, "TnP_MuonID_"+ID+"_"+X, module)        
        setattr(process, "run_"+ID+"_"+X, cms.Path(module))
