CC=aarch64-linux-gnu-gcc
# 开启arm64的neon指令集
CFLAG=-mcpu=cortex-a53 -ftree-vectorize -O2

a.out: main.c libmath.so
	$(CC) main.c -ldl
	LD_LIBRARY_PATH=. qemu-aarch64 -L /usr/aarch64-linux-gnu ./a.out
libmath.so: math.c
	$(CC) -c -fPIC $(CFLAG) math.c
	$(CC) -shared -o libmath.so math.o
x86:
	gcc -c -fPIC math.c
	gcc -shared -o libmath.so math.o
	gcc main.c -ldl
	LD_LIBRARY_PATH=. ./a.out
clean:
	rm *.o libmath.so a.out
clean_all:
	rm *.o libmath.so a.out config.txt *.bin 
