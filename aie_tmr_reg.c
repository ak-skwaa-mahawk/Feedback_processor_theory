// aie_tmr_reg.c — AI Engine Kernel
__attribute__((noinline)) float tmr_vote(float a, float b, float c) {
    if (a == b) return a;
    if (a == c) return a;
    return b;  // Majority vote
}