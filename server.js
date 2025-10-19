import express from 'express';
import http from 'http';
import { Server } from 'socket.io';
import { getEmbedding, cosineSim, harmonicCombine, queryNvidiaLLM, queryGPT, queryClaude } from './llmHelpers.js'; // modular helper functions

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static('public'));

const ITERATIONS = 3;
const TURNS = 5;

async function runTrinityTurn(prompt) {
  let iterationPrompt = prompt;
  let logs = [];

  for (let iter = 1; iter <= ITERATIONS; iter++) {
    const nvidiaResp = await queryNvidiaLLM(iterationPrompt);
    const gptResp = await queryGPT(iterationPrompt);
    const claudeResp = await queryClaude(iterationPrompt);

    const embeddings = await Promise.all([
      getEmbedding(nvidiaResp),
      getEmbedding(gptResp),
      getEmbedding(claudeResp)
    ]);

    const combined = harmonicCombine([nvidiaResp, gptResp, claudeResp], embeddings);
    
    logs.push({
      iteration: iter,
      nvidia: nvidiaResp,
      gpt: gptResp,
      claude: claudeResp,
      combined
    });

    iterationPrompt = combined;

    // Emit to frontend
    io.emit('update', logs[logs.length - 1]);
  }

  return iterationPrompt;
}

// Demo: multi-turn conversation
io.on('connection', (socket) => {
  console.log('Client connected');

  socket.on('startConversation', async (initialPrompt) => {
    let conversationHistory = initialPrompt;

    for (let turn = 1; turn <= TURNS; turn++) {
      const turnOutput = await runTrinityTurn(conversationHistory);
      conversationHistory += "\n" + turnOutput;
      io.emit('turnComplete', { turn, turnOutput });
    }
  });
});

server.listen(3000, () => console.log('Server running on http://localhost:3000'));