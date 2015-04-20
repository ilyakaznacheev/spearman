__global__ void subtract_and_square(float *dest, float *a, float *b)
{
  // const int i = threadIdx.x;
  // dest[i] = ( a[i] - b[i] ) * ( a[i] - b[i] );
    dest[threadIdx.x] = ( a[threadIdx.x] - b[threadIdx.x] ) * ( a[threadIdx.x] - b[threadIdx.x] );
    // dest[threadIdx.x] = 0;
    // dest[threadIdx.y] = 0;
}