a.out: main.c math.so
	gcc main.c -ldl
	LD_LIBRARY_PATH=. ./a.out
math.so: math.c
	gcc -c -fPIC math.c
	gcc -shared -o libmath.so math.o
arm64:
	aarch64-linux-gnu-gcc -c -fPIC math.c
	aarch64-linux-gnu-gcc -shared -o libmath.so math.o
	aarch64-linux-gnu-gcc main.c -ldl
	LD_LIBRARY_PATH=. qemu-aarch64 -L /usr/aarch64-linux-gnu ./a.out
clean:
	rm a.out add.o libadd.so out.bin out1.bin
