// fpt_aie.cpp — AI Engine Kernel (400 tiles)
#include <aie_api/aie.hpp>

void qgh_1024_kernel(input_window<int8> *glyph_in, input_window<int8> *ref_glyph, output_window<float> *R_out) {
    v128int8 g = window_readincr(glyph_in);
    v128int8 r = window_readincr(ref_glyph);
    
    v32accfloat dot = mul(g, r);
    v32accfloat norm_g = mul(g, g);
    v32accfloat norm_r = mul(r, r);
    
    float R = reduce_add(dot) / (sqrt(reduce_add(norm_g)) * sqrt(reduce_add(norm_r)) + 1e-8);
    window_write(R_out, R >= 0.997f ? 1.0f : 0.0f);  // C190 VETO
}