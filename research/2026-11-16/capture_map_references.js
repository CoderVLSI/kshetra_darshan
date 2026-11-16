async (page) => {
  const output = "D:/Kshetra_Darshan/research/2026-11-16/output/playwright";
  await page.setViewportSize({width: 1440, height: 1000});
  const entries = [{"id":"lanka_shankari","name":"Shankari / Koneswaram","query":"Thirukoneswaram Kovil Trincomalee Sri Lanka"},{"id":"kanchipuram_kamakshi","name":"Kamakshi Amman","query":"Kamakshi Amman Temple Kanchipuram"},{"id":"pradyumna_shrinkhala","name":"Shrinkhala at Pradyumna (traditional identification)","query":"Pandua Minar Hooghly West Bengal"},{"id":"mysore_chamundeshwari","name":"Chamundeshwari","query":"Sri Chamundeshwari Temple Chamundi Hill Mysuru"},{"id":"alampur_jogulamba","name":"Jogulamba","query":"Jogulamba Temple Alampur Telangana"},{"id":"srisailam_bhramaramba","name":"Bhramaramba–Mallikarjuna","query":"Sri Bhramaramba Mallikarjuna Temple Srisailam"},{"id":"kolhapur_mahalakshmi","name":"Mahalakshmi / Ambabai","query":"Shree Ambabai Mahalakshmi Temple Kolhapur"},{"id":"mahur_renuka","name":"Ekaveerika / Renuka","query":"Renuka Mata Temple Mahur Maharashtra"},{"id":"ujjain_mahakali","name":"Mahakali / Harsiddhi","query":"Harsiddhi Mata Temple Ujjain"},{"id":"pithapuram_puruhutika","name":"Puruhutika / Padagaya","query":"Kukkuteswara Swamy Temple Padagaya Pithapuram"},{"id":"jajpur_biraja","name":"Girija / Biraja","query":"Maa Biraja Temple Jajpur Odisha"},{"id":"draksharama_manikyamba","name":"Manikyamba / Bhimeswara","query":"Bhimeswara Swamy Manikyamba Temple Draksharamam"},{"id":"kamakhya","name":"Kamarupa / Kamakhya","query":"Kamakhya Temple Guwahati Assam"},{"id":"prayag_madhaveswari","name":"Madhaveswari at Prayaga (game selects Alopi)","query":"Alopi Devi Mandir Alopibagh Prayagraj"},{"id":"jwalamukhi_vaishnavi","name":"Vaishnavi / Jwalamukhi","query":"Jwalamukhi Temple Kangra Himachal Pradesh"},{"id":"gaya_mangalagauri","name":"Mangala Gauri","query":"Mangla Gauri Temple Gaya Bihar"},{"id":"kashi_vishalakshi","name":"Vishalakshi","query":"Vishalakshi Temple Mir Ghat Varanasi"},{"id":"kashmir_sharada","name":"Saraswati / Sharada Peeth","query":"Sharada Peeth ruins Sharda Neelum Valley"},{"id":"madurai_meenakshi","name":"Meenakshi–Sundareswarar (existing game extra)","query":"Meenakshi Amman Temple Madurai"},{"id":"kalighat","name":"Kalighat Kali (existing game extra)","query":"Kalighat Kali Temple Kolkata"},{"id":"tuljapur_bhavani","name":"Tulja Bhavani (existing game extra)","query":"Shri Tulja Bhavani Temple Tuljapur"}];
  let log = [];
  for (const item of entries) {
    try {
      await page.goto('https://www.google.com/maps?t=k&q=' + encodeURIComponent(item.query), {waitUntil: 'domcontentloaded', timeout: 45000});
      await page.waitForTimeout(6500);
      const selectedUrl = page.url();
      const selectedTitle = await page.title();
      const options = await page.locator('a[href*="/maps/place/"]').evaluateAll(nodes => nodes.map(n => ({name: n.getAttribute('aria-label') || n.textContent, url: n.href})).filter(n => n.name));
      let pinUrl = selectedUrl;
      let position = pinUrl.match(/!3d(-?[0-9.]+)!4d(-?[0-9.]+)/);
      if (!position && options.length) {
        pinUrl = options[0].url;
        position = pinUrl.match(/!3d(-?[0-9.]+)!4d(-?[0-9.]+)/);
      }
      const record = {...item, selectedUrl, selectedTitle, options, pinUrl, lookup_position: position ? [Number(position[1]), Number(position[2])] : null, status: 'captured; visual identity review pending', captureDate: '2026-11-16', imageDate: null};
      if (position) {
        await page.goto('https://www.google.com/maps/@' + position[1] + ',' + position[2] + ',300m/data=!3m1!1e3', {waitUntil:'domcontentloaded', timeout:45000});
        await page.waitForTimeout(4500);
      }
      record.captureUrl = page.url();
      const filename = item.id + '_satellite.png';
      await page.screenshot({path:output + '/' + filename, fullPage:false});
      record.file = filename;
      log.push(record);
      console.log('MAP_CAPTURED ' + item.id + ' ' + selectedTitle);
    } catch (e) {
      log.push({...item, status:'failed', error:String(e)});
      console.log('MAP_FAILED ' + item.id);
    }
  }
  return log;
}
