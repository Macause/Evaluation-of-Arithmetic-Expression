"""沿用 maze-pathfinding 專案中自行實作的鏈結串列 Stack。

來源：https://github.com/Macause/maze-pathfinding/blob/main/data_structures.py
"""


class Node:
    """節點儲存一個值，以及下一個節點的參照。"""

    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node


class Stack:
    """後進先出：在 head 加入及取出。

    push、pop、peek、size 與 is_empty 皆為 O(1)，n 個節點佔 O(n) 空間。
    節點不限制值的型別，因此數值與運算子可以使用同一種 Stack。
    """

    def __init__(self):
        # head 指向堆疊頂端；空堆疊沒有任何節點。
        self.head = None
        self._size = 0

    def push(self, item):
        """將 item 放在頂端。"""
        # 新節點接在原本的頭節點前面。
        self.head = Node(item, self.head)
        self._size += 1

    def pop(self):
        """移除並回傳頂端值；空堆疊拋出 IndexError。"""
        if self.is_empty():
            raise IndexError("無法從空 Stack 取出元素")
        value = self.head.value
        # 頂端往下一個節點移動，原本的頂端便離開鏈結串列。
        self.head = self.head.next
        self._size -= 1
        return value

    def peek(self):
        """回傳頂端值，但不移除節點。"""
        if self.is_empty():
            raise IndexError("無法查看空 Stack 的元素")
        return self.head.value

    def is_empty(self):
        """判斷是否沒有元素。"""
        return self._size == 0

    def size(self):
        """回傳目前元素數量。"""
        return self._size

    def __len__(self):
        """讓內建 len(stack) 能取得元素數量。"""
        return self._size

    def clear(self):
        """解除整條鏈結的參照並歸零數量，節點由 Python 回收。"""
        self.head = None
        self._size = 0
