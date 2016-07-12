import FWCore.ParameterSet.Config as cms
import sys, os, shutil
from optparse import OptionParser
### USAGE: cmsRun fitMuonID.py TEST tight loose mc mc_all
###_id: tight, loose, medium, soft
###
###
###

#_*_*_*_*_*_
#Read Inputs
#_*_*_*_*_*_

#args = sys.argv[1:]
#iteration = ''
#if len(args) > 1: iteration = args[1]
#print "The iteration is", iteration
#_id = 'tight'
#if len(args) > 2: _id = args[2]
#print 'The _id is', _id 
#scenario = "data_all"
#if len(args) > 3: scenario = args[3]
#print "Will run scenario ", scenario
#sample = 'data'
#if len(args) > 4: sample = args[4]
#print 'The sample is', sample 

args = sys.argv[1:]
iteration = ''
if len(args) > 1: iteration = args[1]
print "The iteration is", iteration
_iso = 'tight'
if len(args) > 2: _iso = args[2]
print 'The _iso is', _iso 
_id = 'tight'
if len(args) > 3: _id = args[3]
print 'The _id is', _id 
scenario = "data_all"
if len(args) > 4: scenario = args[4]
print "Will run scenario ", scenario
sample = 'data'
if len(args) > 5: sample = args[5]
print 'The sample is', sample 
if len(args) > 6: binning = args[6]
print 'The binning is', binning


process = cms.Process("TagProbe")
process.load('FWCore.MessageService.MessageLogger_cfi')
process.source = cms.Source("EmptySource")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )

if not _iso in ['noiso', 'loose', 'tight', 'tkloose', 'tktight']: 
    print '@ERROR: _iso should be \'noiso\', \'loose\', \'tight\', \'tkloose\' or \'tktight\'. You used', _iso, '.Abort'
    sys.exit()
if not _id in ['loose', 'medium', 'medium_ichep', 'tight', 'soft', 'highpt']: 
    print '@ERROR: _id should be \'loos\', \'medium\', \'medium_ichep\', \'tight\', \'soft\', or \'highpt\'. You used', _id, '.Abort'
    sys.exit()

#_*_*_*_*_*_*_*_*_*_*_*_*
#Prepare variables, den, num and fit funct
#_*_*_*_*_*_*_*_*_*_*_*_*

#Set-up the mass range
_mrange = "70"
if not _iso == 'noiso': 
    _mrange = "77"
print '_mrange is', _mrange


if _id == "loose":
    Template = cms.EDAnalyzer("TagProbeFitTreeAnalyzer",
            NumCPU = cms.uint32(1),
        SaveWorkspace = cms.bool(False),
    
    
        Variables = cms.PSet(
            #essential for all den/num
            weight = cms.vstring("weight","-100","100",""),
            mass = cms.vstring("Tag-muon Mass", _mrange, "130", "GeV/c^{2}"),
            #variables for track only DEN
            tag_nVertices   = cms.vstring("Number of vertices", "0", "999", ""),
            phi    = cms.vstring("muon #phi at vertex", "-3.1416", "3.1416", ""),
            pt = cms.vstring("muon p_{T}", "0", "1000", "GeV/c"),
            eta    = cms.vstring("muon #eta", "-2.5", "2.5", ""),
            abseta = cms.vstring("muon |#eta|", "0", "2.5", ""),
            pair_probeMultiplicity = cms.vstring("pair_probeMultiplicity", "1","30",""),
            #for Iso
            combRelIsoPF04dBeta = cms.vstring("dBeta rel iso dR 0.4", "-2", "9999999", ""),
            #tag selection
            tag_combRelIsoPF04dBeta = cms.vstring("Tag dBeta rel iso dR 0.4", "-2", "9999999", ""),
            tag_pt = cms.vstring("Tag p_{T}", "0", "1000", "GeV/c"),
            ),
    
        Categories = cms.PSet(
            PF    = cms.vstring("PF Muon", "dummy[pass=1,fail=0]"),
            #tag selection
            tag_IsoMu22 = cms.vstring("PF Muon", "dummy[pass=1,fail=0]"),
        ),
    
        Expressions = cms.PSet(
            #ID 
            Loose_noIPVar = cms.vstring("Loose_noIPVar", "PF==1", "PF"),
        ),
    
        Cuts = cms.PSet(
            #ID
            Loose_noIP = cms.vstring("Loose_noIP", "Loose_noIPVar", "0.5"),
            #Isolations
            LooseIso4 = cms.vstring("LooseIso4" ,"combRelIsoPF04dBeta", "0.25"),
            TightIso4 = cms.vstring("TightIso4" ,"combRelIsoPF04dBeta", "0.15"),
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
            vpvPlusExpoMin70 = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
                "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
            ),
            vpvPlusCheb = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                #par3
                "RooChebychev::backgroundPass(mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})",
                "RooChebychev::backgroundFail(mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})",
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
            )
        ),
    
        binnedFit = cms.bool(True),
        binsForFit = cms.uint32(40),
        saveDistributionsPlot = cms.bool(False),
    
        Efficiencies = cms.PSet(), # will be filled later
    )
elif _id == "medium":
    Template = cms.EDAnalyzer("TagProbeFitTreeAnalyzer",
            NumCPU = cms.uint32(1),
        SaveWorkspace = cms.bool(False),
    
    
        Variables = cms.PSet(
            #essential for all den/num
            weight = cms.vstring("weight","-100","100",""),
            mass = cms.vstring("Tag-muon Mass", _mrange, "130", "GeV/c^{2}"),
            #variables for track only DEN
            pt = cms.vstring("muon p_{T}", "0", "1000", "GeV/c"),
            eta    = cms.vstring("muon #eta", "-2.5", "2.5", ""),
            tag_nVertices   = cms.vstring("Number of vertices", "0", "999", ""),
            phi    = cms.vstring("muon #phi at vertex", "-3.1416", "3.1416", ""),
            abseta = cms.vstring("muon |#eta|", "0", "2.5", ""),
            pair_probeMultiplicity = cms.vstring("pair_probeMultiplicity", "0","30",""),
            #for Iso
            combRelIsoPF04dBeta = cms.vstring("dBeta rel iso dR 0.4", "-2", "9999999", ""),
            #tag selection
            tag_combRelIsoPF04dBeta = cms.vstring("Tag dBeta rel iso dR 0.4", "-2", "9999999", ""),
            tag_pt = cms.vstring("Tag p_{T}", "0", "1000", "GeV/c"),
            ),
    
        Categories = cms.PSet(
            Medium2016  = cms.vstring("Medium Id. Muon (ICHEP version)", "dummy[pass=1,fail=0]"),
            #tag selection
            tag_IsoMu22 = cms.vstring("PF Muon", "dummy[pass=1,fail=0]"),
        ),
    
        Expressions = cms.PSet(
            #ID 
            Medium2016_noIPVar= cms.vstring("Medium2016_noIPVar", "Medium2016==1", "Medium2016"),
        ),
    
        Cuts = cms.PSet(
            #ID
            Medium2016_noIP= cms.vstring("Medium2016_noIP", "Medium2016_noIPVar", "0.5"),
            #Isolations
            LooseIso4 = cms.vstring("LooseIso4" ,"combRelIsoPF04dBeta", "0.25"),
            TightIso4 = cms.vstring("TightIso4" ,"combRelIsoPF04dBeta", "0.15"),
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
            vpvPlusExpoMin70 = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
                "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
            ),
            vpvPlusCheb = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                #par3
                "RooChebychev::backgroundPass(mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})",
                "RooChebychev::backgroundFail(mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})",
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
            )
        ),
    
        binnedFit = cms.bool(True),
        binsForFit = cms.uint32(40),
        saveDistributionsPlot = cms.bool(False),
    
        Efficiencies = cms.PSet(), # will be filled later
    )
elif _id == 'tight':
    Template = cms.EDAnalyzer("TagProbeFitTreeAnalyzer",
            NumCPU = cms.uint32(1),
        SaveWorkspace = cms.bool(False),
    
    
        Variables = cms.PSet(
            #essential for all den/num
            weight = cms.vstring("weight","-100","100",""),
            mass = cms.vstring("Tag-muon Mass", _mrange, "130", "GeV/c^{2}"),
            #variables for track only DEN
            pt = cms.vstring("muon p_{T}", "0", "1000", "GeV/c"),
            eta    = cms.vstring("muon #eta", "-2.5", "2.5", ""),
            tag_nVertices   = cms.vstring("Number of vertices", "0", "999", ""),
            phi    = cms.vstring("muon #phi at vertex", "-3.1416", "3.1416", ""),
            abseta = cms.vstring("muon |#eta|", "0", "2.5", ""),
            pair_probeMultiplicity = cms.vstring("pair_probeMultiplicity", "0","30",""),
            #variables for tightID
            dzPV = cms.vstring("dzPV", "-1000", "1000", ""),
            #for Iso
            combRelIsoPF04dBeta = cms.vstring("dBeta rel iso dR 0.4", "-2", "9999999", ""),
            relTkIso = cms.vstring("trk rel iso dR 0.3", "-2", "9999999", ""),
            #tag selection
            tag_combRelIsoPF04dBeta = cms.vstring("Tag dBeta rel iso dR 0.4", "-2", "9999999", ""),
            tag_pt = cms.vstring("Tag p_{T}", "0", "1000", "GeV/c"),
            ),
    
        Categories = cms.PSet(
            Tight2012 = cms.vstring("Tight Id. Muon", "dummy[pass=1,fail=0]"),
            #tag selection
            tag_IsoMu22 = cms.vstring("PF Muon", "dummy[pass=1,fail=0]"),
        ),
    
        Expressions = cms.PSet(
            #ID 
            Tight2012_zIPCutVar = cms.vstring("Tight2012_zIPCut", "Tight2012 == 1 && abs(dzPV) < 0.5", "Tight2012", "dzPV"),
        ),
    
        Cuts = cms.PSet(
            #ID
            Tight2012_zIPCut = cms.vstring("Tight2012_zIPCut", "Tight2012_zIPCutVar", "0.5"),
            #Isolations
            LooseIso4 = cms.vstring("LooseIso4" ,"combRelIsoPF04dBeta", "0.25"),
            TightIso4 = cms.vstring("TightIso4" ,"combRelIsoPF04dBeta", "0.15"),
            LooseTkIso3 = cms.vstring("LooseTkIso3" ,"relTkIso", "0.10"),
            TightTkIso3 = cms.vstring("TightTkIso3" ,"relTkIso", "0.05"),
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
            vpvPlusExpoMin70 = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
                "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
            ),
            vpvPlusCheb = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                #par3
                "RooChebychev::backgroundPass(mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})",
                "RooChebychev::backgroundFail(mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})",
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
            )
        ),
    
        binnedFit = cms.bool(True),
        binsForFit = cms.uint32(40),
        saveDistributionsPlot = cms.bool(False),
    
        Efficiencies = cms.PSet(), # will be filled later
    )
elif _id == 'highpt':
    Template = cms.EDAnalyzer("TagProbeFitTreeAnalyzer",
            NumCPU = cms.uint32(1),
        SaveWorkspace = cms.bool(False),
    
    
        Variables = cms.PSet(
            #essential for all den/num
            weight = cms.vstring("weight","-100","100",""),
            pair_newTuneP_mass = cms.vstring("Tag-muon Mass", _mrange, "130", "GeV/c^{2}"),
            #variables for track only DEN
            pair_newTuneP_probe_pt = cms.vstring("muon p_{T} (tune-P)", "0", "1000", "GeV/c"),
            eta    = cms.vstring("muon #eta", "-2.5", "2.5", ""),
            tag_nVertices   = cms.vstring("Number of vertices", "0", "999", ""),
            phi    = cms.vstring("muon #phi at vertex", "-3.1416", "3.1416", ""),
            abseta = cms.vstring("muon |#eta|", "0", "2.5", ""),
            pair_probeMultiplicity = cms.vstring("pair_probeMultiplicity", "0","30",""),
            #variables for tightID
            dzPV = cms.vstring("dzPV", "-1000", "1000", ""),
            #for Iso
            relTkIso = cms.vstring("trk rel iso dR 0.3", "-2", "9999999", ""),
            #tag selection
            tag_combRelIsoPF04dBeta = cms.vstring("Tag dBeta rel iso dR 0.4", "-2", "9999999", ""),
            tag_pt = cms.vstring("Tag p_{T}", "0", "1000", "GeV/c"),
            ),
    
        Categories = cms.PSet(
            HighPt = cms.vstring("High-pT Id. Muon", "dummy[pass=1,fail=0]"),
            #tag selection
            tag_IsoMu22 = cms.vstring("PF Muon", "dummy[pass=1,fail=0]"),
        ),
    
        Expressions = cms.PSet(
            #ID 
            HighPt_zIPCutVar = cms.vstring("HighPt_zIPCut", "HighPt == 1 && abs(dzPV) < 0.5", "HighPt", "dzPV"),
        ),
    
        Cuts = cms.PSet(
            #ID
            HighPt_zIPCut = cms.vstring("HighPt_zIPCut", "HighPt_zIPCutVar", "0.5"),
            #Isolations
            LooseTkIso3 = cms.vstring("LooseTkIso3" ,"relTkIso", "0.10"),
            TightTkIso3 = cms.vstring("TightTkIso3" ,"relTkIso", "0.05"),
        ),
    
                              
        PDFs = cms.PSet(
            voigtPlusExpo = cms.vstring(
                "Voigtian::signal(pair_newTuneP_mass, mean[90,80,100], width[2.495], sigma[3,1,20])",
                "Exponential::backgroundPass(pair_newTuneP_mass, lp[0,-5,5])",
                "Exponential::backgroundFail(pair_newTuneP_mass, lf[0,-5,5])",
                "efficiency[0.9,0,1]",
                "signalFractionInPassing[0.9]"
            ),
            vpvPlusExpo = cms.vstring(
                "Voigtian::signal1(pair_newTuneP_mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
                "Voigtian::signal2(pair_newTuneP_mass, mean2[90,80,100], width,        sigma2[4,2,10])",
                "SUM::signal(vFrac[0.8,0,1]*signal1, signal2)",
                "Exponential::backgroundPass(pair_newTuneP_mass, lp[-0.1,-1,0.1])",
                "Exponential::backgroundFail(pair_newTuneP_mass, lf[-0.1,-1,0.1])",
                "efficiency[0.9,0,1]",
                "signalFractionInPassing[0.9]"
            ),
            vpvPlusExpoMin70 = cms.vstring(
                "Voigtian::signal1(pair_newTuneP_mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
                "Voigtian::signal2(pair_newTuneP_mass, mean2[90,80,100], width,        sigma2[4,3,10])",
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                "Exponential::backgroundPass(pair_newTuneP_mass, lp[-0.1,-1,0.1])",
                "Exponential::backgroundFail(pair_newTuneP_mass, lf[-0.1,-1,0.1])",
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
            ),
            vpvPlusCheb = cms.vstring(
                "Voigtian::signal1(pair_newTuneP_mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
                "Voigtian::signal2(pair_newTuneP_mass, mean2[90,80,100], width,        sigma2[4,3,10])",
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                #par3
                "RooChebychev::backgroundPass(pair_newTuneP_mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})",
                "RooChebychev::backgroundFail(pair_newTuneP_mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})",
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
            )
        ),
    
        binnedFit = cms.bool(True),
        binsForFit = cms.uint32(40),
        saveDistributionsPlot = cms.bool(False),
    
        Efficiencies = cms.PSet(), # will be filled later
    )
elif _id == 'soft':
    Template = cms.EDAnalyzer("TagProbeFitTreeAnalyzer",
            NumCPU = cms.uint32(1),
        SaveWorkspace = cms.bool(False),
    
    
        Variables = cms.PSet(
            #essential for all den/num
            weight = cms.vstring("weight","-100","100",""),
            mass = cms.vstring("Tag-muon Mass", _mrange, "130", "GeV/c^{2}"),
            #variables for track only DEN
            pt = cms.vstring("muon p_{T}", "0", "1000", "GeV/c"),
            eta    = cms.vstring("muon #eta", "-2.5", "2.5", ""),
            tag_nVertices   = cms.vstring("Number of vertices", "0", "999", ""),
            phi    = cms.vstring("muon #phi at vertex", "-3.1416", "3.1416", ""),
            abseta = cms.vstring("muon |#eta|", "0", "2.5", ""),
            pair_probeMultiplicity = cms.vstring("pair_probeMultiplicity", "0","30",""),
            #variables for tightID
            dB = cms.vstring("dB", "-1000", "1000", ""),
            dzPV = cms.vstring("dzPV", "-1000", "1000", ""),
            tkTrackerLay = cms.vstring("tkTrackerLay", "-10","1000",""),
            tkPixelLay = cms.vstring("tkPixelLay", "-10","1000",""),
            #tag selection
            tag_combRelIsoPF04dBeta = cms.vstring("Tag dBeta rel iso dR 0.4", "-2", "9999999", ""),
            tag_pt = cms.vstring("Tag p_{T}", "0", "1000", "GeV/c"),
            ),
    
        Categories = cms.PSet(
            TMOST = cms.vstring("TMOneStationTight", "dummy[pass=1,fail=0]"),
            Track_HP = cms.vstring("High-Purity muons", "dummy[pass=1,fail=0]"),
            #tag selection
            tag_IsoMu22 = cms.vstring("PF Muon", "dummy[pass=1,fail=0]"),
        ),
    
        Expressions = cms.PSet(
            #ID 
            SoftVar = cms.vstring("SoftVar", "TMOST == 1 && tkTrackerLay > 5 && tkPixelLay > 0 && abs(dzPV) < 20 && abs(dB) < 0.3 && Track_HP == 1", "TMOST","tkTrackerLay", "tkPixelLay", "dzPV", "dB", "Track_HP"),
        ),
    
        Cuts = cms.PSet(
            #ID
            SoftID = cms.vstring("Soft", "SoftVar", "0.5"),
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
            vpvPlusExpoMin70 = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
                "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
            ),
            vpvPlusCheb = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                #par3
                "RooChebychev::backgroundPass(mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})",
                "RooChebychev::backgroundFail(mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})",
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
            )
        ),
    
        binnedFit = cms.bool(True),
        binsForFit = cms.uint32(40),
        saveDistributionsPlot = cms.bool(False),
    
        Efficiencies = cms.PSet(), # will be filled later
    )

#_*_*_*_*_*_*_*_*_*_*_*_*
#Denominators and Binning
#_*_*_*_*_*_*_*_*_*_*_*_*
#For ID

if _id == "highpt" : 
    ETA_BINS = cms.PSet(
        pair_newTuneP_probe_pt  = cms.vdouble(20, 500),
        eta = cms.vdouble(-2.4, -2.1, -1.6, -1.2, -0.9, -0.3, -0.2, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"), 
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
    ETA_BINS_HPT = cms.PSet(
        pair_newTuneP_probe_pt  = cms.vdouble(55, 500),
        eta = cms.vdouble(-2.4, -2.1, -1.6, -1.2, -0.9, -0.3, -0.2, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"), 
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
    COARSE_ETA_BINS = cms.PSet(
        #Main
        pair_newTuneP_probe_pt     = cms.vdouble(20, 500),
        abseta = cms.vdouble(0.0, 0.9, 1.2, 2.1, 2.4),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"), 
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
    PT_ALLETA_BINS = cms.PSet(
        #Main
        pair_newTuneP_probe_pt     = cms.vdouble(20, 25, 30, 40, 50, 55, 60, 80, 120, 200, 500),
        abseta = cms.vdouble(  0.0, 2.4),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"), 
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
    PT_ETA_BINS = cms.PSet(
        #Main
        #pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120, 200),
        pair_newTuneP_probe_pt     = cms.vdouble(20, 25, 30, 40, 50, 55, 60, 80, 120, 200, 500),
        #For testing bkg function
        #pt     = cms.vdouble(60, 80, 120, 200),
        abseta = cms.vdouble( 0., 0.9, 1.2, 2.1, 2.4),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"), 
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
        
    )
    PT_HIGHABSETA = cms.PSet(
        pair_newTuneP_probe_pt     = cms.vdouble(20, 30, 40, 50, 55, 60, 80, 120, 200, 500),
        abseta = cms.vdouble(2.1, 2.4),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"), 
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
    VTX_BINS_ETA24  = cms.PSet(
        pair_newTuneP_probe_pt     = cms.vdouble( 20, 500 ),
        abseta = cms.vdouble(0.0, 2.4),
        tag_nVertices = cms.vdouble(0.5,2.5,4.5,6.5,8.5,10.5,12.5,14.5,16.5,18.5,20.5,22.5,24.5,26.5,28.5,30.5),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"),
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
    PHI_BINS = cms.PSet(
        pair_newTuneP_probe_pt     = cms.vdouble(20, 500),
        abseta = cms.vdouble(0.0, 2.4),
        phi =  cms.vdouble(-3.1416, -2.618, -2.0944, -1.5708, -1.0472, -0.5236, 0, 0.5236, 1.0472, 1.5708, 2.0944, 2.618, 3.1416),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"),
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
else:
        ETA_BINS = cms.PSet(
        pt  = cms.vdouble(20, 500),
        eta = cms.vdouble(-2.4, -2.1, -1.6, -1.2, -0.9, -0.3, -0.2, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"), 
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
    ETA_BINS_HPT = cms.PSet(
        pt  = cms.vdouble(55, 500),
        eta = cms.vdouble(-2.4, -2.1, -1.6, -1.2, -0.9, -0.3, -0.2, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"), 
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
    COARSE_ETA_BINS = cms.PSet(
        #Main
        pt     = cms.vdouble(20, 500),
        abseta = cms.vdouble(0.0, 0.9, 1.2, 2.1, 2.4),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"), 
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
    PT_ALLETA_BINS = cms.PSet(
        #Main
        pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120, 200, 500),
        abseta = cms.vdouble(  0.0, 2.4),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"), 
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
    PT_ETA_BINS = cms.PSet(
        #Main
        #pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120, 200),
        pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120, 200, 500),
        #For testing bkg function
        #pt     = cms.vdouble(60, 80, 120, 200),
        abseta = cms.vdouble( 0., 0.9, 1.2, 2.1, 2.4),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"), 
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
        
    )
    PT_HIGHABSETA = cms.PSet(
        pt     = cms.vdouble(20, 30, 40, 50, 60, 80, 120, 200, 500),
        abseta = cms.vdouble(2.1, 2.4),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"), 
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
    VTX_BINS_ETA24  = cms.PSet(
        pt     = cms.vdouble( 20, 500 ),
        abseta = cms.vdouble(0.0, 2.4),
        tag_nVertices = cms.vdouble(0.5,2.5,4.5,6.5,8.5,10.5,12.5,14.5,16.5,18.5,20.5,22.5,24.5,26.5,28.5,30.5),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"),
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
    PHI_BINS = cms.PSet(
        pt     = cms.vdouble(20, 500),
        abseta = cms.vdouble(0.0, 2.4),
        phi =  cms.vdouble(-3.1416, -2.618, -2.0944, -1.5708, -1.0472, -0.5236, 0, 0.5236, 1.0472, 1.5708, 2.0944, 2.618, 3.1416),
        pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
        #tag selections
        tag_pt = cms.vdouble(23, 500),
        tag_IsoMu22 = cms.vstring("pass"),
        tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
    
#For IP on ID
LOOSE_ETA_BINS = cms.PSet(
    pt  = cms.vdouble(20, 500),
    eta = cms.vdouble(-2.4, -2.1, -1.6, -1.2, -0.9, -0.3, -0.2, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    PF = cms.vstring("pass"), 
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
LOOSE_COARSE_ETA_BINS = cms.PSet(
    #Main
    pt     = cms.vdouble(20, 500),
    abseta = cms.vdouble(0.0, 0.9, 1.2, 2.1, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    PF = cms.vstring("pass"), 
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
LOOSE_PT_ALLETA_BINS = cms.PSet(
    pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120, 200, 500),
    abseta = cms.vdouble(  0.0, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    PF = cms.vstring("pass"), 
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
LOOSE_PT_ETA_BINS = cms.PSet(
    #pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120, 200),
    pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120,  200, 500),
    abseta = cms.vdouble( 0., 0.9, 1.2, 2.1, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    PF = cms.vstring("pass"), 
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
LOOSE_VTX_BINS_ETA24  = cms.PSet(
    pt     = cms.vdouble( 20, 500 ),
    abseta = cms.vdouble(  0.0, 2.4),
    tag_nVertices = cms.vdouble(0.5,2.5,4.5,6.5,8.5,10.5,12.5,14.5,16.5,18.5,20.5,22.5,24.5,26.5,28.5,30.5),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    PF = cms.vstring("pass"), 
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"),
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
LOOSE_PHI_BINS = cms.PSet(
    pt     = cms.vdouble(20, 500),
    abseta = cms.vdouble(  0.0, 2.4),
    phi =  cms.vdouble(-3.1416, -2.618, -2.0944, -1.5708, -1.0472, -0.5236, 0, 0.5236, 1.0472, 1.5708, 2.0944, 2.618, 3.1416),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    PF = cms.vstring("pass"), 
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"),
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
#MEDIUM
MEDIUM_ETA_BINS = cms.PSet(
    pt  = cms.vdouble(20, 500),
    eta = cms.vdouble(-2.4, -2.1, -1.6, -1.2, -0.9, -0.3, -0.2, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    Medium2016 = cms.vstring("pass"), 
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
MEDIUM_COARSE_ETA_BINS = cms.PSet(
    #Main
    pt     = cms.vdouble(20, 500),
    abseta = cms.vdouble(0.0, 0.9, 1.2, 2.1, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    Medium2016 = cms.vstring("pass"), 
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
MEDIUM_PT_ALLETA_BINS = cms.PSet(
    pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120, 200, 500),
    abseta = cms.vdouble(  0.0, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    Medium2016 = cms.vstring("pass"), 
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
MEDIUM_PT_ETA_BINS = cms.PSet(
    #pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120, 200),
    pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120, 200, 500),
    abseta = cms.vdouble( 0., 0.9, 1.2, 2.1, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    Medium2016 = cms.vstring("pass"), 
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    
)
MEDIUM_VTX_BINS_ETA24  = cms.PSet(
    pt     = cms.vdouble( 20, 500 ),
    abseta = cms.vdouble(  0.0, 2.4),
    tag_nVertices = cms.vdouble(0.5,2.5,4.5,6.5,8.5,10.5,12.5,14.5,16.5,18.5,20.5,22.5,24.5,26.5,28.5,30.5),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    Medium2016 = cms.vstring("pass"), 
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"),
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
MEDIUM_PHI_BINS = cms.PSet(
    pt     = cms.vdouble(20, 500),
    abseta = cms.vdouble(  0.0, 2.4),
    phi =  cms.vdouble(-3.1416, -2.618, -2.0944, -1.5708, -1.0472, -0.5236, 0, 0.5236, 1.0472, 1.5708, 2.0944, 2.618, 3.1416),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    Medium2016 = cms.vstring("pass"), 
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"),
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )
#TIGHT
TIGHT_ETA_BINS = cms.PSet(
    pt  = cms.vdouble(20, 500),
    eta = cms.vdouble(-2.4, -2.1, -1.6, -1.2, -0.9, -0.3, -0.2, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    Tight2012 = cms.vstring("pass"), 
    dzPV = cms.vdouble(-0.5, 0.5),
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
TIGHT_COARSE_ETA_BINS = cms.PSet(
    #Main
    pt     = cms.vdouble(20, 500),
    abseta = cms.vdouble(0.0, 0.9, 1.2, 2.1, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    Tight2012 = cms.vstring("pass"), 
    dzPV = cms.vdouble(-0.5, 0.5),
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
TIGHT_PT_ALLETA_BINS = cms.PSet(
    pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120,  200, 500),
    abseta = cms.vdouble(  0.0, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    Tight2012 = cms.vstring("pass"), 
    dzPV = cms.vdouble(-0.5, 0.5),
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
TIGHT_PT_ETA_BINS = cms.PSet(
    #pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120, 200),
    pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120, 200, 500),
    abseta = cms.vdouble( 0., 0.9, 1.2, 2.1, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    Tight2012 = cms.vstring("pass"), 
    dzPV = cms.vdouble(-0.5, 0.5),
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
TIGHT_VTX_BINS_ETA24  = cms.PSet(
    pt     = cms.vdouble( 20, 500 ),
    abseta = cms.vdouble(  0.0, 2.4),
    tag_nVertices = cms.vdouble(0.5,2.5,4.5,6.5,8.5,10.5,12.5,14.5,16.5,18.5,20.5,22.5,24.5,26.5,28.5,30.5),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    Tight2012 = cms.vstring("pass"), 
    dzPV = cms.vdouble(-0.5, 0.5),
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"),
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
TIGHT_PHI_BINS = cms.PSet(
    pt     = cms.vdouble(20, 500),
    abseta = cms.vdouble(0.0, 2.4),
    phi =  cms.vdouble(-3.1416, -2.618, -2.0944, -1.5708, -1.0472, -0.5236, 0, 0.5236, 1.0472, 1.5708, 2.0944, 2.618, 3.1416),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    Tight2012 = cms.vstring("pass"), 
    dzPV = cms.vdouble(-0.5, 0.5),
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"),
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )

#HIGHPT
HIGHPT_ETA_BINS = cms.PSet(
    pair_newTuneP_probe_pt  = cms.vdouble(20, 500),
    eta = cms.vdouble(-2.4, -2.1, -1.6, -1.2, -0.9, -0.3, -0.2, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    HighPt = cms.vstring("pass"), 
    dzPV = cms.vdouble(-0.5, 0.5),
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
HIGHPT_ETA_BINS_HPT = cms.PSet(
    pair_newTuneP_probe_pt  = cms.vdouble(55, 500),
    eta = cms.vdouble(-2.4, -2.1, -1.6, -1.2, -0.9, -0.3, -0.2, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    HighPt = cms.vstring("pass"), 
    dzPV = cms.vdouble(-0.5, 0.5),
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
HIGHPT_COARSE_ETA_BINS = cms.PSet(
    #Main
    pair_newTuneP_probe_pt     = cms.vdouble(20, 500),
    abseta = cms.vdouble(0.0, 0.9, 1.2, 2.1, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    HighPt = cms.vstring("pass"), 
    dzPV = cms.vdouble(-0.5, 0.5),
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
HIGHPT_PT_ALLETA_BINS = cms.PSet(
    pair_newTuneP_probe_pt     = cms.vdouble(20, 25, 30, 40, 50, 55, 60, 80, 120,  200, 500),
    abseta = cms.vdouble(  0.0, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    HighPt = cms.vstring("pass"), 
    dzPV = cms.vdouble(-0.5, 0.5),
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
HIGHPT_PT_ETA_BINS = cms.PSet(
    #pt     = cms.vdouble(20, 25, 30, 40, 50, 60, 80, 120, 200),
    pair_newTuneP_probe_pt     = cms.vdouble(20, 25, 30, 40, 50, 55, 60, 80, 120, 200, 500),
    abseta = cms.vdouble( 0., 0.9, 1.2, 2.1, 2.4),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    HighPt = cms.vstring("pass"), 
    dzPV = cms.vdouble(-0.5, 0.5),
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"), 
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
HIGHPT_VTX_BINS_ETA24  = cms.PSet(
    pair_newTuneP_probe_pt = cms.vdouble( 20, 500 ),
    abseta = cms.vdouble(  0.0, 2.4),
    tag_nVertices = cms.vdouble(0.5,2.5,4.5,6.5,8.5,10.5,12.5,14.5,16.5,18.5,20.5,22.5,24.5,26.5,28.5,30.5),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    HighPt = cms.vstring("pass"), 
    dzPV = cms.vdouble(-0.5, 0.5),
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"),
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
)
HIGHPT_PHI_BINS = cms.PSet(
    pair_newTuneP_probe_pt = cms.vdouble(20, 500),
    abseta = cms.vdouble(0.0, 2.4),
    phi =  cms.vdouble(-3.1416, -2.618, -2.0944, -1.5708, -1.0472, -0.5236, 0, 0.5236, 1.0472, 1.5708, 2.0944, 2.618, 3.1416),
    pair_probeMultiplicity = cms.vdouble(0.5, 1.5),
    HighPt = cms.vstring("pass"), 
    dzPV = cms.vdouble(-0.5, 0.5),
    #tag selections
    tag_pt = cms.vdouble(23, 500),
    tag_IsoMu22 = cms.vstring("pass"),
    tag_combRelIsoPF04dBeta = cms.vdouble(-0.5, 0.2),
    )

if sample == "mc_noTrigg":
    process.TnP_MuonID = Template.clone(
        InputFileNames = cms.vstring(
            #'../Production/tnpZ_MC_noTrgMatch_SmallTree_v2.root',
            '../Production/tnpZ_MC_noTrgMatch_SmallTree_v3.root',
            ),
        InputTreeName = cms.string("fitter_tree"),
        InputDirectoryName = cms.string("tpTree"),
        OutputFileName = cms.string("TnP_MuonID_%s.root" % scenario),
        Efficiencies = cms.PSet(),
        )
if sample == "mc_wTrigg":
    process.TnP_MuonID = Template.clone(
        InputFileNames = cms.vstring(
            #'../Production/tnpZ_MC_wTrgMatch_SmallTree.root',
            '../Production/tnpZ_MC_wTrgMatch_SmallTree_v3.root',
            ),
        InputTreeName = cms.string("fitter_tree"),
        InputDirectoryName = cms.string("tpTree"),
        OutputFileName = cms.string("TnP_MuonID_%s.root" % scenario),
        Efficiencies = cms.PSet(),
        )
if sample == "mc_MAD":
    process.TnP_MuonID = Template.clone(
        InputFileNames = cms.vstring(
            #'samples/TnPTree_76X_DYLL_M50_MadGraphMLM_withNVtxWeights_total.root'
            #'root://eoscms//eos/cms/store/group/phys_muon/perrin/Ntuples/80X/tnpZ_MC_noTrgMatch.root'
            #'/afs/cern.ch/work/g/gaperrin/private/TnP/TnP_Muon/CMSSW_8_0_1/src/MuonAnalysis/TagAndProbe/test/zmumu/Example/Production/tnpZ_MC_SmallTree.root'
            '../Production/TnPTree_80X_DYLL_M50_MadGraphMLM_part1and2_withNVtxWeights.root',
            ),
        InputTreeName = cms.string("fitter_tree"),
        InputDirectoryName = cms.string("tpTree"),
        OutputFileName = cms.string("TnP_MuonID_%s.root" % scenario),
        Efficiencies = cms.PSet(),
        )
if sample == "mc_2016B":
    process.TnP_MuonID = Template.clone(
        InputFileNames = cms.vstring(
            '../Production/TnPTree_80X_DYLL_M50_MadGraphMLM_part1and2_withNVtxWeights_DataAndTopup.root',
            ),
        InputTreeName = cms.string("fitter_tree"),
        InputDirectoryName = cms.string("tpTree"),
        OutputFileName = cms.string("TnP_MuonID_%s.root" % scenario),
        Efficiencies = cms.PSet(),
        )
if sample == "data":
    process.TnP_MuonID = Template.clone(
        InputFileNames = cms.vstring(
            #'root://eoscms//eos/cms//store/group/phys_muon/TagAndProbe/Run2016/80X_v1/data/TnPTree_80X_Run2016B_v2_DCSOnly_RunList.root'
            '../Production/TnPTree_80X_Run2016B_v2_DCSOnly_RunList.root'
            ),
        InputTreeName = cms.string("fitter_tree"),
        InputDirectoryName = cms.string("tpTree"),
        OutputFileName = cms.string("TnP_MuonID_%s.root" % scenario),
        Efficiencies = cms.PSet(),
        )
if sample == "data_2016B":
    process.TnP_MuonID = Template.clone(
        InputFileNames = cms.vstring(
            'root://eoscms//eos/cms//store/group/phys_muon/TagAndProbe/Run2016/80X_v1/data/TnPTree_80X_Run2016B_v2_GoldenJSON_Run271036to273730_NotCompleted.root',
            'root://eoscms//eos/cms//store/group/phys_muon/TagAndProbe/Run2016/80X_v1/data/TnPTree_80X_Run2016B_v2_GoldenJSON_Run273731_to_274240_IncludingMissingLumi_NotCompleted.root'
            ),
        InputTreeName = cms.string("fitter_tree"),
        InputDirectoryName = cms.string("tpTree"),
        OutputFileName = cms.string("TnP_MuonID_%s.root" % scenario),
        Efficiencies = cms.PSet(),
        )
if scenario == "mc_all":
    print "Including the weight for MC"
    process.TnP_MuonID.WeightVariable = cms.string("weight")
    process.TnP_MuonID.Variables.weight = cms.vstring("weight","0","10","")
    

ID_BINS = []

#_*_*_*_*_*_*_*_*_*_*
#IDs/Den pair
#_*_*_*_*_*_*_*_*_*_*

#Loose ID
if _id == 'loose' and _iso == 'noiso':
    if binning == 'eta':
        ID_BINS = [
        (("Loose_noIP"), ("NUM_LooseID_DEN_genTracks_PAR_eta", ETA_BINS)),
        ]
    elif binning == 'pt_alleta':
        ID_BINS = [
        (("Loose_noIP"), ("NUM_LooseID_DEN_genTracks_PAR_pt_alleta_bin1", PT_ALLETA_BINS)),
        ]
    elif binning == 'pt_spliteta':
        ID_BINS = [
        (("Loose_noIP"), ("NUM_LooseID_DEN_genTracks_PAR_pt_spliteta_bin1", PT_ETA_BINS)),
        ]
    elif binning == 'all':
        ID_BINS = [
        (("Loose_noIP"), ("NUM_LooseID_DEN_genTracks_PAR_eta", ETA_BINS)),
        (("Loose_noIP"), ("NUM_LooseID_DEN_genTracks_PAR_pt_alleta_bin1", PT_ALLETA_BINS)),
        (("Loose_noIP"), ("NUM_LooseID_DEN_genTracks_PAR_pt_spliteta_bin1", PT_ETA_BINS)),
        #(("Loose_noIP"), ("NUM_LooseID_DEN_genTracks_PAR_pt_vtx", VTX_BINS_ETA26)),
        #(("Loose_noIP"), ("NUM_LooseID_DEN_genTracks_PAR_phi", PHI_BINS)),
        ]

#Medium ID
elif _id == 'medium' and _iso == 'noiso':
    if binning == 'eta':
        ID_BINS = [
        (("Medium2016_noIP"), ("NUM_MediumID_DEN_genTracks_PAR_eta", ETA_BINS)),
        ]
    elif binning == 'pt_alleta':
        ID_BINS = [
        (("Medium2016_noIP"), ("NUM_MediumID_DEN_genTracks_PAR_pt_alleta_bin1", PT_ALLETA_BINS)),
        ]
    elif binning == 'pt_spliteta':
        ID_BINS = [
        (("Medium2016_noIP"), ("NUM_MediumID_DEN_genTracks_PAR_pt_spliteta_bin1", PT_ETA_BINS)),
        ]
    elif binning == 'all':
        ID_BINS = [
        #(("Medium2016_noIP"), ("NUM_MediumID_DEN_genTracks_PAR_eta", ETA_BINS)),
        #(("Medium2016_noIP"), ("NUM_MediumID_DEN_genTracks_PAR_pt_alleta_bin1", PT_ALLETA_BINS)),
        #(("Medium2016_noIP"), ("NUM_MediumID_DEN_genTracks_PAR_pt_spliteta_bin1", PT_ETA_BINS)),
        (("Medium2016_noIP"), ("NUM_MediumID_DEN_genTracks_PAR_pt_vtx", VTX_BINS_ETA24)),
        (("Medium2016_noIP"), ("NUM_MediumID_DEN_genTracks_PAR_pt_phi", PHI_BINS)),
        ]
        
#Tight ID
elif _id == 'tight' and _iso == 'noiso':
    if binning == 'eta':
        ID_BINS = [
        (("Tight2012_zIPCut"), ("NUM_TightIDandIPCut_DEN_genTracks_PAR_eta", ETA_BINS)),
        ]
    elif binning == 'pt_alleta':
        ID_BINS = [
        (("Tight2012_zIPCut"), ("NUM_TightIDandIPCut_DEN_genTracks_PAR_pt_alleta_bin1", PT_ALLETA_BINS)),
        ]
    elif binning == 'pt_spliteta':
        ID_BINS = [
        (("Tight2012_zIPCut"), ("NUM_TightIDandIPCut_DEN_genTracks_PAR_pt_spliteta_bin1", PT_ETA_BINS)),
        ]
    elif binning == 'all':
        ID_BINS = [
        (("Tight2012_zIPCut"), ("NUM_TightIDandIPCut_DEN_genTracks_PAR_eta", ETA_BINS)),
        (("Tight2012_zIPCut"), ("NUM_TightIDandIPCut_DEN_genTracks_PAR_pt_alleta_bin1", PT_ALLETA_BINS)),
        (("Tight2012_zIPCut"), ("NUM_TightIDandIPCut_DEN_genTracks_PAR_pt_spliteta_bin1", PT_ETA_BINS)),
        #(("Tight2012_zIPCut"), ("NUM_TightIDandIPCut_DEN_genTracks_PAR_vtx", VTX_BINS_ETA24)),
        #(("Tight2012_zIPCut"), ("NUM_TightIDandIPCut_DEN_genTracks_PAR_phi", PHI_BINS)),
        ]

#High-pT ID
elif _id == 'highpt' and _iso == 'noiso':
    if binning == 'eta':
        ID_BINS = [
        (("HighPt_zIPCut"), ("NUM_HighPtIDandIPCut_DEN_genTracks_PAR_eta", ETA_BINS)),
        (("HighPt_zIPCut"), ("NUM_HighPtIDandIPCut_DEN_genTracks_PAR_eta", ETA_BINS_HPT)),
        ]
    elif binning == 'pt_alleta':
        ID_BINS = [
        (("HighPt_zIPCut"), ("NUM_HighPtIDandIPCut_DEN_genTracks_PAR_pt_alleta_bin1", PT_ALLETA_BINS)),
        ]
    elif binning == 'pt_spliteta':
        ID_BINS = [
        (("HighPt2012_zIPCut"), ("NUM_HighPtIDandIPCut_DEN_genTracks_PAR_pt_spliteta_bin1", PT_ETA_BINS)),
        ]
    elif binning == 'all':
        ID_BINS = [
        (("HighPt_zIPCut"), ("NUM_HighPtIDandIPCut_DEN_genTracks_PAR_eta", ETA_BINS)),
        (("HighPt_zIPCut"), ("NUM_HighPtIDandIPCut_DEN_genTracks_PAR_eta", ETA_BINS_HPT)),
        (("HighPt_zIPCut"), ("NUM_HighPtIDandIPCut_DEN_genTracks_PAR_pt_alleta_bin1", PT_ALLETA_BINS)),
        (("HighPt_zIPCut"), ("NUM_HighPtIDandIPCut_DEN_genTracks_PAR_pt_spliteta_bin1", PT_ETA_BINS)),
        #(("HighPt_zIPCut"), ("NUM_HighPtIDandIPCut_DEN_genTracks_PAR_vtx", VTX_BINS_ETA24)),
        #(("HighPt_zIPCut"), ("NUM_HighPtIDandIPCut_DEN_genTracks_PAR_phi", PHI_BINS)),
        ]

#SoftID
elif _id == 'soft' and _iso == 'noiso':
    if binning == 'eta':
        ID_BINS = [
        (("SoftID"), ("NUM_SoftID_DEN_genTracks_PAR_eta", ETA_BINS)),
        ]
    elif binning == 'pt_alleta':
        ID_BINS = [
        (("SoftID"), ("NUM_SoftID_DEN_genTracks_PAR_pt_alleta_bin1", PT_ALLETA_BINS)),
        ]
    elif binning == 'pt_spliteta':
        ID_BINS = [
        (("SoftID"), ("NUM_SoftID_DEN_genTracks_PAR_pt_spliteta_bin1", PT_ETA_BINS)),
        ]
    elif binning == 'all':
        ID_BINS = [
        (("SoftID"), ("NUM_SoftID_DEN_genTracks_PAR_eta", ETA_BINS)),
        (("SoftID"), ("NUM_SoftID_DEN_genTracks_PAR_pt_alleta_bin1", PT_ALLETA_BINS)),
        (("SoftID"), ("NUM_SoftID_DEN_genTracks_PAR_pt_spliteta_bin1", PT_ETA_BINS)),
        ]

        
#_*_*_*_*_*_*_*_*_*_*
#ISOs
#_*_*_*_*_*_*_*_*_*_*
#Loose Iso
elif _id == 'loose' and _iso == 'loose':
    if binning == 'eta':
        ID_BINS = [
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_LooseID_PAR_eta", LOOSE_ETA_BINS)),
        ]
    elif binning == 'pt_alleta':
        ID_BINS = [
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_LooseID_PAR_pt_alleta_bin1", LOOSE_PT_ALLETA_BINS)),
        ]
    elif binning == 'pt_spliteta':
        ID_BINS = [
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_LooseID_PAR_pt_spliteta_bin1", LOOSE_PT_ETA_BINS)),
        ]
    elif binning == 'all':
        ID_BINS = [
        #(("LooseIso4"), ("NUM_LooseRelIso_DEN_LooseID_PAR_eta", LOOSE_ETA_BINS)),
        #(("LooseIso4"), ("NUM_LooseRelIso_DEN_LooseID_PAR_pt_alleta_bin1", LOOSE_PT_ALLETA_BINS)),
        #(("LooseIso4"), ("NUM_LooseRelIso_DEN_LooseID_PAR_pt_spliteta_bin1", LOOSE_PT_ETA_BINS)),
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_LooseID_PAR_vtx", LOOSE_VTX_BINS_ETA24)),
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_LooseID_PAR_phi", LOOSE_PHI_BINS)),
        ]

elif _id == 'medium' and _iso == 'loose':
    if binning == 'eta':
        ID_BINS = [
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_MediumID_PAR_eta", MEDIUM_ETA_BINS)),
        ]
    elif binning == 'pt_alleta':
        ID_BINS = [
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_MediumID_PAR_pt_alleta_bin1", MEDIUM_PT_ALLETA_BINS)),
        ]
    elif binning == 'pt_spliteta':
        ID_BINS = [
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_MediumID_PAR_pt_spliteta_bin1", MEDIUM_PT_ETA_BINS)),
       ] 
    elif binning == 'all':
        ID_BINS = [
        #(("LooseIso4"), ("NUM_LooseRelIso_DEN_MediumID_PAR_eta", MEDIUM_ETA_BINS)),
        #(("LooseIso4"), ("NUM_LooseRelIso_DEN_MediumID_PAR_pt_alleta_bin1", MEDIUM_PT_ALLETA_BINS)),
        #(("LooseIso4"), ("NUM_LooseRelIso_DEN_MediumID_PAR_pt_spliteta_bin1", MEDIUM_PT_ETA_BINS)),
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_MediumID_PAR_vtx", MEDIUM_VTX_BINS_ETA24)),
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_MediumID_PAR_phi", MEDIUM_PHI_BINS)),
        ]

elif _id == 'tight' and _iso == 'loose':
    if binning == 'eta':
        ID_BINS = [
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_TightID_PAR_eta", TIGHT_ETA_BINS)),
        ]
    elif binning == 'pt_alleta':
        ID_BINS = [
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_TightID_PAR_pt_alleta_bin1", TIGHT_PT_ALLETA_BINS)),
        ]
    elif binning == 'pt_spliteta':
        ID_BINS = [
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_TightID_PAR_pt_spliteta_bin1", TIGHT_PT_ETA_BINS)),
        ]
    elif binning == 'all':
        ID_BINS = [
        #(("LooseIso4"), ("NUM_LooseRelIso_DEN_TightID_PAR_eta", TIGHT_ETA_BINS)),
        #(("LooseIso4"), ("NUM_LooseRelIso_DEN_TightID_PAR_pt_alleta_bin1", TIGHT_PT_ALLETA_BINS)),
        #(("LooseIso4"), ("NUM_LooseRelIso_DEN_TightID_PAR_pt_spliteta_bin1", TIGHT_PT_ETA_BINS)),
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_TightID_PAR_vtx", TIGHT_VTX_BINS_ETA24)),
        (("LooseIso4"), ("NUM_LooseRelIso_DEN_TightID_PAR_phi", TIGHT_PHI_BINS)),
        ]

#Tight Iso
elif _id == 'tight' and _iso == 'tight':
    if binning == 'eta':
        ID_BINS = [
        (("TightIso4"), ("NUM_TightRelIso_DEN_TightID_PAR_eta", TIGHT_ETA_BINS)),
        ]
    elif binning == 'pt_alleta':
        ID_BINS = [
        (("TightIso4"), ("NUM_TightRelIso_DEN_TightID_PAR_pt_alleta_bin1", TIGHT_PT_ALLETA_BINS)),
        ]
    elif binning == 'pt_spliteta':
        ID_BINS = [
        (("TightIso4"), ("NUM_TightRelIso_DEN_TightID_PAR_pt_spliteta_bin1", TIGHT_PT_ETA_BINS)),
        ]
    elif binning == 'vtx':
        ID_BINS = [
        (("TightIso4"), ("NUM_TightRelIso_DEN_TightID_PAR_vtx", TIGHT_VTX_BINS_ETA24)),
        ]
    elif binning == 'phi':
        ID_BINS = [
        (("TightIso4"), ("NUM_TightRelIso_DEN_TightID_PAR_phi", TIGHT_PHI_BINS)),
        ]
    elif binning == 'all':
        ID_BINS = [
        (("TightIso4"), ("NUM_TightRelIso_DEN_TightID_PAR_eta", TIGHT_ETA_BINS)),
        (("TightIso4"), ("NUM_TightRelIso_DEN_TightID_PAR_pt_alleta_bin1", TIGHT_PT_ALLETA_BINS)),
        (("TightIso4"), ("NUM_TightRelIso_DEN_TightID_PAR_pt_spliteta_bin1", TIGHT_PT_ETA_BINS)),
        (("TightIso4"), ("NUM_TightRelIso_DEN_TightID_PAR_vtx", TIGHT_VTX_BINS_ETA24)),
        (("TightIso4"), ("NUM_TightRelIso_DEN_TightID_PAR_phi", TIGHT_PHI_BINS)),
        ]

elif _id == 'medium' and _iso == 'tight':
    if binning == 'eta':
        ID_BINS = [
        (("TightIso4"), ("NUM_TightRelIso_DEN_MediumID_PAR_eta", MEDIUM_ETA_BINS)),
        ]
    elif binning == 'pt_alleta':
        ID_BINS = [
        (("TightIso4"), ("NUM_TightRelIso_DEN_MediumID_PAR_pt_alleta_bin1", MEDIUM_PT_ALLETA_BINS)),
        ]
    elif binning == 'pt_spliteta':
        ID_BINS = [
        (("TightIso4"), ("NUM_TightRelIso_DEN_MediumID_PAR_pt_spliteta_bin1", MEDIUM_PT_ETA_BINS)),
        ]
    elif binning == 'all':
        ID_BINS = [
        (("TightIso4"), ("NUM_TightRelIso_DEN_MediumID_PAR_eta", MEDIUM_ETA_BINS)),
        (("TightIso4"), ("NUM_TightRelIso_DEN_MediumID_PAR_pt_alleta_bin1", MEDIUM_PT_ALLETA_BINS)),
        (("TightIso4"), ("NUM_TightRelIso_DEN_MediumID_PAR_pt_spliteta_bin1", MEDIUM_PT_ETA_BINS)),
        #(("TightIso4"), ("NUM_TightRelIso_DEN_MediumID_PAR_vtx", MEDIUM_VTX_BINS_ETA24)),
        #(("TightIso4"), ("NUM_TightRelIso_DEN_MediumID_PAR_phi", MEDIUM_PHI_BINS)),
        ]

#Tight tk Iso
elif _id == 'highpt' and _iso == 'tktight':
    if binning == 'eta':
        ID_BINS = [
        (("TightTkIso3"), ("NUM_TightRelTkIso_DEN_HighPtID_PAR_eta", HIGHPT_ETA_BINS)),
        (("TightTkIso3"), ("NUM_TightRelTkIso_DEN_HighPtID_PAR_eta", HIGHPT_ETA_BINS_HPT)),
        ]
    elif binning == 'pt_alleta':
        ID_BINS = [
        (("TightTkIso3"), ("NUM_TightRelTkIso_DEN_HighPtID_PAR_pt_alleta_bin1", HIGHPT_PT_ALLETA_BINS)),
        ]
    elif binning == 'pt_spliteta':
        ID_BINS = [
        (("TightTkIso3"), ("NUM_TightRelTkIso_DEN_HighPtID_PAR_pt_spliteta_bin1", HIGHPT_PT_ETA_BINS)),
        ]
    elif binning == 'vtx':
        ID_BINS = [
        (("TightTkIso3"), ("NUM_TightRelTkIso_DEN_HighPtID_PAR_vtx", HIGHPT_VTX_BINS_ETA24)),
        ]
    elif binning == 'phi':
        ID_BINS = [
        (("TightTkIso3"), ("NUM_TightRelTkIso_DEN_HighPtID_PAR_phi", HIGHPT_PHI_BINS)),
        ]
    elif binning == 'all':
        ID_BINS = [
        (("TightTkIso3"), ("NUM_TightRelTkIso_DEN_HighPtID_PAR_eta", HIGHPT_ETA_BINS)),
        (("TightTkIso3"), ("NUM_TightRelTkIso_DEN_HighPtID_PAR_eta", HIGHPT_ETA_BINS_HPT)),
        (("TightTkIso3"), ("NUM_TightRelTkIso_DEN_HighPtID_PAR_pt_alleta_bin1", HIGHPT_PT_ALLETA_BINS)),
        (("TightTkIso3"), ("NUM_TightRelTkIso_DEN_HighPtID_PAR_pt_spliteta_bin1", HIGHPT_PT_ETA_BINS)),
        (("TightTkIso3"), ("NUM_TightRelTkIso_DEN_HighPtID_PAR_vtx", HIGHPT_VTX_BINS_ETA24)),
        (("TightTkIso3"), ("NUM_TightRelTkIso_DEN_HighPtID_PAR_phi", HIGHPT_PHI_BINS)),
        ]

#Loose tk Iso
elif _id == 'highpt' and _iso == 'tktight':
    if binning == 'eta':
        ID_BINS = [
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_HighPtID_PAR_eta", HIGHPT_ETA_BINS)),
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_HighPtID_PAR_eta", HIGHPT_ETA_BINS_HPT)),
        ]
    elif binning == 'pt_alleta':
        ID_BINS = [
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_HighPtID_PAR_pt_alleta_bin1", HIGHPT_PT_ALLETA_BINS)),
        ]
    elif binning == 'pt_spliteta':
        ID_BINS = [
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_HighPtID_PAR_pt_spliteta_bin1", HIGHPT_PT_ETA_BINS)),
        ]
    elif binning == 'vtx':
        ID_BINS = [
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_HighPtID_PAR_vtx", HIGHPT_VTX_BINS_ETA24)),
        ]
    elif binning == 'phi':
        ID_BINS = [
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_HighPtID_PAR_phi", HIGHPT_PHI_BINS)),
        ]
    elif binning == 'all':
        ID_BINS = [
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_HighPtID_PAR_eta", HIGHPT_ETA_BINS)),
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_HighPtID_PAR_eta", HIGHPT_ETA_BINS_HPT)),
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_HighPtID_PAR_pt_alleta_bin1", HIGHPT_PT_ALLETA_BINS)),
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_HighPtID_PAR_pt_spliteta_bin1", HIGHPT_PT_ETA_BINS)),
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_HighPtID_PAR_vtx", HIGHPT_VTX_BINS_ETA24)),
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_HighPtID_PAR_phi", HIGHPT_PHI_BINS)),
        ]

#Loose tk Iso
elif _id == 'tight' and _iso == 'tkloose':
    if binning == 'eta':
        ID_BINS = [
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_TightID_PAR_eta", TIGHT_ETA_BINS)),
        ]
    elif binning == 'pt_alleta':
        ID_BINS = [
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_TightID_PAR_pt_alleta_bin1", TIGHT_PT_ALLETA_BINS)),
        ]
    elif binning == 'pt_spliteta':
        ID_BINS = [
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_TightID_PAR_pt_spliteta_bin1", TIGHT_PT_ETA_BINS)),
        ]
    elif binning == 'vtx':
        ID_BINS = [
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_TightID_PAR_vtx", TIGHT_VTX_BINS_ETA24)),
        ]
    elif binning == 'phi':
        ID_BINS = [
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_TightID_PAR_phi", TIGHT_PHI_BINS)),
        ]
    elif binning == 'all':
        ID_BINS = [
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_TightID_PAR_eta", TIGHT_ETA_BINS)),
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_TightID_PAR_pt_alleta_bin1", TIGHT_PT_ALLETA_BINS)),
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_TightID_PAR_pt_spliteta_bin1", TIGHT_PT_ETA_BINS)),
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_TightID_PAR_vtx", TIGHT_VTX_BINS_ETA24)),
        (("LooseTkIso3"), ("NUM_LooseRelTkIso_DEN_TightID_PAR_phi", TIGHT_PHI_BINS)),
        ]

else:
    print "@ERROR: no combination for _id", _id, "and _iso", _iso, '. Abort.'
    sys.exit()


#_*_*_*_*_*_*_*_*_*_*_*
#Launch fit production
#_*_*_*_*_*_*_*_*_*_*_*

for ID, ALLBINS in ID_BINS:
    X = ALLBINS[0]
    B = ALLBINS[1]
    _output = os.getcwd() + '/Efficiency' + iteration
    if not os.path.exists(_output):
        print 'Creating', '/Efficiency' + iteration,', the directory where the fits are stored.'  
        os.makedirs(_output)
    if scenario == 'data_all':
        _output += '/DATA' + '_' + sample
    elif scenario == 'mc_all':
        _output += '/MC' + '_' + sample
    if not os.path.exists(_output):
        os.makedirs(_output)
    module = process.TnP_MuonID.clone(OutputFileName = cms.string(_output + "/TnP_MC_%s.root" % (X)))
    #save the fitconfig in the plot directory
    shutil.copyfile(os.getcwd()+'/fitMuon.py',_output+'/fitMuon.py')
    shape = cms.vstring("vpvPlusExpo")
    #shape = "vpvPlusCheb"
    if not "Iso" in ID:  #customize only for ID
        if _id == "highpt" :
            elif (len(B.pair_newTuneP_probe_pt)==11): 
                shape = cms.vstring("vpvPlusExpo","*pt_bin6*","vpvPlusCheb","*pt_bin7*","vpvPlusCheb","*pt_bin8*","vpvPlusCheb","*pt_bin9*","vpvPlusCheb")
        else:
            elif (len(B.pt)==10): 
                shape = cms.vstring("vpvPlusExpo","*pt_bin5*","vpvPlusCheb","*pt_bin6*","vpvPlusCheb","*pt_bin7*","vpvPlusCheb","*pt_bin8*","vpvPlusCheb")
    DEN = B.clone(); num = ID;    

    #compute isolation efficiency 
    if scenario == 'data_all':
        if num.find("Iso4") != -1: 
            setattr(module.Efficiencies, ID+"_"+X, cms.PSet(
                EfficiencyCategoryAndState = cms.vstring(num,"below"),
                UnbinnedVariables = cms.vstring("mass"),
                BinnedVariables = DEN,
                BinToPDFmap = shape
                ))
        else:
            setattr(module.Efficiencies, ID+"_"+X, cms.PSet(
                EfficiencyCategoryAndState = cms.vstring(num,"above"),
                UnbinnedVariables = cms.vstring("mass"),
                BinnedVariables = DEN,
                BinToPDFmap = shape
                ))
        setattr(process, "TnP_MuonID_"+ID+"_"+X, module)        
        setattr(process, "run_"+ID+"_"+X, cms.Path(module))
    elif scenario == 'mc_all':
        if num.find("Iso4") != -1: 
            setattr(module.Efficiencies, ID+"_"+X, cms.PSet(
                EfficiencyCategoryAndState = cms.vstring(num,"below"),
                UnbinnedVariables = cms.vstring("mass","weight"),
                BinnedVariables = DEN,
                BinToPDFmap = shape
                ))
        else:
            setattr(module.Efficiencies, ID+"_"+X, cms.PSet(
                EfficiencyCategoryAndState = cms.vstring(num,"above"),
                UnbinnedVariables = cms.vstring("mass","weight"),
                BinnedVariables = DEN,
                BinToPDFmap = shape
                ))
        setattr(process, "TnP_MuonID_"+ID+"_"+X, module)        
        setattr(process, "run_"+ID+"_"+X, cms.Path(module))

