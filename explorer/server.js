#!/usr/bin/env node
/**
 * Projekt BitsCoin 2025
 * Autorzy: Grupa Siedemtrzy
 * Fork SHA-256 – niezależna sieć BitsCoin
 * © 2025 Grupa Siedemtrzy. Wszelkie prawa zastrzeżone.
 */

const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const cors = require('cors');
app.use(cors());
const PORT = 3000;

// Serwuj statyczne pliki z public/
app.use(express.static(path.join(__dirname, 'public')));

// Endpoint zwracający listę bloków
app.get('/api/blocks', (req, res) => {
  const chainPath = path.resolve(__dirname, '..', 'core', 'chain.json');
  fs.readFile(chainPath, 'utf8', (err, data) => {
    if (err) return res.status(500).json({ error: err.toString() });
    const chain = JSON.parse(data);
    res.json(chain);
  });
});

app.listen(PORT, () => {
  console.log(`Explorer: http://localhost:${PORT}`);
});
