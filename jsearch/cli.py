"""命令行入口模块"""
import argparse
import logging
from jsearch.processor import VideoProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def parse_size(size_str: str) -> int:
    """
    解析大小字符串为MB

    支持格式: 1G, 1024M, 1073741824
    """
    size_str = size_str.strip().upper()

    if size_str.endswith('G'):
        return int(size_str[:-1]) * 1024
    elif size_str.endswith('M'):
        return int(size_str[:-1])
    elif size_str.endswith('K'):
        return int(size_str[:-1]) // 1024
    else:
        # 默认为MB
        return int(size_str)


def main():
    parser = argparse.ArgumentParser(
        description="视频文件搜索和处理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  jsearch /path/to/videos
  jsearch /path/to/videos --min-size 2G
  jsearch /path/to/videos --min-size 500M --limit 5
  jsearch /path/to/videos --output ./processed
        """
    )

    parser.add_argument(
        "directory",
        help="要搜索的目录路径"
    )

    parser.add_argument(
        "-m", "--min-size",
        default="1G",
        type=parse_size,
        help="最小文件大小 (默认: 1G)，支持格式: 1G, 500M, 1024 (MB)"
    )

    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=3,
        help="处理文件数量限制 (默认: 3)"
    )

    parser.add_argument(
        "-o", "--output",
        default="output",
        help="输出目录 (默认: output)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细日志"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    processor = VideoProcessor(
        min_size_mb=args.min_size,
        limit=args.limit,
        output_dir=args.output
    )

    processor.process_directory(args.directory)


if __name__ == "__main__":
    main()
