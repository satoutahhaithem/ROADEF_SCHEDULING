# Roadef Scheduling
This repository contains a Python program designed for scheduling sessions for the ROADEF 2024 conference. The program encodes the problem into Maximum Satisfiability (Max-SAT), which can be then solved through dedicated solvers to efficiently allocate sessions while minimising working-group conflicts. 


# Dependencies 
Your machine must be equipped with Python 3 and pip. Follow the steps below to set up the environment and install the necessary packages. It's recommended to use a virtual environment for better management of dependencies.

```bash
pip install numpy
pip install python-sat[pblib,aiger]
```
