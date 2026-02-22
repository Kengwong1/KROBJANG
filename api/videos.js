/*
  /api/videos.js — Vercel Serverless Function
  วิธี: YouTube RSS Feed (ไม่กิน quota) + filter keyword จาก title
  
  หลักการ:
  1. ทุกหมวดใช้ "ช่องเฉพาะทาง" เป็นหลัก (ช่องกีฬา=สยามกีฬา, ช่องเพลง=GMM Grammy)
  2. ช่องใหญ่ที่มีหลายประเภท (PPTV, ไทยรัฐ) → filter จาก title keyword
  3. ถ้า filter แล้วได้น้อยกว่า 3 → แสดงทั้งหมด (ดีกว่าว่าง)
*/

const CHANNELS = {

  // ── ข่าว: ช่องข่าวล้วน ไม่ต้อง filter ──────────────
  news: [
    { id: 'UCrFDdD-EE05N7gjwZho2wqw', name: 'ไทยรัฐ',          kw: null },
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ทีวี',    kw: null },
    { id: 'UC5wKpLWxAZBZrunls3mzwEw', name: 'เรื่องเล่าเช้านี้',kw: null },
    { id: 'UC5TOFhyb_LxL2VG_Zenhpzw', name: 'Thai PBS',         kw: null },
    { id: 'UC7FCQJFK1sfwD_uobB45Xng', name: 'PPTV HD 36',       kw: null },
    { id: 'UCqUBA96OsqMgSFvTwLXY9yw', name: 'TNN Online',       kw: null },
    { id: 'UC6x41swVZP3rEmy-ODxLMFA', name: 'ข่าวช่อง 8',      kw: null },
    { id: 'UCASFOneKa9lsHvc2NqKufqg', name: 'Workpoint News',   kw: null },
  ],

  // ── บันเทิง: ช่องบันเทิงล้วน ──────────────────────
  entertain: [
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint',   kw: null },
    { id: 'UC48h7Dst_hX82HxOf3xJw_w', name: 'ช่อง 3',      kw: null },
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'ช่อง One31',  kw: null },
    { id: 'UC2OtDM92rPHk0GKnYNGOCzA', name: 'ช่อง 7 HD',   kw: null },
    { id: 'UCtBu8Wb2BUoduUXJS9Uss7Q', name: 'ช่อง 8',      kw: null },
    { id: 'UC8BzJM6_VbZTdiNLD4R1jxQ', name: 'GMMTV',       kw: null },
  ],

  // ── กีฬา: ช่องกีฬาเฉพาะ + filter คำว่ากีฬาในช่องใหญ่ ──
  sport: [
    // ช่องกีฬาล้วน → ไม่ต้อง filter
    { id: 'UCzORJV8l3o_tQs4SHY-HJaA', name: 'สยามกีฬา',  kw: null },
    // ช่องใหญ่ → filter คำกีฬา
    { id: 'UC7FCQJFK1sfwD_uobB45Xng', name: 'PPTV กีฬา',
      kw: ['ฟุตบอล','กีฬา','บอล','แข่ง','ผล','นักกีฬา','ทีม','สนาม','ลีก','ถ่ายทอด'] },
    { id: 'UCrFDdD-EE05N7gjwZho2wqw', name: 'ไทยรัฐ กีฬา',
      kw: ['ฟุตบอล','กีฬา','บอล','แข่ง','ผล','นักกีฬา','ทีม','สนาม','ลีก'] },
    { id: 'UCqUBA96OsqMgSFvTwLXY9yw', name: 'TNN กีฬา',
      kw: ['ฟุตบอล','กีฬา','บอล','แข่ง','ผล','นักกีฬา','ทีม','สนาม'] },
    { id: 'UC5TOFhyb_LxL2VG_Zenhpzw', name: 'Thai PBS กีฬา',
      kw: ['ฟุตบอล','กีฬา','บอล','แข่ง','ผล','นักกีฬา','ทีม'] },
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ กีฬา',
      kw: ['ฟุตบอล','กีฬา','บอล','แข่ง','ผล','นักกีฬา','ทีม'] },
  ],

  // ── ละคร/ซีรี่: ช่องละครล้วน + filter ──────────────
  movie: [
    // GMMTV, One31, ช่อง 3, ช่อง 7 เน้นละครอยู่แล้ว
    { id: 'UC8BzJM6_VbZTdiNLD4R1jxQ', name: 'GMMTV',         kw: null },
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'ช่อง One31',    kw: null },
    { id: 'UC48h7Dst_hX82HxOf3xJw_w', name: 'ช่อง 3',        kw: null },
    { id: 'UC2OtDM92rPHk0GKnYNGOCzA', name: 'ช่อง 7 HD',     kw: null },
    { id: 'UCtBu8Wb2BUoduUXJS9Uss7Q', name: 'ช่อง 8',        kw: null },
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ ละคร',
      kw: ['ละคร','ซีรี่','ตอนที่','ep','ฉาก','ย้อนหลัง','พระเอก','นาง'] },
  ],

  // ── เพลง/MV: ช่องเพลงล้วน → ทุก video = เพลง ──────
  music: [
    { id: 'UCF-YFQPG8-VPmcWdAkEqAkg', name: 'GMM Grammy Official', kw: null },
    { id: 'UC9CP-k0UwCRIr3RTDP3GdMQ', name: 'Grammy Gold Official', kw: null },
    { id: 'UCDNHjPnVEeEHrLUDT_AxMkA', name: 'RS Music',             kw: null },
    { id: 'UC8BzJM6_VbZTdiNLD4R1jxQ', name: 'GMMTV Music',
      kw: ['mv','เพลง','ost','official','music','cover','คอนเสิร์ต'] },
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint Music',
      kw: ['mv','เพลง','ost','official','music','คอนเสิร์ต','ร้อง'] },
    { id: 'UC2OtDM92rPHk0GKnYNGOCzA', name: 'ช่อง 7 เพลง',
      kw: ['mv','เพลง','ost','official','music','คอนเสิร์ต','ร้อง'] },
  ],

  // ── เทค: ช่องเทคล้วน + filter ───────────────────────
  tech: [
    // ช่องเทคโดยตรง → ไม่ต้อง filter
    { id: 'UCt7mzJGKpRE1JwNclE_BKOA', name: 'Blognone',  kw: null },
    { id: 'UCqajGCbBop4FFHnBSmINpQQ', name: 'Droidsans', kw: null },
    // ช่องข่าว → filter เทค
    { id: 'UCrFDdD-EE05N7gjwZho2wqw', name: 'ไทยรัฐ เทค',
      kw: ['เทค','มือถือ','ai','รีวิว','tech','review','gadget','iphone','android','แอป','ซอฟต์แวร์','ดิจิทัล'] },
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ เทค',
      kw: ['เทค','มือถือ','ai','รีวิว','tech','review','gadget','iphone','android','แอป','ดิจิทัล'] },
    { id: 'UC5TOFhyb_LxL2VG_Zenhpzw', name: 'Thai PBS เทค',
      kw: ['เทค','มือถือ','ai','tech','gadget','ดิจิทัล','นวัตกรรม','วิทยาศาสตร์'] },
    { id: 'UCqUBA96OsqMgSFvTwLXY9yw', name: 'TNN Tech',
      kw: ['เทค','มือถือ','ai','tech','review','gadget','ดิจิทัล'] },
  ],

  // ── การ์ตูน: ช่องการ์ตูนล้วน ────────────────────────
  cartoon: [
    { id: 'UCJlejBGlsKkzOGu9RBXM_LA', name: 'Cartoon Network TH', kw: null },
    { id: 'UCFOJoJE1T7kFKnKMpNmEwkA', name: 'Nickelodeon TH',     kw: null },
    { id: 'UCjmJDI5RkLgTIJC5v_VEbQ', name: 'Disney TH',           kw: null },
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint การ์ตูน',
      kw: ['การ์ตูน','cartoon','animation','ตอนที่','ep','anime'] },
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'One31 การ์ตูน',
      kw: ['การ์ตูน','cartoon','animation','ตอนที่','ep','anime'] },
  ],

  // ── เกมส์: ช่องเกมส์ล้วน ────────────────────────────
  game: [
    { id: 'UCgYkuL87rovnBj4m3hn2VwA', name: 'ROV Thailand',   kw: null },
    { id: 'UCFQMnBA3CS502aghlcr0_aw', name: 'Free Fire TH',   kw: null },
    { id: 'UCbmNph6atAoGfqLoCL_duAg', name: 'Garena TH',     kw: null },
    { id: 'UCHtL3mp77nrCyJTq8K6DEMA', name: 'RoV Pro League', kw: null },
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint เกมส์',
      kw: ['เกม','gaming','rov','freefire','esport','สตรีม','live','tournament','แข่งเกม'] },
  ],
};

// parse YouTube RSS XML → video array
function parseRSS(xml, channelName) {
  const videos = [];
  const entries = xml.split('<entry>').slice(1);
  for (const entry of entries) {
    const videoId = (entry.match(/<yt:videoId>(.*?)<\/yt:videoId>/) || [])[1] || '';
    const title   = (entry.match(/<title>(.*?)<\/title>/)           || [])[1] || '';
    const date    = (entry.match(/<published>(.*?)<\/published>/)    || [])[1] || '';
    if (!videoId) continue;
    // decode HTML entities ใน title
    const cleanTitle = title.replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'");
    videos.push({
      id:    videoId,
      title: cleanTitle,
      thumb: `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`,
      ch:    channelName,
      date,
    });
  }
  return videos;
}

// ดึง RSS + filter keyword
async function fetchChannel(channelId, channelName, keywords = null) {
  const url = `https://www.youtube.com/feeds/videos.xml?channel_id=${channelId}`;
  try {
    const res = await fetch(url);
    if (!res.ok) return [];
    const xml    = await res.text();
    let videos   = parseRSS(xml, channelName); // RSS ให้มาสูงสุด 15 วิดีโอ

    if (keywords && keywords.length > 0) {
      const filtered = videos.filter(v =>
        keywords.some(k => v.title.toLowerCase().includes(k.toLowerCase()))
      );
      // ถ้า filter แล้วได้ >= 2 เอา filtered / ถ้าน้อยกว่า → เอาทั้งหมด
      videos = filtered.length >= 2 ? filtered : videos;
    }

    return videos.slice(0, 10);
  } catch {
    return [];
  }
}

export default async function handler(req, res) {
  const cat      = req.query.cat || 'news';
  const channels = CHANNELS[cat];

  if (!channels) {
    return res.status(400).json({ error: 'Unknown category' });
  }

  try {
    const results = await Promise.all(
      channels.map(ch => fetchChannel(ch.id, ch.name, ch.kw))
    );

    const grouped = {};
    channels.forEach((ch, i) => {
      if (results[i] && results[i].length > 0) {
        grouped[ch.name] = results[i];
      }
    });

    // Cache 3 ชั่วโมง (RSS อัปเดตบ่อย)
    res.setHeader('Cache-Control', 's-maxage=10800, stale-while-revalidate=3600');
    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.status(200).json(grouped);

  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: err.message });
  }
}
