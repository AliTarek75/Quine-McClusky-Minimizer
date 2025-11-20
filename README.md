# Quine McClusky Logic Minimizer

A custom Python implementation of the Quine-McCluskey algorithm for minimizing Boolean functions.

I built this as a student project to challenge myself: no external libraries, just pure Python logic. It takes a list of minterms and outputs the simplified Boolean equation. It is probably inefficient in some areas, So if you find any errors or unexpected outputs. Feel free to report them. 

## What it does
* Converts complex truth tables made from minterms and don't cares into the simplest possible equations.
* Uses Petrick's Method to find the best solution even when there are no obvious "essential" terms.
* It shows all possible solutions, If there are two equally good answers, it shows both.

## Technical details
Even though this is a scratch implementation using strings which are slow on their own, I tried to add several optimizations, by tracking minterm coverage during the merge phase to avoid expensive recalculation at the end, and detecting essential terms early to shrink the table before doing the heavy calculations in the Petrick's phase.

## Usage

1.  Run the script:
    ```bash
    python logic_minimizer.py
    ```
2.  Enter your values when prompted:
    * **Minterms:** `0, 1, 2, 5, 6, 7`
    * **Variables:** `A, B, C`

## Example Output
```text
 [+] Configuration: 3 Variables
 [+] Processing 6 Minterms and 0 Don't Cares...
--------------------------------------------------
 [i] Prime Implicants generated: 6
     1-1, -10, 0-0, -01, 11-, 00-

 [i] Essential PIs identified: 0
--------------------------------------------------

Minimized Equations:
  > Option 1:  F = BC' + A'B' + AC
  > Option 2:  F = B'C + A'C' + AB
```
