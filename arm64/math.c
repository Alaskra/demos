#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void preprocess(float *out, float *in, float mean[3], float std[3], int N,
                int H, int W) {
  // input and output shape is NCHW, C=3
  // subtract mean and divide std(std = sqrt(sum(x - x_mean)^2 / N))
  int C = 3;
  float *in_arr, *out_arr;
  int size_hw = H * W;
  for (int i = 0; i < N; ++i) {
    for (int j = 0; j < 3; ++j) {
      in_arr = in + i * 3 * size_hw + j * size_hw;
      out_arr = out + i * 3 * size_hw + j * size_hw;
      for (int k = 0; k < size_hw; ++k) {
        out_arr[k] = (in_arr[k] - mean[j]) / std[j];
      }
    }
  }
}

static void partition(float *arr, float *arr_idx, int start, int end, int k) {
  // method 4: https://zhuanlan.zhihu.com/p/76734219
  // prerequest: 1 <= k < end-start+1
  // move k largest element to start
  float val = arr[end];
  int i = start - 1;
  float tmp;
  for (int j = start; j <= end; ++j) {
    if (arr[j] >= val) {
      ++i;
      if (arr_idx != NULL) {
        tmp = arr_idx[i];
        arr_idx[i] = arr_idx[j];
        arr_idx[j] = tmp;
      }
      tmp = arr[i];
      arr[i] = arr[j];
      arr[j] = tmp;
    }
  }
  int num = i - start + 1;
  if (num == k) {
    return;
  } else if (num > k) {
    partition(arr, arr_idx, start, i - 1, k);
  } else {
    partition(arr, arr_idx, i + 1, end, k - num);
  }
}

void postprocess(float *out, float *in, int k, int mode, int N, int C) {
  // input shape is NC, output shape is Nk or 2Nk based on different mode
  // calcalate topk
  // mode 0: output value
  // mode 1: output index
  // mode 2: output value and index
  float *arr = malloc(sizeof(float) * C);
  float *arr_idx = malloc(sizeof(float) * C);
  if (mode == 0) {
    // output k max values
    for (int i = 0; i < N; ++i) {
      memcpy(arr, in + i * C, C * sizeof(float));
      partition(arr, NULL, 0, C - 1, k);
      memcpy(out + i * k, arr, k * sizeof(float));
    }
  } else if (mode == 1) {
    for (int i = 0; i < N; ++i) {
      memcpy(arr, in + i * C, C * sizeof(float));
      for (int j = 0; j <= C; ++j)
        arr_idx[j] = j;
      partition(arr, arr_idx, 0, C - 1, k);
      memcpy(out + i * k, arr_idx, k * sizeof(float));
    }
  } else if (mode == 2) {
    for (int i = 0; i < N; ++i) {
      memcpy(arr, in + i * C, C * sizeof(float));
      for (int j = 0; j <= C; ++j)
        arr_idx[j] = j;
      partition(arr, arr_idx, 0, C - 1, k);
      memcpy(out + i * k, arr, k * sizeof(float));
      memcpy(out + N * k + i * k, arr_idx, k * sizeof(float));
    }
  }
}
