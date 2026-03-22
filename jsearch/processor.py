"""视频处理核心模块"""
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


# 视频文件扩展名
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.rmvb', '.rm'}


class VideoNormalizer:
    """视频文件名称规范化器"""

    # 番号正则模式：2-5位字母 + 可选连字符 + 3位数字
    PATTERN = r'([A-Za-z]{2,5})-?(\d{3})'
    # 默认存储路径
    DEFAULT_STORAGE_PATH = os.path.expanduser("~/.jsearch/prefixes.json")

    def __init__(self, storage_path: str = None):
        """
        初始化规范化器

        :param storage_path: 前缀存储文件路径
        """
        self.storage_path = storage_path or self.DEFAULT_STORAGE_PATH
        # 记录已解析的英文前缀及其出现次数
        self.prefix_counter: Counter = Counter()
        # 当前已确认的前缀（出现次数>=2的）
        self.confirmed_prefixes: set[str] = set()
        self._load_prefixes()

    def _load_prefixes(self):
        """从文件加载已确认的前缀"""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.confirmed_prefixes = set(data.get('confirmed_prefixes', []))
                self.prefix_counter = Counter(data.get('prefix_counter', {}))
            logger.info(f"加载已确认前缀: {self.confirmed_prefixes}")
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"加载前缀文件失败: {e}")

    def save_prefixes(self):
        """保存已确认的前缀到文件"""
        # 确保目录存在
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        data = {
            'confirmed_prefixes': list(self.confirmed_prefixes),
            'prefix_counter': dict(self.prefix_counter)
        }

        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"保存已确认前缀: {self.confirmed_prefixes}")
        except OSError as e:
            logger.warning(f"保存前缀文件失败: {e}")

    def extract_code(self, filename: str) -> Optional[str]:
        """
        从文件名中提取番号

        :param filename: 文件名（不含路径和扩展名）
        :return: 规范化后的番号（大写），如 "FSDSS-533"
        """
        # 1. 先尝试使用已确认的前缀匹配
        for prefix in self.confirmed_prefixes:
            pattern = rf'\b{prefix}-?(\d{{3}})\b'
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return f"{prefix.upper()}-{match.group(1)}"

        # 2. 通用模式匹配
        match = re.search(self.PATTERN, filename)
        if match:
            prefix = match.group(1).upper()
            number = match.group(2)
            code = f"{prefix}-{number}"

            # 更新前缀计数
            self.prefix_counter[prefix] += 1
            if self.prefix_counter[prefix] >= 2:
                self.confirmed_prefixes.add(prefix)

            return code

        return None

    def is_normalized(self, filename: str) -> bool:
        """
        检查文件名是否已规范化

        :param filename: 文件名（不含路径和扩展名）
        :return: 是否符合标准格式（大写字母+连字符+3位数字）
        """
        pattern = r'^[A-Z]{2,5}-\d{3}$'
        return bool(re.match(pattern, filename))

    def normalize(self, file_path: str) -> Optional[str]:
        """
        规范化视频文件名

        :param file_path: 原文件路径
        :return: 规范化后的文件路径，如果已规范化则返回None
        """
        path = Path(file_path)
        stem = path.stem  # 文件名不含扩展名
        suffix = path.suffix  # 扩展名

        # 检查是否已规范化
        if self.is_normalized(stem):
            return None

        # 提取番号
        code = self.extract_code(stem)
        if not code:
            logger.warning(f"无法从文件名提取番号: {stem}")
            return None

        # 生成新文件名
        new_stem = code
        new_path = path.parent / f"{new_stem}{suffix}"

        # 重命名
        try:
            path.rename(new_path)
            logger.info(f"重命名: {path.name} -> {new_path.name}")
            return str(new_path)
        except (OSError, PermissionError) as e:
            logger.error(f"重命名失败 {path.name}: {e}")
            return None


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
            if len(videos) > limit:
                break
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() not in VIDEO_EXTENSIONS:
                    continue

                try:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    if size_mb >= self.min_size_mb:
                        videos.append((str(file_path), int(size_mb)))
                    if len(videos) > limit:
                        print("已发现所有电影")
                        break
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
        self.normalizer = VideoNormalizer()

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

        # 规范化文件名
        normalized_videos = []
        for path, size in videos:
            new_path = self.normalizer.normalize(path)
            normalized_path = new_path if new_path else path
            normalized_videos.append((normalized_path, size))

        # 处理视频
        for path, size in normalized_videos:
            logger.info(f"\n正在处理: {path} ({size}MB)")
            try:
                processor.process(path, output_dir=self.output_dir)
                logger.info(f"处理成功: {path} -> 输出目录: {self.output_dir}")
            except Exception as e:
                logger.error(f"处理失败: {path}, 错误: {e}")
                continue

        # 保存确认的前缀
        self.normalizer.save_prefixes()
