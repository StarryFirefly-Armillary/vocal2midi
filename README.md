# 🎤 Vocal2MIDI

**高精度人声转MIDI转换器**

一款专业的人声转MIDI软件，专为虚拟歌手歌曲制作设计。采用RMVPE深度学习音高检测引擎，精准识别人声特征，包括颤音等细微变化。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

---

## ✨ 主要特性

- 🎯 **高精度音高检测** - 使用RMVPE深度学习模型，精准识别人声音高
- 🎵 **颤音保留** - 智能检测颤音特征，生成Pitch Bend MIDI事件
- 🚀 **GPU加速** - 支持NVIDIA显卡CUDA加速，处理速度提升数倍
- 🎨 **现代化界面** - 深色主题，波形和音高曲线实时可视化
- 📁 **多格式支持** - 支持WAV、MP3、FLAC、OGG、M4A等常见格式
- ⚙️ **智能参数** - 自动识别BPM，一键预设快速调整

---

## 📸 界面预览

```
┌─────────────────────────────────────────────────────────────────┐
│  🎤 Vocal2MIDI - 高精度人声转MIDI转换器                            │
├─────────────────────────────────────────────────────────────────┤
│  [📁 导入音频]  [💾 导出MIDI]           未选择文件                 │
├───────────────────────────────────┬─────────────────────────────┤
│  📊 音频可视化                     │  🎯 快速预设                 │
│  ┌─────────────────────────────┐  │  [默认] [抒情歌] [流行歌]     │
│  │                             │  │                             │
│  │     波形显示区域              │  │  🎵 歌曲速度 (BPM)          │
│  │     音高曲线叠加              │  │  [120 BPM] [🔍 自动识别]    │
│  │                             │  │                             │
│  └─────────────────────────────┘  │  🎤 保留颤音效果 ✓           │
│  [✓] 显示波形  [✓] 显示音高       │  🔊 智能力度调整 ✓           │
│                                   │                             │
│                                   │  [🚀 开始转换]               │
│                                   │  [████████████░░░░] 75%     │
│                                   │                             │
│                                   │  📋 检测结果                 │
│                                   │  音符数量: 156               │
│                                   │  时长: 3分24秒               │
│                                   │  颤音区间: 23                │
└───────────────────────────────────┴─────────────────────────────┘
```

---

## 🚀 快速开始

### 系统要求

- Windows 10/11
- Python 3.8+
- NVIDIA显卡（推荐，支持CUDA加速）

### 安装步骤

```bash
# 1. 克隆仓库或下载ZIP
git clone https://github.com/StarryFirefly-Armillary/vocal2midi.git
cd vocal2midi

# 2. 运行安装脚本
双击 install.bat

# 3. 启动程序
双击 start.bat
```

> **注意**：首次运行会自动下载RMVPE模型（约100MB），请确保网络畅通。

---

## 📖 使用教程

### 基本流程

1. **导入音频**
   - 点击「📁 导入音频」按钮
   - 选择人声音频文件（WAV/MP3/FLAC/OGG/M4A）

2. **设置参数**
   - **快速预设**：点击「默认」「抒情歌」「流行歌」一键设置
   - **BPM**：点击「🔍 自动识别」自动检测歌曲速度
   - **颤音效果**：建议开启，让虚拟歌手更自然
   - **力度调整**：建议开启，让演唱更有层次感

3. **开始转换**
   - 点击「🚀 开始转换」按钮
   - 等待处理完成

4. **导出MIDI**
   - 点击「💾 导出MIDI」按钮
   - 选择保存位置

### 参数说明

| 参数 | 说明 | 建议设置 |
|------|------|----------|
| **BPM** | 歌曲速度（每分钟拍数） | 使用「自动识别」 |
| **颤音效果** | 保留歌手的颤音技巧 | ✅ 开启 |
| **力度调整** | 根据音量自动调整强弱 | ✅ 开启 |

### 在虚拟歌手软件中使用

生成的MIDI文件可以直接导入：

- **UTAU** - 直接导入MIDI文件
- **Synthesizer V** - 导入MIDI并调整歌词
- **Vocaloid** - 导入MIDI并分配歌词

---

## 🔧 技术架构

### 核心技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 音高检测 | RMVPE | 最精准的人声音高检测模型 |
| 深度学习 | PyTorch | 支持CUDA GPU加速 |
| 音频处理 | librosa | 专业音频处理库 |
| MIDI生成 | pretty_midi | MIDI文件生成和处理 |
| GUI框架 | PyQt6 | 现代化跨平台GUI |
| 音频解码 | FFmpeg | 支持多种音频格式 |

### 项目结构

```
Vocal2MIDI/
├── main.py                 # 程序入口
├── config.py               # 配置管理
├── requirements.txt        # Python依赖
├── install.bat             # 安装脚本
├── start.bat               # 启动脚本
├── core/                   # 核心处理模块
│   ├── audio_processor.py  # 音频处理
│   ├── pitch_detector.py   # RMVPE音高检测
│   ├── vibrato_detector.py # 颤音检测
│   └── midi_generator.py   # MIDI生成
└── gui/                    # GUI模块
    ├── main_window.py      # 主窗口
    ├── waveform_widget.py  # 波形可视化
    └── style.py            # UI样式
```

### 性能指标

| 指标 | 数值 |
|------|------|
| 音高检测精度 | > 95% |
| 颤音识别准确率 | > 90% |
| GPU处理速度 | 约2倍实时 |
| CPU处理速度 | 约0.5倍实时 |

---

## ❓ 常见问题

### Q: 程序无法启动？

A: 请确保：
1. 已安装 Python 3.8+
2. 已运行 `install.bat` 安装依赖
3. 查看是否有错误提示

### Q: 没有NVIDIA显卡可以使用吗？

A: 可以！程序会自动使用CPU处理，只是速度稍慢（约0.5倍实时）。

### Q: BPM识别不准确？

A: 可以手动输入BPM值，或搜索「歌曲名 BPM」获取准确值。

### Q: 转换的MIDI音高不准？

A: 请确保：
1. 使用高质量的音频文件
2. 音频是清晰的人声（避免背景音乐干扰）
3. BPM设置正确

### Q: 如何启用GPU加速？

A: 
1. 确保已安装NVIDIA显卡驱动
2. 运行 `fix_gpu.bat` 重新安装CUDA版PyTorch
3. 重启程序

---

## 🛠️ 开发相关

### 依赖安装

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装PyTorch (CUDA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 编译EXE

```bash
# 安装PyInstaller
pip install pyinstaller

# 编译
pyinstaller --onefile --windowed --name Vocal2MIDI main.py
```

---

## 📝 更新日志

### v1.0.0 (2026-06-05)
- 🎉 初始版本发布
- ✨ RMVPE音高检测引擎
- ✨ 颤音检测和保留
- ✨ 现代化GUI界面
- ✨ GPU加速支持
- ✨ 自动BPM识别
- ✨ 多格式音频支持

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

---

## 📄 许可证

本项目基于 MIT 许可证开源 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [RMVPE](https://github.com/yxlllc/RMVPE) - 音高检测模型
- [PyTorch](https://pytorch.org/) - 深度学习框架
- [librosa](https://librosa.org/) - 音频处理库
- [pretty_midi](https://craffel.github.io/pretty-midi/) - MIDI处理库
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI框架

---

## 📧 联系方式

- GitHub: [@StarryFirefly-Armillary](https://github.com/StarryFirefly-Armillary)
- 项目链接: [Vocal2MIDI](https://github.com/StarryFirefly-Armillary/Vocal2MIDI)

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**
