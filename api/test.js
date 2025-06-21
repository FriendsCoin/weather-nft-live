// Simple API endpoint for Vercel
export default function handler(req, res) {
  res.status(200).json({ 
    message: 'Weather NFT API is working!',
    timestamp: new Date().toISOString()
  });
}