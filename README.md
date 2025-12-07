# 箭头旋转动画生成器

一个使用 Python 和 matplotlib 生成旋转箭头动画的工具，支持导出为带透明背景的 MOV 格式视频。

## 功能特性

- 🎯 生成旋转箭头动画
- 🎨 支持自定义箭头大小、颜色等参数
- 🎬 导出为支持透明背景的 MOV 格式
- ⚙️ 使用面向对象设计，易于扩展和定制

## 安装要求

### Python 依赖

```bash
pip install matplotlib numpy
```

### 系统依赖

- **ffmpeg**: 用于合成 MOV 视频文件
  - Windows: 从 [ffmpeg官网](https://ffmpeg.org/download.html) 下载并添加到系统 PATH
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg` 或 `sudo yum install ffmpeg`

## 使用方法

### 基本使用

使用默认参数生成动画：

```python
from generateArrow import ArrowAnimationGenerator

generator = ArrowAnimationGenerator()
generator.run()
```

### 自定义参数

```python
from generateArrow import ArrowAnimationGenerator

# 创建生成器实例，自定义参数
generator = ArrowAnimationGenerator(
    arrow_size=150,        # 箭头长度（像素）
    arrow_width=60,        # 箭头头部宽度（像素）
    arrow_body_width=15,   # 箭头身体宽度（像素）
    arrow_color='blue',    # 箭头颜色
    width=600,             # 视频宽度（像素）
    height=600,            # 视频高度（像素）
    fps=30,                # 帧率
    duration=20.0,         # 视频时长（秒）
    frequency=0.5,         # 旋转频率（Hz，0.5表示每2秒转一圈）
    output_file='my_arrow.mov'  # 输出文件名
)

# 运行生成器
generator.run()
```

### 命令行使用

直接运行脚本：

```bash
python generateArrow.py
```

## API 文档

### ArrowAnimationGenerator 类

#### 构造函数

```python
ArrowAnimationGenerator(
    arrow_size: int = 100,
    arrow_width: int = 40,
    arrow_body_width: int = 10,
    arrow_color: str = 'red',
    width: int = 400,
    height: int = 400,
    fps: int = 30,
    duration: float = 20.0,
    frequency: float = 0.5,
    output_file: str = 'arrow_rotation.mov'
)
```

**参数说明：**

- `arrow_size` (int): 箭头长度（像素），默认 100
- `arrow_width` (int): 箭头头部宽度（像素），默认 40
- `arrow_body_width` (int): 箭头身体宽度（像素），默认 10
- `arrow_color` (str): 箭头颜色，默认 'red'（支持 matplotlib 颜色格式）
- `width` (int): 视频宽度（像素），默认 400
- `height` (int): 视频高度（像素），默认 400
- `fps` (int): 帧率，默认 30
- `duration` (float): 视频时长（秒），默认 20.0
- `frequency` (float): 旋转频率（Hz），默认 0.5（每 2 秒转一圈）
- `output_file` (str): 输出文件名，默认 'arrow_rotation.mov'

#### 主要方法

##### `run()`

执行完整的动画生成流程。生成 PNG 序列，使用 ffmpeg 合成 MOV 文件，并清理临时文件。

```python
generator.run()
```

**异常：**
- `RuntimeError`: 如果生成过程中出错（ffmpeg 不可用或合成失败）

##### `generate_frames(temp_dir: str)`

生成 PNG 图片序列。

**参数：**
- `temp_dir` (str): 临时目录路径

**异常：**
- `RuntimeError`: 如果生成帧时出错

##### `create_video(temp_dir: str)`

使用 ffmpeg 合成 MOV 文件。

**参数：**
- `temp_dir` (str): 临时目录路径（包含 PNG 序列）

**异常：**
- `RuntimeError`: 如果 ffmpeg 不可用或合成失败

##### `create_arrow_polygon(angle: float) -> np.ndarray`

创建箭头多边形，围绕偏移后的中心点旋转。

**参数：**
- `angle` (float): 旋转角度（弧度）

**返回：**
- `np.ndarray`: 旋转后的箭头顶点坐标数组

## 工作原理

1. **初始化**: 创建 matplotlib 图形和轴，设置透明背景
2. **生成帧**: 逐帧计算箭头旋转角度，生成 PNG 图片序列（支持透明通道）
3. **合成视频**: 使用 ffmpeg 的 `qtrle` 编码器将 PNG 序列合成为 MOV 文件
4. **清理**: 自动删除临时 PNG 文件

## 输出格式

- **视频格式**: MOV (QuickTime)
- **编码器**: qtrle (QuickTime Animation)
- **像素格式**: ARGB（支持透明通道）
- **背景**: 透明

## 注意事项

1. 确保已安装 ffmpeg 并添加到系统 PATH
2. 生成过程会创建临时目录存储 PNG 序列，完成后自动清理
3. 生成时间取决于视频时长和帧率（600 帧约需几分钟）
4. 输出文件会覆盖同名文件（如果存在）

## 示例

### 示例 1: 快速生成

```python
from generateArrow import ArrowAnimationGenerator

generator = ArrowAnimationGenerator()
generator.run()
```

### 示例 2: 自定义蓝色大箭头

```python
from generateArrow import ArrowAnimationGenerator

generator = ArrowAnimationGenerator(
    arrow_size=200,
    arrow_width=80,
    arrow_color='blue',
    duration=10.0,
    frequency=1.0  # 每秒转一圈
)
generator.run()
```

### 示例 3: 高分辨率慢速旋转

```python
from generateArrow import ArrowAnimationGenerator

generator = ArrowAnimationGenerator(
    width=800,
    height=800,
    fps=60,
    duration=30.0,
    frequency=0.25  # 每4秒转一圈
)
generator.run()
```

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

