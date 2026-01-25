# doubt

Force Claude to re-validate its responses when you have doubts.

## Usage

Add `!rv` anywhere in your prompt:

```
Analyze this code !rv
```

When Claude tries to stop, it will be blocked and forced to re-verify everything.

## How It Works

1. **doubt-detector** (UserPromptSubmit): Detects `!rv` and activates doubt mode
2. **doubt-validator** (Stop): Blocks Claude and demands re-verification

## Why?

Sometimes Claude hallucinates. This forces a second look when you're not sure you can trust the response.

## Why `!rv` instead of `!doubt`?

The keyword `doubt` itself affects Claude's behavior - seeing "doubt" in the prompt makes Claude start doubting from the beginning. Using a neutral keyword like `!rv` (re-validate) lets Claude work normally first, then verify at the end.
