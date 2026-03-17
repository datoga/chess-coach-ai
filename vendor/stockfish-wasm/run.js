#!/usr/bin/env node
/**
 * Stockfish WASM UCI bridge for Python subprocess communication.
 * Reads UCI commands from stdin, writes responses to stdout.
 * Usage: echo "uci\nposition fen ...\ngo depth 15\nquit" | node run.js
 */
const path = require("path");

// Load the lite single-threaded WASM build
const sf = require(path.join(__dirname, "stockfish-18-lite-single.js"));

const engine = sf();

engine.addMessageListener((msg) => {
  process.stdout.write(msg + "\n");
});

process.stdin.setEncoding("utf8");
let buffer = "";

process.stdin.on("data", (chunk) => {
  buffer += chunk;
  const lines = buffer.split("\n");
  buffer = lines.pop(); // keep incomplete line in buffer
  for (const line of lines) {
    const cmd = line.trim();
    if (cmd) {
      if (cmd === "quit") {
        process.exit(0);
      }
      engine.postMessage(cmd);
    }
  }
});

process.stdin.on("end", () => {
  if (buffer.trim()) {
    engine.postMessage(buffer.trim());
  }
  // Give engine time to respond before exit
  setTimeout(() => process.exit(0), 2000);
});
