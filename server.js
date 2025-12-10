import express from 'express';
import fetch from 'node-fetch';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json({ limit: '2mb' }));
app.use(express.static(__dirname));

app.post('/api/cartoon', async (req, res) => {
  const { prompt, size = '1024x1024', style = 'cartoon' } = req.body || {};
  const key = process.env.NANOBANANA_API_KEY;

  if (!prompt) {
    return res.status(400).json({ error: 'Missing prompt' });
  }
  if (!key) {
    return res.status(400).json({ error: 'Missing API key. Set NANOBANANA_API_KEY on the server.' });
  }

  try {
    const upstream = await fetch('https://nanobananaapi.ai/v1/cartoon', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${key}`
      },
      body: JSON.stringify({ prompt, size, style })
    });

    const text = await upstream.text();

    if (!upstream.ok) {
      return res.status(upstream.status).json({ error: text || 'Upstream error' });
    }

    let data;
    try {
      data = JSON.parse(text);
    } catch (err) {
      return res.status(502).json({ error: 'Invalid JSON from upstream' });
    }

    const image = data.image_url || data.image_base64;
    if (!image) {
      return res.status(502).json({ error: 'No image returned from upstream' });
    }

    const normalized = image.startsWith('http')
      ? image
      : `data:image/png;base64,${image}`;

    res.json({ image: normalized });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Proxy request failed' });
  }
});

app.listen(PORT, () => {
  console.log(`AI Cartoon Creator running on http://localhost:${PORT}`);
});

