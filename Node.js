import axios from 'axios';
import OpenAI from 'openai';

const openai = new OpenAI({ apiKey: process.env.OPENAI_KEY });

// -------------------- Configuration --------------------
const API_KEYS = {
  nvidia: process.env.NVAPI_KEY,
  gpt: process.env.GPT_KEY,
  claude: process.env.CLAUDE_KEY
};

const MODELS = {
  nvidia: "meta/llama-4-maverick-17b-128e-instruct",
  gpt: "gpt-4o-mini",
  claude: "claude-v1"
};

const MAX_TOKENS = 512;
const ITERATIONS = 3; // Convergence per turn
const TURNS = 5;      // Total conversation turns

// -------------------- Helper Functions --------------------

// 1️⃣ Query NVIDIA LLM
async function queryNvidiaLLM(prompt) {
  const payload = {
    model: MODELS.nvidia,
    messages: [{ role: "user", content: prompt }],
    max_tokens: MAX_TOKENS,
    temperature: 1.0
  };

  const response = await axios.post(
    "https://integrate.api.nvidia.com/v1/chat/completions",
    payload,
    { headers: { "Authorization": `Bearer ${API_KEYS.nvidia}` } }
  );

  return response.data.choices[0].message.content;
}

// 2️⃣ Query GPT (placeholder)
async function queryGPT(prompt) {
  return `GPT reply for: ${prompt}`;
}

// 3️⃣ Query Claude (placeholder)
async function queryClaude(prompt) {
  return `Claude reply for: ${prompt}`;
}

// 4️⃣ Embeddings
async function getEmbedding(text) {
  const response = await openai.embeddings.create({
    model: "text-embedding-3-large",
    input: text
  });
  return response.data[0].embedding;
}

// 5️⃣ Cosine similarity
function cosineSim(vecA, vecB) {
  let dot = 0, normA = 0, normB = 0;
  for (let i = 0; i < vecA.length; i++) {
    dot += vecA[i] * vecB[i];
    normA += vecA[i] ** 2;
    normB += vecB[i] ** 2;
  }
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

// 6️⃣ Harmonic combination
function harmonicCombine(outputs, embeddings) {
  const n = outputs.length;
  const weights = Array(n).fill(0);

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (i !== j) weights[i] += cosineSim(embeddings[i], embeddings[j]);
    }
  }

  const sum = weights.reduce((a, b) => a + b, 0);
  const normWeights = weights.map(w => w / sum);
  const combined = outputs.map((text, i) => `[${(normWeights[i]*100).toFixed(1)}%] ${text}`);
  return combined.join(" | ");
}

// -------------------- Multi-Turn Conversation --------------------
async function runTrinityConversation(initialPrompt, turns = TURNS) {
  let conversationHistory = initialPrompt;

  for (let turn = 1; turn <= turns; turn++) {
    console.log(`\n=== Turn ${turn} ===`);
    
    let prompt = conversationHistory;

    // Iterative convergence per turn
    for (let iter = 1; iter <= ITERATIONS; iter++) {
      const nvidiaResp = await queryNvidiaLLM(prompt);
      const gptResp = await queryGPT(prompt);
      const claudeResp = await queryClaude(prompt);

      const embeddings = await Promise.all([
        getEmbedding(nvidiaResp),
        getEmbedding(gptResp),
        getEmbedding(claudeResp)
      ]);

      prompt = harmonicCombine([nvidiaResp, gptResp, claudeResp], embeddings);
    }

    console.log(`Converged Turn Output:\n${prompt}\n`);
    
    // Update conversation history
    conversationHistory += "\n" + prompt;
  }

  return conversationHistory;
}

// -------------------- Run Demo --------------------
(async () => {
  const initialPrompt = "Let's discuss how multi-LLM systems can converge harmonically.";
  const finalConversation = await runTrinityConversation(initialPrompt);
  console.log("\n=== Final Multi-Turn Converged Conversation ===\n", finalConversation);
})();