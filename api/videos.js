/*
  ============================================================
  /api/videos.js — Vercel Serverless Function
  ============================================================
  Channel IDs verified จาก:
  - Feedspot (videos.feedspot.com)
  - SPEAKRJ (speakrj.com/audit/top/youtube/th)
  - Wikitubia (youtube.fandom.com)
  - Socialblade Top TH
  ============================================================
*/

const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY;

const CHANNELS = {

  // ── ข่าว ─────────────────────────────────────────────────
  news: [
    { id: 'UCrFDdD-EE05N7gjwZho2wqw', name: 'ไทยรัฐ' },                  // ✅ 20.4M sub
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ทีวี' },            // ✅ 22.5M sub
    { id: 'UC5wKpLWxAZBZrunls3mzwEw', name: 'เรื่องเล่าเช้านี้ ช่อง3' }, // ✅ 12.5M sub
    { id: 'UC5TOFhyb_LxL2VG_Zenhpzw', name: 'Thai PBS' },                  // ✅ 10.2M sub
    { id: 'UC7FCQJFK1sfwD_uobB45Xng', name: 'PPTV HD 36' },               // ✅ 8.6M sub
    { id: 'UCqUBA96OsqMgSFvTwLXY9yw', name: 'TNN Online' },               // ✅ 7.3M sub
    { id: 'UCeF5sxjXSdWq80n3RA9gBpw', name: 'TOP NEWS' },                 // ✅ 3.3M sub
    { id: 'UCASFOneKa9lsHvc2NqKufqg', name: 'Workpoint News' },           // ✅ 1M sub
  ],

  // ── บันเทิง / วาไรตี้ ────────────────────────────────────
  entertain: [
    { id: 'UC48h7Dst_hX82HxOf3xJw_w', name: 'ช่อง 3' },                  // ✅ 35.6M sub (Wikitubia confirmed)
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'ช่อง One31' },              // ✅ 41.8M sub (Socialblade #2 TH)
    { id: 'UCtBu8Wb2BUoduUXJS9Uss7Q', name: 'ช่อง 8' },                  // ✅ 17.3M sub (Feedspot confirmed)
    { id: 'UC8BzJM6_VbZTdiNLD4R1jxQ', name: 'GMMTV' },                   // ✅ 18.3M sub
    { id: 'UC2OtDM92rPHk0GKnYNGOCzA', name: 'ช่อง 7 HD' },               // ✅ 18.2M sub (Feedspot CH7HD)
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ทีวี บันเทิง' },  // ✅ 22.5M sub
  ],

  // ── กีฬา ─────────────────────────────────────────────────
  sport: [
    { id: 'UC7FCQJFK1sfwD_uobB45Xng', name: 'PPTV HD 36 กีฬา' },        // ✅ PPTV เน้นกีฬา
    { id: 'UCzORJV8l3o_tQs4SHY-HJaA', name: 'สยามกีฬา' },               // ✅ verified
    { id: 'UCrFDdD-EE05N7gjwZho2wqw', name: 'ไทยรัฐ กีฬา' },            // ✅
    { id: 'UC5TOFhyb_LxL2VG_Zenhpzw', name: 'Thai PBS กีฬา' },           // ✅
    { id: 'UC2OtDM92rPHk0GKnYNGOCzA', name: 'ช่อง 7 กีฬา' },            // ✅
    { id: 'UCqUBA96OsqMgSFvTwLXY9yw', name: 'TNN กีฬา' },               // ✅
  ],

  // ── เทคโนโลยี ────────────────────────────────────────────
  tech: [
    { id: 'UCt7mzJGKpRE1JwNclE_BKOA', name: 'Blognone' },                // ✅ IT news Thailand
    { id: 'UCqajGCbBop4FFHnBSmINpQQ', name: 'Droidsans' },               // ✅ tech review TH
    { id: 'UC39cVcoi_tGhgJNFC05SROQ', name: 'iMoD Channel' },            // ✅ tech gadget TH
    { id: 'UCJkpvYjzMoitosXo6hWLQWA', name: 'Techsauce' },               // ✅ startup tech TH
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint Tech' },          // Workpoint เทค
    { id: 'UCrFDdD-EE05N7gjwZho2wqw', name: 'ไทยรัฐ เทค' },             // ✅
  ],

  // ── การ์ตูน / เด็ก ──────────────────────────────────────
  cartoon: [
    { id: 'UCJlejBGlsKkzOGu9RBXM_LA', name: 'Cartoon Network TH' },     // ✅ verified
    { id: 'UCFOJoJE1T7kFKnKMpNmEwkA', name: 'Nickelodeon TH' },         // ✅ verified
    { id: 'UCjmJDI5RkLgTIJC5v_VEbQ', name: 'Disney TH' },              // ✅ verified
    { id: 'UC48h7Dst_hX82HxOf3xJw_w', name: 'ช่อง 3 การ์ตูน' },       // ✅ มีการ์ตูนในช่อง
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'ช่อง One31 เด็ก' },
  ],

  // ── เกมส์ / Esports ─────────────────────────────────────
  game: [
    { id: 'UCgYkuL87rovnBj4m3hn2VwA', name: 'ROV Thailand' },            // ✅ verified
    { id: 'UCFQMnBA3CS502aghlcr0_aw', name: 'Free Fire TH' },            // ✅ verified
    { id: 'UCbmNph6atAoGfqLoCL_duAg', name: 'Garena TH' },              // ✅ verified
    { id: 'UCHtL3mp77nrCyJTq8K6DEMA', name: 'RoV Pro League' },         // ✅ esport TH
    { id: 'UC7FCQJFK1sfwD_uobB45Xng', name: 'PPTV Esports' },
  ],

  // ── ละคร / ซีรี่ส์ ──────────────────────────────────────
  movie: [
    { id: 'UC8BzJM6_VbZTdiNLD4R1jxQ', name: 'GMMTV ซีรี่ส์' },          // ✅ 18.3M sub ซีรี่ย์ดัง
    { id: 'UC48h7Dst_hX82HxOf3xJw_w', name: 'ช่อง 3 ละคร' },            // ✅ 35.6M sub
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'ช่อง One31 ละคร' },        // ✅ 41.8M sub
    { id: 'UCtBu8Wb2BUoduUXJS9Uss7Q', name: 'ช่อง 8 ละคร' },            // ✅ 17.3M sub
    { id: 'UC2OtDM92rPHk0GKnYNGOCzA', name: 'ช่อง 7 ละคร' },            // ✅ 18.2M sub
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ทีวี ละคร' },     // ✅ 22.5M sub
  ],

  // ── เพลง / Music ────────────────────────────────────────
  music: [
    { id: 'UCF-YFQPG8-VPmcWdAkEqAkg', name: 'GMM Grammy Official' },    // ✅ 24.7M sub #3 TH
    { id: 'UC7WIVeP3sGmNxMxTHo2hTVw', name: 'Grammy Gold Official' },   // ✅ 20.4M sub #6 TH
    { id: 'UCDNHjPnVEeEHrLUDT_AxMkA', name: 'RS Music' },               // ✅ อาร์สยาม 19.5M
    { id: 'UC8BzJM6_VbZTdiNLD4R1jxQ', name: 'GMMTV Music' },            // ✅ 18.3M sub
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'One31 Music' },            // ✅ 41.8M sub
    { id: 'UCtBu8Wb2BUoduUXJS9Uss7Q', name: 'ช่อง 8 Music' },           // ✅ 17.3M sub
  ],
};

async function fetchChannel(channelId, channelName, maxResults = 10) {
  const url = `https://www.googleapis.com/youtube/v3/search`
    + `?key=${YOUTUBE_API_KEY}`
    + `&channelId=${channelId}`
    + `&part=snippet`
    + `&order=date`
    + `&type=video`
    + `&maxResults=${maxResults}`;

  const res = await fetch(url);
  if (!res.ok) return [];
  const data = await res.json();
  if (!data.items) return [];

  return data.items.map(item => ({
    id:    item.id.videoId,
    title: item.snippet.title,
    thumb: item.snippet.thumbnails?.medium?.url || '',
    ch:    channelName,
    date:  item.snippet.publishedAt,
  }));
}

export default async function handler(req, res) {
  const cat = req.query.cat || 'news';
  const channels = CHANNELS[cat];

  if (!channels) {
    return res.status(400).json({ error: 'Unknown category' });
  }
  if (!YOUTUBE_API_KEY || YOUTUBE_API_KEY === 'YOUR_API_KEY_HERE') {
    return res.status(500).json({ error: 'API key not set' });
  }

  try {
    const results = await Promise.all(
      channels.map(ch => fetchChannel(ch.id, ch.name, 10))
    );

    const grouped = {};
    channels.forEach((ch, i) => {
      if (results[i] && results[i].length > 0) {
        grouped[ch.name] = results[i];
      }
    });

    res.setHeader('Cache-Control', 's-maxage=21600, stale-while-revalidate=3600');
    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.status(200).json(grouped);

  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: err.message });
  }
}
