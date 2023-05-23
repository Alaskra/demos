#include <stdio.h>
#include <stdlib.h>

void preprocess(float *out, float *in, float mean[3], float std[3], int N, int H, int W) {
  // shape is NCHW, C=3
  // subtract mean and divide std(std = sqrt(sum(x - x_mean)^2 / N))
  int C = 3;
  float *in_arr, *out_arr;
  int size_hw = H * W;
  for (int i=0; i < N; ++i) {
    for (int j=0; j < 3; ++j) {
      in_arr = in + i * 3 * size_hw + j*size_hw;
      out_arr = out + i *3*size_hw + j*size_hw;
      for (int k=0; k<size_hw; ++k) {
        out_arr[k] = (in_arr[k]-mean[j])/std[j];
        printf("arr[%d][%d][%d]:%f\n", i, j, k, out_arr[k]);
      }
    }
  }
}

// void postprocess(float *out, float *in, int k, int mode, int N, int C) {
//   float *arr = malloc(sizeof(float)*C);
//   if (mode == 0) {
//     // output k max values
//     for (int i=0; i < N; ++i) {
//       memcpy(arr, in+i*C);
//     }
//   }
// }
