import random


class Node:
    def __init__(self, value, priority=None):
        self.value = value
        self.priority = priority
        self.left = None
        self.right = None


class Treap:

    def print_tree(self, node, level):
        if node is None:
            return
        self.print_tree(node.right, level + 1)
        print("   " * level, "->", f"{node.value} {node.priority}")
        self.print_tree(node.left, level + 1)

    def left_rotate(self, node):
        right_child = node.right
        right_child_left = right_child.left
        right_child.left = node
        node.right = right_child_left

        return right_child

    def right_rotate(self, node):
        
        left_child = node.left
        left_child_right = left_child.right
        left_child.right = node
        node.left = left_child_right
        
        return left_child

    def insert(self, node, value, priority=None):
        if node is None:
            return Node(value, priority)

        if value < node.value:
            node.left = self.insert(node.left, value, priority)
            if node.left.priority > node.priority:
                node = self.right_rotate(node)
        elif value > node.value:
            node.right = self.insert(node.right, value, priority)
            if node.right.priority > node.priority:
                node = self.left_rotate(node)

        return node

    def find(self, node, value):
        if node is None:
            return None
        if node.value==value:
            return node
        
        elif value > node.value:
            if node.right is None:
                return None
            return self.find(node.right, value)
        else:
            if node.left is None:
                return None
            return self.find(node.left, value)


    def delete(self, node, value):
        if node is None:
            return None

        if value > node.value:
            node.right = self.delete(node.right, value)
        elif value < node.value:
            node.left = self.delete(node.left, value)

        else:
            if node.left is None and node.right is None:
                return None
            elif node.left is None:
                node = self.left_rotate(node)
                node.left = self.delete(node.left, value)
            elif node.right is None:
                node = self.right_rotate(node)
                node.right = self.delete(node.right, value)


            else:
                if node.left.priority > node.right.priority:
                    node = self.right_rotate(node)
                    node.right = self.delete(node.right, value)
                else:
                    node = self.left_rotate(node)
                    node.left = self.delete(node.left, value)

        return node


    def inorder(self, node):
        result = []
        if node:
            result.extend(self.inorder(node.left))
            result.append(node.value)
            result.extend(self.inorder(node.right))

        return result



treap = Treap()
root = None
root = treap.insert(root, 5, 10)
root = treap.insert(root, 3, 20)
root = treap.insert(root, 4, 30)
treap.print_tree(root, 0)