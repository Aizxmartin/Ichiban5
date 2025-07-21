def calculate_adjustments(subject_info, comp_row):
    AG_RATE = 40  # $/sf for above grade
    subject_ag_sf = subject_info.get("sqft", 0)
    comp_ag_sf = comp_row.get("AG SF", comp_row.get("Above Grade Finished Area", 0))
    ag_diff = subject_ag_sf - comp_ag_sf
    ag_adjustment = ag_diff * AG_RATE
    total_adjustment = ag_adjustment
    return total_adjustment, ag_adjustment, ag_diff
