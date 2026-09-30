const fs = require("fs");
const path = require("path");

const fileArg = process.argv[2]; // e.g. contracts/VulnerableVault.sol
const fileName = path.basename(fileArg);
const source = fs.readFileSync(fileArg, "utf8");

const input = {
  language: "Solidity",
  sources: { [fileName]: { content: source } },
  settings: {
    outputSelection: {
      "*": {
        "*": [
          "abi",
          "userdoc",
          "devdoc",
          "evm.bytecode.object",
          "evm.bytecode.sourceMap",
          "evm.deployedBytecode.object",
          "evm.deployedBytecode.sourceMap",
          "evm.methodIdentifiers",
        ],
        "": ["ast"],
      },
    },
  },
};

const outPath = fileArg.replace(/\.sol$/, ".input.json");
fs.writeFileSync(outPath, JSON.stringify(input, null, 2));
console.log(outPath);
