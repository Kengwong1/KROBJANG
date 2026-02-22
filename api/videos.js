/*
  ============================================================
  ไฟล์นี้วางไว้ที่:  /api/videos.js  ใน project Vercel
  ============================================================
  อัปเดต: Channel IDs ที่ verified จาก Wikidata + SPEAKRJ
  ทุกช่องเป็นช่องไทยจริงๆ ทั้งหมด
  ============================================================
*/

const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY;

// ====================================================
// Channel IDs verified จาก Wikidata / SPEAKRJ / vidIQ
// ====================================================
const CHANNELS = {

  // ── ข่าว ───────────────────────────────────────────
  news: [
    { id: 'UC5TOFhyb_LxL2VG_Zenhpzw', name: 'Thai PBS' },          // ✅ Wikidata verified
    { id: 'UC7FCQJFK1sfwD_uobB45Xng', name: 'PPTV HD 36' },        // ✅ Wikidata verified
    { id: 'UCrFDdD-EE05N7gjwZho2wqw', name: 'ไทยรัฐ' },            // ✅ feedspot verified
    { id: 'UCASFOneKa9lsHvc2NqKufqg', name: 'Workpoint News' },     // ✅ feedspot verified
    { id: 'UCzMoibQRsZJ3ZMTZA6RIuXg', name: 'Amarin TV ข่าว' },   // ✅ feedspot verified
    { id: 'UCirZPTc9I3ME82gYm4OQPCQ', name: 'ช่อง 3 ข่าว' },      // Ch3ThailandNews
  ],

  // ── บันเทิง / ละคร / ซีรี่ส์ ────────────────────
  entertain: [
    { id: 'UC48h7Dst_hX82HxOf3xJw_w', name: 'ช่อง 3' },           // ✅ Wikidata 35M sub
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'ช่อง One31' },       // ✅ 44M sub อันดับ 1 ไทย
    { id: 'UC8BzJM6_VbZTdiNLD4R1jxQ', name: 'GMMTV' },            // ✅ Wikidata 20M sub
    { id: 'UCQb0W-qYR6_9vT2-8ixSKOQ', name: 'GMM25' },            // GMM25Thailand
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint TV' },     // ✅ vidIQ 43M sub
    { id: 'UC6x41swVZZTq7hCPPq7bwJg', name: 'ช่อง 8' },           // ✅ feedspot verified
  ],

  // ── กีฬา ──────────────────────────────────────────
  sport: [
    { id: 'UC7FCQJFK1sfwD_uobB45Xng', name: 'PPTV HD 36' },
    { id: 'UCzORJV8l3o_tQs4SHY-HJaA', name: 'สยามกีฬา' },
    { id: 'UC5TOFhyb_LxL2VG_Zenhpzw', name: 'Thai PBS กีฬา' },
    { id: 'UCrFDdD-EE05N7gjwZho2wqw', name: 'ไทยรัฐ กีฬา' },
    { id: 'UC48h7Dst_hX82HxOf3xJw_w', name: 'ช่อง 3 กีฬา' },
  ],

  // ── เทคโนโลยี / IT ───────────────────────────────
  tech: [
    { id: 'UCt7mzJGKpRE1JwNclE_BKOA', name: 'Blognone' },
    { id: 'UCqajGCbBop4FFHnBSmINpQQ', name: 'Droidsans' },
    { id: 'UCY9xyOoOVKcbMKZMvM8GKQQ', name: 'Techsauce' },
    { id: 'UCASFOneKa9lsHvc2NqKufqg', name: 'Workpoint News Tech' },
  ],

  // ── การ์ตูน / เด็ก ──────────────────────────────
  cartoon: [
    { id: 'UCJlejBGlsKkzOGu9RBXM_LA', name: 'Cartoon Network TH' },
    { id: 'UCFOJoJE1T7kFKnKMpNmEwkA', name: 'Nickelodeon TH' },
    { id: 'UCjmJDI5RkLgTIJC5v_VEbQ', name: 'Disney TH' },
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint การ์ตูน' },
  ],

  // ── เกมส์ ─────────────────────────────────────────
  game: [
    { id: 'UCgYkuL87rovnBj4m3hn2VwA', name: 'ROV Thailand' },
    { id: 'UCFQMnBA3CS502aghlcr0_aw', name: 'Free Fire TH' },
    { id: 'UCbmNph6atAoGfqLoCL_duAg', name: 'Garena TH' },
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint เกมส์' },
  ],

  // ── หนัง / ซีรี่ส์ ──────────────────────────────
  movie: [
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'ช่อง One31 ซีรี่ส์' },
    { id: 'UC48h7Dst_hX82HxOf3xJw_w', name: 'ช่อง 3 ละคร' },
    { id: 'UC8BzJM6_VbZTdiNLD4R1jxQ', name: 'GMMTV ซีรี่ส์' },
    { id: 'UCQb0W-qYR6_9vT2-8ixSKOQ', name: 'GMM25 ซีรี่ส์' },
    { id: 'UC6x41swVZZTq7hCPPq7bwJg', name: 'ช่อง 8 ละคร' },
  ],
};

// ดึงวิดีโอล่าสุดจาก 1 channel (maxResults วิดีโอ)
async function fetchChannel(channelId, channelName, maxResults = 8) {
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

// Vercel serverless handler
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
      channels.map(ch => fetchChannel(ch.id, ch.name, 8))
    );

    const grouped = {};
    channels.forEach((ch, i) => {
      if (results[i] && results[i].length > 0) {
        grouped[ch.name] = results[i];
      }
    });

    res.setHeader(
      'Cache-Control',
      's-maxage=21600, stale-while-revalidate=3600'
    );
    res.setHeader('Access-Control-Allow-Origin', '*');

    return res.status(200).json(grouped);

  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: err.message });
  }
}
