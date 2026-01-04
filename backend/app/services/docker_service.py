import docker
import socket
import os
from contextlib import closing
from docker.types import DeviceRequest


class DockerService:
    client = docker.from_env()

    @staticmethod
    def find_free_port() -> int:
        """寻找一个可用的宿主机端口 (用于映射 Jupyter)"""
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    @staticmethod
    def run_container(
            image_tag: str,
            user_id: int,
            exp_id: int,
            cpu_limit: float,
            mem_limit: str,
            use_gpu: bool,
            host_work_dir: str,  # 宿主机挂载路径
            container_work_dir: str = "/workspace"  # 容器内路径
    ) -> dict:
        """
        启动容器的核心逻辑
        """
        # 1. 准备端口和 Token
        host_port = DockerService.find_free_port()
        token = os.urandom(16).hex()  # 生成随机 Token 用于 Jupyter 安全验证

        # 2. 准备 GPU 配置
        device_requests = []
        if use_gpu:
            # 请求所有 GPU (需安装 nvidia-container-toolkit)
            device_requests.append(DeviceRequest(count=-1, capabilities=[['gpu']]))

        # 3. 启动容器
        try:
            container = DockerService.client.containers.run(
                image=image_tag,
                detach=True,
                # 端口映射: 容器8888 -> 宿主机随机端口
                ports={'8888/tcp': host_port},
                # 挂载目录: 保证学生代码重启不丢
                volumes={host_work_dir: {'bind': container_work_dir, 'mode': 'rw'}},
                # 资源限制
                nano_cpus=int(cpu_limit * 1e9),  # docker sdk 单位是纳秒
                mem_limit=mem_limit,
                device_requests=device_requests,
                # 环境变量 (设置 Jupyter Token)
                environment={
                    "JUPYTER_TOKEN": token,
                    "NB_UID": 1000  # 避免权限问题，通常设为 1000
                },
                working_dir=container_work_dir,
                # 命名规范: user_1_exp_101
                name=f"u{user_id}_e{exp_id}",
                # 自动重启策略
                restart_policy={"Name": "on-failure", "MaximumRetryCount": 3}
            )

            return {
                "container_id": container.id,
                "host_port": host_port,
                "url_token": token
            }
        except Exception as e:
            print(f"Docker启动失败: {e}")
            raise e

    @staticmethod
    def stop_remove_container(container_id: str):
        """
        停止并删除容器
        """
        try:
            # 获取容器对象
            container = DockerService.client.containers.get(container_id)

            # 停止容器 (如果正在运行)
            # timeout=1 表示给1秒时间让进程自己退出，然后强制kill，加快速度
            container.stop(timeout=1)

            # 删除容器 (remove 也会清理掉匿名卷，但不会删掉我们要的 bind mount)
            container.remove()

            print(f"容器 {container_id} 已清理")
            return True
        except docker.errors.NotFound:
            print(f"容器 {container_id} 已经在Docker中不存在了")
            return False  # 容器本来就不在，也算成功
        except Exception as e:
            print(f"停止容器失败: {e}")
            raise e