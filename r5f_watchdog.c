// r5f_watchdog.c
if (sefi_detected) {
    PMU_GLOBAL->GLOBAL_GEN_STORAGE6 = 0xDEADBEEF;
    NVIC_SystemReset();
}