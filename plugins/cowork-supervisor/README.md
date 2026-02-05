# Cowork Supervisor

> Strategic orchestrator that coordinates multiple Claude Code plugins to solve complex tasks

## Overview

Cowork Supervisor is a Claude Code plugin that acts as an intelligent orchestrator. Instead of learning how to use each plugin individually (Finance, Legal, Marketing, Data, etc.), you describe your task in natural language and the Supervisor:

1. **Clarifies** your intent through targeted questions
2. **Discovers** available plugins and their capabilities
3. **Plans** the execution strategy
4. **Orchestrates** multiple plugins in parallel/sequential execution
5. **Aggregates** results into a coherent response

## Installation

### Method 1: Plugin Marketplace (Recommended)

```bash
# Add the marketplace
/plugin marketplace add team-attention/cowork-supervisor

# Install the plugin
/plugin install cowork-supervisor
```

### Method 2: Direct Installation

```bash
# Clone the repository
git clone https://github.com/team-attention/cowork-supervisor.git

# Navigate to Claude Code plugins directory
cd ~/.claude/plugins/

# Create symlink or copy
ln -s /path/to/cowork-supervisor .
```

### Method 3: Manual

1. Download or clone this repository
2. Copy to `~/.claude/plugins/cowork-supervisor/`
3. Restart Claude Code

## Quick Start

```
/supervise "Analyze competitor TechCorp's financial health and IP portfolio"
```

The Supervisor will:
1. Ask clarifying questions (which competitor? what aspects? timeframe?)
2. Discover available plugins (Finance, Legal detected)
3. Present an execution plan for your approval
4. Execute plugins in parallel where possible
5. Aggregate results into a comprehensive analysis

## How It Works

```
Your Task Description
         |
         v
  [Intent Clarifier]
         |  Asks: What exactly do you need?
         |  Asks: Which domains are involved?
         v
  [Capability Discoverer]
         |  Scans: What plugins are installed?
         |  Maps: Which plugins can help?
         v
  [Supervisor Planner]
         |  Creates: Execution plan
         |  You: Approve or modify
         v
  [Orchestra]
         |  Executes: Parallel when possible
         |  Handles: Errors and fallbacks
         v
  [Aggregator]
         |  Combines: Results from all plugins
         |  Resolves: Conflicts between sources
         v
  Final Response with Sources
```

## Usage Examples

### Basic: Single Domain

```
/supervise "Create a marketing campaign for our new product"
```

### Cross-Domain: Multiple Plugins

```
/supervise "Analyze acquisition target: financial health, legal risks, and market position"
```

### Complex: Multi-Phase Workflow

```
/supervise "Quarterly business review: sales performance, customer feedback, and competitive landscape"
```

## Supported Plugins

The Supervisor can coordinate any installed Claude Code plugin:

| Domain | Example Plugins |
|--------|----------------|
| Finance | Budget analysis, Financial reports, Forecasting |
| Legal | Contract review, IP analysis, Compliance check |
| Marketing | Campaign planning, Market research, Brand analysis |
| Sales | Pipeline analysis, Territory planning, Forecasting |
| Data | Data connectors, Analytics, ETL |
| Customer Support | Ticket analysis, Satisfaction tracking |
| Product | Roadmap planning, Feature analysis |

## Project Structure

```
cowork-supervisor/
├── .claude-plugin/
│   ├── plugin.json        # Plugin manifest
│   └── capabilities.yaml  # Capability declaration
├── agents/
│   ├── supervisor.md      # Main orchestrator
│   ├── intent-clarifier.md
│   ├── capability-discoverer.md
│   ├── supervisor-planner.md
│   ├── orchestra.md
│   └── aggregator.md
├── skills/
│   └── cowork-supervisor/
│       └── SKILL.md
├── commands/
│   └── supervise.md
├── README.md
├── LICENSE
└── CHANGELOG.md
```

## Configuration

No configuration required. The Supervisor automatically:
- Detects installed plugins via `~/.claude/plugins/installed_plugins.json`
- Scans marketplace directories for available capabilities
- Adapts to your plugin ecosystem

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for [Claude Code](https://claude.ai/claude-code)
- Inspired by multi-agent orchestration patterns
- Part of the [Team Attention](https://github.com/team-attention) plugin ecosystem
