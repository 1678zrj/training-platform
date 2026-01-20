import secrets

import docker
import socket
import os
from contextlib import closing
from docker.types import DeviceRequest


class DockerService:
    client = docker.from_env()
    NETWORK_NAME = "jupyter-bridge-net"
    # @staticmethod
    # def find_free_port() -> int:
    #     """寻找一个可用的宿主机端口 (用于映射 Jupyter)"""
    #     with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
    #         s.bind(('', 0))
    #         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #         return s.getsockname()[1]

    @staticmethod
    def run_container(
            image_tag: str,
            user_id: int,
            exp_id: int,
            cpu_limit: float,
            mem_limit: str,
            use_gpu: bool,
            host_work_dir: str,  # 宿主机挂载路径
            host_dataset_dir: str, # 宿主机公共数据集挂载路径
            container_work_dir: str = "/home/jovyan/work",  # 容器内路径
            container_dataset_dir: str = "/datasets",
            gpu_device_ids: str = None # GPU的分配
    ) -> dict:

        container = None

        """
        启动容器的核心逻辑
        """
        # 1. 准备端口和 Token
        # host_port = DockerService.find_free_port()
        container_name = f"u{user_id}_e{exp_id}"

        base_url_path = f"/lab/{container_name}"

        token = os.urandom(16).hex()  # 生成随机 Token 用于 Jupyter 安全验证
        # 【新增】生成唯一的 Base URL 路径

        # 2. 准备 GPU 配置
        device_requests = []
        if use_gpu and gpu_device_ids:
            # 请求所有 GPU (需安装 nvidia-container-toolkit)
            if gpu_device_ids=="all":
                device_requests.append(DeviceRequest(count=-1, capabilities=[['gpu']]))
            else:
                gpu_ids = [id_.strip() for id_ in gpu_device_ids.split(",") if id_.strip()]
                device_requests.append(
                    DeviceRequest(
                        device_ids=gpu_ids,
                        capabilities=[['gpu']]
                    )
                )
        volumes = {
            # 用户实验目录（读写）
            host_work_dir: {
                'bind': container_work_dir,
                'mode': 'rw'
            },
            # 公共数据集（只读）
            host_dataset_dir: {
                'bind': container_dataset_dir,
                'mode': 'ro'
            }
        }

        # 3. 构造 Jupyter 启动命令
        # 核心修改点：显式指定启动命令，注入允许 iframe 的 Header 配置
        # 注意：这会覆盖 Dockerfile 中的 CMD
        jupyter_cmd = [
            "jupyter", "lab",
            "--ip=0.0.0.0",  # 监听所有 IP，Docker 必须
            "--port=8888",  # 容器内部端口
            "--no-browser",  # 不自动打开浏览器
            "--allow-root",  # 允许 root 运行（防止部分容器报错）
            "--ServerApp.token=" + token,  # 显式指定 Token
            "--ServerApp.allow_origin='*'",  # 允许跨域
            f"--ServerApp.base_url={base_url_path}/",
            # "--ServerApp.allow_remote_access=True",  # 必选：允许 nip.io 访问
            # 下面这一行是解决“拒绝连接/拒绝嵌入”的关键：
            "--ServerApp.tornado_settings={'headers': {'Content-Security-Policy': 'frame-ancestors *', 'Access-Control-Allow-Origin': '*'}}",
            f"--ServerApp.cookie_options={{'path': '{base_url_path}/'}}"
        ]
        # 4. 启动容器
        try:
            container = DockerService.client.containers.create(
                image=image_tag,
                detach=True,
                network=DockerService.NETWORK_NAME,
                # 传入我们构造的带参数的启动命令
                command=jupyter_cmd,
                # 端口映射: 容器8888 -> 宿主机随机端口
                # ports={'8888/tcp': host_port},
                # 改成这样确保只有本机才能够访问容器
                ports={'8888/tcp': ('127.0.0.1', 0)},
                # 挂载目录: 保证学生代码重启不丢
                volumes=volumes,
                # 资源限制
                nano_cpus=int(cpu_limit * 1e9),  # docker sdk 单位是纳秒
                mem_limit=mem_limit,
                device_requests=device_requests,
                # 环境变量 (设置 Jupyter Token)
                environment={
                    # "JUPYTER_TOKEN": token,
                    "NB_UID": 1000  # 避免权限问题，通常设为 1000
                },
                working_dir=container_work_dir,
                # 命名规范: user_1_exp_101
                name=container_name,
                # 自动重启策略
                restart_policy={"Name": "on-failure", "MaximumRetryCount": 3}
            )
            container_id = container.id  # ✅ 此时已确定

            # 2️⃣ start（若失败，容器仍可 remove）
            container.start()

            # 3️⃣ inspect / reload
            container.reload()
            host_port = int(
                container.attrs["NetworkSettings"]["Ports"]["8888/tcp"][0]["HostPort"]
            )
            return {
                "container_id": container.id,
                "host_port": host_port,
                "url_token": token,
                "base_url": base_url_path  # 【新增】返回这个路径给前端
            }
        except Exception as e:
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
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



