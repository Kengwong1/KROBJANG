/*
  /api/videos.js — Vercel Serverless Function
  Channel IDs verified จาก HypeAuditor, VidIQ, Feedspot, SPEAKRJ
  แก้ปัญหา "ไม่ตรงหมวด" ด้วย keyword filter (q=) ใน YouTube API
*/

const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY;

// keyword filter ต่อหมวด (ว่าง = ดึงล่าสุดทั้งหมด)
const KEYWORDS = {
  news:    '',
  entertain: '',
  sport:   'ฟุตบอล|กีฬา|บอล|แข่ง|ผล',
  movie:   'ละคร|ซีรี่|EP|ตอน|พระเอก|นาง',
  music:   'MV|เพลง|official|music video',
  tech:    'เทคโนโลยี|มือถือ|AI|รีวิว|tech|review|gadget',
  cartoon: 'การ์ตูน|cartoon|animation|anime|ตอน',
  game:    'เกม|gaming|ROV|FreeFire|esport|live|สตรีม',
};

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
    { id: 'UCrFDdD-EE05N7gjwZho2wqw', name: 'ไทยรัฐ กีฬา' },
    { id: 'UC5TOFhyb_LxL2VG_Zenhpzw', name: 'Thai PBS กีฬา' },
    { id: 'UCqUBA96OsqMgSFvTwLXY9yw', name: 'TNN กีฬา' },
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ กีฬา' },
  ],
  movie: [
    { id: 'UC8BzJM6_VbZTdiNLD4R1jxQ', name: 'GMMTV ซีรี่ส์' },
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'ช่อง One31 ละคร' },
    { id: 'UC48h7Dst_hX82HxOf3xJw_w', name: 'ช่อง 3 ละคร' },
    { id: 'UC2OtDM92rPHk0GKnYNGOCzA', name: 'ช่อง 7 ละคร' },
    { id: 'UCtBu8Wb2BUoduUXJS9Uss7Q', name: 'ช่อง 8 ละคร' },
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ ละคร' },
  ],
  music: [
    { id: 'UCF-YFQPG8-VPmcWdAkEqAkg', name: 'GMM Grammy Official' },
    { id: 'UC9CP-k0UwCRIr3RTDP3GdMQ', name: 'Grammy Gold Official' },
    { id: 'UCDNHjPnVEeEHrLUDT_AxMkA', name: 'RS Music' },
    { id: 'UC8BzJM6_VbZTdiNLD4R1jxQ', name: 'GMMTV Music' },
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'One31 Music' },
    { id: 'UC2OtDM92rPHk0GKnYNGOCzA', name: 'ช่อง 7 เพลง' },
  ],
  tech: [
    { id: 'UCt7mzJGKpRE1JwNclE_BKOA', name: 'Blognone' },
    { id: 'UCqajGCbBop4FFHnBSmINpQQ', name: 'Droidsans' },
    { id: 'UCrFDdD-EE05N7gjwZho2wqw', name: 'ไทยรัฐ เทค' },
    { id: 'UCzMoibQRslh_1bTuW0YXc6A', name: 'อมรินทร์ เทค' },
    { id: 'UC5TOFhyb_LxL2VG_Zenhpzw', name: 'Thai PBS เทค' },
    { id: 'UCqUBA96OsqMgSFvTwLXY9yw', name: 'TNN Tech' },
  ],
  cartoon: [
    { id: 'UCJlejBGlsKkzOGu9RBXM_LA', name: 'Cartoon Network TH' },
    { id: 'UCFOJoJE1T7kFKnKMpNmEwkA', name: 'Nickelodeon TH' },
    { id: 'UCjmJDI5RkLgTIJC5v_VEbQ', name: 'Disney TH' },
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint การ์ตูน' },
    { id: 'UCBcRF18a7Qf58cCRy5xuWwQ', name: 'One31 การ์ตูน' },
  ],
  game: [
    { id: 'UCgYkuL87rovnBj4m3hn2VwA', name: 'ROV Thailand' },
    { id: 'UCFQMnBA3CS502aghlcr0_aw', name: 'Free Fire TH' },
    { id: 'UCbmNph6atAoGfqLoCL_duAg', name: 'Garena TH' },
    { id: 'UCHtL3mp77nrCyJTq8K6DEMA', name: 'RoV Pro League' },
    { id: 'UC3ZkCd7XtUREnjjt3cyY_gg', name: 'Workpoint เกมส์' },
  ],
};

async function fetchChannel(channelId, channelName, keyword = '', maxResults = 10) {
  let url = `https://www.googleapis.com/youtube/v3/search`
    + `?key=${YOUTUBE_API_KEY}`
    + `&channelId=${channelId}`
    + `&part=snippet`
    + `&order=date`
    + `&type=video`
    + `&maxResults=${maxResults}`;

  if (keyword) {
    url += `&q=${encodeURIComponent(keyword)}`;
  }

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
  const cat     = req.query.cat || 'news';
  const channels = CHANNELS[cat];
  const keyword  = KEYWORDS[cat] || '';

  if (!channels) {
    return res.status(400).json({ error: 'Unknown category' });
  }
  if (!YOUTUBE_API_KEY || YOUTUBE_API_KEY === 'YOUR_API_KEY_HERE') {
    return res.status(500).json({ error: 'API key not set' });
  }

  try {
    const results = await Promise.all(
      channels.map(ch => fetchChannel(ch.id, ch.name, keyword, 10))
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
