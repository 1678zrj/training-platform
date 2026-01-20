import os
import shutil

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from fastapi import HTTPException
from app.crud import crud_experiment
from app.models.lab import Experiment, Container, Image
from app.services.docker_service import DockerService


class ContainerService:
    @staticmethod
    def get_or_create_container(session: Session, user_id: int, exp_id: int) -> Container:
        # 1. 检查是否已有的容器操作记录
        statement = select(Container).where(
            Container.user_id == user_id,
            Container.experiment_id == exp_id,
        )
        container = session.exec(statement).first()

        # 如果数据库表中有记录
        if container:
            if container.status == "deleting":
                raise HTTPException(
                    status_code=409,
                    detail="容器正在被销毁中，请稍后重试"
                )
            return container
        container = Container(
            user_id=user_id,
            experiment_id=exp_id,
            status="creating"
        )
        try:
            session.add(container)
            session.commit()
            session.refresh(container)
        except IntegrityError:
            session.rollback()
            container = session.exec(
                select(Container)
                .where(
                    Container.user_id == user_id,
                    Container.experiment_id == exp_id
                )
            ).one()
            if container.status == "deleting":
                raise HTTPException(
                    status_code=409,
                    detail="容器正在销毁中，请稍后重试"
                )
            return container
        # 占位成功后启动docker
        container_id_created = None
        try:

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
            host_dataset_dir = os.path.join(os.getcwd(), "media", "datasets")

            # 4. 调用 DockerService 启动

            docker_info = DockerService.run_container(
                image_tag=image.docker_tag,
                user_id=user_id,
                exp_id=exp_id,
                cpu_limit=experiment.cpu_limit,
                mem_limit=experiment.memory_limit,
                use_gpu=experiment.use_gpu,
                host_work_dir=base_path,
                host_dataset_dir=host_dataset_dir,
                container_work_dir=image.work_dir,
                gpu_device_ids=experiment.gpu_device_ids
            )
            container_id_created = docker_info["container_id"]

            #  行锁校验
            locked = session.exec(
                select(Container)
                .where(
                    Container.id==container.id
                ).with_for_update()
            ).first()
            if not locked or locked.status == "deleting":
                raise RuntimeError("容器在创建过程中有删除操作，因此中断")
            locked.container_id = docker_info["container_id"]
            locked.host_port = docker_info["host_port"]
            locked.url_token = docker_info["url_token"]
            locked.base_url = docker_info["base_url"]
            locked.status = "running"
            session.add(locked)
            session.commit()
            session.refresh(locked)
            return locked
        except Exception:
            if container_id_created:
                DockerService.stop_remove_container(container_id_created)
            try:
                stale = session.get(Container,container.id)
                if stale and stale.status == "creating":
                    session.delete(stale)
                    session.commit()
            except Exception:
                session.rollback()
            raise


    @staticmethod
    def stop_experiment(session: Session, user_id: int, exp_id: int):
        # ---------- 1. 加锁读取 ----------
        container = session.exec(
            select(Container)
            .where(
                Container.user_id == user_id,
                Container.experiment_id == exp_id
            )
            .with_for_update()
        ).first()

        if not container:
            return {"message": "No container found"}

        # ---------- 2. 状态机 ----------
        if container.status == "deleting":
            return {"message": "Already deleting"}

        if container.status == "creating":
            # 让创建线程负责补偿
            container.status = "deleting"
            session.add(container)
            session.commit()
            return {"message": "Marked for deletion during creation"}

        # ---------- 3. running / stopped ----------
        container.status = "deleting"
        session.add(container)
        session.commit()

        # ---------- 4. Docker 删除 ----------
        if container.container_id:
            DockerService.stop_remove_container(container.container_id)

        # ---------- 5. DB 删除 ----------
        row = session.exec(
            select(Container).where(Container.id == container.id)
        ).first()

        if row:
            session.delete(row)
            session.commit()

        return {"message": "Deleted successfully"}

    @staticmethod
    def reset_workspace(session: Session, user_id: int, exp_id: int):
        """
        重置实验环境：
        1. 检查约束：必须没有运行中的容器记录
        2. 删除用户的挂载目录
        3. 重新从模板复制文件
        """
        # 1. 【约束检查】数据库中不能有记录
        existing = session.exec(
            select(Container).where(
                Container.user_id == user_id,
                Container.experiment_id == exp_id
            )
        ).first()

        if existing:
            # 如果有记录（无论是 creating, running 还是 deleting），都不允许重置
            # 必须要求用户先点“结束实验”彻底清理掉
            raise HTTPException(
                status_code=400,
                detail="请先结束当前实验，确容器已停止后再重置环境"
            )

        # 2. 获取实验配置 (为了拿到 template_path)
        experiment = session.get(Experiment, exp_id)
        if not experiment:
            raise HTTPException(status_code=404, detail="实验不存在")

        # 3. 确定路径
        # 基础路径: data/workspace/u{user_id}/e{exp_id}
        base_work_path = os.path.join(os.getcwd(), "media", "workspace", f"u{user_id}", f"e{exp_id}")

        # 模板路径 (注意处理开头的 /)
        template_path = None
        if experiment.template_path:
            template_path = os.path.join(os.getcwd(), "media", "template", experiment.template_path.lstrip("/"))

        try:
            # 4. 【危险操作】删除现有目录
            if os.path.exists(base_work_path):
                shutil.rmtree(base_work_path)

            # 5. 【恢复】重新创建目录并复制模板
            # 如果有模板，复制模板；如果没有模板，只创建一个空文件夹
            if template_path and os.path.exists(template_path):
                shutil.copytree(template_path, base_work_path)
            else:
                os.makedirs(base_work_path, exist_ok=True)

            return {"message": "环境已重置，您可以重新开始实验"}

        except Exception as e:
            # 文件操作失败（比如权限问题）
            print(f"Reset workspace error: {e}")
            raise HTTPException(status_code=500, detail="重置文件系统失败，请联系管理员")