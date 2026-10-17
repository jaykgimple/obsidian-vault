# Open-Source Toolkit — ArtCraft (github.com/storytold)

Cloned into `/root/toolkit/`. Standing reference for avatar/video/voice work
(Podsona, OmniVoke, voice). Org = ArtCraft, "tools and models for makers/builders".

## cloud-worker — MiniMax H3 video model harness (GPU, NOT the CPU VPS)

- Runs **MiniMax H3** (open-weights video model, native stereo audio, 24fps,
  5-15s, ~1MP) via ComfyUI on RunPod GPU (rig: 1x B200 180GB).
- t2v / i2v / ref2v workflows, weight downloads, benchmark + concurrency +
  cost-per-video docs (`docs/`).
- Direct open-weights alternative to the paid video models behind OmniVoke.
- Requires GPU (RunPod or Modal), not the CPU VPS.

## vits-finetuning — self-hosted voice cloning (train GPU, infer CPU)

- Fine-tunable VITS. Training ~11-14GB VRAM (needs a GPU).
- Exports to TorchScript; `infer_ts.py --device cpu` runs inference on CPU, i.e.
  on the VPS. Self-hosted alternative to Fish Audio / OpenRouter TTS.

## realtime-voice-conversion — voice conversion (CycleGAN-VC)

- Rust audio sidecar (proto/zeromq) + Python CycleGAN-VC. ~4-6s latency
  real-time on GPU; batch conversion is CPU-viable.

## storyteller-ml — TTS monorepo (Tacotron core + more)

## torchscript-models — PyTorch -> TorchScript JIT for libtorch/CPU deployment

- Porting guide for embedding trained models in Rust/binaries via libtorch.
  Useful for shipping voice models that run anywhere (incl. the CPU VPS).