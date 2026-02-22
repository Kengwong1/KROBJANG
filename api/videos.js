/*
  ============================================================
  ไฟล์นี้วางไว้ที่:  /api/videos.js  ใน project Vercel
  ============================================================
  วิธีใช้:
  1. เปิดไฟล์นี้ แล้วใส่ YouTube API Key ของคุณตรง บรรทัด 16
  2. Push ขึ้น Vercel — Vercel จะ deploy เป็น serverless function ให้อัตโนมัติ
  3. video.html จะเรียก /api/videos?cat=news  ฯลฯ

  CACHE: Vercel Edge Cache 6 ชั่วโมง
  → YouTube API ถูกเรียกแค่ 4 ครั้ง/วัน ต่อ category
  → คนดูกี่หมื่นคนก็ดึงจาก cache ไม่กิน quota
  ============================================================
*/

// ====================================================
// ⚙️  ใส่ YouTube Data API Key ของคุณตรงนี้
// ====================================================
// เปลี่ยนจาก
const YOUTUBE_API_KEY = 'YOUR_API_KEY_HERE';

// เป็น
const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY;
// ====================================================

// Channel IDs จริงของช่องไทย แยกตาม category
const CHANNELS = {
  news: [
    { id: 'UCupvZG-5ko_eiXAupbDfxWw', name: 'Thai PBS' },
    { id: 'UCOBFxMDAwL6NKZS5YVKmgbw', name: 'PPTVHD36' },
    { id: 'UCQb0W-qYR6_9vT2-8ixSKOQ', name: 'Workpoint News' },
    { id: 'UC3MElBjZhDLEBpbH9eMJoJQ', name: 'ไทยรัฐ TV' },
  ],
  entertain: [
    { id: 'UCm2TSh9NJQZQ5fH6iA1LENA', name: 'ช่อง 8' },
    { id: 'UCQb0W-qYR6_9vT2-8ixSKOQ', name: 'Workpoint' },
    { id: 'UC5E7QNf-jYQNfmhEIBkAIcA', name: 'GMM Grammy' },
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'One31' },
  ],
  sport: [
    { id: 'UCzORJV8l3o_tQs4SHY-HJaA', name: 'สยามกีฬา' },
    { id: 'UCCNuBDUXVQfRHCLWZBjcXbw', name: 'True Sport TH' },
    { id: 'UCupvZG-5ko_eiXAupbDfxWw', name: 'Thai PBS' },
    { id: 'UCOBFxMDAwL6NKZS5YVKmgbw', name: 'PPTVHD36' },
  ],
  tech: [
    { id: 'UCt7mzJGKpRE1JwNclE_BKOA', name: 'Blognone' },
    { id: 'UCqajGCbBop4FFHnBSmINpQQ', name: 'Droidsans' },
    { id: 'UCY9xyOoOVKcbMKZMvM8GKQQ', name: 'Techsauce' },
  ],
  cartoon: [
    { id: 'UCJlejBGlsKkzOGu9RBXM_LA', name: 'Cartoon Network TH' },
    { id: 'UCFOJoJE1T7kFKnKMpNmEwkA', name: 'Nickelodeon TH' },
    { id: 'UCjmJDI5RkLgTIJC5v_VEbQ', name: 'Disney TH' },
  ],
  game: [
    { id: 'UCgYkuL87rovnBj4m3hn2VwA', name: 'ROV Thailand' },
    { id: 'UCFQMnBA3CS502aghlcr0_aw', name: 'Free Fire TH' },
    { id: 'UCbmNph6atAoGfqLoCL_duAg', name: 'Garena TH' },
  ],
};

// ดึงวิดีโอล่าสุดจาก 1 channel (5 วิดีโอ)
async function fetchChannel(channelId, channelName) {
  const url = `https://www.googleapis.com/youtube/v3/search`
    + `?key=${YOUTUBE_API_KEY}`
    + `&channelId=${channelId}`
    + `&part=snippet`
    + `&order=date`           // เรียงล่าสุดก่อน
    + `&type=video`
    + `&maxResults=6`;

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
    // ดึงทุก channel พร้อมกัน
    const results = await Promise.all(
      channels.map(ch => fetchChannel(ch.id, ch.name))
    );

    // รวมและ group ตาม channel name
    const grouped = {};
    channels.forEach((ch, i) => {
      grouped[ch.name] = results[i];
    });

    // ส่งกลับพร้อม Cache-Control 6 ชั่วโมง
    // Vercel Edge Cache จะเก็บไว้ → คนดูกี่หมื่นก็ดึง cache
    res.setHeader(
      'Cache-Control',
      's-maxage=21600, stale-while-revalidate=3600'
      //              ^ 6 ชม.             ^ อัปเดต background อีก 1 ชม.
    );
    res.setHeader('Access-Control-Allow-Origin', '*');

    return res.status(200).json(grouped);

  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: err.message });
  }
}

