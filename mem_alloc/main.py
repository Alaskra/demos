from itertools import permutations


class Allocator:
    class Block:
        def __init__(self, step_start, step_end, size, name):
            self.step_start = step_start
            self.step_end = step_end
            self.size = size
            self.name = name

        def lifetime(self):
            return self.step_end - self.step_start + 1

        def __str__(self):
            return f"blcok {self.name}: range=[{self.step_start}, {self.step_end}], size={self.size}"

        def __repr__(self):
            return f"blcok {self.name}: range=[{self.step_start}, {self.step_end}], size={self.size}"

    def __init__(self, blocks):
        # block representation: (step_start, step_end, size)
        self.blocks = [
            Allocator.Block(x[0], x[1], x[2], idx) for idx, x in enumerate(blocks)
        ]
        self.max_step = max([x.step_end for x in self.blocks])
        self.reset()

    def reset(self):
        self.allocation = {x.name: None for x in self.blocks}  # block offsets
        self.intervals = []
        for _ in range(self.max_step + 1):
            self.intervals.append([[0, float("inf")]])

    def find_base_and_update(self, block):
        step_start = block.step_start
        step_end = block.step_end
        sz = block.size
        base = 0
        # find base
        update_base = True
        while update_base:
            update_base = False
            for intervals in self.intervals[step_start : step_end + 1]:
                for s, e in intervals:
                    if base < s:
                        base = s
                        update_base = True
                    if s <= base and base + sz - 1 <= e:
                        break
        # update
        for intervals in self.intervals[step_start : step_end + 1]:
            pos = 0
            for i, interval in enumerate(intervals):
                s, e = interval
                if s <= base and base + sz - 1 <= e:
                    pos = i
                    break
            s, e = intervals.pop(pos)
            if base + sz - 1 < e:
                intervals.insert(pos, [base + sz, e])
            if s < base:
                intervals.insert(pos, [s, base - 1])
        return base

    def allocation_size(self):
        allocation_size = 0
        for key, value in self.allocation.items():
            allocation_size = max(allocation_size, value + self.blocks[key].size)
        return allocation_size

    def draw(self):
        import matplotlib.pyplot as plt

        plt.xlim(0, self.allocation_size())
        plt.ylim(0, self.max_step + 1)
        # plt.ylim(self.max_step + 1, 0)
        plt.xlabel("memory space")
        plt.ylabel("time step")
        for block in self.blocks:
            x1 = x4 = self.allocation[block.name]
            x2 = x3 = self.allocation[block.name] + block.size
            y1 = y2 = block.step_start
            y3 = y4 = block.step_end + 1
            plt.fill([x1, x2, x3, x4, x1], [y1, y2, y3, y4, y1], color="deepskyblue")
            plt.plot([x1, x2, x3, x4, x1], [y1, y2, y3, y4, y1], color="black")
            plt.text(
                (x1 + x2) / 2,
                (y1 + y4) / 2,
                f"{block.size}",
                fontsize=10,
                ha="center",
                va="center",
            )
        plt.show()
        print(self.blocks)
        print(self.allocation)

    def alloc_greedy_size(self):
        sorted_blocks = sorted(
            self.blocks, reverse=True, key=lambda x: (x.size, x.lifetime())
        )
        for block in sorted_blocks:
            base = self.find_base_and_update(block)
            self.allocation[block.name] = base

    def alloc_greedy_breath(self):
        breath = [0] * (self.max_step + 1)
        for block in self.blocks:
            for step in range(block.step_start, block.step_end + 1):
                breath[step] += block.size
        time_steps = sorted(
            list(range(self.max_step + 1)), reverse=True, key=lambda x: breath[x]
        )
        sorted_blocks = []
        for step in time_steps:
            for block in self.blocks:
                if (
                    block.step_start <= step <= block.step_end
                    and block not in sorted_blocks
                ):
                    sorted_blocks.append(block)
        for block in sorted_blocks:
            base = self.find_base_and_update(block)
            self.allocation[block.name] = base

    def alloc_best_fit_heuristic(self, arg=64):
        # arg is in [64,65,...,112]
        def priority(block):
            # return priority of block based on different strategy
            # test shows origin is the best
            origin = (
                block.lifetime(),
                max(block.step_start - s, e - block.step_end),
                block.size,
            )
            choices = []
            for x, y, z in permutations(origin):
                choices.append((x, y, z))
                choices.append((x, y, -z))
                choices.append((x, -y, z))
                choices.append((x, -y, -z))
                choices.append((-x, y, z))
                choices.append((-x, y, -z))
                choices.append((-x, -y, z))
                choices.append((-x, -y, -z))
            return choices[arg - 64]
            # return (
            #     block.lifetime(),
            #     max(block.step_start - s, e - block.step_end),
            #     block.size,
            # )

        bases = [[0, self.max_step, 0]]  # [step_start, step_end, base]
        unallacated_num = len(self.blocks)
        while True:  # loop until all block allocated
            # find min base to alloc
            min_base_idx = 0
            min_base = bases[0][2]
            for i in range(1, len(bases)):
                if bases[i][2] < min_base:
                    min_base = bases[i][2]
                    min_base_idx = i
            # find block that fit this base
            s, e, _ = bases[min_base_idx]
            filtered_blocks = filter(
                lambda block: self.allocation[block.name] == None
                and s <= block.step_start
                and block.step_end <= e,
                self.blocks,
            )
            filtered_blocks = list(filtered_blocks)
            if len(filtered_blocks) == 0:
                # no fit block for this base, update this base
                # find neighbor with min base, and merge with it
                base0 = float("inf")
                base1 = float("inf")
                if min_base_idx != 0:
                    base0 = bases[min_base_idx - 1][2]
                if min_base_idx != len(bases) - 1:
                    base1 = bases[min_base_idx + 1][2]
                bases[min_base_idx][2] = min(base0, base1)
            else:
                # find best block to allocate
                candidate_block = filtered_blocks[0]
                for block in filtered_blocks[1:]:
                    if priority(block) > priority(candidate_block):
                        candidate_block = block
                # allocate block
                del bases[min_base_idx]
                bases.insert(min_base_idx, [candidate_block.step_end + 1, e, min_base])
                bases.insert(
                    min_base_idx,
                    [
                        candidate_block.step_start,
                        candidate_block.step_end,
                        min_base + candidate_block.size,
                    ],
                )
                bases.insert(
                    min_base_idx, [s, candidate_block.step_start - 1, min_base]
                )
                self.allocation[candidate_block.name] = min_base
                unallacated_num -= 1
                if unallacated_num == 0:
                    break
            # update bases
            new_bases = [[-1, -1, -1]]
            for base in bases:
                if base[0] > base[1]:
                    continue
                if new_bases[-1][2] == base[2]:
                    new_bases[-1][1] = base[1]
                else:
                    new_bases.append(base)
            bases = new_bases[1:]

    def alloc_customize(self, arg):
        if arg in [0, 1, 2, 3, 4, 5, 6, 7]:
            # simple greedy methods, test result show that large size first is better, than large lifetime
            if arg == 0:
                key = lambda x: (x.lifetime(), x.size)
            elif arg == 1:
                key = lambda x: (x.lifetime(), -x.size)
            elif arg == 2:
                key = lambda x: (-x.lifetime(), x.size)
            elif arg == 3:
                key = lambda x: (-x.lifetime(), -x.size)
            elif arg == 4:
                key = lambda x: (x.size, x.lifetime())
            elif arg == 5:
                key = lambda x: (x.size, -x.lifetime())
            elif arg == 6:
                key = lambda x: (-x.size, x.lifetime())
            elif arg == 7:
                key = lambda x: (-x.size, -x.lifetime())
            sorted_blocks = sorted(self.blocks, key=key)
            for block in sorted_blocks:
                base = self.find_base_and_update(block)
                self.allocation[block.name] = base
        elif arg == 8:
            self.alloc_greedy_size()
        elif arg == 9:
            self.alloc_greedy_breath()
        elif arg == 10:
            self.alloc_best_fit_heuristic()
        elif arg in list(range(64, 112)):
            self.alloc_best_fit_heuristic(arg)
        else:
            print("unsupport strategy")
            quit()


def papper_example():
    # block represent tuple: (step_start, step_end, size)
    blocks = [
        (0, 1, 32),
        (5, 7, 64),
        (1, 4, 28),
        (6, 8, 10),
        (2, 5, 36),
        (7, 8, 40),
        (3, 5, 16),
        (4, 5, 8),
    ]
    s = Allocator(blocks)
    s.alloc_greedy_size()
    s.draw()
    s.reset()
    s.alloc_best_fit_heuristic()
    s.draw()


def example():
    # block represent tuple: (step_start, step_end, size)
    blocks_best_fit = [
        (0, 0, 9),
        (9, 9, 9),
        (0, 8, 1),
        (1, 9, 1),
    ]

    blocks = [
        (0, 1, 32),
        (1, 4, 28),
        (6, 8, 10),
        (2, 5, 36),
        (7, 8, 40),
        (3, 5, 16),
        (4, 5, 8),
    ]

    blocks_size_more_important = [
        [0, 2, 2],
        [4, 6, 2],
        [1,2,2],
        [3,4,4],
        [5,6,2],
        [2,3,7]
    ]
    # s = Allocator(blocks_size_more_important)
    s = Allocator(blocks)
    s.alloc_greedy_size()
    s.draw()
    s.reset()
    s.alloc_best_fit_heuristic(arg=96)
    s.draw()


def random_test():
    from random import randint

    # strategys = list(range(8))+[8, 9, 10]+list(range(64, 64+48))  # all strategys
    # strategys = list(range(64, 64 + 48))
    # strategys = [64,96]
    # strategys = [96,8]
    # strategys = [64, 72, 96, 104, 8]
    strategys = [8,9,10]
    x = {i: 0 for i in strategys}  # best times
    xx = {i: 0 for i in strategys}  # best times, more strict(only one best strategy)
    sz = {i: 0 for i in strategys}  # space size needed, less is better
    print("=========space size===========")
    for _ in range(1000):
        blocks = []
        # for _ in range(randint(4, 50)):
        for _ in range(randint(4, 30)):
            start = randint(0, 50)
            block = [start, start + randint(0, 50), randint(1, 20)]
            # block = [start, start + randint(0, 20), randint(1, 40)]
            blocks.append(block)
        s = Allocator(blocks)
        for i in strategys:
            s.reset()
            s.alloc_customize(i)
            sz[i] = s.allocation_size()
            # s.draw()
            # quit()
        print(sz.values())
        m = min(sz.values())
        if list(sz.values()).count(m) == 1:
            only_one = True
        else:
            only_one = False
        for i in strategys:
            if sz[i] == m:
                x[i] += 1
                if only_one:
                    xx[i] += 1
    value10 = sorted(list(x.values()), reverse=True)[min(9, len(x) - 1)]
    value3 = sorted(list(x.values()), reverse=True)[min(2, len(x) - 1)]
    value1 = sorted(list(x.values()), reverse=True)[0]
    print("=========best strategys===========")
    best10 = []  # best 10 strategy
    best3 = []  # best 3 strategy
    best1 = []  # best 1 strategy
    for k, v in x.items():
        if v >= value10:
            best10.append(k)
        if v >= value3:
            best3.append(k)
        if v >= value1:
            best1.append(k)
    print(f"best10:{best10}")
    print(f"best3:{best3}")
    print(f"best1:{best1}")
    print("=========best times==========")
    print(x.values())
    print(xx.values())


# papper_example()
# example()
random_test()
