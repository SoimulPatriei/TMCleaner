
"""An adaptation of Aho Corasick algorithm"""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"


class AhoNode:
    def __init__(self):
        self.goto = {}
        self.out = []
        self.fail = None
 
def aho_create_forest(patterns):
    root = AhoNode()
 
    for path in patterns:
        node = root
        for symbol in path:
            node = node.goto.setdefault(symbol, AhoNode())
        node.out.append(path)
    return root
 
 
def aho_create_statemachine(patterns):
    root = aho_create_forest(patterns)
    queue = []
    for node in root.goto.itervalues():
        queue.append(node)
        node.fail = root
 
    while len(queue) > 0:
        rnode = queue.pop(0)
 
        for key, unode in rnode.goto.iteritems():
            queue.append(unode)
            fnode = rnode.fail
            while fnode != None and not fnode.goto.has_key(key):
                fnode = fnode.fail
            unode.fail = fnode.goto[key] if fnode else root
            unode.out += unode.fail.out
 
    return root
 
 
def aho_find_all(s, root, resList):
    node = root
 
    for i in xrange(len(s)):
        while node != None and not node.goto.has_key(s[i]):
            node = node.fail
        if node == None:
            node = root
            continue
        node = node.goto[s[i]]
        for pattern in node.out:
            resList.append(str(i - len(pattern) + 1) +"\t"+pattern)
 
 
def on_occurence(pos, patterns):
    """List of occurences ... """
    
    # print "At pos %s found pattern: %s" % (pos, patterns)
    
    
def main():
    
    text="abbey brooks stays home and plays chess and chess and abbey . "
    wList=['abbey','abbey brooks', 'chess', 'home']
    root = aho_create_statemachine(wList)
    
    resList=[]
    aho_find_all(text, root, resList)
    print ("The results have been ...")
    
    for occurence in resList:
        print occurence
    
    
    
       
if __name__ == '__main__':
  main()    
    



