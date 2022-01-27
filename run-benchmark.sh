#!/usr/bin/env bash

# resovle too many file opened issue
ulimit -n 100000

timeout=20

exp_dir="results"
min_n_peers=1
max_n_peers=40
for n_peers in $(seq $min_n_peers $max_n_peers); do
    out_dir="${exp_dir}/${n_peers}"
    exe="export RUST_LOG=info && ./target/release/zenoh-p2p-benchmark --n-peers $n_peers --output-dir $out_dir 2>&1 | tee ${out_dir}/log.txt"
    mkdir -p $out_dir
    psrecord "$exe" \
        --log ${out_dir}/usage.txt \
        --include-children \
        --duration $timeout
    pkill zenoh-p2p-benchmark
    sleep 1
done
