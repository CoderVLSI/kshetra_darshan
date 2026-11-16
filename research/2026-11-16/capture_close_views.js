async (page) => {
const entries = [["lanka_shankari",8.5824436,81.2453556,130],["kanchipuram_kamakshi",12.8404465,79.7036765,250],["pradyumna_shrinkhala",23.0744286,88.2853432,100],["mysore_chamundeshwari",12.2725072,76.6707214,180],["alampur_jogulamba",15.8769909,78.1346258,140],["srisailam_bhramaramba",16.0740593,78.8673168,250],["kolhapur_mahalakshmi",16.6948594,74.2226431,160],["mahur_renuka",19.8325926,77.923314,130],["ujjain_mahakali",23.1844864,75.7646561,100],["pithapuram_puruhutika",17.107282,82.2457305,170],["jajpur_biraja",20.8337649,86.3380219,150],["draksharama_manikyamba",16.7928723,82.0633432,170],["kamakhya",26.1664108,91.7055031,120],["prayag_madhaveswari",25.4440046,81.8707401,100],["jwalamukhi_vaishnavi",31.8753944,76.3240824,120],["gaya_mangalagauri",24.7751444,85.0023466,100],["kashi_vishalakshi",25.3099438,83.011898,90],["kashmir_sharada",34.7920875,74.1899531,100],["madurai_meenakshi",9.9195045,78.1193418,300],["kalighat",22.5203132,88.3420716,120],["tuljapur_bhavani",18.0124474,76.0660281,170]];
const output = 'D:/Kshetra_Darshan/research/2026-11-16/output/playwright/';
const log = [];
await page.setViewportSize({width:1440,height:1000});
for(const [id,lat,lon,distance] of entries) {
 await page.goto('https://www.google.com/maps/@'+lat+','+lon+','+distance+'m/data=!3m1!1e3',{waitUntil:'domcontentloaded',timeout:45000});
 await page.waitForTimeout(4500);
 const file = id+'_satellite_close.png';
 await page.screenshot({path:output+file,fullPage:false});
 log.push({id,lookup_position:[lat,lon],captureUrl:page.url(),file,captureDate:'2026-11-16',imageDate:null});
}
return log;
}
