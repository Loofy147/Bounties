const fs = require("fs");
const path = require("path");
const solc = require("solc");

function compile(fileName) {
  const source = fs.readFileSync(path.join(__dirname, "contracts", fileName), "utf8");
  const input = {
    language: "Solidity",
    sources: { [fileName]: { content: source } },
    settings: {
      outputSelection: { "*": { "*": ["abi", "evm.bytecode.object"] } },
    },
  };
  const output = JSON.parse(solc.compile(JSON.stringify(input)));
  if (output.errors) {
    const fatal = output.errors.filter((e) => e.severity === "error");
    if (fatal.length) {
      fatal.forEach((e) => console.error(e.formattedMessage));
      throw new Error("compilation failed");
    }
  }
  return output.contracts[fileName];
}

module.exports = { compile };
