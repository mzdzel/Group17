#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned int uint;

//结构体定义
typedef struct Node
{
	struct Node* left;
	struct Node* right;
	struct Node* parent;
	uint level;
	uint data;
	char* str;
}merkletree;

//用于创建新节点的宏函数
#define new_node(tree, depth){\
	tree = (merkletree *)malloc(sizeof(merkletree)); \
	tree->left = NULL; \
	tree->right = NULL; \
	tree->parent = NULL; \
	tree->level = (uint)depth; \
	tree->data = 0;	\
	tree->str = NULL;	\
}

void print_tree(merkletree* tree, int height)
{
	merkletree* p = tree;
	int i;
	if (p == NULL)
		return;

	if (p->left == NULL && p->right == NULL)
	{
		for (int i = 0; i < height - p->level; i++)
			printf("\t" );

		printf("-->%s\n", p->str);
	}
	else
	{
		print_tree(tree->left, height);
		printf("\n");
		for (i = 0; i < height - p->level; i++)
			printf("\t");
		printf("-->%-6d\n", p->data);

		print_tree(tree->right, height);
	}
}

uint hash(char* s1, char* s2)
{
	uint tmp = 3, hash = 0;

	if (s1 != NULL)
		while (*s1 != '\0' && *s1 != 0)
		{
			hash = hash * tmp + *s1;
			s1++;
		}
	
	if (s2 != NULL)
		while (*s2 != '\0' && *s2 != 0)
		{
			hash = hash * tmp + *s2;
			s2++;
		}
	return hash & 0x7FFFFFFF;
}

uint hash_nodes(uint n1, uint n2)
{
	uint tmp = 7, hash = 0;
	hash = n1 + n2;
	hash *= tmp;
	return hash & 0x7FFFFFFF;
}

merkletree* last_node(merkletree* tree)
{
	merkletree* p = tree, * tmp;

	if (p->left == NULL && p->right == NULL)
		return p;
	else if (p->right == NULL && p->left != NULL)
		return last_node(p->left);
	else if (p->right != NULL)
		return last_node(p->right);
}

merkletree* find_new_node(merkletree* tree)
{
	merkletree* p = tree->parent;

	while (p->left != NULL && p->right != NULL && p->parent != NULL)
		p = p->parent;
	if (p->parent == NULL && p->left != NULL && p->right != NULL)
		return NULL;
	else
		return p;
}

merkletree* initial(merkletree* tree, char** s, int n)
{
	merkletree* node, * tmp, * p;
	int i;

	if (n == 0)
	{
		printf("Initialization finish!\n");
		return tree;
	}
	else
	{
		new_node(node, 0);
		node->str = (char*)malloc(strlen(*s) + 1);
		memset(node->str, '\0', strlen(*s) + 1);
		for (int i = 0; i < strlen(*s); i++)
			node->str[i] = (*s)[i];
		
		if (tree == NULL)
		{
			new_node(tree, 1);
			tree->left = node;
			node->parent = tree;

			tree->data = hash(tree->left->str, tree->right == NULL ? NULL : tree->right->str);
			tree = initial(tree, s + 1, n - 1);

		}
		else
		{
			p = find_new_node(last_node(tree));

			if (p != NULL)
			{
				if (p->left->left == NULL && p->right == NULL)
				{
					p->right = node;
					node->parent = p;
					p->data = hash(p->left->str, p->right == NULL ? NULL : p->right->str);
				}
				else
				{
					i = p->level - 1;
					new_node(tmp, i);
					p->right = tmp;
					tmp->parent = p;
					p = p->right;
					i = p->level - 1;

					while (i > 0)
					{
						new_node(tmp, i);
						p->left = tmp;
						tmp->parent = p;

						p = p->left;
						i--;
					}

					p->left = node;
					node->parent = p;
					p->data = hash(p->left->str, p->right == NULL ? NULL : p->right->str);
				}
			}
			else
			{
				tmp = tree;

				new_node(tree, tmp->level + 1);
				tree->left = tmp;
				tmp->parent = tree;

				new_node(tmp, tree->level - 1);
				tree->right = tmp;
				tmp->parent = tree;

				p = tree->right;
				i = p->level - 1;

				while (i > 0)
				{
					new_node(tmp, i);
					p->left = tmp;
					tmp->parent = p;
					p = p->left;
					i--;
				}
				p->left = node;
				node->parent = p;
				p->data = hash(p->left->str, p->right == NULL ? NULL : p->right->str);
			}

			if (p != tree)
			{
				p = p->parent;
				while (p != tree)
				{
					p->data=hash_nodes(p->left->data, p->right == NULL ? 0 : p->right->data);
					p = p->parent;
				}
				p->data = hash_nodes(p->left->data, p->right == NULL ? 0 : p->right->data);
			}
			tree = initial(tree, s + 1, n - 1);
		}
	}
}

void delete_tree(merkletree* tree)
{
	if (tree->level == 0)
	{
		free(tree->str);
		free(tree);
	}
	else
	{
		if (tree->left != NULL)
			delete_tree(tree->left);
		if (tree->right != NULL)
			delete_tree(tree->right);
		free(tree);
	}
}

char** divide_string(char* str, int* number) 
{
	char* p = str, * tmp = str, ** result, ** res;
	int num = 0, i;

	while (*p != '\0') 
	{
		if (*p == ',' || *p == '.' || *p == '!' || *p == '?' || *p == ';') 
		{
			num += 2;
			tmp = p + 1;
		}
		else if (*p == ' ') 
		{ 
			if (p - tmp == 0)
				tmp = p + 1;
			else 
			{
				num += 1;
				tmp = p + 1;
			}
		}
		p++;
	}
	if (p - tmp > 0)
		num += 1;

	result = (char**)malloc(sizeof(char*) * num);
	res = result;

	tmp = str;
	p = str;

	while (*p != '\0') 
	{
		if (*p == ',' || *p == '.' || *p == '!' || *p == '?' || *p == ';') 
		{
			*res = (char*)malloc(sizeof(char) * (p - tmp + 1));
			memset(*res, '\0', p - tmp + 1);
			for (i = 0; i < p - tmp; i++)
				(*res)[i] = *(tmp + i);
			res++;

			*res = (char*)malloc(sizeof(char) * 2);
			memset(*res, '\0', 2);
			(*res)[0] = *p;
			res++;

			p++;
			tmp = p;
		}
		else if (*p == ' ') 
		{
			if (p - tmp == 0) 
			{
				p++;
				tmp = p;
			}
			else 
			{
				*res = (char*)malloc(sizeof(char) * (p - tmp + 1));
				memset(*res, '\0', p - tmp + 1);
				for (i = 0; i < p - tmp; i++)
					(*res)[i] = *(tmp + i);
				res++;

				p++;
				tmp = p;
			}
		}
		else
			p++;
	}
	if (p - tmp > 0) 
	{
		*res = (char*)malloc(sizeof(char) * (p - tmp + 1));
		memset(*res, '\0', p - tmp + 1);
		for (i = 0; i < p - tmp; i++)
			(*res)[i] = *(tmp + i);
	}

	*number = num;
	return result;
}

void delete_string(char** s, int n) 
{
	for (int i = 0; i < n; i++)
		free(*(s + i));
	free(s);
}

int main()
{
	char** s;
	int n;
	merkletree* tree = NULL;

	char message[] = "Hello!This is Baekhunee.I'm writing a merkle tree!";
	s = divide_string(message, &n);

	tree = initial(tree, s, n);
	if (tree != NULL)
	{
		printf("\nMerkle Tree:\n");
		print_tree(tree, tree->level);
		printf("\n\n");
	}
	delete_string(s, n);
	delete_tree(tree);

	return 0;
}