## 介绍

编译arm64程序（dlopen, mmap），然后使用qemu user mode运行

实现了preprocess和postpreprocess两个函数，并将其与torch的输出对比

## 环境

ubuntu18

apt install qemu-user qemu-user-static gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu binutils-aarch64-linux-gnu-dbg build-essential

python3.10

安装pytorch

## 运行

python test.py

## 参考

https://azeria-labs.com/arm-on-x86-qemu-user/
