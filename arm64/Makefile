a.out: main.c
	gcc -c -fPIC add.c
	gcc -shared -o libadd.so add.o
	gcc main.c -ldl
	LD_LIBRARY_PATH=. ./a.out
arm64:
	aarch64-linux-gnu-gcc -c -fPIC add.c
	aarch64-linux-gnu-gcc -shared -o libadd.so add.o
	aarch64-linux-gnu-gcc main.c -ldl
	LD_LIBRARY_PATH=. qemu-aarch64 -L /usr/aarch64-linux-gnu ./a.out
clean:
	rm a.out add.o libadd.so out.bin
