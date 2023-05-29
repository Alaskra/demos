# generate data and config file,
# then compile and run arm64 program and compare torch output and arm64 output

import torch
import torchvision.transforms as transforms
import struct
import subprocess
import numpy as np

config_filename = "config.txt"


def normalize():
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    N, C, H, W = 2, 3, 2, 2

    t = torch.ones((N, C, H, W), dtype=torch.float32)
    input_filename = "in_norm.bin"
    output_filename = "out_norm.bin"
    mean_and_std = " ".join([str(x) for x in mean + std])
    with open(config_filename, "a") as f:
        f.write(
            f"preprocess {output_filename} {input_filename} {mean_and_std} {N} {H} {W}\n"
        )

    # Apply the normalization using transforms.Normalize
    t.numpy().tofile(input_filename)
    t = transforms.Normalize(mean=mean, std=std)(t)
    t.numpy().tofile("torch_" + output_filename)
    # t.numpy().tofile("asd.bin")


def topk(mode):
    N, C, k = 3, 10, 2
    t = torch.arange(0, N * C, dtype=torch.float32).resize_(N, C)
    input_filename = f"in_topk_mode{mode}.bin"
    output_filename = f"out_topk_mode{mode}.bin"
    with open(config_filename, "a") as f:
        f.write(f"postprocess {output_filename} {input_filename} {k} {mode} {N} {C}\n")
    t.numpy().tofile(input_filename)

    # Apply the normalization using transforms.Normalize
    t = torch.topk(t, k)
    if mode == 0:
        t[0].numpy().tofile("torch_" + output_filename)
    elif mode == 1:
        t[1].numpy().astype(np.float32).tofile("torch_" + output_filename)
    elif mode == 2:
        torch.cat((t[0], t[1])).numpy().tofile("torch_" + output_filename)


subprocess.call("make clean_all", shell=True)
normalize()
topk(0)
topk(1)
topk(2)
subprocess.call("make", shell=True)
