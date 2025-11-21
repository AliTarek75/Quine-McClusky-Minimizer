# Logic minimizer using Quine McClusky
# v1.3 | Author: Ali Tarek

def flip_binary(num_list, size):
    # Converts integers to binary strings with leading zeros.
    temp = []
    for item in num_list:
        binary = bin(item)[2:]
        length = len(binary)
        temp.append("0"*(size-length) + binary)
    return temp

def merge_terms(number1, number2):
    # Compares two binary strings. If they differ by exactly 1 bit,
    position = -1

    # Use zip to iterate without index lookups
    for i, (char1, char2) in enumerate(zip(number1, number2)):
        if char1 != char2:
            # If more than one difference, or incompatible X positions, fail fast
            if position != -1 or char1 == '-' or char2 == '-': return False, ""
            position = i
    
    if position != -1:
        return True, number1[:position] + "-" + number1[position+1:] 
    else: return False, "" 


def elimination(group, prime_implicants, coverage_old = {}):
    # Merges groups of terms and tracks which minterms they cover.
    # Calculates coverage on the go to avoid recalculating minterms from binary.

    coverage_new = {}
    num = len(group)-1
    temp_group = [[] for _ in range(0, num)]
    flat = [x for sub in group for x in sub] # Flattening to check for non-merged terms later
    insiders = []

    for i in range(0, num):
        for j in group[i]:
            for k in group[i+1]:
                merged_terms = merge_terms(j, k)
                if merged_terms[0]:
                    temp_group[i].append(merged_terms[1])
                    insiders.append(j)
                    insiders.append(k)
                    
                    # The new child term covers everything its parents covered.
                    if coverage_old:
                        coverage_new[merged_terms[1]] = []
                        coverage_new[merged_terms[1]].extend(coverage_old[j])
                        coverage_new[merged_terms[1]].extend(coverage_old[k])

    # Identify Prime Implicants (Terms that could not be merged further)
    prime_implicants.extend(list(set(flat) - set(insiders)))
    
    # Carry over coverage data for PIs found in this stage
    if prime_implicants:
        prime_implicants_coverage = {k: v for k, v in coverage_old.items() if k in prime_implicants}
        coverage_new = {**prime_implicants_coverage, **coverage_new}
    
    # Remove duplicates from the new groups
    temp_group = [list(dict.fromkeys(sub)) for sub in temp_group]
    
    return temp_group, coverage_new

def quine(minterms, dont_care, variables):
    num_vars = len(variables)

    prime_implicants = []
    essential_PI = []
    solutions = []
    solutions_variable = []

    extended_PI = {}
    reversed_PI = {}
    
    # 1. Grouping Phase
    groups = [[] for _ in range(0, num_vars+1)]
    minterms_bin = flip_binary(minterms, num_vars) + flip_binary(dont_care, num_vars)

    # Initial coverage map
    extended_PI = {k: [v] for k, v in zip(minterms_bin, minterms+dont_care)}
    for binary in minterms_bin:
        groups[binary.count("1")].append(binary)
    
    temp = groups.copy()
    while temp:
        temp, test = elimination(temp, prime_implicants, extended_PI)
        if test: extended_PI = test
        if not temp: prime_implicants.extend(temp)

    # 2. Coverage Table Setup
    # Map Minterms -> List of PIs that cover them
    for key, value in extended_PI.items():
        for minterm in value:
            if minterm in minterms: # Ignore Don't Cares for coverage requirements
                if minterm not in reversed_PI:
                    reversed_PI[minterm] = []
                reversed_PI[minterm].append(key)

    # 3. ESSENTIAL PRIME IMPLICANT DOMINANC
    # If a minterm is covered by only 1 PI, that PI is Essential.
    # We select it, then remove all minterms it covers from the table.

    for minterm, pi_list in list(reversed_PI.items()).copy():
        if len(pi_list) == 1 and pi_list[0] not in essential_PI and minterm in reversed_PI:
            essential_PI.append(pi_list[0])
            del reversed_PI[minterm]
            
            # Deletes other minterms covered by this Essential PI
            for k, v in list(reversed_PI.items()).copy(): 
                if pi_list[0] in v: del reversed_PI[k]
                    
    # 4. Petrick's Method

    combinations = [[]]
    for lst in reversed_PI.values():
        new_combinations = []
        for combo in combinations:
            for item in lst:
                # Create candidate solution
                candidate = list(dict.fromkeys(combo + [item]))
                candidate.sort() # Sort to treat [A,B] and [B,A] as identical
                if candidate not in new_combinations:
                    new_combinations.append(candidate)
        combinations = new_combinations
        
    if len(combinations) > 2000:
        combinations.sort(key=len)
        combinations = combinations[:1000]

    # 5. Final Selection
    # Add Essentials back to the combinations
    for i in range(0, len(combinations)):
        combinations[i] += essential_PI
        combinations[i].sort()

    # Find the shortest solution
    minimum = min(map(len, combinations))
    for lst in combinations:
        if len(lst) == minimum:
            solutions.append(lst)

    # Convert binary strings back to variables (A, B', etc.)
    for item in solutions:
        solution = ""
        for implicant in item:
            if implicant == "-"*num_vars:
                solution = "1 + "
                break
            for i in range(0, num_vars):
                if implicant[i] == "1":
                    solution += variables[i]
                elif implicant[i] == "0":
                    solution += variables[i] + "'"
            solution += " + "
        solutions_variable.append(solution[:-3])

    return {
        "simplified_forms": solutions_variable,
        "solutions": solutions,
        "essential_prime_implicants": essential_PI,
        "prime_implicants": prime_implicants
    }


if __name__ == "__main__":
    print(
        """
=======================================================
        Logic minimizer using Quine McClusky
        v1.3 | Made By Ali Tarek
=======================================================
        """
    )

    try:
        raw_minterms = input(" [?] Minterms (e.g. 0, 1, 2): ").replace(" ", "").split(",")
        minterms = [int(x) for x in raw_minterms if x]
        
        raw_dc = input(" [?] Don't Cares (optional): ").replace(" ", "").split(",")
        dont_care = [int(x) for x in raw_dc if x]
        
        raw_vars = input(" [?] Variable Names (e.g. A, B, C): ").replace(" ", "").split(",")
        variables = [x for x in raw_vars if x]
    except ValueError:
        print("\n [!] Error: Invalid input. Please enter integers for minterms and don't cares.")
        raise SystemExit

    print("\n--------------------------------------------------")
    print(f" [+] Configuration: {len(variables)} Variables")
    print(f" [+] Processing {len(minterms)} Minterms and {len(dont_care)} Don't Cares...")
    
    result = quine(minterms, dont_care, variables)

    print("--------------------------------------------------")
    print(f" [i] Prime Implicants generated: {len(result['prime_implicants'])}")
    # Print up to 20 primes 
    count = 0
    if 0 < len(result['prime_implicants']) <= 10:
        print("    ", ", ".join(result['prime_implicants']))

    elif 10 < len(result['prime_implicants']) <= 20:
        print("    ", ", ".join(result['prime_implicants'][:10]) + ",")
        print("    ", ", ".join(result['prime_implicants'][10:20]))
        
    elif len(result['prime_implicants']) > 20:
        print("    ", ", ".join(result['prime_implicants'][:10]) + ",")
        print("    ", ", ".join(result['prime_implicants'][10:20]) + ",")
        print("    ", f"And {len(result['prime_implicants'])-20} more.")
    

    print(f"\n [i] Essential PIs identified: {len(result['essential_prime_implicants'])}")
    # Print all Essentials 
    if result['essential_prime_implicants']: 
        print("    ", ", ".join(result['essential_prime_implicants']))

    print("--------------------------------------------------\n")

    # 4. Solution Output
    print("Minimized Equations:")
    if not result["simplified_forms"]:
        print("  [!] No solution found (Check constraints or inputs).")
    
    for idx, eq in enumerate(result["simplified_forms"], 1):
        label = f"Option {idx}" if len(result["simplified_forms"]) > 1 else "Result"
        print(f"  > {label}:  F = {eq}")

    print("\n=======================================================\n")