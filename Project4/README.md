项目名：do your best to optimize SM3 implementation (software)
# 实验完成人
程雨森
学号：202100460090
# 运行指导
代码可以直接运行
# 处理器信息：
处理器：11th Gen Intel(R) Core(TM) i7-11800H @ 2.30GHz   2.30 GHz
# 实现过程：
在代码中定义了这几个函数leftshift()：实现循环左移的函数，FF()和GG()：SM3压缩函数中的两个置换函数，P0()和P1()：SM3压缩函数中的两个线性函数，compress()：SM3压缩函数，其中，FF()和GG()是SM3压缩函数中的两个置换函数，用于对数据进行混淆；P0()和P1()是SM3压缩函数中的两个线性函数，用于对数据进行线性变换。compress()函数是SM3的核心计算部分，用于将每个512位的消息块压缩成256位的摘要。在该函数内部，先将消息块按照一定的规则进行填充，然后将填充后的消息块拆分成16个32位的字，再扩展到68个32位字，最后进行64轮计算（每轮计算包括置换、线性函数和循环左移等操作），最终得到256位的摘要。该代码实现了三种不同的计算方式：串行计算、4线程并行计算和8线程并行计算。其中，4线程和8线程的并行计算使用了C++11中的std::thread库。

# 运行结果：
如result4_1.jpg、result4_2.jpg所示
通过以上两图对比可以看出，仅是重新实现SM3，单次运行时间就已缩短近3000倍

