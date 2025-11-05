// qgh_1024_aie.c — 1024-bit QGH Kernel
void qgh_1024_kernel(input_window<int8> *in_g, input_window<int8> *in_r, output_window<float> *R) {
    v128int8 g = window_readincr(in_g);
    v128int8 r = window_readincr(in_r);
    
    v32accfloat dot = mul(g, r);           // 1024-bit dot
    v32accfloat norm_g = mul(g, g);
    v32accfloat norm_r = mul(r, r);
    
    float R_val = reduce_add(dot) / (sqrt(reduce_add(norm_g)) * sqrt(reduce_add(norm_r)));
    window_write(R, R_val >= 0.997f ? 1.0f : 0.0f);  // C190 VETO
}