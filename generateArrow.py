import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import numpy as np

# 可调参数
ARROW_SIZE = 100  # 箭头长度（像素）
ARROW_WIDTH = 40  # 箭头头部宽度（像素）
ARROW_BODY_WIDTH = 10  # 箭头身体宽度（像素）
ARROW_COLOR = 'red'  # 箭头颜色

# 视频参数
WIDTH = 400
HEIGHT = 400
FPS = 30
DURATION = 10  # 秒
FREQUENCY = 0.5  # Hz（每2秒转一圈）

# 计算总帧数
TOTAL_FRAMES = FPS * DURATION

# 创建图形和轴
fig, ax = plt.subplots(figsize=(WIDTH/100, HEIGHT/100), dpi=100)
ax.set_xlim(-WIDTH/2, WIDTH/2)
ax.set_ylim(-HEIGHT/2, HEIGHT/2)
ax.set_aspect('equal')
ax.axis('off')  # 隐藏坐标轴

# 旋转中心偏移（向尾端偏移20%）
ROTATION_OFFSET = - ARROW_SIZE * 0.1  # 向尾端（y轴负方向）偏移

# 创建箭头（使用Polygon绘制，中心在原点）
def create_arrow_polygon(angle):
    """创建箭头多边形，围绕偏移后的中心点旋转"""
    # 箭头形状：从中心点向前的箭头
    # 箭头头部在y轴正方向，尾部在y轴负方向
    # 旋转中心向尾端偏移20%，所以所有点的y坐标需要减去偏移量
    # 头部结束位置（y坐标）
    head_end_y = ARROW_SIZE/2 - ARROW_WIDTH
    
    arrow_points = np.array([
        [0, ARROW_SIZE/2 - ROTATION_OFFSET],  # 箭头尖端
        [-ARROW_WIDTH/2, ARROW_SIZE/2 - ARROW_WIDTH - ROTATION_OFFSET],  # 左翼
        [-ARROW_WIDTH/4, ARROW_SIZE/2 - ARROW_WIDTH - ROTATION_OFFSET],  # 左翼内侧
        [-ARROW_BODY_WIDTH/2, head_end_y - ROTATION_OFFSET],  # 左身体起点（从头部结束位置开始使用恒定宽度）
        [-ARROW_BODY_WIDTH/2, -ARROW_SIZE/2 - ROTATION_OFFSET],  # 左尾部（恒定宽度）
        [ARROW_BODY_WIDTH/2, -ARROW_SIZE/2 - ROTATION_OFFSET],  # 右尾部（恒定宽度）
        [ARROW_BODY_WIDTH/2, head_end_y - ROTATION_OFFSET],  # 右身体起点（从头部结束位置开始使用恒定宽度）
        [ARROW_WIDTH/4, ARROW_SIZE/2 - ARROW_WIDTH - ROTATION_OFFSET],  # 右翼内侧
        [ARROW_WIDTH/2, ARROW_SIZE/2 - ARROW_WIDTH - ROTATION_OFFSET],  # 右翼
    ])
    
    # 旋转矩阵（顺时针旋转）
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    rotation_matrix = np.array([[cos_a, sin_a], [-sin_a, cos_a]])
    
    # 应用旋转
    rotated_points = arrow_points @ rotation_matrix.T
    
    return rotated_points

# 初始化箭头
arrow_polygon = None

def animate(frame):
    """动画更新函数"""
    global arrow_polygon
    
    # 清除之前的箭头
    if arrow_polygon is not None:
        arrow_polygon.remove()
    
    # 计算当前角度（顺时针旋转，0.5Hz）
    # 0.5Hz意味着每2秒转一圈（360度）
    t = frame / FPS  # 当前时间（秒）
    angle = 2 * np.pi * FREQUENCY * t  # 正角度配合顺时针旋转矩阵
    
    # 创建新的箭头
    points = create_arrow_polygon(angle)
    arrow_polygon = patches.Polygon(points, closed=True, 
                                     facecolor=ARROW_COLOR, 
                                     edgecolor=ARROW_COLOR)
    ax.add_patch(arrow_polygon)
    
    return [arrow_polygon]

# 创建动画
anim = animation.FuncAnimation(fig, animate, frames=TOTAL_FRAMES, 
                              interval=1000/FPS, blit=True, repeat=False)

# 保存为MOV文件
print(f"正在生成MOV文件...")
print(f"分辨率: {WIDTH}x{HEIGHT}")
print(f"帧率: {FPS} fps")
print(f"时长: {DURATION} 秒")
print(f"总帧数: {TOTAL_FRAMES}")
print(f"箭头大小: {ARROW_SIZE}, 头部宽度: {ARROW_WIDTH}, 身体宽度: {ARROW_BODY_WIDTH}")

output_file = 'arrow_rotation.mov'
writer = animation.FFMpegWriter(fps=FPS, codec='libx264', bitrate=5000)
anim.save(output_file, writer=writer)

print(f"完成！已保存为: {output_file}")

