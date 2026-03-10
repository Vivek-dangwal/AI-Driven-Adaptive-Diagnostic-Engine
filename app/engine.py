def update_ability(current_ability: float, difficulty: float, is_correct: bool):
    # 'k' is the sensitivity. A small 'k' means the score moves slowly.
    k = 0.15 
    
    if is_correct:
        # If right, we increase the score[cite: 24].
        # We give more credit if they solved a hard question!
        new_ability = current_ability + (k * (1 - current_ability) * difficulty)
    else:
        # If wrong, we decrease the score[cite: 25].
        # We drop the score more if they missed an easy question!
        new_ability = current_ability - (k * current_ability * (1 - difficulty))
    
    # The assignment says score must stay between 0.1 and 1.0[cite: 18].
    return round(max(0.1, min(1.0, new_ability)), 2)