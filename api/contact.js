export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const apiKey = process.env.REALVISOR_API_KEY;
    if (!apiKey) {
        console.error('REALVISOR_API_KEY is not set');
        return res.status(500).json({ error: 'Server configuration error' });
    }

    try {
        const response = await fetch('https://api-production-88cf.up.railway.app/api/v1/public/api-leads/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey
            },
            body: JSON.stringify(req.body)
        });

        const data = await response.json();

        if (response.ok) {
            return res.status(200).json(data);
        } else {
            return res.status(response.status).json(data);
        }
    } catch (error) {
        console.error('Realvisor API error:', error);
        return res.status(500).json({ error: 'Failed to submit lead' });
    }
}
