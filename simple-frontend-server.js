const express = require('express');
const path = require('path');

const app = express();
const PORT = 8081;

// Serve static files
app.use(express.static('.'));

// Serve marketplace-inspired page as default
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'marketplace-inspired.html'));
});

// Alternative main pages
app.get('/futuristic', (req, res) => {
  res.sendFile(path.join(__dirname, 'futuristic-main.html'));
});

// Serve admin panels
app.get('/admin', (req, res) => {
  res.sendFile(path.join(__dirname, 'admin-futuristic.html'));
});

app.get('/admin-old', (req, res) => {
  res.sendFile(path.join(__dirname, 'admin-panel.html'));
});

// Test purchase page
app.get('/purchase', (req, res) => {
  res.sendFile(path.join(__dirname, 'test-purchase.html'));
});

// Animated events page
app.get('/events', (req, res) => {
  res.sendFile(path.join(__dirname, 'animated-events.html'));
});

app.listen(PORT, () => {
  console.log(`Frontend server running at http://localhost:${PORT}`);
  console.log(`Open your browser to test WeatherNFT.live`);
});