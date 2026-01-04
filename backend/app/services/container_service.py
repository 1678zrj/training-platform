import os
import shutil
from sqlmodel import Session, select
from fastapi import HTTPException
from app.crud import crud_experiment
from app.models.lab import Experiment, Container, Image
from app.services.docker_service import DockerService


class ContainerService:
    @staticmethod
    def get_or_create_container(session: Session, user_id: int, exp_id: int) -> Container:
        # 1. 检查是否已有运行中的容器
        statement = select(Container).where(
            Container.user_id == user_id,
            Container.experiment_id == exp_id,
            Container.status == "running"
        )
        existing_container = session.exec(statement).first()

        # 如果容器还在，直接返回（实现“断点续做”）
        if existing_container:
            # 这里可以加一步 check_container_alive(existing_container.container_id)
            # 如果 Docker 里其实已经死掉了，应该在这里删库并重建
            return existing_container

        # 2. 获取实验和镜像信息
        experiment = session.get(Experiment, exp_id)
        if not experiment:
            raise HTTPException(status_code=404, detail="实验不存在")

        # 需要联表查询 Image 表获取 tag
        image = session.get(Image, experiment.image_id)
        if not image:
            raise HTTPException(status_code=404, detail="镜像未定义")

        # 3. 准备宿主机挂载目录
        # 路径结构: media/workspace/user_{id}/exp_{id}
        base_path = os.path.join(os.getcwd(), "media", "workspace", f"u{user_id}", f"e{exp_id}")
        os.makedirs(base_path, exist_ok=True)

        # [可选] 如果目录是空的，从 template_path 复制代码模板进去
        if not os.listdir(base_path) and experiment.template_path:
            template_src = os.path.join(os.getcwd(), "media", "template",experiment.template_path.lstrip("/"))
            if os.path.exists(template_src):
                # 复制所有文件到学生目录
                shutil.copytree(template_src, base_path, dirs_exist_ok=True)

        # 4. 调用 DockerService 启动
        try:
            docker_info = DockerService.run_container(
                image_tag=image.docker_tag,
                user_id=user_id,
                exp_id=exp_id,
                cpu_limit=experiment.cpu_limit,
                mem_limit=experiment.memory_limit,
                use_gpu=experiment.use_gpu,
                host_work_dir=base_path,
                container_work_dir=image.work_dir
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"容器启动失败: {str(e)}")

        # 5. 存入数据库
        new_container = Container(
            user_id=user_id,
            experiment_id=exp_id,
            container_id=docker_info["container_id"],
            host_port=docker_info["host_port"],
            url_token=docker_info["url_token"],
            status="running"
        )
        session.add(new_container)
        session.commit()
        session.refresh(new_container)

        return new_container

    @staticmethod
    def stop_experiment(session: Session, user_id: int, exp_id: int):
        """
        停止实验：清理Docker资源 + 删除数据库记录
        """
        # 1. 查数据库找容器记录
        statement = select(Container).where(
            Container.user_id == user_id,
            Container.experiment_id == exp_id
        )
        container_record = session.exec(statement).first()

        if not container_record:
            # 只有记录不存在，说明本来就没在跑，直接返回成功
            return {"message": "实验未运行"}

        # 2. 调用 DockerService 清理物理容器
        # 即使数据库有记录，Docker里可能已经被意外删了，所以这里要做容错
        try:
            DockerService.stop_remove_container(container_record.container_id)
        except Exception as e:
            # 记录日志但不要崩溃，继续清理数据库，否则产生死数据
            print(f"警告: Docker清理异常，但这可能不影响数据库清理. {e}")

        # 3. 删除数据库中的 Container 记录
        # 注意：这里我们只删 Container 表，UserLab 表的状态保留或更新，不删 UserLab
        session.delete(container_record)
        session.commit()

        return {"message": "实验已停止，资源已释放"}