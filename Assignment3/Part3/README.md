# Assignment3 Part3

This part of the repository simulates the Distance Vector Routing algorithm using C source files.

## Requirements

- GCC or compatible C compiler
- Linux or Windows (with WSL, MinGW, or similar)

## Compilation and Execution

### Compilation
To compile the simulation:
```bash
gcc -o dvr distance_vector.c node0.c node1.c node2.c node3.c -Wall
```
This creates an executable named `dvr`.

### Running the Simulation
You can run the simulation with an optional trace level parameter:
```bash 
./dvr
```
or
```bash
./dvr 2 # Run with detailed tracing
```


## Trace Levels

| Level | Description                                      |
|-------|--------------------------------------------------|
| 0     | Minimal output: Final routing tables and key events |
| 1     | Basic tracing: Packet transmissions and table updates |
| 2     | Detailed tracing: Packet contents and decisions |
| 3     | Full debug: Internal steps and queuing details  |

**Note:** Higher trace levels provide more visibility into the simulation.

