class Allocator:
    class Block:
        def __init__(self, step_start, step_end, size, name) -> None:
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
        # block represent tuple: (step_start, step_end, size)
        self.blocks = [
            Allocator.Block(x[0], x[1], x[2], idx) for idx, x in enumerate(blocks)
        ]
        self.max_step = max([x.step_end for x in self.blocks])
        self.allocation = {x.name: None for x in self.blocks}  # block offsets
        self.intervals = []
        for _ in range(self.max_step + 1):
            self.intervals.append([[0, float("inf")]])
    
    def clear(self):
        self.allocation = {x.name: None for x in self.blocks}  # block offsets
        self.intervals = []
        for _ in range(self.max_step + 1):
            self.intervals.append([[0, float("inf")]])

    def find_base_and_update(self, step_start, step_end, sz):
        base = 0
        # find base
        while True:
            update_base = False
            for step in range(step_start, step_end + 1):
                intervals = self.intervals[step]
                for i in range(len(intervals)):
                    s, e = intervals[i]
                    if s <= base and base + sz - 1 <= e:
                        break
                    if base < s:
                        base = s
                        update_base = True
                        if s <= base and base + sz - 1 <= e:
                            break
            if not update_base:
                break
        # breakpoint()
        # update
        for step in range(step_start, step_end + 1):
            intervals = self.intervals[step]
            pos = 0
            for i in range(len(intervals)):
                s, e = intervals[i]
                if s <= base and base + sz - 1 <= e:
                    pos = i
                    break
            s, e = intervals.pop(pos)
            if base + sz - 1 < e:
                intervals.insert(pos, [base + sz, e])
            if s < base:
                intervals.insert(pos, [s, base - 1])
        # breakpoint()
        return base

    def allocation_size(self):
        allocation_size = 0
        for key, value in self.allocation.items():
            allocation_size = max(allocation_size, value+self.blocks[key].size)
        return allocation_size

    def draw(self):
        import matplotlib.pyplot as plt

        plt.xlim(0, self.allocation_size())
        # plt.ylim(0, self.max_step + 1)
        plt.ylim(self.max_step + 1, 0)
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
        sorted_blocks = sorted(self.blocks, reverse=True, key=lambda x: x.size)
        for block in sorted_blocks:
            base = self.find_base_and_update(
                block.step_start, block.step_end, block.size
            )
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
            base = self.find_base_and_update(
                block.step_start, block.step_end, block.size
            )
            self.allocation[block.name] = base

    def alloc_best_fit_heuristic(self):
        def priority(block0, block1):
            # return True if block0 have higher priority to allocate
            # TODO: try different stregy to find best priority
            nonlocal s, e
            if block0.lifetime() > block1.lifetime():
                return True
            elif block.lifetime() == candidate_block.lifetime():
                max0 = max(block0.step_start - s, e - block0.step_end)
                max1 = max(block1.step_start - s, e - block1.step_end)
                if max0 > max1:
                    return True
                elif max0 == max1 and block0.size > block1.size:
                    return True
            return False

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
            candidate_block = None
            s, e, _ = bases[min_base_idx]
            # breakpoint()
            for block in self.blocks:
                if (
                    self.allocation[block.name] == None
                    and s <= block.step_start
                    and block.step_end <= e
                ):
                    if candidate_block == None or priority(block, candidate_block):
                        candidate_block = block
            if candidate_block == None:
                # no fit block for this base, update this base
                # find neighbor with min base, and merge with it
                base0 = float("inf")
                base1 = float("inf")
                if min_base_idx != 0:
                    base0 = bases[min_base_idx - 1][2]
                if min_base_idx != len(bases) - 1:
                    base1 = bases[min_base_idx + 1][2]
                if base0 < base1:
                    min_base_idx -= 1
                    step_start, _, _ = bases.pop(min_base_idx)
                    _, step_end, _ = bases.pop(min_base_idx)
                    bases.insert(min_base_idx, [step_start, step_end, base0])
                elif base1 < base0:
                    step_start, _, _ = bases.pop(min_base_idx)
                    _, step_end, _ = bases.pop(min_base_idx)
                    bases.insert(min_base_idx, [step_start, step_end, base1])
                else:  # the case that two neighbor have the same base
                    min_base_idx -= 1
                    step_start, _, _ = bases.pop(min_base_idx)
                    _, _, _ = bases.pop(min_base_idx)
                    _, step_end, _ = bases.pop(min_base_idx)
                    bases.insert(min_base_idx, [step_start, step_end, base1])
            else:
                # allocate block
                del bases[min_base_idx]
                if e != candidate_block.step_end:
                    bases.insert(
                        min_base_idx, [candidate_block.step_end + 1, e, min_base]
                    )
                bases.insert(
                    min_base_idx,
                    [
                        candidate_block.step_start,
                        candidate_block.step_end,
                        min_base + candidate_block.size,
                    ],
                )
                if candidate_block.step_start != s:
                    bases.insert(
                        min_base_idx, [s, candidate_block.step_start - 1, min_base]
                    )
                self.allocation[candidate_block.name] = min_base
                unallacated_num -= 1
                if unallacated_num == 0:
                    break


# block represent tuple: (step_start, step_end, size)
# blocks = [
#     (0, 1, 32),
#     (5, 7, 64),
#     (1, 4, 28),
#     (6, 8, 10),
#     (2, 5, 36),
#     (7, 8, 40),
#     (3, 5, 16),
#     (4, 5, 8),
# ]
# s = Allocator(blocks)
# s.alloc_greedy_size()
# # s.alloc_greedy_breath()
# # s.alloc_best_fit_heuristic()
# s.draw()

from random import randint
x1 = x2 = x3 = 0 # best times
for _ in range(100):
    blocks = []
    for _ in range(randint(4, 30)):
        start = randint(0, 50)
        block = [start, start+randint(0, 50), randint(1, 20)]
        blocks.append(block)
    s = Allocator(blocks)
    s.alloc_greedy_size()
    s1 = s.allocation_size()
    s.clear()
    s.alloc_greedy_breath()
    s2 = s.allocation_size()
    s.clear()
    s.alloc_best_fit_heuristic()
    s3 = s.allocation_size()
    print(f"[{s1}, {s2}, {s3}]")
    m = min(s1, s2, s3)
    if s1 == m:
        x1 += 1
    if s2 == m:
        x2 += 1
    if s3 == m:
        x3 += 1
print(f"[{x1}, {x2}, {x3}]")