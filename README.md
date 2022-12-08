### readme

BUAA程序语言设计原理大作业，Easy Shading Language，一种简易的array-based着色器语言。

##### 运行说明

```
1. 进入根目录的compiler文件夹下
2. 运行python main.py --file ../example-easy/shaders/new_src/{*.esl}，编译*.esl文件
3. 得到main.frag.esl.spvasm文件
4. 运行..\example-easy\TOOLS\spirv-as.exe .\main.frag.esl.spvasm -o ..\example-easy\shaders\spv\main.frag.spv，将main.frag.esl.spvasm文件处理为二进制文件main.frag.spv
5. 进入根目录的example文件夹下，运行VKexample_mingw.exe查看运行效果
```

详见文档./doc/ESL着色器语言设计.md。

