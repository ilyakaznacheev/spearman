__global__ void subtract_and_square(float *dest, float *a, float *b)
{
    const int index = threadIdx.x * (threadIdx.y + 1);
    dest[index] = ( a[index] - b[index] ) * ( a[index] - b[index] );
}