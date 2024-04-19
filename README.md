    # Scheduling Problem for Roadef
    This repository contains a Python program designed for scheduling sessions for the ROADEF 2024 conference. The program encodes the problem into Maximum Satisfiability (Max-SAT) , which can be then solved through dedicated solvers to efficiently allocate sessions while minimising working-group conflicts.

    # Installation Instructions
    Before running the program, ensure you have Python 3 and pip installed on your system and install the NumPy and PySAT packages:

    # for preference create virtual envirement 

    ```bash
    python3 -m venv myenv
    source myenv/bin/activate
    ```


    ```bash
    pip install numpy
    pip install python-sat[pblib,aiger]
    pip install python-sat
    ```