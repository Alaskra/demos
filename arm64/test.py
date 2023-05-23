# generate data and config file

import torch
import torchvision.transforms as transforms
import struct

config_filename = "config.txt"

def save_tensor_to_file(tensor, file_name):
    # prerequest: tensor.dtype is float32
    f = open(file_name, "wb")
    for i in tensor.flatten():
        b = struct.pack('f', float(i))
        # IEEE754规定了浮点数以大尾端存储，所以没有大小尾端的问题（而int会有）
        f.write(b)
    f.close()

def normalize():
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    N, C, H, W = 2, 3, 2, 2

    t = torch.ones((N, C, H, W), dtype=torch.float32)
    intput_filename = "in_norm.bin"
    output_filename = "out_norm.bin"
    mean_and_std = " ".join([str(x) for x in mean+std])
    with open(config_filename, 'a') as f:
        f.write(f"preprocess {output_filename} {intput_filename} {mean_and_std} {N} {H} {W}\n")

    # Apply the normalization using transforms.Normalize
    save_tensor_to_file(t, intput_filename)
    t = transforms.Normalize(mean=mean, std=std)(t)
    save_tensor_to_file(t, "torch_"+output_filename)

def topk():
    N, C, k, mode = 3, 10, 2, 0
    t = torch.ones((N, C), dtype=torch.float32)
    input_filename = "in_topk.bin"
    output_filename = f"out_topk_mode{mode}.bin"
    with open(config_filename, 'a') as f:
        f.write(f"postprocess {output_filename} {input_filename} {k} {mode} {N} {C}\n")
    save_tensor_to_file(t, input_filename)

    # Apply the normalization using transforms.Normalize
    t = torch.topk(t, k)
    save_tensor_to_file(t[0], "torch_"+output_filename)
    print(t)

normalize()
