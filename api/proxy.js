// api/proxy.js
import fetch from "node-fetch";

export default async function handler(req, res) {
  const { channelId, maxResults = 12 } = req.query;
  const apiKey = process.env.YOUTUBE_API_KEY; // Key ที่ตั้งใน Environment Variables

  if (!channelId) {
    return res.status(400).json({ error: "Missing channelId parameter" });
  }

  const apiUrl = `https://www.googleapis.com/youtube/v3/search?key=${apiKey}&channelId=${channelId}&part=snippet,id&order=date&maxResults=${maxResults}`;

  try {
    const response = await fetch(apiUrl);
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch videos", details: error.message });
  }
}
