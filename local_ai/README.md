# Lightweight Local AI (CPU-friendly)

This is a minimal local chat assistant designed to keep resource usage low. It uses a small GGUF model with `llama.cpp` via `llama-cpp-python`.

## Why it won't lag your PC
- Defaults to **half your CPU cores**.
- Keeps context size and batch size small.
- Lets you force **CPU-only** mode (no GPU overhead).

## 1) Install dependencies

```bash
cd local_ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Download a tiny model

Pick a **small** GGUF model (0.5B–1.5B parameters). Example sources:
- Qwen2.5 0.5B GGUF
- Phi-2 GGUF
- TinyLlama 1.1B GGUF

Place the file somewhere like `models/`.

## 3) Run

```bash
python run.py --model-path models/qwen2.5-0.5b-instruct.gguf
```

Optional tuning to reduce load:

```bash
python run.py \
  --model-path models/qwen2.5-0.5b-instruct.gguf \
  --n-threads 2 \
  --n-ctx 512 \
  --n-batch 32 \
  --n-gpu-layers 0
```

## 4) Optional config file

Create `config.json` for defaults:

```json
{
  "model_path": "models/qwen2.5-0.5b-instruct.gguf",
  "n_ctx": 512,
  "n_threads": 2,
  "n_batch": 32,
  "n_gpu_layers": 0,
  "system_prompt": "You are a helpful local assistant. Keep responses concise."
}
```

Run with:

```bash
python run.py --config config.json
```

## Tips for low lag
- Use **0.5B–1.5B** models for fastest responses.
- Keep `n_ctx` <= 512.
- Set `n_threads` to 1–2 on older CPUs.
- Keep background apps closed while running.
