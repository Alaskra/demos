#include <stdio.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <dlfcn.h>

int main() {

    int fd0 = open("in0.bin", O_RDONLY);
    int fd1 = open("in1.bin", O_RDONLY);

    int fd = open("out.bin", O_RDWR | O_CREAT, S_IRUSR | S_IWUSR);
    if (fd0 == -1||fd1 == -1||fd == -1) {
        perror("open");
        return 1;
    }


    if (ftruncate(fd, 4) == -1) {
        perror("ftruncate");
        return 1;
    }

    int *in0 = (int*)mmap(NULL, 4, PROT_READ, MAP_PRIVATE, fd0, 0);
    printf("addr in0: %p\n", in0);
    int *in1 = (int*)mmap(NULL, 4, PROT_READ, MAP_PRIVATE, fd1, 0);
    printf("addr in1: %p\n", in1);
    int *out = (int*)mmap(NULL, 4, PROT_READ | PROT_WRITE, MAP_PRIVATE, fd, 0);
    printf("addr out: %p\n", out);
    if (in0 == MAP_FAILED||in1 == MAP_FAILED||out == MAP_FAILED) {
        perror("mmap");
        return 1;
    }

    
    void *handle;
    char *error;
    int (*add)(int*, int*, int*);
    handle = dlopen("./libadd.so", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "%s\n", dlerror());
        return 1;
    }
    add = dlsym(handle, "add");
    if ((error = dlerror()) != NULL) {
        fprintf(stderr, "%s\n", error);
        return 1;
    }

    add(in0, in1, out);

    if (munmap(in0, 4) == -1) {
        perror("munmap");
        return 1;
    }
    if (munmap(in1, 4) == -1) {
        perror("munmap");
        return 1;
    }
    if (munmap(out, 4) == -1) {
        perror("munmap");
        return 1;
    }

    close(fd);
    close(fd0);
    close(fd1);

    return 0;
}
