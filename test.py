import  collections

buf = collections.deque(maxlen = 3)

buf.append(1)
buf.append(2)
buf.append(3)
buf.append(4)

for _ in range(3):
    print(buf.popleft())