void printTree(TString dir="tpTree", TString cut=" run == 273425 && tag_IsoMu20==1 && tag_pt > 22 && tag_abseta < 2.1 && tag_combRelIsoPF04dBeta < 0.15 && pt > 22 && combRelIsoPF04dBeta < 0.15 && abseta > 2.1 && abseta < 2.4 && Tight2012==1 && l1pt >= 16 && l1q >= 12 && l1dr < 0.3") {
    TTree *in  = (TTree *)gFile->Get(dir+"/fitter_tree");
    
    TTree *out = in->CopyTree(cut);
    std::cout << "INPUT TREE (" << in->GetEntries() << " ENTRIES)" << std::endl;
    //in->Print();
    std::cout << "OUTPUT TREE (" << out->GetEntries() << " ENTRIES)" << std::endl;
    
    ULong64_t event;
    UInt_t lumi;
    UInt_t run;

    out->SetBranchAddress("run", &run);
    out->SetBranchAddress("lumi", &lumi);
    out->SetBranchAddress("event", &event);
    for (int i = 0, n = out->GetEntries(); i < n; ++i) {
        out->GetEntry(i);

	std::cout << run << ":" << lumi << ":" << event << std::endl;
    }
}
