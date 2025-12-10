# API Reference

## Firmware (C)

### Predictive Sentinel

#### `sentinel_init(sentinel_state_t* sentinel)`
Initializes a sentinel monitoring channel.

**Parameters:**
- `sentinel`: Pointer to sentinel state structure

**Returns:** None

**Example:**
```c
sentinel_state_t rx_sentinel;
sentinel_init(&rx_sentinel);