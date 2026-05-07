"""命令行入口模块"""
import argparse
import logging
from pathlib import Path
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
        default=str(Path.cwd()),
        help="输出目录 (默认: 当前目录)"
    )

    headless_group = parser.add_mutually_exclusive_group()
    headless_group.add_argument(
        "-H", "--headless",
        action="store_true",
        dest="headless",
        help="无头模式"
    )
    headless_group.add_argument(
        "--no-headless",
        action="store_false",
        dest="headless",
        help="关闭无头模式"
    )
    # 设置默认值为开启无头模式
    parser.set_defaults(headless=True)

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细日志"
    )

    parser.add_argument(
        "-c", "--chromedriver-path",
        default=None,
        help="ChromeDriver 路径"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 打印参数配置
    print("\n" + "="*50)
    print("参数配置:")
    print("="*50)
    print(f"  目录: {args.directory}")
    print(f"  最小文件大小: {args.min_size}MB")
    print(f"  处理数量限制: {args.limit}")
    print(f"  输出目录: {args.output}")
    print(f"  无头模式: {args.headless}")
    print(f"  ChromeDriver 路径: {args.chromedriver_path if args.chromedriver_path else '默认'}")
    print(f"  详细日志: {args.verbose}")
    print("="*50 + "\n")

    processor = VideoProcessor(
        min_size_mb=args.min_size,
        limit=args.limit,
        output_dir=args.output,
        headless=args.headless,
        chromedriver_path=args.chromedriver_path
    )

    processor.process_directory(args.directory)


if __name__ == "__main__":
    main()
