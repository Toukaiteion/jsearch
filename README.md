# jsearch

视频文件搜索和处理工具。

## 功能

- 递归搜索目录下所有视频文件
- 按文件大小筛选（默认大于1G）
- 取前N个文件进行处理（默认3个）
- 调用 jcatch 处理视频元数据

## 安装

```bash
pip install -e .
```

## 使用

```bash
# 基本用法
jsearch /path/to/videos

# 指定最小文件大小
jsearch /path/to/videos --min-size 2G
jsearch /path/to/videos --min-size 500M

# 指定处理数量
jsearch /path/to/videos --limit 5

# 指定输出目录
jsearch /path/to/videos --output ./processed

# 组合使用
jsearch /path/to/videos --min-size 2G --limit 5 --output ./output
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `directory` | 搜索目录 | 必填 |
| `-m, --min-size` | 最小文件大小 | 1G |
| `-l, --limit` | 处理数量限制 | 3 |
| `-o, --output` | 输出目录 | output |
| `-v, --verbose` | 详细日志 | false |

## 支持的视频格式

mp4, mkv, avi, mov, wmv, flv, webm, m4v, ts, rmvb, rm
