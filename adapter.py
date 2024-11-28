import subprocess

class adapter:
    def __init__(self, cwd, env):
        self.cwd = cwd
        self.env = env

    def run_command(self, command):
        print(f"This step launches a command: {command}")

        # 构建 Conda run 命令
        full_command = [
            "/gpfs/junlab/xiazeyu21/miniconda3/condabin/conda",  # Conda 路径
            "run", "-n", self.env,  # 使用指定的 Conda 环境
            "bash", "-c", f"cd {self.cwd} && {command}"  # 切换到指定工作目录并执行命令
        ]

        # 执行命令并捕获输出
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True  # 获取标准输出/错误的文本格式
        )
        
        # 输出结果
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        return result.returncode, result.stdout if result.returncode == 0 else result.stderr
