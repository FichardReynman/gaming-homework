"""Pure game rules for the RAM Tower Rescue puzzle."""
from dataclasses import dataclass, field

@dataclass
class MemoryBlock:
    block_id: int
    owner: str | None = None
    active: bool = False
    protected: bool = False
    allocated_to_target: bool = False

    @property
    def is_free(self):
        return self.owner is None and not self.allocated_to_target

@dataclass
class PuzzleResult:
    status: str
    message: str

@dataclass
class RAMPuzzle:
    target_program: str = "School Project App"
    target_required_blocks: int = 3
    blocks: list[MemoryBlock] = field(default_factory=list)
    status: str = "PUZZLE"

    def __post_init__(self):
        if not self.blocks:
            self.reset()

    def reset(self):
        # 0-1: inactive Music Player; 2-3: protected active System Monitor;
        # 4-5: free. The target needs three blocks.
        self.blocks = [
            MemoryBlock(0, "Music Player", active=False),
            MemoryBlock(1, "Music Player", active=False),
            MemoryBlock(2, "System Monitor", active=True, protected=True),
            MemoryBlock(3, "System Monitor", active=True, protected=True),
            MemoryBlock(4),
            MemoryBlock(5),
        ]
        self.status = "PUZZLE"

    @property
    def target_count(self):
        return sum(block.allocated_to_target for block in self.blocks)

    @property
    def free_count(self):
        return sum(block.is_free for block in self.blocks)

    def release_block(self, block_id):
        if self.status != "PUZZLE":
            return PuzzleResult("invalid", "The puzzle is not active. Retry to play again.")
        block = self._get(block_id)
        if block is None:
            return PuzzleResult("invalid", "That memory block does not exist.")
        if block.allocated_to_target:
            block.allocated_to_target = False
            return PuzzleResult("ok", "Returned one block to available memory.")
        if block.owner is None:
            return PuzzleResult("invalid", "This block is already free.")
        if block.protected or block.active:
            self.status = "FAILURE"
            return PuzzleResult("failure", "ACCESS VIOLATION: that block belongs to an active program. Active data is protected.")
        block.owner = None
        return PuzzleResult("ok", "Released one block from an inactive program.")

    def allocate_block(self, block_id):
        if self.status != "PUZZLE":
            return PuzzleResult("invalid", "The puzzle is not active. Retry to play again.")
        block = self._get(block_id)
        if block is None:
            return PuzzleResult("invalid", "That memory block does not exist.")
        if block.allocated_to_target:
            return PuzzleResult("invalid", "That block is already assigned to the School Project App.")
        if block.owner is not None:
            return PuzzleResult("invalid", "This block is occupied. Release it only if its program is inactive.")
        block.allocated_to_target = True
        return PuzzleResult("ok", "Allocated one free block to the School Project App.")

    def submit(self):
        if self.status != "PUZZLE":
            return PuzzleResult(self.status.lower(), "Retry the puzzle to make another attempt.")
        if self.target_count < self.target_required_blocks:
            self.status = "FAILURE"
            return PuzzleResult("failure", f"Not enough memory: the School Project App has {self.target_count} of {self.target_required_blocks} required blocks.")
        self.status = "SUCCESS"
        return PuzzleResult("success", "Rescue complete! The School Project App has enough memory, and active data stayed protected.")

    def _get(self, block_id):
        return next((block for block in self.blocks if block.block_id == block_id), None)
