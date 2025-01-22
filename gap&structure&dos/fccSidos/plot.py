import numpy as np
import matplotlib.pyplot as plt

# 定义文件路径
file_path = './dos.dat'

# 读取文件内容
with open(file_path, 'r') as file:
    dos_data = file.readlines()

# 过滤并解析数据
energy = []
dos = []

# 遍历每一行，跳过非数字或无效行
for line in dos_data:
    try:
        # 尝试将行分解为两个浮点数
        e, d = map(float, line.split())
        energy.append(e)
        dos.append(d)
    except ValueError:
        # 跳过无法解析为浮点数的行
        continue

# 将数据转换为 numpy 数组，方便后续处理
energy = np.array(energy)
dos = np.array(dos)

# 绘制 DOS 图像
plt.figure(figsize=(8, 6))
plt.plot(energy, dos, color='blue', lw=2)
plt.title("Density of States (DOS)", fontsize=16)
plt.xlabel("Energy (eV)", fontsize=14)
plt.ylabel("Density of States", fontsize=14)
plt.grid(True)
plt.tight_layout()

# 显示图像
plt.savefig('dos.png')
