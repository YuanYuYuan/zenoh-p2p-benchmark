# Zenoh Peer-to-peer Benchmark

## Prerequisites

1. Build Rust source code for running the benchmark.

```
cargo build --release
```

2. Install Python dependencies for plotting the results.

```
pip3 install -r ./requirements.txt
```

## Usage

```
./run-benchmark.sh
```

The results will be stored at the directory `results`.

```
results
├── 1
│   ├── log.txt        <-- Full log of Rust exectuion
│   ├── result.json    <-- Experiment result, e.g. delivery_ratio, average_time
│   │                      Not presented if the exp failed on this setting
│   └── usage.txt      <-- CPU & memory usage
├── 10
│   ├── log.txt
│   ├── result.json
│   └── usage.txt
...
```

## Results

TBA
