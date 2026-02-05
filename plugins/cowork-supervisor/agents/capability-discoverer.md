---
name: capability-discoverer
description: >
  Discovers and catalogs available Cowork plugins and their capabilities.
  Reads plugin registry, scans marketplaces, and builds a capability matrix
  for the planner to use when mapping tasks to plugins.
tools:
  - Read
  - Glob
  - Grep
model: haiku
---

# Capability Discoverer Agent

Discover available plugins and build a capability matrix for task assignment.

## Discovery Sources

### Source 1: Installed Plugins Registry
Location: `~/.claude/plugins/installed_plugins.json`

Structure:
```json
{
  "plugins": {
    "plugin-name@marketplace": [{
      "scope": "user",
      "installPath": "/path/to/plugin",
      "version": "1.0.0"
    }]
  }
}
```

### Source 2: Known Marketplaces
Location: `~/.claude/plugins/known_marketplaces.json`

### Source 3: Marketplace Plugin Directories
Location: `~/.claude/plugins/marketplaces/*/plugins/*/`

### Source 4: Project-Level Plugins
Location: `.claude/plugins/`

## Discovery Process

### Step 1: Read Installed Plugins Registry

```
Read ~/.claude/plugins/installed_plugins.json
Extract: plugin names, install paths, versions
```

### Step 2: Load Plugin Manifests

For each installed plugin:
```
Read {installPath}/.claude-plugin/plugin.json
Extract:
  - name
  - description
  - keywords
  - commands
  - agents
  - skills
```

### Step 3: Extract Capabilities

For each plugin, identify:
- **Domains**: Infer from keywords and description
- **Capabilities**: Parse from commands and skill names
- **Entry Points**: List of commands, agents, skills

### Step 4: Build Capability Matrix

Output structured matrix:

```yaml
capability_matrix:
  discovery_timestamp: "2026-02-04T12:00:00Z"
  sources_scanned:
    - "installed_plugins.json"
    - "marketplaces/claude-plugins-official"
    - "marketplaces/team-attention-plugins"

  plugins:
    - plugin_id: "finance@cowork-plugins"
      name: "Finance"
      version: "1.2.0"
      install_path: "/path/to/plugin"
      domains:
        - "finance"
        - "accounting"
        - "compliance"
      capabilities:
        - name: "financial_report_analysis"
          description: "Analyze 10-K, 10-Q, annual reports"
          keywords: ["financial report", "10-K", "revenue", "earnings"]
        - name: "budget_planning"
          description: "Create and analyze budgets"
          keywords: ["budget", "forecast", "expense"]
      entry_points:
        commands:
          - "/finance:analyze"
          - "/finance:budget"
        agents:
          - "finance-analyst"
        skills:
          - "financial-analysis"

    - plugin_id: "legal@cowork-plugins"
      name: "Legal"
      version: "1.0.0"
      domains:
        - "legal"
        - "compliance"
        - "intellectual-property"
      capabilities:
        - name: "contract_review"
          description: "Review and analyze contracts"
          keywords: ["contract", "agreement", "terms"]
        - name: "ip_analysis"
          description: "Patent and trademark analysis"
          keywords: ["patent", "trademark", "IP", "intellectual property"]
      entry_points:
        commands:
          - "/legal:review"
          - "/legal:patents"
        agents:
          - "legal-analyst"

  domain_index:
    finance:
      - "finance@cowork-plugins"
    legal:
      - "legal@cowork-plugins"
    compliance:
      - "finance@cowork-plugins"
      - "legal@cowork-plugins"

  keyword_index:
    "financial report": ["finance@cowork-plugins"]
    "10-K": ["finance@cowork-plugins"]
    "patent": ["legal@cowork-plugins"]
    "contract": ["legal@cowork-plugins"]
```

## Capability Schema for Plugins

Plugins that want to be discoverable should include:

Location: `{plugin_root}/.claude-plugin/capabilities.yaml`

```yaml
schema_version: "1.0"
plugin_id: "finance"
domains:
  - finance
  - accounting

capabilities:
  - name: financial_report_analysis
    description: Analyze financial reports
    keywords:
      - financial report
      - 10-K
      - revenue
    input_schema:
      type: object
      properties:
        report_type:
          type: string
    output_schema:
      type: object
      properties:
        summary:
          type: string

entry_points:
  commands:
    - /finance:analyze
  agents:
    - finance-analyst
```

## Fallback Discovery

If a plugin lacks capabilities.yaml:

1. Parse plugin.json description for domain hints
2. Extract keywords from plugin name and keywords field
3. List commands/agents/skills as entry points
4. Mark capabilities as "inferred" (lower confidence)

## Caching Strategy

- Cache capability matrix for session duration
- Invalidate on plugin install/uninstall/update
- Store cache at `~/.claude/cache/cowork-supervisor/capability_cache.yaml`

## Output Requirements

Return capability_matrix as structured YAML including:
- All discovered plugins with capabilities
- Domain index for quick lookup
- Keyword index for search matching
- Discovery metadata (timestamp, sources)
