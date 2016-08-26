//Chain with radmonlumi files
TChain t("t");
t.Add("/scr1/RadMonLumi/2016/OfflineLumi/OfflineRadmonLumi/offlineRadmonLumi*.root");

TCut warm ="tstamp - fillColl>40*60"
TCut rt = "counts[12]/lumi <5.5 && counts[12]/lumi >3"
TCut stable = "beamStatus == \"STABLE BEAMS\""
TCut pxl = "lumiSource==\"PXL\""
TCut plt = "lumiSource==\"PLTZERO\""


// Lumi vs rate
t.Draw("lumi:counts[12]*1.05", warm&&rt&&stable)

//Mean Lumi vs mean rate
t.Draw("lumi/23.1:counts[12]/(lsEnd-lsStart)", warm&&rt&&stable)

t.Draw("counts[12]/lumi:lumi>>h2", warm&&rt&&stable)
h2.Draw();
h2_pfx.Draw();


//Combined lumi
TChain t("t");
t.Add("/scr1/RadMonLumi/2016/LumiCombined/*.root");
t.Draw("lumiOffline/lumiOnline", "lumiOffline/lumiOnline>0.8&&lumiOffline/lumiOnline<1.2");

//Start of lum
