# CS3853 Group 13, project milestone 1:
import sys, math, os


# project milestone 2: page table and physical memory management classes
class PageTable:
    def __init__(self):
        # 512K entries
        self.entries = [None] * (512 * 1024)
        self.pages_owned = []

    def is_valid(self, v_page_num):
        return self.entries[v_page_num] is not None

    def get_physical_page(self, v_page_num):
        return self.entries[v_page_num]

    def map(self, v_page_num, p_page_num):
        self.entries[v_page_num] = p_page_num
        self.pages_owned.append((v_page_num, p_page_num))

    def unmap(self, v_page_num):
        self.entries[v_page_num] = None
        self.pages_owned = [p for p in self.pages_owned if p[0] != v_page_num]


class PhysicalMemoryManager:

    def __init__(self, total_mb, percent_used):
        total_bytes = total_mb * 1024 * 1024
        self.total_pages = total_bytes // 4096

        self.num_os_pages = int(self.total_pages * (percent_used / 100))
        self.free_pages = list(range(self.num_os_pages, self.total_pages))
        self.page_to_process = {}

    def get_free_page(self):
        return self.free_pages.pop(0) if self.free_pages else None


class Cache:
    def __init__(self, cache_size_kb, block_size, associativity):
        self.block_size = block_size
        pass

    def invalidate_page(self, p_page_num):
        num_blocks_in_page = 4096 // self.block_size

        # Calculate the starting physical address for this page
        start_phys_addr = p_page_num * 4096

        for i in range(num_blocks_in_page):

            target_addr = start_phys_addr + (i * self.block_size)

            pass


def handle_memory_access(address, proc, phys_mem, all_procs, cache):
    v_page_num = address // 4096
    if proc["page_table"].is_valid(v_page_num):
        return "hit"
    p_page_num = phys_mem.get_free_page()
    if p_page_num is None:
        p_page_num = snag_victim_page(all_procs, cache)  # Added cache here
        proc["page_table"].map(v_page_num, p_page_num)
        return "fault"  # Changed "snag" to "fault" to match the counter name
    else:
        proc["page_table"].map(v_page_num, p_page_num)
        return "free"


def snag_victim_page(all_procs, cache):
    for p in all_procs:
        if p["page_table"].pages_owned:
            v_vic, p_vic = p["page_table"].pages_owned.pop(0)
            p["page_table"].unmap(v_vic)

            # Invalidate all cache blocks that belong to this physical page
            cache.invalidate_page(p_vic)

            return p_vic
    return None


def read_args():
    args = sys.argv[1:]

    values = {"files": []}

    i = 0

    # go through all command line inputs:
    while i < len(args):
        # cache size:
        if args[i] == "-s":
            values["cache_size"] = int(args[i + 1])
            i += 2
        # block size:
        elif args[i] == "-b":
            values["block_size"] = int(args[i + 1])
            i += 2
        # associativity:
        elif args[i] == "-a":
            values["associativity"] = int(args[i + 1])
            i += 2
        # replacement policy:
        elif args[i] == "-r":
            values["replacement"] = args[i + 1].upper()
            i += 2
        # physical memory:
        elif args[i] == "-p":
            values["physical_memory"] = int(args[i + 1])
            i += 2
        # percent for system:
        elif args[i] == "-u":
            values["percent_system"] = float(args[i + 1])
            i += 2
        # time slice:
        elif args[i] == "-n":
            values["time_slice"] = int(args[i + 1])
            i += 2
        # trace files:
        elif args[i] == "-f":
            values["files"].append(args[i + 1])
            i += 2
        # if input is not correct:
        else:
            print("Error: invalid input")
            sys.exit(1)

    return values


def check_args(values):
    # list of all needed inputs:
    needed = [
        "cache_size",
        "block_size",
        "associativity",
        "replacement",
        "physical_memory",
        "percent_system",
        "time_slice",
    ]

    # check if all inputs in needed list are in:
    for item in needed:
        if item not in values:
            print("Error: missing input")
            sys.exit(1)

    # check trace files:
    if len(values["files"]) < 1 or len(values["files"]) > 3:
        print("Error: need 1 to 3 trace files")
        sys.exit(1)

    # possible input choices:
    valid_cache = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
    valid_block = [8, 16, 32, 64]
    valid_assoc = [1, 2, 4, 8, 16]
    valid_replace = ["RR", "RND"]
    valid_memory = [128, 256, 512, 1024, 2048, 4096]

    # error messages for invalid inputs:
    if values["cache_size"] not in valid_cache:
        print("Error: invalid cache size")
        sys.exit(1)

    if values["block_size"] not in valid_block:
        print("Error: invalid block size")
        sys.exit(1)

    if values["associativity"] not in valid_assoc:
        print("Error: invalid associativity")
        sys.exit(1)

    if values["replacement"] not in valid_replace:
        print("Error: invalid replacement policy")
        sys.exit(1)

    if values["physical_memory"] not in valid_memory:
        print("Error: invalid physical memory")
        sys.exit(1)

    if values["percent_system"] < 0 or values["percent_system"] > 100:
        print("Error: invalid percent for system")
        sys.exit(1)

    if values["time_slice"] == 0 or values["time_slice"] < -1:
        print("Error: invalid time slice")
        sys.exit(1)

    # check if cache math works out:
    cache_size_bytes = values["cache_size"] * 1024
    total_blocks = cache_size_bytes // values["block_size"]

    if cache_size_bytes % values["block_size"] != 0:
        print("Error: cache size must divide evenly by block size")
        sys.exit(1)

    if total_blocks % values["associativity"] != 0:
        print("Error: blocks must divide evenly by associativity")
        sys.exit(1)


def get_replacement_name(policy):
    if policy == "RR":
        return "Round Robin"
    else:
        return "Random"


def get_time_slice_text(time_slice):
    if time_slice == -1:
        return "max"
    else:
        return str(time_slice)


def calculate_values(values):
    # basic sizes:
    cache_size_bytes = values["cache_size"] * 1024
    physical_memory_bytes = values["physical_memory"] * 1024 * 1024
    page_size = 4096
    page_table_entries = 512 * 1024

    # cache calculations:
    total_blocks = cache_size_bytes // values["block_size"]
    total_rows = total_blocks // values["associativity"]

    block_offset_bits = int(math.log2(values["block_size"]))
    index_bits = int(math.log2(total_rows))
    physical_address_bits = int(math.log2(physical_memory_bytes))
    tag_bits = physical_address_bits - index_bits - block_offset_bits

    # valid bit and tag bits for each block:
    overhead_bits_per_block = 1 + tag_bits
    overhead_size = math.ceil((total_blocks * overhead_bits_per_block) / 8)

    implementation_memory_bytes = cache_size_bytes + overhead_size
    implementation_memory_kb = implementation_memory_bytes / 1024
    cost = implementation_memory_kb * 0.07

    # physical memory calculations:
    number_physical_pages = physical_memory_bytes // page_size
    number_pages_for_system = int(
        (values["percent_system"] / 100.0) * number_physical_pages
    )

    physical_page_bits = int(math.log2(number_physical_pages))
    page_table_entry_size = 1 + physical_page_bits  # valid bit + phys page bits

    total_ram_page_tables = math.ceil(
        (page_table_entries * len(values["files"]) * page_table_entry_size) / 8
    )
    # return all calculated vals:
    return {
        "total_blocks": total_blocks,
        "tag_bits": tag_bits,
        "index_bits": index_bits,
        "total_rows": total_rows,
        "overhead_size": overhead_size,
        "implementation_memory_bytes": implementation_memory_bytes,
        "implementation_memory_kb": implementation_memory_kb,
        "cost": cost,
        "number_physical_pages": number_physical_pages,
        "number_pages_for_system": number_pages_for_system,
        "physical_page_bits": physical_page_bits,
        "page_table_entry_size": page_table_entry_size,
        "total_ram_page_tables": total_ram_page_tables,
    }


def print_results(values, results):
    print("MILESTONE #1:  Input Parameters and Calculated Values")
    print("Cache Simulator - CS 3853 - Team #13")
    print()

    print("Trace File(s):")
    for file_name in values["files"]:
        print(f"        {os.path.basename(file_name)}")
    print()

    print("***** Cache Input Parameters *****")
    print()
    print(f"Cache Size:                     {values['cache_size']} KB")
    print(f"Block Size:                     {values['block_size']} bytes")
    print(f"Associativity:                  {values['associativity']}")
    print(
        f"Replacement Policy:             {get_replacement_name(values['replacement'])}"
    )
    print(f"Physical Memory:                {values['physical_memory']} MB")
    print(f"Percent Memory Used by System:  {values['percent_system']:.1f}%")
    print(
        f"Instructions / Time Slice:      {get_time_slice_text(values['time_slice'])}"
    )
    print()

    print("***** Cache Calculated Values *****")
    print()
    print(f"Total # Blocks:                 {results['total_blocks']}")
    print(
        f"Tag Size:                       {results['tag_bits']} bits        (based on actual physical memory)"
    )
    print(f"Index Size:                     {results['index_bits']} bits")
    print(f"Total # Rows:                   {results['total_rows']}")
    print(f"Overhead Size:                  {results['overhead_size']} bytes")
    print(
        f"Implementation Memory Size:     {results['implementation_memory_kb']:.2f} KB  ({results['implementation_memory_bytes']} bytes)"
    )
    print(f"Cost:                           ${results['cost']:.2f} @ $0.07 per KB")
    print()

    print("***** Physical Memory Calculated Values *****")
    print()
    print(f"Number of Physical Pages:       {results['number_physical_pages']}")
    print(
        f"Number of Pages for System:     {results['number_pages_for_system']}         ( {values['percent_system'] / 100:.2f} * {results['number_physical_pages']} = {results['number_pages_for_system']} )"
    )
    print(
        f"Size of Page Table Entry:       {results['page_table_entry_size']} bits        (1 valid bit, {results['physical_page_bits']} for PhysPage)"
    )
    print(
        f"Total RAM for Page Table(s):    {results['total_ram_page_tables']} bytes  (512K entries * {len(values['files'])} .trc files * {results['page_table_entry_size']} / 8)"
    )


def main():
    values = read_args()
    check_args(values)
    results = calculate_values(values)
    print_results(values, results)

    total_hits = 0
    total_from_free = 0
    total_page_faults = 0

    cache = Cache(values["cache_size"], values["block_size"], values["associativity"])

    # --- Setup for Simulation ---
    phys_mem = PhysicalMemoryManager(
        values["physical_memory"], values["percent_system"]
    )
    processes = []
    for f in values["files"]:
        processes.append(
            {"page_table": PageTable(), "file": open(f, "r"), "done": False}
        )

    # --- The Main Loop (Time Slice Logic) ---
    while any(not p["done"] for p in processes):

        # 2. Give each process a "turn"
        for proc in processes:
            if proc["done"]:
                continue

            # Determine time slice size
            n = values["time_slice"]
            if n == -1:
                n = 1000000  # If -1, run until file ends

            # 3. Run 'n' instructions for this specific process
            instructions_processed = 0
            while instructions_processed < n:
                line = proc["file"].readline()

                # If we hit EOF, mark process as done and free its pages
                if not line:
                    proc["done"] = True
                    # Return pages to free list and invalidate cache
                    for v_p, p_p in proc["page_table"].pages_owned:
                        cache.invalidate_page(p_p)
                        phys_mem.free_pages.append(p_p)
                    break

                line = line.strip()
                if not line or not line.startswith("EIP"):
                    continue

                # We found an instruction! Read the mandatory second line
                line1 = line
                line2 = proc["file"].readline()
                if not line2:  # Should not happen in a valid .trc
                    proc["done"] = True
                    break

                # --- EXTRACT ADDRESSES ---
                # Instruction Address
                instr_addr = int(line1[10:18], 16)

                # Data Write (dstM)
                dst_addr = None
                dst_addr_str = line2[6:14]
                if dst_addr_str != "00000000" and "--------" not in line2[15:23]:
                    dst_addr = int(dst_addr_str, 16)

                # Data Read (srcM)
                src_addr = None
                src_addr_str = line2[33:41]
                if src_addr_str != "00000000" and "--------" not in line2[42:50]:
                    src_addr = int(src_addr_str, 16)

                # --- PROCESS ACCESSES AND UPDATE COUNTERS ---
                for addr in [instr_addr, dst_addr, src_addr]:
                    if addr is not None:
                        res = handle_memory_access(
                            addr, proc, phys_mem, processes, cache
                        )
                        if res == "hit":
                            total_hits += 1
                        elif res == "free":
                            total_from_free += 1
                        elif res == "fault":
                            total_page_faults += 1

                instructions_processed += 1

    # --- FINAL MILESTONE #2 OUTPUT ---
    pages_avail = phys_mem.total_pages - phys_mem.num_os_pages
    total_mapped = total_hits + total_from_free + total_page_faults

    print("\nMILESTONE #2: - Virtual Memory Simulation Results")
    print("\n***** VIRTUAL MEMORY SIMULATION RESULTS *****")
    print(f"\nPhysical Pages Used By SYSTEM: {phys_mem.num_os_pages}")
    print(f"Pages Available to User:       {pages_avail}")
    print(f"\nVirtual Pages Mapped:          {total_mapped}")
    print("-" * 35)
    print(f"        Page Table Hits:    {total_hits}")
    print(f"        Pages from Free:    {total_from_free}")
    print(f"        Total Page Faults:  {total_page_faults}")

    print("\nPage Table Usage Per Process:")
    print("-" * 30)

    pte_size_bits = results["page_table_entry_size"]
    for i, proc in enumerate(processes):
        # Count current entries or final entries
        used_entries = len(proc["page_table"].pages_owned)
        percent_used = (used_entries / 524288) * 100
        wasted_bytes = int((524288 - used_entries) * pte_size_bits / 8)

        file_name = os.path.basename(values["files"][i])
        print(f"[{i}] {file_name}:")
        print(
            f"        Used Page Table Entries: {used_entries}  ( {percent_used:.3f}%)"
        )
        print(f"        Page Table Wasted: {wasted_bytes} bytes")


if __name__ == "__main__":
    main()
