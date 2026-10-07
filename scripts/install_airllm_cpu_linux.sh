#!/usr/bin/env bash
set -euo pipefail
python_bin="${PYTHON_BIN:-python}"
"$python_bin" -m pip install --upgrade pip
if command -v nvidia-smi >/dev/null 2>&1; then
  echo "NVIDIA GPU detected. Installing normal AirLLM stack."
  "$python_bin" -m pip install "airllm>=4,<5"
else
  echo "No NVIDIA GPU detected. Installing CPU-only PyTorch to avoid CUDA/NVIDIA wheels."
  "$python_bin" -m pip install torch --index-url https://download.pytorch.org/whl/cpu
  "$python_bin" -m pip install "airllm>=4,<5"
fi
echo "AirLLM installation complete."
"$python_bin" -c "import torch, airllm; print('torch=',torch.__version__); print('cuda=',torch.cuda.is_available()); print('airllm=',airllm.__version__ if hasattr(airllm,'__version__') else 'installed')"
