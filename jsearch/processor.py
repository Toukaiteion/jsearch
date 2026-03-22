"""视频处理核心模块"""
import os
from pathlib import Path
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


# 视频文件扩展名
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.rmvb', '.rm'}


class VideoFinder:
    """视频文件查找器"""

    def __init__(self, min_size_mb: int = 1024):
        """
        初始化查找器

        :param min_size_mb: 最小文件大小（MB）
        """
        self.min_size_mb = min_size_mb

    def find_videos(self, directory: str, limit: int = 3) -> List[Tuple[str, int]]:
        """
        查找目录下大于指定大小的视频文件

        :param directory: 搜索目录
        :param limit: 返回数量限制
        :return: (文件路径, 大小MB) 的列表
        """
        videos = []
        dir_path = Path(directory)

        if not dir_path.exists():
            logger.error(f"目录不存在: {directory}")
            return videos

        if not dir_path.is_dir():
            logger.error(f"路径不是目录: {directory}")
            return videos

        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() not in VIDEO_EXTENSIONS:
                    continue

                try:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    if size_mb >= self.min_size_mb:
                        videos.append((str(file_path), int(size_mb)))
                except (OSError, PermissionError) as e:
                    logger.warning(f"无法读取文件 {file_path}: {e}")

        # 按大小降序排序，取前N个
        videos.sort(key=lambda x: x[1], reverse=True)
        return videos[:limit]


class VideoProcessor:
    """视频处理器"""

    def __init__(self, min_size_mb: int = 1024, limit: int = 3, output_dir: str = "output"):
        """
        初始化处理器

        :param min_size_mb: 最小文件大小（MB）
        :param limit: 处理数量限制
        :param output_dir: 输出目录
        """
        self.min_size_mb = min_size_mb
        self.limit = limit
        self.output_dir = output_dir
        self.finder = VideoFinder(min_size_mb)

    def process_directory(self, directory: str):
        """
        处理目录下的视频文件

        :param directory: 输入目录
        """
        logger.info(f"开始扫描目录: {directory}")
        logger.info(f"过滤条件: 大于 {self.min_size_mb}MB, 取前 {self.limit} 个")

        videos = self.finder.find_videos(directory, self.limit)

        if not videos:
            logger.warning("未找到符合条件的视频文件")
            return

        logger.info(f"找到 {len(videos)} 个视频文件:")
        for i, (path, size) in enumerate(videos, 1):
            logger.info(f"  {i}. {path} ({size}MB)")

        self._process_videos(videos)

    def _process_videos(self, videos: List[Tuple[str, int]]):
        """
        使用 jcatch 处理视频文件

        :param videos: (文件路径, 大小MB) 的列表
        """
        try:
            from jcatch.core import MediaProcessor
            from jcatch.scrapers import JavBusScraper
        except ImportError:
            logger.error("未找到 jcatch 库，请先安装: pip install jcatch")
            return

        scraper = JavBusScraper()
        processor = MediaProcessor(scraper)

        for path, size in videos:
            logger.info(f"\n正在处理: {path} ({size}MB)")
            try:
                processor.process(path, output=self.output_dir)
                logger.info(f"处理成功: {path} -> 输出目录: {self.output_dir}")
            except Exception as e:
                logger.error(f"处理失败: {path}, 错误: {e}")
                continue
