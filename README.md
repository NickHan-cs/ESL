# readme

BUAA程序语言设计原理大作业，Easy Shading Language，一种简易的array-based着色器语言。

### 运行说明

```
1. 进入根目录的compiler文件夹下
2. 运行python main.py --file ../example-easy/shaders/new_src/{*.esl}，编译*.esl文件
3. 得到main.frag.esl.spvasm文件
4. 运行..\example-easy\TOOLS\spirv-as.exe .\main.frag.esl.spvasm -o ..\example-easy\shaders\spv\main.frag.spv，将main.frag.esl.spvasm文件处理为二进制文件main.frag.spv
5. 进入根目录的example文件夹下，运行VKexample_mingw.exe查看运行效果（命令行运行会报错，需要在win图形界面双击运行）
```

详见文档./doc/ESL着色器语言设计.md。

### 样例

***以下为该项目当前可运行的样例***，其他预期样例可见文档./doc/ESL着色器语言设计.md。

```
使用本编译器编译运行测试
cd compiler
python main.py --file ../example-easy/shaders/new_src/*.esl
..\example-easy\TOOLS\spirv-as.exe .\main.frag.esl.spvasm -o ..\example-easy\shaders\spv\main.frag.spv
win下图形界面双击运行根目录下 \example-easy\VKexample_mingw.exe 即可预览测试效果
```

#### 样例1

```
将运行说明中的*.esl替换为main.frag2.esl，可得到以下效果
```

<img src="/docs/pics/example0.png" alt="词法分析流程图" style="zoom:67%;" />

#### 样例2

```
将运行说明中的*.esl替换为main.frag0.esl，可得到以下效果
```

<img src="/docs/pics/example1.png" alt="词法分析流程图" style="zoom:67%;" />

#### 样例3

```
将运行说明中的*.esl替换为main.frag1.esl，可得到以下效果
```

<img src="/docs/pics/example2.png" alt="词法分析流程图" style="zoom:67%;" />
