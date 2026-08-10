// aie_ecc_mem.c
void aie_mem_write(uint64_t addr, uint64_t data) {
    uint8_t ecc = compute_ecc8(data);
    write_data_memory(addr, data);
    write_ecc_memory(addr, ecc);
}