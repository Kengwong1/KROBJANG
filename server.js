const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');
const app = express();
const port = 3000;

app.use(cors());

// API สำหรับดึง RSS Feed
app.get('/api/youtube-feed', async (req, res) => {
    const rssUrl = req.query.url;
    if (!rssUrl) {
        return res.status(400).send('RSS URL is required.');
    }

    try {
        const response = await fetch(rssUrl);
        const data = await response.text();
        res.header('Content-Type', 'application/xml').send(data);
    } catch (error) {
        console.error('Error fetching RSS feed:', error);
        res.status(500).send('Error fetching RSS feed.');
    }
});

app.get('/', (req, res) => {
    res.send('Server is running. Please open the video.html file in your browser.');
});

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});