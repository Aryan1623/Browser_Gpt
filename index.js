const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const axios = require('axios');
const { spawn } = require('child_process');

dotenv.config();
const app = express();
const port = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

const HF_TOKEN = process.env.HF_API_TOKEN;
const IDEA_URL = 'http://localhost:6000/generate-ideas';
const SUMMARIZER_URL = 'http://localhost:8000/summarize';
const DESCRIPTION_URL = 'http://localhost:8002/describe';

const headers = {
  Authorization: `Bearer ${HF_TOKEN}`,
  'Content-Type': 'application/json',
};

function trimToSecondLastFullStop(text) {
  const indices = [];
  for (let i = 0; i < text.length; i++) {
    if (text[i] === '.' && (i === text.length - 1 || text[i + 1] === ' ')) {
      indices.push(i);
    }
  }
  if (indices.length >= 2) {
    return text.slice(0, indices[indices.length - 2] + 1).trim();
  }
  return text;
}

// === Summarization Endpoint ===
app.post('/summarize', async (req, res) => {
  const { text } = req.body;
  if (!text || !text.trim()) {
    return res.status(400).json({ error: 'Text is required for summarization.' });
  }

  try {
    const response = await axios.post(SUMMARIZER_URL, { text });
    const summary = trimToSecondLastFullStop(response.data.summary || '');
    res.json({ summary });
  } catch (err) {
    console.error('Summarization error:', err.response?.data || err.message);
    res.status(500).json({ error: 'Failed to summarize text.' });
  }
});

// === Idea Generator Endpoint ===
app.post('/ideagenerator', async (req, res) => {
  const { prompt } = req.body;
  if (!prompt || !prompt.trim()) {
    return res.status(400).json({ error: 'Prompt is required for idea generation.' });
  }

  try {
    const response = await axios.post(IDEA_URL, { prompt });

    const ideas = response.data?.ideas;
    if (!ideas || !Array.isArray(ideas)) {
      return res.status(500).json({ error: 'Invalid response from Python idea generator.' });
    }

    res.json({ ideas });
  } catch (err) {
    console.error('Idea generation error:', err.message);
    res.status(500).json({ error: 'Failed to generate ideas.' });
  }
});

// === Description Endpoint ===
app.post('/describe', async (req, res) => {
  const { topic } = req.body;
  if (!topic || !topic.trim()) {
    return res.status(400).json({ error: 'Topic is required for detailed explanation.' });
  }

  try {
    const response = await axios.post(DESCRIPTION_URL, { topic });

    const description = response.data?.description;
    if (!description) {
      return res.status(500).json({ error: 'No description received from Python backend.' });
    }

    res.json({ description });
  } catch (err) {
    console.error('Description error:', err.message);
    res.status(500).json({ error: 'Failed to fetch description.' });
  }
});

// === PDF Generator Endpoint ===
app.post('/generatepdf', async (req, res) => {
  const { text } = req.body;

  if (!text || !text.trim()) {
    return res.status(400).json({ error: 'Text is required for PDF generation.' });
  }

  try {
    const response = await axios.post(
      'http://localhost:7000/generate-pdf',
      { text },
      { responseType: 'stream' }
    );

    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', 'attachment; filename="generated_idea.pdf"');
    response.data.pipe(res);
  } catch (error) {
    console.error('PDF generation error:', error.message);
    res.status(500).json({ error: 'Failed to generate PDF.' });
  }
});

// === Health Check ===
app.get('/', (req, res) => {
  res.send('Backend running with Summarizer, Description, Idea Generator & PDF services.');
});

// === Start Python Services Using Global Python ===
const startPythonService = (scriptName) => {
  const subprocess = spawn('python', [scriptName]);

  subprocess.stdout.on('data', (data) => {
    console.log(`${scriptName}: ${data.toString().trim()}`);
  });

  subprocess.stderr.on('data', (data) => {
    console.error(`${scriptName} error: ${data.toString().trim()}`);
  });

  subprocess.on('exit', (code) => {
    console.log(`${scriptName} exited with code ${code}`);
  });
};

// Start all Python services
['summary.py', 'description.py', 'idea_generator.py', 'pdf.py'].forEach(startPythonService);

// Start Express Server
app.listen(port, () => {
  console.log(`✅ Server listening on port ${port}`);
});
