# MarrowAI

MarrowAI is an offline-first Linux assistant designed around a structured planning pipeline and a safety gate before execution.

## Quick start

```bash
python -m pip install -e .
marrowai --help
```

## Desktop GUI

On Ubuntu with a desktop session, launch the graphical application with:

```bash
marrowai-gui
```

The GUI provides safe chat, local Ollama status, installed model selection, and
a Download button for pulling a model while online. If Ollama is installed but
stopped, MarrowAI starts the local service automatically. After the model is
pulled, Ollama serves it locally and MarrowAI can continue working without
internet.

The model menu includes `llama3.2`, `mistral`, `phi3`, `qwen2.5`, `gemma2`,
and `deepseek-r1:7b`. Select one, click Download while online, then use it
offline through Ollama. The GUI also provides local speech output through
`espeak-ng`/`espeak` and can speak assistant responses. Microphone speech input
is not included yet; the GUI reports that limitation instead of pretending an
audio recording was transcribed.

The Debian installer automatically installs Ollama and starts its local
service. Internet is required once for Ubuntu packages and Ollama; internet is
also required when downloading the model selected by the user. After that,
MarrowAI and the selected model run locally without internet.

## Bounded autonomous workflows

MarrowAI plans a request, checks every step against the safety gate, and runs
ordered allowlisted tools automatically. The current tools are file listing,
backend scaffolding, test execution, and text output. Unknown or destructive
tools are blocked rather than executed.

For example:

```bash
marrowai "Create a FastAPI backend and run its tests"
```

## MVP behavior

The first vertical slice proves a safe text flow:

```bash
marrowai run "List the files in the current workspace"
```

This generates a structured plan, checks the plan against a risk model, and executes only allowed actions.
