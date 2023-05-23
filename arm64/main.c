#include "math.h"
#include <dlfcn.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

typedef struct data {
  char file_name[100];
  int fd;
  void *addr;
} Data;

float abs_float(float f) {
  if (f < 0) {
    return -f;
  } else {
    return f;
  }
}

void calc_diff(float *output, float *base, int size) {
  // relative error
  // RE = (1/n) * Σ(|yᵢ - ŷᵢ| / |yᵢ|) * 100%
  float err = 0;
  int sub;
  for (int i = 0; i < size; ++i) {
    err += abs_float(output[i] - base[i]) / abs_float(base[i]);
    // printf("%f, %f\n", output[i], base[i]);
  }
  err /= size;
  printf("relative error: %f\n", err);
}

void open_map_in(Data *data) {
  data->fd = open(data->file_name, O_RDONLY);
  if (data->fd == -1) {
    perror("open");
    exit(-1);
  }
  data->addr = mmap(NULL, 4, PROT_READ, MAP_PRIVATE, data->fd, 0);
  if (data->addr == MAP_FAILED) {
    perror("mmap");
    exit(-1);
  }
  // printf("addr: %p\n", data->addr);
}

void open_map_out(Data *data) {
  data->fd = open(data->file_name, O_RDWR | O_CREAT, S_IRUSR | S_IWUSR);
  if (data->fd == -1) {
    perror("open");
    exit(-1);
  }
  if (ftruncate(data->fd, 4) == -1) {
    perror("ftruncate");
    exit(-1);
  }
  data->addr = mmap(NULL, 4, PROT_READ | PROT_WRITE, MAP_SHARED, data->fd, 0);
  if (data->addr == MAP_FAILED) {
    perror("mmap");
    exit(-1);
  }
  // printf("addr: %p\n", data->addr);
}

void close_map(Data data) {
  if (munmap(data.addr, 4) == -1) {
    perror("munmap");
    exit(-1);
  }
  close(data.fd);
}

int run() {
  Data in, out;
  char *error;
  void *func;
  void *handle = dlopen("./libmath.so", RTLD_LAZY);
  if (!handle) {
    fprintf(stderr, "%s\n", dlerror());
    exit(-1);
  }
  char *bufs[20];
  for (int i = 0; i < 20; ++i) {
    bufs[i] = malloc(100);
  }
  FILE *file_config = fopen("config.txt", "r");
  if (file_config == NULL) {
    perror("open");
    exit(-1);
  }
  while (fscanf(file_config, "%s", bufs[0]) != EOF) {
    if (strcmp(bufs[0], "preprocess") == 0) {
      for (int i = 1; i <= 11; ++i)
        fscanf(file_config, "%s", bufs[i]);
      Data in, out;
      strcpy(out.file_name, bufs[1]);
      strcpy(in.file_name, bufs[2]);
      open_map_in(&in);
      open_map_out(&out);
      func = dlsym(handle, bufs[0]);
      if ((error = dlerror()) != NULL) {
        fprintf(stderr, "%s\n", error);
        exit(-1);
      }
      float mean[3] = {atof(bufs[3]), atof(bufs[4]), atof(bufs[5])};
      float std[3] = {atof(bufs[6]), atof(bufs[7]), atof(bufs[8])};
      int N = atoi(bufs[9]);
      int H = atoi(bufs[10]);
      int W = atoi(bufs[11]);
      ((func_preprocess)func)(out.addr, in.addr, mean, std, N, H, W);
      close_map(in);
      close_map(out);
      Data out_torch;
      strcpy(bufs[0], "torch_");
      strcat(bufs[0], out.file_name);
      strcpy(out_torch.file_name, bufs[0]);
      open_map_in(&out);
      open_map_in(&out_torch);
      calc_diff((float *)out.addr, (float *)out_torch.addr, 3 * N * H * W);
    } else if (strcmp(bufs[0], "postprocess") == 0) {
      for (int i = 1; i <= 6; ++i)
        fscanf(file_config, "%s", bufs[i]);
      Data in, out;
      strcpy(out.file_name, bufs[1]);
      strcpy(in.file_name, bufs[2]);
      open_map_in(&in);
      open_map_out(&out);
      func = dlsym(handle, bufs[0]);
      if ((error = dlerror()) != NULL) {
        fprintf(stderr, "%s\n", error);
        exit(-1);
      }
      int k = atoi(bufs[3]);
      int mode = atoi(bufs[4]);
      int N = atoi(bufs[5]);
      int C = atoi(bufs[6]);
      ((func_postprocess)func)(out.addr, in.addr, k, mode, N, C);
      close_map(in);
      close_map(out);
      Data out_torch;
      strcpy(bufs[0], "torch_");
      strcat(bufs[0], out.file_name);
      strcpy(out_torch.file_name, bufs[0]);
      open_map_in(&out);
      open_map_in(&out_torch);
      if (mode == 0 || mode == 1)
        calc_diff((float *)out.addr, (float *)out_torch.addr, N * k);
      else if (mode == 2)
        calc_diff((float *)out.addr, (float *)out_torch.addr, 2 * N * k);
    } else {
      printf("error not support: %s\n", bufs[0]);
      exit(-1);
    }
  }
  return 0;
}

int main() { run(); }
