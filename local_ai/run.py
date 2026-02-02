#!/usr/bin/env python3
"""Lightweight local AI chat using llama.cpp (CPU-friendly)."""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Iterable


@dataclass
class Settings:
    model_path: str
    n_ctx: int
    n_threads: int
    n_batch: int
    n_gpu_layers: int
    system_prompt: str


def load_settings(args: argparse.Namespace) -> Settings:
    if args.config:
        with open(args.config, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    else:
        data = {}

    cpu_count = os.cpu_count() or 4
    return Settings(
        model_path=args.model_path or data.get("model_path", ""),
        n_ctx=args.n_ctx or data.get("n_ctx", 512),
        n_threads=args.n_threads or data.get("n_threads", max(1, cpu_count // 2)),
        n_batch=args.n_batch or data.get("n_batch", 64),
        n_gpu_layers=args.n_gpu_layers
        if args.n_gpu_layers is not None
        else data.get("n_gpu_layers", 0),
        system_prompt=args.system_prompt or data.get(
            "system_prompt",
            "You are a helpful local assistant. Keep responses concise.",
        ),
    )


def iter_messages() -> Iterable[str]:
    print("Type your message and press Enter. Type /exit to quit.")
    while True:
        try:
            message = input("> ").strip()
        except EOFError:
            break
        if not message:
            continue
        if message.lower() in {"/exit", "/quit"}:
            break
        yield message


def run_chat(settings: Settings) -> int:
    if not settings.model_path:
        print("Model path is required. Use --model-path or config file.")
        return 2
    if not os.path.exists(settings.model_path):
        print(f"Model not found: {settings.model_path}")
        return 2

    try:
        from llama_cpp import Llama
    except ImportError:
        print("Missing dependency: llama-cpp-python")
        print("Install with: pip install -r requirements.txt")
        return 2

    llm = Llama(
        model_path=settings.model_path,
        n_ctx=settings.n_ctx,
        n_threads=settings.n_threads,
        n_batch=settings.n_batch,
        n_gpu_layers=settings.n_gpu_layers,
        verbose=False,
    )

    chat_history: list[dict[str, str]] = [
        {"role": "system", "content": settings.system_prompt}
    ]

    for message in iter_messages():
        chat_history.append({"role": "user", "content": message})
        response = llm.create_chat_completion(
            messages=chat_history,
            temperature=0.2,
            max_tokens=256,
            stop=["</s>", "User:"],
        )
        assistant_message = response["choices"][0]["message"]["content"].strip()
        print(f"AI: {assistant_message}\n")
        chat_history.append({"role": "assistant", "content": assistant_message})

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lightweight local AI chat")
    parser.add_argument("--model-path", help="Path to a GGUF model file")
    parser.add_argument("--config", help="Optional JSON config file")
    parser.add_argument("--n-ctx", type=int, help="Context size (tokens)")
    parser.add_argument("--n-threads", type=int, help="CPU threads to use")
    parser.add_argument("--n-batch", type=int, help="Batch size")
    parser.add_argument(
        "--n-gpu-layers",
        type=int,
        help="GPU layers to offload (0 for CPU only)",
    )
    parser.add_argument(
        "--system-prompt",
        help="System prompt to steer assistant behavior",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    settings = load_settings(args)
    return run_chat(settings)


if __name__ == "__main__":
    raise SystemExit(main())
