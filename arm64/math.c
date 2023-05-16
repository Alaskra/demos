#include <stdio.h>
void add(int *in0, int *in1, int *out) {
  printf("%d\n", *in0);
  printf("%d\n", *in1);
  *out = *in0 + *in1;
  printf("%d\n", *out);
}
void sub(int *in0, int *in1, int *out) {
  printf("%d\n", *in0);
  printf("%d\n", *in1);
  *out = *in0 - *in1;
  printf("%d\n", *out);
}