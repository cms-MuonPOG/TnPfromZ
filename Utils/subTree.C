#include <iostream>
#include "TTree.h"
#include "TFile.h"
#include "TDirectory.h"

using namespace std;

void subTree(TString dir="tpTree", TString cut="tag_IsoMu20 && tag_combRelIsoPF04dBeta < 0.15", TString newFile="TnPTree_80X_Run2016B_v2_GoldenJSON_Run271036to275125_incomplete_subTree_v2.root") {
	
    //TFile* f_in = TFile::Open("root://eoscms//eos/cms/store/group/phys_muon/TagAndProbe/Run2016/80X_v3/data/TnPTree_80X_Run2016C_v2_GoldenJSON_Run275784to276097.root","read");
    //TFile* f_in = TFile::Open("root://eoscms//eos/cms/store/group/phys_muon/TagAndProbe/Run2016/80X_v3/data/TnPTree_80X_Run2016C_v2_GoldenJSON_Run275126to275783.root","read");
    //TFile* f_in = TFile::Open("root://eoscms//eos/cms/store/group/phys_muon/TagAndProbe/Run2016/80X_v3/data/TnPTree_80X_Run2016B_v2_GoldenJSON_Run275126to275783.root","read");
    TFile* f_in = TFile::Open("root://eoscms//eos/cms/store/group/phys_muon/TagAndProbe/Run2016/80X_v3/data/TnPTree_80X_Run2016B_v2_GoldenJSON_Run271036to275125_incomplete.root","read");
    //TFile* f_in = TFile::Open("root://eoscms//eos/cms/store/group/phys_muon/TagAndProbe/Run2016/80X_v3/DY_madgraphMLM/TnPTree_80X_DYLL_M50_MadGraphMLM_part1.root","read");
    //TFile* f_in = TFile::Open("root://eoscms//eos/cms/store/group/phys_muon/TagAndProbe/Run2016/80X_v3/DY_madgraphMLM/TnPTree_80X_DYLL_M50_MadGraphMLM_part2.root","read");
    //TFile* f_in = TFile::Open("root://eoscms//eos/cms/store/group/phys_muon/TagAndProbe/Run2016/80X_v3/DY_madgraphMLM/TnPTree_80X_DYLL_M50_MadGraphMLM_part3.root","read");
    //TFile* f_in = TFile::Open("root://eoscms//eos/cms/store/group/phys_muon/TagAndProbe/Run2016/80X_v3/DY_madgraphMLM/TnPTree_80X_DYLL_M50_MadGraphMLM_part4.root","read");
    //TFile* f_in = TFile::Open("root://eoscms//eos/cms/store/group/phys_muon/TagAndProbe/Run2016/80X_v3/DY_madgraphMLM/TnPTree_80X_DYLL_M50_MadGraphMLM_part5.root","read");

    cut = "(pt > 20 || pair_newTuneP_probe_pt >20) && mass > 69.5 && mass < 130.5 && pair_probeMultiplicity > 0.5 && pair_probeMultiplicity < 1.5 && tag_IsoMu22 == 1";
    TTree *in  = (TTree *)f_in->Get(dir+"/fitter_tree");
    TFile *fout = new TFile(newFile, "RECREATE");
    TDirectory *dout = fout->mkdir(dir); dout->cd();
    TTree *out = in->CopyTree(cut);
    std::cout << "INPUT TREE (" << in->GetEntries() << " ENTRIES)" << std::endl;
    //in->Print();
    std::cout << "OUTPUT TREE (" << out->GetEntries() << " ENTRIES)" << std::endl;
    //out->Print();
    dout->WriteTObject(out, "fitter_tree");
    fout->Close();
}
