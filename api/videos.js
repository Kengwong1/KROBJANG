/*
  /api/videos.js — Vercel Serverless Function
  ใช้ YouTube RSS Feed แทน Data API → ฟรี 100% ไม่กิน quota!
  RSS URL: https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID
*/

// Channel IDs verified ✅
const CHANNELS = {
  news: [
    { id: 'UCrFDdD-EE05N7gjwZho2wqw', name: 'ไทยรัฐ' },
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ทีวี' },
    { id: 'UC5wKpLWxAZBZrunls3mzwEw', name: 'เรื่องเล่าเช้านี้' },
    { id: 'UC5TOFhyb_LxL2VG_Zenhpzw', name: 'Thai PBS' },
    { id: 'UC7FCQJFK1sfwD_uobB45Xng', name: 'PPTV HD 36' },
    { id: 'UCqUBA96OsqMgSFvTwLXY9yw', name: 'TNN Online' },
    { id: 'UC6x41swVZP3rEmy-ODxLMFA', name: 'ข่าวช่อง 8' },
    { id: 'UCASFOneKa9lsHvc2NqKufqg', name: 'Workpoint News' },
  ],
  entertain: [
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint' },
    { id: 'UC48h7Dst_hX82HxOf3xJw_w', name: 'ช่อง 3' },
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'ช่อง One31' },
    { id: 'UC2OtDM92rPHk0GKnYNGOCzA', name: 'ช่อง 7 HD' },
    { id: 'UCtBu8Wb2BUoduUXJS9Uss7Q', name: 'ช่อง 8' },
    { id: 'UC8BzJM6_VbZTdiNLD4R1jxQ', name: 'GMMTV' },
  ],
  sport: [
    { id: 'UCzORJV8l3o_tQs4SHY-HJaA', name: 'สยามกีฬา' },
    { id: 'UC7FCQJFK1sfwD_uobB45Xng', name: 'PPTV กีฬา' },
    { id: 'UCrFDdD-EE05N7gjwZho2wqw', name: 'ไทยรัฐ' },
    { id: 'UCqUBA96OsqMgSFvTwLXY9yw', name: 'TNN' },
    { id: 'UC5TOFhyb_LxL2VG_Zenhpzw', name: 'Thai PBS' },
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ทีวี' },
  ],
  movie: [
    { id: 'UC8BzJM6_VbZTdiNLD4R1jxQ', name: 'GMMTV' },
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'ช่อง One31' },
    { id: 'UC48h7Dst_hX82HxOf3xJw_w', name: 'ช่อง 3' },
    { id: 'UC2OtDM92rPHk0GKnYNGOCzA', name: 'ช่อง 7 HD' },
    { id: 'UCtBu8Wb2BUoduUXJS9Uss7Q', name: 'ช่อง 8' },
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ทีวี' },
  ],
  music: [
    { id: 'UCF-YFQPG8-VPmcWdAkEqAkg', name: 'GMM Grammy Official' },
    { id: 'UC9CP-k0UwCRIr3RTDP3GdMQ', name: 'Grammy Gold Official' },
    { id: 'UCDNHjPnVEeEHrLUDT_AxMkA', name: 'RS Music' },
    { id: 'UC8BzJM6_VbZTdiNLD4R1jxQ', name: 'GMMTV' },
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint Music' },
    { id: 'UC2OtDM92rPHk0GKnYNGOCzA', name: 'ช่อง 7 เพลง' },
  ],
  tech: [
    { id: 'UCt7mzJGKpRE1JwNclE_BKOA', name: 'Blognone' },
    { id: 'UCqajGCbBop4FFHnBSmINpQQ', name: 'Droidsans' },
    { id: 'UCrFDdD-EE05N7gjwZho2wqw', name: 'ไทยรัฐ' },
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ทีวี' },
    { id: 'UC5TOFhyb_LxL2VG_Zenhpzw', name: 'Thai PBS' },
    { id: 'UCqUBA96OsqMgSFvTwLXY9yw', name: 'TNN Online' },
  ],
  cartoon: [
    { id: 'UCJlejBGlsKkzOGu9RBXM_LA', name: 'Cartoon Network TH' },
    { id: 'UCFOJoJE1T7kFKnKMpNmEwkA', name: 'Nickelodeon TH' },
    { id: 'UCjmJDI5RkLgTIJC5v_VEbQ', name: 'Disney TH' },
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint' },
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'ช่อง One31' },
  ],
  game: [
    { id: 'UCgYkuL87rovnBj4m3hn2VwA', name: 'ROV Thailand' },
    { id: 'UCFQMnBA3CS502aghlcr0_aw', name: 'Free Fire TH' },
    { id: 'UCbmNph6atAoGfqLoCL_duAg', name: 'Garena TH' },
    { id: 'UCHtL3mp77nrCyJTq8K6DEMA', name: 'RoV Pro League' },
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint' },
  ],
};

// keywords สำหรับ filter title ให้ตรงหมวด (ใช้กับ RSS ที่ได้มา)
const KEYWORDS = {
  news:     null,
  entertain:null,
  sport:    ['ฟุตบอล','กีฬา','บอล','แข่ง','ผล','สนาม','นักกีฬา','sport','ทีม'],
  movie:    ['ละคร','ซีรี่','ตอนที่','ep.','episode','นาง','พระเอก','ฉาก','ย้อนหลัง'],
  music:    ['mv','เพลง','official','music video','ost','cover','คอนเสิร์ต'],
  tech:     ['เทค','มือถือ','ai','รีวิว','tech','review','gadget','iphone','android','ซอฟต์แวร์'],
  cartoon:  ['การ์ตูน','cartoon','animation','anime','ตอนที่','ep'],
  game:     ['เกม','gaming','rov','freefire','esport','สตรีม','live','tournament'],
};

// parse XML RSS → array of videos
function parseRSS(xml, channelName, maxItems = 10) {
  const items = [];
  const entries = xml.split('<entry>').slice(1);
  for (const entry of entries.slice(0, maxItems)) {
    const videoId = (entry.match(/<yt:videoId>(.*?)<\/yt:videoId>/) || [])[1] || '';
    const title   = (entry.match(/<title>(.*?)<\/title>/)           || [])[1] || '';
    const date    = (entry.match(/<published>(.*?)<\/published>/)    || [])[1] || '';
    const thumb   = `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
    if (videoId) items.push({ id: videoId, title, thumb, ch: channelName, date });
  }
  return items;
}

// ดึง RSS ของ 1 channel
async function fetchRSS(channelId, channelName, keywords = null, maxItems = 10) {
  const url = `https://www.youtube.com/feeds/videos.xml?channel_id=${channelId}`;
  try {
    const res = await fetch(url, { headers: { 'Accept': 'application/xml' } });
    if (!res.ok) return [];
    const xml  = await res.text();
    let videos = parseRSS(xml, channelName, 50); // ดึงมา 50 แล้วค่อย filter

    // filter ตาม keyword ถ้ามี
    if (keywords && keywords.length > 0) {
      const kw = keywords.map(k => k.toLowerCase());
      const filtered = videos.filter(v =>
        kw.some(k => v.title.toLowerCase().includes(k))
      );
      // ถ้า filter แล้วเหลือน้อยกว่า 3 → เอาของเดิมทั้งหมด (channel นั้นอาจไม่มีเนื้อหาตรงหมวด)
      videos = filtered.length >= 3 ? filtered : videos;
    }

    return videos.slice(0, maxItems);
  } catch {
    return [];
  }
}

export default async function handler(req, res) {
  const cat      = req.query.cat || 'news';
  const channels = CHANNELS[cat];
  const keywords = KEYWORDS[cat] || null;

  if (!channels) {
    return res.status(400).json({ error: 'Unknown category' });
  }

  try {
    const results = await Promise.all(
      channels.map(ch => fetchRSS(ch.id, ch.name, keywords, 10))
    );

    const grouped = {};
    channels.forEach((ch, i) => {
      if (results[i] && results[i].length > 0) {
        grouped[ch.name] = results[i];
      }
    });

    // Cache 6 ชั่วโมง — RSS ไม่กิน quota เลย ดึงกี่ครั้งก็ได้
    res.setHeader('Cache-Control', 's-maxage=21600, stale-while-revalidate=3600');
    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.status(200).json(grouped);

  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: err.message });
  }
}
