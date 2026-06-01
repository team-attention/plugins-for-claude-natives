#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const YAML = require('yaml');

const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const CYAN = '\x1b[36m';
const RED = '\x1b[31m';
const NC = '\x1b[0m';

const packageRoot = path.resolve(__dirname, '..');
const targetDir = process.cwd();
const claudeDir = path.join(targetDir, '.claude');
const codexDir = path.join(targetDir, '.codex');
const yamlModuleDir = path.dirname(require.resolve('yaml/package.json'));

function parseArgs(argv) {
  const args = argv.slice(2);
  const flags = new Set(args);

  const targetIndex = args.indexOf('--target');
  let target = 'auto';
  if (targetIndex !== -1 && args[targetIndex + 1]) {
    target = args[targetIndex + 1];
  } else if (flags.has('--both')) {
    target = 'both';
  } else if (flags.has('--codex')) {
    target = 'codex';
  } else if (flags.has('--claude')) {
    target = 'claude';
  }

  if (!['auto', 'claude', 'codex', 'both'].includes(target)) {
    throw new Error(`Invalid --target "${target}". Use auto|claude|codex|both.`);
  }

  return { target };
}

console.log(`${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}`);
console.log(`${CYAN}  Agent Council - Installation${NC}`);
console.log(`${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}`);
console.log();

function copyRecursive(src, dest) {
  const stat = fs.statSync(src);

  if (stat.isDirectory()) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    const files = fs.readdirSync(src);
    for (const file of files) {
      copyRecursive(path.join(src, file), path.join(dest, file));
    }
  } else {
    fs.copyFileSync(src, dest);
    // Preserve executable permission for .sh files
    if (src.endsWith('.sh')) {
      fs.chmodSync(dest, 0o755);
    }
  }
}

function commandExists(command) {
  try {
    const checkCmd = process.platform === 'win32' ? `where ${command}` : `command -v ${command}`;
    execSync(checkCmd, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

try {
  const { target: requestedTarget } = parseArgs(process.argv);

  const detected = {
    claude: commandExists('claude'),
    codex: commandExists('codex'),
    gemini: commandExists('gemini'),
    // Antigravity CLI (`agy`): successor to the Gemini CLI. The worker falls back to
    // it automatically for the `gemini` member when the Gemini CLI is gone.
    agy: commandExists('agy'),
  };

  const hasClaudeDir = fs.existsSync(claudeDir);
  const hasCodexDir = fs.existsSync(codexDir);

  let target = requestedTarget;
  if (requestedTarget === 'auto') {
    const wantClaude = hasClaudeDir || detected.claude;
    const wantCodex = hasCodexDir || detected.codex;

    if (wantClaude && wantCodex) target = 'both';
    else if (wantCodex) target = 'codex';
    else if (wantClaude) target = 'claude';
    else target = 'claude';

    console.log(`${CYAN}Auto-detected target:${NC} ${target}`);
    if (!wantClaude && !wantCodex) {
      console.log(
        `${YELLOW}  ⓘ Could not detect Claude Code or Codex CLI; defaulting to "claude". Use --target codex if needed.${NC}`
      );
    }
    console.log();
  }

  const installs = [];
  if (target === 'claude' || target === 'both') {
    installs.push({
      label: 'Claude Code',
      rootDir: claudeDir,
      skillsDest: path.join(claudeDir, 'skills', 'agent-council'),
      displayPath: '.claude/skills/agent-council',
      hostRole: 'claude',
    });
  }
  if (target === 'codex' || target === 'both') {
    installs.push({
      label: 'Codex CLI',
      rootDir: codexDir,
      skillsDest: path.join(codexDir, 'skills', 'agent-council'),
      displayPath: '.codex/skills/agent-council',
      hostRole: 'codex',
    });
  }

  // Copy skills folder to target(s)
  const skillsSrc = path.join(packageRoot, 'skills', 'agent-council');
  const templateConfigPath = path.join(packageRoot, 'council.config.yaml');
  const templateConfigText = fs.existsSync(templateConfigPath) ? fs.readFileSync(templateConfigPath, 'utf8') : null;

  for (const install of installs) {
    if (!fs.existsSync(install.rootDir)) {
      fs.mkdirSync(install.rootDir, { recursive: true });
    }

    if (fs.existsSync(skillsSrc)) {
      console.log(`${YELLOW}Installing skills (${install.label})...${NC}`);
      copyRecursive(skillsSrc, install.skillsDest);
      console.log(`${GREEN}  ✓ ${install.displayPath}${NC}`);
    }

    // Ship runtime dependencies needed by the skill at execution time.
    const runtimeModulesDir = path.join(install.skillsDest, 'node_modules');
    if (!fs.existsSync(runtimeModulesDir)) fs.mkdirSync(runtimeModulesDir, { recursive: true });

    console.log(`${YELLOW}Installing runtime deps (${install.label})...${NC}`);
    copyRecursive(yamlModuleDir, path.join(runtimeModulesDir, 'yaml'));
    console.log(`${GREEN}  ✓ ${install.displayPath}/node_modules/yaml${NC}`);

    // Copy config file to skill folder if not exists
    const configDest = path.join(install.skillsDest, 'council.config.yaml');
    if (!fs.existsSync(configDest)) {
      console.log(`${YELLOW}Installing config (${install.label})...${NC}`);
      if (!templateConfigText) {
        console.log(`${YELLOW}  ⓘ Template council.config.yaml not found; writing an empty config.${NC}`);
        fs.writeFileSync(
          configDest,
          ['council:', '  members: []', '  chairman:', '    role: "auto"', '  settings:', '    parallel: true', ''].join(
            '\n'
          ),
          'utf8'
        );
        console.log(`${GREEN}  ✓ ${install.displayPath}/council.config.yaml${NC}`);
        continue;
      }

      const doc = YAML.parseDocument(templateConfigText);
      const membersNode = doc.getIn(['council', 'members']);

      if (membersNode && YAML.isCollection(membersNode)) {
        const enabledMembers = membersNode.items.filter((item) => {
          const member = item.toJSON();
          const nameLc = String(member.name || '').toLowerCase();
          if (nameLc === install.hostRole) return false;

          const baseCommand = String(member.command || '')
            .trim()
            .split(/\s+/)[0];
          if (!baseCommand) return false;

          return commandExists(baseCommand);
        });

        membersNode.items = enabledMembers;

        if (enabledMembers.length === 0) {
          console.log(
            `${YELLOW}  ⓘ No member CLIs detected from template. Writing members: []; edit council.config.yaml to add members.${NC}`
          );
        }
      } else {
        console.log(`${YELLOW}  ⓘ Template is missing council.members; writing template as-is.${NC}`);
      }

      fs.writeFileSync(configDest, String(doc), 'utf8');
      console.log(`${GREEN}  ✓ ${install.displayPath}/council.config.yaml${NC}`);
    } else if (fs.existsSync(configDest)) {
      console.log(`${YELLOW}  ⓘ council.config.yaml already exists (${install.label}), skipping${NC}`);
    }
  }

  console.log();
  console.log(`${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}`);
  console.log(`${GREEN}  Installation complete!${NC}`);
  console.log(`${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}`);
  console.log();
  if (installs.some((i) => i.hostRole === 'claude')) {
    console.log(`${CYAN}Usage in Claude:${NC}`);
    console.log(`  "Summon the council"`);
    console.log(`  "Let's hear opinions from other AIs"`);
    console.log();
  }
  if (installs.some((i) => i.hostRole === 'codex')) {
    console.log(`${CYAN}Usage in Codex:${NC}`);
    console.log(`  "Summon the council"`);
    console.log(`  "Let's hear opinions from other AIs"`);
    console.log();
  }
  console.log();
  console.log(`${CYAN}Direct execution:${NC}`);
  if (installs.some((i) => i.hostRole === 'claude')) {
    console.log(`  .claude/skills/agent-council/scripts/council.sh "your question"`);
  }
  if (installs.some((i) => i.hostRole === 'codex')) {
    console.log(`  .codex/skills/agent-council/scripts/council.sh "your question"`);
  }
  console.log();
  console.log(`${YELLOW}Note: Only detected CLIs are enabled as members in the generated config.${NC}`);
  console.log(`${YELLOW}      Detected: claude=${detected.claude} codex=${detected.codex} gemini=${detected.gemini} agy=${detected.agy}${NC}`);

} catch (error) {
  console.error(`${RED}Error during installation: ${error.message}${NC}`);
  process.exit(1);
}
