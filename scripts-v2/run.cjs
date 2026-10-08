// A single local entry point. No deployment, network integration or bundler.
const { spawn, spawnSync } = require("node:child_process");
const path = require("node:path");
const fs = require("node:fs");
const root = path.resolve(__dirname, "..");
process.chdir(root);
const python = path.join(
  root,
  ".venv",
  process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
);
const mode = process.argv[2];
function run(program, args, env = process.env) {
  const result = spawnSync(program, args, { cwd: root, env, stdio: "inherit" });
  if (result.error) throw result.error;
  if (result.status !== 0)
    throw new Error(`${args.join(" ")} failed (${result.status})`);
}
function py(name) {
  run(python, [`scripts-v2/${name}.py`]);
}
async function main() {
  if (!["build", "verify", "export"].includes(mode))
    throw new Error("Use build, verify or export");
  if (!fs.existsSync(python))
    throw new Error(
      "Create .venv and install requirements.txt first (see README).",
    );
  if (mode === "build") {
    fs.mkdirSync("output-v2/build", { recursive: true });
    for (const name of [
      "build_rest",
      "build_prototype",
      "build_legal",
      "package",
    ])
      py(name);
    return;
  }
  if (!fs.existsSync("dist/index.html"))
    throw new Error("Run npm run build first.");
  for (const dir of ["output-v2/mockups", "output-v2/pdf", "output-v2/review"])
    fs.mkdirSync(dir, { recursive: true });
  const server = spawn(
    python,
    [
      "-u",
      "-m",
      "http.server",
      "0",
      "--bind",
      "127.0.0.1",
      "--directory",
      mode === "verify" ? "dist" : "prototype",
    ],
    { cwd: root, stdio: ["ignore", "pipe", "ignore"] },
  );
  try {
    const base = await new Promise((resolve, reject) => {
      let output = "";
      server.on("error", reject);
      server.on("exit", (code) =>
        reject(new Error(`Preview server exited: ${code}`)),
      );
      server.stdout.on("data", (chunk) => {
        output += chunk;
        const match = output.match(/port (\d+)/);
        if (match) resolve(`http://127.0.0.1:${match[1]}`);
      });
    });
    const env = { ...process.env, BASE_URL: base };
    if (mode === "verify") {
      run(process.execPath, ["scripts-v2/verify.cjs"], env);
      for (const file of ["navigation-check", "polish-check", "motion-check", "smooth-check", "seo-browser"])
        run(process.execPath, [`scripts-v2/${file}.cjs`], env);
      run(python, ["scripts-v2/verify_seo.py"], env);
    } else {
      run(process.execPath, ["scripts-v2/verify.cjs", "--export"], env);
      py("build_pdf");
      py("pdf_check");
    }
  } finally {
    server.kill();
  }
}
main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
