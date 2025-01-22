#!/bin/bash

# 定义需要保留的文件名数组
keep_files=("INCAR1" "INCAR2" "INCAR3" "clear.sh" "gap_GW.sh" "run.sh" "POSCAR" "POTCAR" "KPOINTS")

# 获取当前目录下的所有文件
for file in *; do
  # 检查文件是否在保留列表中
  keep=false
  for keep_file in "${keep_files[@]}"; do
    if [[ $file == $keep_file || $file == *.json ]]; then
      keep=true
      break
    fi
  done
  
  # 如果文件不在保留列表中，删除文件
  if [ "$keep" = false ] && [ -f "$file" ]; then
    rm "$file"  # 删除文件
    echo "Deleted: $file"
  fi
done
