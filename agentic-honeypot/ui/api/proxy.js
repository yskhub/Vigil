// Simple proxy for Vercel serverless functions
// Forwards requests from the UI to the backend configured by BACKEND_URL
// Ensure you set BACKEND_URL (e.g. https://your-backend-host) and API_KEY in Vercel Environment Variables

module.exports = async (req, res) => {
  try {
    const backend = (process.env.BACKEND_URL || '').replace(/\/$/, '');
    const apiKey = process.env.API_KEY || process.env.BACKEND_API_KEY || '';
    if (!backend) {
      res.status(500).json({ error: 'BACKEND_URL not configured in environment' });
      return;
    }

    // req.url contains the path including query string, remove the /api/proxy prefix
    const originalUrl = req.url || '';
    const forwardPath = originalUrl.replace(/^\/api\/proxy/, '') || '/';
    const target = backend + forwardPath;

    // collect raw body
    let raw = '';
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      raw = await new Promise((resolve, reject) => {
        let data = '';
        req.on('data', chunk => { data += chunk; });
        req.on('end', () => resolve(data));
        req.on('error', err => reject(err));
      });
    }

    // Build headers to forward
    const headers = { ...req.headers };
    // ensure we send JSON for typical requests
    if (raw && !headers['content-type']) headers['content-type'] = 'application/json';
    // override or set API key header
    if (apiKey) headers['x-api-key'] = apiKey;
    // remove host header to avoid issues
    delete headers.host;

    // Use global fetch available in Vercel Node runtime
    const fetchRes = await fetch(target, {
      method: req.method,
      headers,
      body: raw && raw.length ? raw : undefined,
    });

    const text = await fetchRes.text();
    // copy status and headers
    res.status(fetchRes.status);
    // copy selected headers
    fetchRes.headers.forEach((value, key) => {
      // avoid hop-by-hop
      if (!['transfer-encoding', 'connection'].includes(key.toLowerCase())) {
        res.setHeader(key, value);
      }
    });
    // send body
    res.send(text);
  } catch (err) {
    res.status(500).json({ error: String(err) });
  }
};
