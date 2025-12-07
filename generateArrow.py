"""
箭头旋转动画生成器

使用matplotlib生成旋转箭头动画，并导出为支持透明背景的MOV格式视频。
通过生成PNG序列并使用ffmpeg合成，确保透明通道的完整性。
"""

import os
import shutil
import subprocess
import tempfile

import matplotlib.animation as animation
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np


class ArrowAnimationGenerator:
    """箭头旋转动画生成器类
    
    生成一个旋转的箭头动画，并导出为支持透明背景的MOV格式视频。
    
    Attributes:
        arrow_size (int): 箭头长度（像素），默认100
        arrow_width (int): 箭头头部宽度（像素），默认40
        arrow_body_width (int): 箭头身体宽度（像素），默认10
        arrow_color (str): 箭头颜色，默认'red'
        width (int): 视频宽度（像素），默认400
        height (int): 视频高度（像素），默认400
        fps (int): 帧率，默认30
        duration (float): 视频时长（秒），默认20
        frequency (float): 旋转频率（Hz），默认0.5（每2秒转一圈）
        output_file (str): 输出文件名，默认'arrow_rotation.mov'
    """
    
    def __init__(
        self,
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
    ):
        """初始化箭头动画生成器
        
        Args:
            arrow_size: 箭头长度（像素）
            arrow_width: 箭头头部宽度（像素）
            arrow_body_width: 箭头身体宽度（像素）
            arrow_color: 箭头颜色
            width: 视频宽度（像素）
            height: 视频高度（像素）
            fps: 帧率
            duration: 视频时长（秒）
            frequency: 旋转频率（Hz），0.5表示每2秒转一圈
            output_file: 输出文件名
        """
        # 箭头参数
        self.arrow_size = arrow_size
        self.arrow_width = arrow_width
        self.arrow_body_width = arrow_body_width
        self.arrow_color = arrow_color
        
        # 视频参数
        self.width = width
        self.height = height
        self.fps = fps
        self.duration = duration
        self.frequency = frequency
        self.output_file = output_file
        
        # 计算总帧数
        self.total_frames = int(self.fps * self.duration)
        
        # 旋转中心偏移（向尾端偏移10%）
        self.rotation_offset = -self.arrow_size * 0.1
        
        # matplotlib对象
        self.fig = None
        self.ax = None
        self.arrow_polygon = None
        self.anim = None
        
        # 初始化图形
        self._init_figure()
    
    def _init_figure(self):
        """初始化matplotlib图形和轴"""
        self.fig, self.ax = plt.subplots(
            figsize=(self.width/100, self.height/100),
            dpi=100
        )
        
        # 设置背景透明
        self.fig.patch.set_facecolor('none')
        self.ax.set_facecolor('none')
        
        # 设置坐标轴范围
        self.ax.set_xlim(-self.width/2, self.width/2)
        self.ax.set_ylim(-self.height/2, self.height/2)
        self.ax.set_aspect('equal')
        self.ax.axis('off')  # 隐藏坐标轴
    
    def create_arrow_polygon(self, angle: float) -> np.ndarray:
        """创建箭头多边形，围绕偏移后的中心点旋转
        
        Args:
            angle: 旋转角度（弧度）
            
        Returns:
            旋转后的箭头顶点坐标数组
        """
        # 头部结束位置（y坐标）
        head_end_y = self.arrow_size / 2 - self.arrow_width
        
        # 定义箭头形状的顶点（中心在原点，头部在y轴正方向）
        arrow_points = np.array([
            [0, self.arrow_size/2 - self.rotation_offset],  # 箭头尖端
            [-self.arrow_width/2, self.arrow_size/2 - self.arrow_width - self.rotation_offset],  # 左翼
            [-self.arrow_width/4, self.arrow_size/2 - self.arrow_width - self.rotation_offset],  # 左翼内侧
            [-self.arrow_body_width/2, head_end_y - self.rotation_offset],  # 左身体起点
            [-self.arrow_body_width/2, -self.arrow_size/2 - self.rotation_offset],  # 左尾部
            [self.arrow_body_width/2, -self.arrow_size/2 - self.rotation_offset],  # 右尾部
            [self.arrow_body_width/2, head_end_y - self.rotation_offset],  # 右身体起点
            [self.arrow_width/4, self.arrow_size/2 - self.arrow_width - self.rotation_offset],  # 右翼内侧
            [self.arrow_width/2, self.arrow_size/2 - self.arrow_width - self.rotation_offset],  # 右翼
        ])
        
        # 旋转矩阵（顺时针旋转）
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        rotation_matrix = np.array([[cos_a, sin_a], [-sin_a, cos_a]])
        
        # 应用旋转
        rotated_points = arrow_points @ rotation_matrix.T
        
        return rotated_points
    
    def animate(self, frame: int) -> list:
        """动画更新函数
        
        Args:
            frame: 当前帧号
            
        Returns:
            更新的图形元素列表
        """
        # 清除之前的箭头
        if self.arrow_polygon is not None:
            self.arrow_polygon.remove()
        
        # 计算当前角度（顺时针旋转）
        t = frame / self.fps  # 当前时间（秒）
        angle = 2 * np.pi * self.frequency * t
        
        # 创建新的箭头
        points = self.create_arrow_polygon(angle)
        self.arrow_polygon = patches.Polygon(
            points,
            closed=True,
            facecolor=self.arrow_color,
            edgecolor=self.arrow_color
        )
        self.ax.add_patch(self.arrow_polygon)
        
        return [self.arrow_polygon]
    
    def _check_ffmpeg(self) -> bool:
        """检查ffmpeg是否可用
        
        Returns:
            如果ffmpeg可用返回True，否则返回False
        """
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def generate_frames(self, temp_dir: str) -> None:
        """生成PNG图片序列
        
        Args:
            temp_dir: 临时目录路径
            
        Raises:
            RuntimeError: 如果生成帧时出错
        """
        print("正在生成PNG序列...")
        
        try:
            for frame in range(self.total_frames):
                # 更新动画到当前帧
                self.animate(frame)
                
                # 保存当前帧
                frame_path = os.path.join(temp_dir, f'frame_{frame:04d}.png')
                self.fig.savefig(
                    frame_path,
                    transparent=True,
                    dpi=100,
                    bbox_inches='tight',
                    pad_inches=0,
                    facecolor='none'
                )
                
                # 显示进度
                if (frame + 1) % 100 == 0:
                    print(f"已生成 {frame + 1}/{self.total_frames} 帧")
            
            print(f"PNG序列生成完成，共 {self.total_frames} 帧")
            
        except Exception as e:
            raise RuntimeError(f"生成PNG序列时出错: {str(e)}")
    
    def create_video(self, temp_dir: str) -> None:
        """使用ffmpeg合成MOV文件
        
        Args:
            temp_dir: 临时目录路径（包含PNG序列）
            
        Raises:
            RuntimeError: 如果ffmpeg不可用或合成失败
        """
        # 检查ffmpeg是否可用
        if not self._check_ffmpeg():
            raise RuntimeError(
                "ffmpeg未找到。请确保已安装ffmpeg并添加到系统PATH中。"
            )
        
        print(f"正在使用ffmpeg合成MOV文件: {self.output_file}")
        
        # 构建ffmpeg命令（使用qtrle编码器支持透明通道）
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # 覆盖输出文件
            '-framerate', str(self.fps),
            '-i', os.path.join(temp_dir, 'frame_%04d.png'),
            '-vcodec', 'qtrle',  # QuickTime Animation编码器，支持透明
            '-pix_fmt', 'argb',  # ARGB像素格式，支持alpha通道
            self.output_file
        ]
        
        # 执行ffmpeg命令
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else result.stdout
            raise RuntimeError(f"ffmpeg合成失败: {error_msg}")
        
        print(f"完成！已保存为: {self.output_file}")
    
    def run(self) -> None:
        """执行完整的动画生成流程
        
        生成PNG序列，使用ffmpeg合成MOV文件，并清理临时文件。
        
        Raises:
            RuntimeError: 如果生成过程中出错
        """
        # 打印参数信息
        print("正在生成动画文件（透明背景）...")
        print(f"分辨率: {self.width}x{self.height}")
        print(f"帧率: {self.fps} fps")
        print(f"时长: {self.duration} 秒")
        print(f"总帧数: {self.total_frames}")
        print(
            f"箭头大小: {self.arrow_size}, "
            f"头部宽度: {self.arrow_width}, "
            f"身体宽度: {self.arrow_body_width}"
        )
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix='arrow_frames_')
        print(f"正在生成PNG序列到临时目录: {temp_dir}")
        
        try:
            # 第一步：生成PNG序列
            self.generate_frames(temp_dir)
            
            # 第二步：使用ffmpeg合成MOV文件
            self.create_video(temp_dir)
            
        finally:
            # 清理临时文件
            print("正在清理临时文件...")
            shutil.rmtree(temp_dir, ignore_errors=True)
            print("清理完成")


def main():
    """主函数：创建并运行箭头动画生成器"""
    generator = ArrowAnimationGenerator()
    generator.run()


if __name__ == '__main__':
    main()
