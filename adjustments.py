
def calculate_adjustments(subject_info, row):
    # Stub logic: simple AG SF difference adjustment
    subject_sqft = subject_info.get("sqft", 0)
    comp_sqft = row.get("Above Grade Finished Area", 0)
    ag_diff = comp_sqft - subject_sqft
    ag_adj_rate = 40  # $/sf
    total_adj = -ag_diff * ag_adj_rate
    return total_adj, ag_adj_rate, ag_diff
