# CS3853 Group 13, project milestone 1:
import sys, math, os
def read_args():
    args = sys.argv[1:]

    values = {
        "files": []
    }

    i = 0

    # go through all command line inputs:
    while i < len(args):
        #cache size:
        if args[i] == "-s":
            values["cache_size"] = int(args[i + 1])
            i += 2
        #block size:
        elif args[i] == "-b":
            values["block_size"] = int(args[i + 1])
            i += 2
        #associativity:
        elif args[i] == "-a":
            values["associativity"] = int(args[i + 1])
            i += 2
        #replacement policy:
        elif args[i] == "-r":
            values["replacement"] = args[i + 1].upper()
            i += 2
        #physical memory:
        elif args[i] == "-p":
            values["physical_memory"] = int(args[i + 1])
            i += 2
        #percent for system:
        elif args[i] == "-u":
            values["percent_system"] = float(args[i + 1])
            i += 2
        #time slice:
        elif args[i] == "-n":
            values["time_slice"] = int(args[i + 1])
            i += 2
        #trace files:
        elif args[i] == "-f":
            values["files"].append(args[i + 1])
            i += 2
        #if input is not correct:
        else:
            print("Error: invalid input")
            sys.exit(1)

    return values


def check_args(values):
    # list of all needed inputs:
    needed = ["cache_size", "block_size", "associativity", "replacement", "physical_memory", "percent_system", "time_slice"]

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
    number_pages_for_system = int((values["percent_system"] / 100.0) * number_physical_pages)

    physical_page_bits = int(math.log2(number_physical_pages))
    page_table_entry_size = 1 + physical_page_bits  # valid bit + phys page bits

    total_ram_page_tables = math.ceil(
        (page_table_entries * len(values["files"]) * page_table_entry_size) / 8
    )
    #return all calculated vals:
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
        "total_ram_page_tables": total_ram_page_tables
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
    print(f"Replacement Policy:             {get_replacement_name(values['replacement'])}")
    print(f"Physical Memory:                {values['physical_memory']} MB")
    print(f"Percent Memory Used by System:  {values['percent_system']:.1f}%")
    print(f"Instructions / Time Slice:      {get_time_slice_text(values['time_slice'])}")
    print()

    print("***** Cache Calculated Values *****")
    print()
    print(f"Total # Blocks:                 {results['total_blocks']}")
    print(f"Tag Size:                       {results['tag_bits']} bits        (based on actual physical memory)")
    print(f"Index Size:                     {results['index_bits']} bits")
    print(f"Total # Rows:                   {results['total_rows']}")
    print(f"Overhead Size:                  {results['overhead_size']} bytes")
    print(f"Implementation Memory Size:     {results['implementation_memory_kb']:.2f} KB  ({results['implementation_memory_bytes']} bytes)")
    print(f"Cost:                           ${results['cost']:.2f} @ $0.07 per KB")
    print()

    print("***** Physical Memory Calculated Values *****")
    print()
    print(f"Number of Physical Pages:       {results['number_physical_pages']}")
    print(f"Number of Pages for System:     {results['number_pages_for_system']}         ( {values['percent_system'] / 100:.2f} * {results['number_physical_pages']} = {results['number_pages_for_system']} )")
    print(f"Size of Page Table Entry:       {results['page_table_entry_size']} bits        (1 valid bit, {results['physical_page_bits']} for PhysPage)")
    print(f"Total RAM for Page Table(s):    {results['total_ram_page_tables']} bytes  (512K entries * {len(values['files'])} .trc files * {results['page_table_entry_size']} / 8)")

# --------------------------------------/\ Milestone 1/\--------------------------------------
# --------------------------------------\/ Milestone 2\/--------------------------------------
# --- TRACE PARSING ---

def parse_trace_line(line):
    """
    Parses a single line from the input trace file.
    Extracts essential data such as the instruction type (EIP vs data), 
    the virtual address, and the length of the instruction/data access.
    """
    pass


# --- MILESTONE 2: VIRTUAL MEMORY ---

class PageTable:
    def __init__(self, page_size, total_physical_memory):
        """
        Initializes the Page Table structure.
        Calculates the number of VPN (Virtual Page Number) bits and 
        offsets based on the provided page size.
        """
        pass

    def translate(self, virtual_address):
        """
        Simulates the translation from a Virtual Address to a Physical Address.
        - Checks if the page is in the table (Hit vs. Page Fault).
        - Updates Page Table statistics (Hit count, Miss count).
        - Returns the physical address to be used by the Cache.
        """
        pass


# --- MILESTONE 3: CACHE & PERFORMANCE ---

class Cache:
    def __init__(self, cache_size, block_size, associativity, replacement_policy="LRU"):
        """
        Initializes the Cache structure (Tags, Valid bits, and LRU counters).
        Calculates the number of bits for the Tag, Index, and Offset.
        """
        pass

    def access(self, physical_address):
        """
        Simulates a cache access (Read/Write).
        - Determines the Index and Tag from the physical address.
        - Checks for a Hit or Miss.
        - If Miss: Implements replacement logic (e.g., LRU) to bring in a new block.
        - Returns True for Hit, False for Miss.
        """
        pass

    def calculate_overhead(self):
        """
        Calculates the 'Implementation Memory Size' or overhead.
        Accounts for the extra bits needed for Tags, Valid bits, and LRU 
        counters beyond just the data storage.
        """
        pass


# --- SIMULATION ENGINE ---

class Simulator:
    def __init__(self, config):
        """
        Orchestrates the PageTable and Cache objects.
        Stores global counters for instructions, total cycles, and stalls.
        """
        pass

    def run(self, trace_file):
        """
        The main simulation loop:
        1. Reads trace file line by line.
        2. Translates Virtual Address -> Physical Address (Milestone 2).
        3. Uses Physical Address to access Cache (Milestone 3).
        4. Calculates cycles based on Hits, Misses, and Page Fault penalties.
        """
        pass

    def report_statistics(self):
        """
        Prints the final required output:
        - Cache/Page Table Hit and Miss rates.
        - Total simulation cycles and final CPI (Cycles Per Instruction).
        - Memory overhead calculations.
        """
        pass

def main():
    values = read_args()
    check_args(values)
    results = calculate_values(values)
    print_results(values, results)


if __name__ == "__main__":
    main()
