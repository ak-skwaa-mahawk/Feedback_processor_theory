// fpt_ppc.c — VxWorks on PowerPC 450 MHz
#include <vxWorks.h>
#include <logLib.h>

void fpt_titan_task() {
    UINT16 correction;
    while (1) {
        if (i2cRead(0x40, 0x10, &correction)) {
            if (veto_flag) {
                logMsg("C190 VETO | TITAN CORE\n", 0,0,0,0,0,0);
            } else {
                motor_set(correction);
            }
        }
        taskDelay(1);
    }
}
ML505 (XC5VLX110T)
 │
 ├── FMC → sensor_scrape[15:0]
 ├── PowerPC → VxWorks RTOS
 ├── LED0   → veto_out (RED)
 ├── LED1   → AGI SOVEREIGN (GREEN)
 ├── RS-232 → nRF Titan Relay
 └── CompactFlash → PoR Orbit Log