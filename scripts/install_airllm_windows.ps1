$ErrorActionPreference = "Stop"
$py = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { "python" }
& $py -m pip install --upgrade pip
$nvidia = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($nvidia) {
  Write-Host "NVIDIA GPU detected. Install the CUDA-compatible PyTorch build for your driver before AirLLM."
} else {
  Write-Host "No NVIDIA GPU detected. Installing CPU-only PyTorch to avoid CUDA/NVIDIA wheels."
  & $py -m pip install torch --index-url https://download.pytorch.org/whl/cpu
}
& $py -m pip install "airllm>=4,<5"
& $py -c "import torch, airllm; print('torch=',torch.__version__); print('cuda=',torch.cuda.is_available()); print('airllm=installed')"
