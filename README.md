# OpenRouter Skill for Claude Code

A Claude Code skill that provides access to 300+ AI models via the [OpenRouter](https://openrouter.ai) API.

## Features

- **Text Completion**: Call any model (GPT-4, Claude, Gemini, Llama, Mistral, etc.)
- **Image Generation**: Generate images with models like Gemini Flash, Flux, and more
- **Model Discovery**: Search and filter models by capability (vision, tools, long context)
- **Multi-Step Workflows**: Chain models together for complex tasks

## Installation

### As a Claude Code Skill

Add this repository as a skill in your Claude Code configuration:

```bash
# Clone to your skills directory
git clone https://github.com/tsilva/agent-skill-openrouter.git ~/.claude/skills/openrouter
```

### Standalone Usage

```bash
# Clone the repository
git clone https://github.com/tsilva/agent-skill-openrouter.git
cd agent-skill-openrouter

# Install dependencies
pip install requests

# Set your API key
export OPENROUTER_API_KEY="sk-or-..."  # Get key at https://openrouter.ai/keys
```

## Usage

### Text Completion

```bash
python scripts/openrouter_client.py chat anthropic/claude-3.5-sonnet "Explain quantum computing"
python scripts/openrouter_client.py chat openai/gpt-4o "Write a haiku" --max-tokens 100
```

### Image Generation

```bash
python scripts/openrouter_client.py image google/gemini-2.5-flash-image "A sunset over mountains" -o sunset.png
python scripts/openrouter_client.py image black-forest-labs/flux.2-pro "Cyberpunk city" --aspect 16:9
```

### Model Discovery

```bash
python scripts/openrouter_client.py models              # List all models
python scripts/openrouter_client.py models vision       # Vision-capable models
python scripts/openrouter_client.py models image_gen    # Image generation models
python scripts/openrouter_client.py find "claude"       # Search by name
```

## Requirements

- Python 3.7+
- `requests` library
- OpenRouter API key ([get one here](https://openrouter.ai/keys))

## License

MIT
