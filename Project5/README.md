项目名：Impl Merkle Tree following RFC6962
# 实验完成人
程雨森
学号：202100460090
# 运行指导
代码可以直接运行
# 处理器信息：
处理器：11th Gen Intel(R) Core(TM) i7-11800H @ 2.30GHz   2.30 GHz
# 实现过程：
为了实现具体功能，在代码中定义了Merkle树的节点结构体merkletree，其中包含左右子节点指针、父节点指针、节点层数、节点数据和节点字符串；定义了哈希函数hash和hash_nodes，分别用于对字符串和节点数据进行哈希；定义了函数last_node和find_new_node，分别用于查找最后一个节点和查找新节点，这两个函数在构建Merkle树时用到；定义了函数initial，用于初始化Merkle树。该函数首先将字符串按照标点符号和空格进行分割，得到一个字符串数组。然后根据字符串数组中的每个字符串构建Merkle树的叶子节点，并根据节点的哈希值构建Merkle树的中间节点和根节点。在构建过程中，如果某个节点的左右子节点都已经存在，则需要查找新节点，并将新节点插入到Merkle树中。最后返回根节点；定义了函数print_tree，用于打印Merkle树。该函数采用递归方式遍历Merkle树，并根据节点的层数打印相应数量的缩进和节点数据或字符串；定义了函数delete_tree和delete_string，分别用于释放Merkle树和字符串数组的内存空间。在main函数中，首先定义了一个包含字符串的数组message，然后调用divide_string函数将字符串按照标点符号和空格进行分割，并得到字符串数组s和字符串数量n。接着调用initial函数初始化Merkle树，并调用print_tree函数打印Merkle树。最后释放字符串数组和Merkle树的内存空间，并返回0。
# 运行结果：
如result5.jpg所示
