const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Mock API responses - no backend needed
app.use('/api', (req, res) => {
  console.log(`Mock API call: ${req.method} ${req.path}`);
  
  if (req.path.includes('/questions/process')) {
    // Mock successful processing response
    res.json({
      success: true,
      results: [
        {
          question: "Are there support and training programs for developers?",
          answer: "Yes, Solana provides comprehensive support and training programs for developers including documentation, tutorials, workshops, and community support.",
          confidence: 0.95
        },
        {
          question: "Do you have testnets?",
          answer: "Yes, Solana operates multiple testnets including devnet and testnet for development and testing purposes.",
          confidence: 0.98
        }
      ],
      processing_time: 2.3
    });
  } else if (req.path.includes('/knowledge')) {
    // Mock knowledge base response
    res.json({
      total_entries: 150,
      last_updated: new Date().toISOString(),
      categories: ["RFP Guidelines", "Technical Requirements", "Support Programs"]
    });
  } else {
    // Default mock response
    res.json({ message: "Mock API response", path: req.path });
  }
});

// Serve static files from the React app build directory
app.use(express.static(path.join(__dirname, 'build')));

// Handle React routing, return all requests to React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
