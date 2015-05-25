__global__ void subtract_and_square(float *dest, float *a, float *b, int n)
{
    // const int index = threadIdx.x * (threadIdx.y + 1);
    // dest[index] = ( a[index] - b[index] ) * ( a[index] - b[index] );
    int index = blockDim.x * blockIdx.x + threadIdx.x;
    if (index < n)
        dest[index] = ( a[index] - b[index] ) * ( a[index] - b[index] );
}