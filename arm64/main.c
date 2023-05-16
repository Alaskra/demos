#include "math.h"
#include <dlfcn.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

void open_map_in(char *file_name, void **addr, int *fd) {
  *fd = open(file_name, O_RDONLY);
  if (*fd == -1) {
    perror("open");
    exit(-1);
  }
  *addr = mmap(NULL, 4, PROT_READ, MAP_PRIVATE, *fd, 0);
  if (*addr == MAP_FAILED) {
    perror("mmap");
    exit(-1);
  }
  printf("addr: %p\n", *addr);
}

void open_map_out(char *file_name, void **addr, int *fd) {
  *fd = open(file_name, O_RDWR | O_CREAT, S_IRUSR | S_IWUSR);
  if (*fd == -1) {
    perror("open");
    exit(-1);
  }
  if (ftruncate(*fd, 4) == -1) {
    perror("ftruncate");
    exit(-1);
  }
  *addr = mmap(NULL, 4, PROT_READ | PROT_WRITE, MAP_SHARED, *fd, 0);
  if (*addr == MAP_FAILED) {
    perror("mmap");
    exit(-1);
  }
  printf("addr: %p\n", *addr);
}

void close_map(void *addr, int fd) {
  if (munmap(addr, 4) == -1) {
    perror("munmap");
    exit(-1);
  }
  close(fd);
}

int main() {
  int fd0, fd1, fd;
  void *in0, *in1, *out;
  char *error;
  void *func;
  void *handle = dlopen("./libmath.so", RTLD_LAZY);
  if (!handle) {
    fprintf(stderr, "%s\n", dlerror());
    exit(-1);
  }
  char func_name[100];
  char in0_name[100];
  char in1_name[100];
  char out_name[100];
  FILE *file_config = fopen("config.txt", "r");
  if (file_config == NULL) {
    perror("open");
    exit(-1);
  }
  while (fscanf(file_config, "%s %s %s %s", func_name, in0_name, in1_name,
                out_name) != EOF) {

    open_map_in(in0_name, &in0, &fd0);
    open_map_in(in1_name, &in1, &fd1);
    open_map_out(out_name, &out, &fd);
    func = dlsym(handle, func_name);
    if ((error = dlerror()) != NULL) {
      fprintf(stderr, "%s\n", error);
      exit(-1);
    }

    if (strcmp(func_name, "add") == 0)
      ((func_add)func)(in0, in1, out);
    else if (strcmp(func_name, "sub") == 0)
      ((func_sub)func)(in0, in1, out);
    else {
        perror("function not support");
        exit(-1);
    }

    close_map(in0, fd0);
    close_map(in1, fd1);
    close_map(out, fd);
  }

  return 0;
}
