from pysat.formula import *
from pysat.pb import EncType as pbenc
from pysat.pb import *
from pysat.card import *
from pysat.solvers import *
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
import sys

# This code require at least two argument when running the command 
if len(sys.argv) < 3:
    print("You must specify the year and maxparrallel session as a parameter (e.g., python3 Scheduling_Problem.py 2024 11)")
    sys.exit(1)

# recover the first argument
data_set_choice = sys.argv[1]

# recover the second parameter 
max_parallel_sessions = int(sys.argv[2]) 

# The third parameter is to say if you want to use it with or without z variable
# Default to 1, adjust as needed
isWithZ = int(sys.argv[3]) if len(sys.argv) > 3 else 1

# The fourth parameter is to change the encoding to cardNetwork for cardianality and best for PBEnc 
# Default to 1, adjust as needed
encType = int(sys.argv[4]) if len(sys.argv) > 4 else 1 

if isWithZ != 1:
    print("You chose to use without variable z. To use with the z variable please enter 0 as the third parameter.")

if encType != 1:
    print("You chose to use Card Best Encoding. To use sort network please enter 0 as the fourth parameter.")


# Choose data set based on the argument (Year selected)
if data_set_choice == "2024":
    if (max_parallel_sessions < 9 ): 
        print ("max_parallel_sessions must more than 9")
        sys.exit(1) 
    else:
        from Data.ROADEF2021 import conference_sessions, slots, papers_range, working_groups, np, npMax, session_groups
elif data_set_choice == "2023":
    if (max_parallel_sessions < 11 ): 
        print ("max_parallel_sessions must be more than 12")
        sys.exit(1) 
    else:
        from Data.ROADEF2022 import conference_sessions, slots, papers_range, working_groups, np, npMax, session_groups 
elif data_set_choice == "2022":
    if (max_parallel_sessions < 10 ): 
        print ("max_parallel_sessions must be more than 11")
        sys.exit(1) 
    else:
        from Data.ROADEF2023 import conference_sessions, slots, papers_range, working_groups, np, npMax, session_groups 
elif  data_set_choice == "2021":
    if (max_parallel_sessions < 4 ): 
        print ("max_parallel_sessions must be more than 5")
        sys.exit(1) 
    else:
        from Data.ROADEF2024 import conference_sessions, slots, papers_range, working_groups, np, npMax, session_groups  
else:
    print("The data available for 2024 , 2023 , 2022 and 2021 only")
    sys.exit(1)





length_of_paper_range = len(papers_range)
if (encType!=0):
    globalEncType = EncType.cardnetwrk
else:
    globalEncType = EncType.sortnetwrk






# Initialize the weighted clause normal form (WCNF) for the constraints
constraints = WCNF()


# Function to compute variable index for session-slot-paper combination
def var_x(s, c, l):
    return (s-1)*slots *length_of_paper_range  + (c-1)*length_of_paper_range + l
    
    

# Function to decode the variable index back to session, slot, and paper count
def decode_var_x(x, slots, papers_range_length):
    # Adjust for 1-indexing
    x -= 1  
    l = x % papers_range_length + 1
    x //= papers_range_length
    c = x % slots + 1
    s = x // slots + 1
    return s, c, l

# Compute the maximum index for var_x
max_var_x = var_x(conference_sessions, slots, length_of_paper_range)


# Function to compute variable index for session-slot (z variable)
def var_z(s, c): 
    return max_var_x + (s - 1) * slots + c

# Define the last variable 
if (isWithZ!=0):
    max_var_z = var_z(conference_sessions, slots)  
    y_var = max_var_z
else:
    max_var_x = var_x(conference_sessions, slots, length_of_paper_range)
    y_var = max_var_x




# First Constraint: At most one amount of papers chosen for a (session, slot) pair
for s in range(1, conference_sessions + 1):
    for c in range(1, slots + 1):
        vars_for_s_c = []
        for l in range(1 , length_of_paper_range + 1):
            vars_for_s_c.append(var_x(s, c, l))
        amo_clause = CardEnc.atmost(lits=vars_for_s_c, bound=1, top_id=y_var,encoding=globalEncType) 
        y_var=amo_clause.nv
        constraints.extend(amo_clause.clauses)
####################################################################################        





# Second Constraint: Subdivision of a session into slots covers all the papers in the session
for s in range(1, conference_sessions +1):
    aux_vars = []  
    aux_weight = []  
    for c in range(1,slots + 1):
        for l in range(1,length_of_paper_range+1):
            aux_vars.append(var_x(s, c, l))
            aux_weight.append(papers_range[l-1])
    if (encType!=0):
        eq_clause = PBEnc.equals(lits=aux_vars, weights=aux_weight,bound=np[s-1], top_id=y_var, encoding=pbenc.best)
    else:
        eq_clause = PBEnc.equals(lits=aux_vars, weights=aux_weight,bound=np[s-1], top_id=y_var, encoding=pbenc.sortnetwrk)
    y_var=eq_clause.nv
    constraints.extend(eq_clause.clauses)
####################################################################################





# Third Constraint : The subdivision respects the maximum length of each slot
for s in range(1, conference_sessions + 1):
    for c in range(1, slots + 1):
        for l in range(1,length_of_paper_range+1):
            if papers_range[l-1] > npMax[c-1]:
               # I create a constraint using the negation of x when l exceeds npMax(c).
                constraints.append([-var_x(s, c, l)])
####################################################################################
                



# Fourth Constraint: Number of parallel sessions is not exceeded for each slot
if (isWithZ!=0):
    for c in range(1, slots + 1):
        neg_z_vars = []
        for s in range(1, conference_sessions + 1):
            neg_z_vars.append(-var_z(s, c))
        atmost_clause = CardEnc.atmost(lits=neg_z_vars, bound=max_parallel_sessions, top_id=y_var, encoding=globalEncType)
        y_var=atmost_clause.nv
        constraints.extend(atmost_clause.clauses)
else:
    for c in range(1, slots + 1):
        x_vars = []
        for s in range(1, conference_sessions + 1):
            for l in range(1,length_of_paper_range+1):
                x_vars.append(var_x(s,c,l))
        atmost_clause = CardEnc.atmost(lits=x_vars, bound=max_parallel_sessions, top_id=y_var, encoding=globalEncType)
        y_var=atmost_clause.nv
        constraints.extend(atmost_clause.clauses)
####################################################################################



if (isWithZ!=0):
    # Implementing the equivalence transformation for session-slot (z variable)
    for s in range(1, conference_sessions + 1):
        for c in range(1, slots + 1):
            z_var = var_z(s, c)
            x_vars=[]
            for l in range(1,length_of_paper_range+1):
                x_vars.append(var_x(s, c, l))
            or_clause = x_vars + [z_var]
            constraints.append(or_clause)

            for x in x_vars:
                constraints.append([-z_var, -x])
    ####################################################################################




# constraint test
####################################################################################
# for s in range(1, conference_sessions+1):
#     if (np[s-1]<6): 
#         for c in range(1,slots+1):
#             for l in range(1,length_of_paper_range+1):
#                 if (papers_range[l-1]!=np[s-1]):
#                     constraints.append([-var_x(s,c,l)])
####################################################################################
            



# Soft Constraints to Minimize Working-Group Conflicts
# Iterate over all possible pairs of sessions (s1, s2), ensuring s1 is less than s2 to avoid duplicates
for s1 in range(1, conference_sessions + 1):

    for s2 in range(s1 + 1, conference_sessions + 1):  # Ensure s1 < s2
        # Identify common working groups between the two sessions     
        common_groups = set(session_groups[s1 - 1]).intersection(session_groups[s2 - 1])

        # For each slot, check if the common groups between these two sessions lead to a conflict
        for c in range(1, slots + 1):
            for g in common_groups:
                # Create a new variable for each potential conflict (increment y_var)
                y_var = y_var + 1

                # Add a soft constraint for this potential conflict with a weight of 1.
                # This means the solver will try to avoid this situation but can still accept it at a cost
                constraints.append([-y_var], weight=1)  
                if (isWithZ!=0):
                # Hard Constraint : Add a constraint to indicate a conflict if both sessions s1 and s2 are scheduled in the same slot c. 
                    constraints.append([var_z(s1,c),var_z(s2,c),y_var])
                else:
                    for l1 in range(1,length_of_paper_range+1):
                            for l2 in range(1,length_of_paper_range+1):
                                # Create a new variable for each potential conflict (increment y_var)
                                # Add a soft constraint for this potential conflict with a weight of 1.
                                # This means the solver will try to avoid this situation but can still accept it at a cost
                                # Hard Constraint : Add a constraint to indicate a conflict if both sessions s1 and s2 are scheduled in the same slot c. 
                                constraints.append([-var_x(s1,c,l1),-var_x(s2,c,l2),y_var])



# for s1 in range(1, conference_sessions + 1):

#     for s2 in range(s1 + 1, conference_sessions + 1):  # Ensure s1 < s2
#         # Identify common working groups between the two sessions     
#         common_groups = set(session_groups[s1 - 1]).intersection(session_groups[s2 - 1])

#         # For each slot, check if the common groups between these two sessions lead to a conflict
#         for c in range(1, slots + 1): 
#                 for g in common_groups:
#                         y_var = y_var + 1
#                         constraints.append([-y_var], weight=1) 
#                         for l1 in range(1,length_of_paper_range+1):
#                             for l2 in range(1,length_of_paper_range+1):
#                                 # Create a new variable for each potential conflict (increment y_var)
#                                 # Add a soft constraint for this potential conflict with a weight of 1.
#                                 # This means the solver will try to avoid this situation but can still accept it at a cost
#                                 # Hard Constraint : Add a constraint to indicate a conflict if both sessions s1 and s2 are scheduled in the same slot c. 
#                                 constraints.append([-var_x(s1,c,l1),-var_x(s2,c,l2),y_var])
    ####################################################################################



# Specific Constraint for Session 34:
# This constraint ensures that session 34 is assigned only to slots 5, 6, or 7.
if (data_set_choice=="2024"):
    print((data_set_choice=="2024"))
    if (isWithZ!=0):
        for i in range (1,5):
            constraints.append([var_z(34,i)])  
    else:
        for i in range (1,5):
            for l in range(1,length_of_paper_range+1):
                constraints.append([-var_x(34,i,l)])         

# ####################################################################################

# constraints.to_file("instance/"+data_set_choice+"/"+str(max_parallel_sessions)+"_session_file.wcnf")
if (isWithZ==0 and encType==0):
    constraints.to_file("./Benchmark/BasicModel/ROADEF_"+data_set_choice+"_"+str(max_parallel_sessions))
elif (isWithZ!=0 and encType==0):
    constraints.to_file("./Benchmark/EnhancedModel/ROADEF_"+data_set_choice+"_"+str(max_parallel_sessions))
else:
    constraints.to_file("./Benchmark/EnhancedModelEnc/ROADEF_"+data_set_choice+"_"+str(max_parallel_sessions))





# Assuming other parts of your code (constraint definitions, SAT model setup) are correctly implemented

def display_assignments_by_slot_with_counts(model, slots, papers_range, conference_sessions):
    print("enter display assignement")
    slot_assignments = {c: {} for c in range(1, slots + 1)}  # Initialize dictionaries for each slot

    # Processing the model to populate slot assignments
    for var in range(max_var_x):
        modelI= model[var]
        if modelI > 0:
            s, c, l = decode_var_x(model[var], slots, length_of_paper_range)
            print(f"  Conference Session {s} in slot {c} with {papers_range[l-1]} papers ")          
        


# To solve the model and display the assignement decomment this part of code 
# with RC2(constraints, solver="Cadical153") as solver:
#     for model in solver.enumerate():
#         print('Model has cost:', solver.cost)
#         # print('Model:', solver.model)

# #         display_assignments_by_slot_with_counts(model, slots, papers_range, conference_sessions)
# #         break  



