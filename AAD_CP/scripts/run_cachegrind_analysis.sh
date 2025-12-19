#!/bin/bash
# Run cachegrind analysis on all algorithms

cd /home/arnav-agnihotri/Downloads/AAD_CP

echo "Running Valgrind Cachegrind Analysis"
echo "====================================="
echo ""

for algo in p1 p2 p4 p5; do
  echo "Analyzing: $algo"
  echo "-----------------------------------"
  
  # Run cachegrind
  valgrind --tool=cachegrind \
           --branch-sim=yes \
           --cache-sim=yes \
           --cachegrind-out-file=cachegrind_${algo}.out \
           ./codes/$algo < dataset/large/large_01.txt > /dev/null 2>&1
  
  echo "Results for $algo:"
  # Extract key metrics
  cg_annotate cachegrind_${algo}.out 2>/dev/null | head -30 | grep -E "I refs|I1 misses|LLi misses|D refs|D1 misses|LLd misses|Branches|Mispredicts"
  echo ""
done

echo "====================================="
echo "Detailed reports saved to cachegrind_*.out"
echo "View with: cg_annotate cachegrind_p1.out"
