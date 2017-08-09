"""
implement a FIFO queue from a singly linked list.
"""

# TODO: Unit test
class Node(object):
    def __init__(self, data):
        self.data = data
        self.next = None

class Queue(object):
    def __init__(self, data=[]):
        # data should be in list format from head to tail
        self.head = None
        self.tail = None
        for element in data:
            self.push(element)

    """
    put new data at tail queue
    """
    def push(self, data):
        if self.head == None:
            node = Node(data)
            self.head = node
        else:
            node = Node(data)
            self.tail.next = node
        self.tail = node
    """
    pop next element from head
    """
    def pop(self):
        head = self.head
        self.head = head.next
        return head.data
    """
    export data from Queue as list
    """
    def to_list(self, copy=False):
        l = []
        q = Queue()
        while self.head != None:
            data = self.pop()
            l.append(data)
            if copy:
                q.push(data)
        self.head = q.head
        return l
