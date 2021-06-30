import re


def wff_status(of_fmla: str) -> bool:
    of_fmla = re.sub("\s", "", f"({of_fmla})")  # No whitespaces and extra parens.
    of_fmla = re.sub("[A-T]", "A", of_fmla)  # Constant predicates as "A".
    of_fmla = re.sub("[a-t]", "a", of_fmla)  # Constants as "a".
    of_fmla = of_fmla.replace("⊥", "(A∧¬A)")  # Falsum as "(A∧¬A)"
    of_fmla = re.sub("(?P<iden>[au-z]=[au-z])", "(\g<iden>)", of_fmla)  # Parens around identity statements.
    of_fmla = re.sub("(?P<lq>«)(?P<dec>.+?)(?P<rq>»)", "\g<lq>(\g<dec>)\g<rq>", of_fmla)  # Parens inside declarations.
    if ":" in of_fmla:
        return False
    of_fmla = re.sub("(?P<qnt>[∀∃])(?P<dom>[u-zU-Zφχψ])", "\g<qnt>\g<dom>:", of_fmla)  # Colons after quantifiers.
    of_fmla = re.sub("(?P<atm>[φχψ])", "(\g<atm>)", of_fmla)  # Parens around third-order atomics.
    of_fmla = re.sub("(?P<atm>[AU-Z]«.+?»*[au-z]*«.+?»*[au-z]*)", "(\g<atm>)", of_fmla)  # Parens around all atomics.
    of_fmla = re.sub("(?P<atm>([AU-Z][au-z]*))", "(\g<atm>)", of_fmla)  # Parens around non-quote atomics.
    of_fmla = re.sub("\((?P<atm>[AU-Z][au-z]*)\)(?P<qt>«)", "\g<atm>\g<qt>", of_fmla)  # Correct "(Aa)«.+?»" error.
    of_fmla = re.sub("(?P<qnt>[∀∃])\(*(?P<var>.+?)\)*:", "\g<qnt>\g<var>:", of_fmla)  # Correct "∀(U):" error.
    of_fmla = re.sub("\((?P<dec>«.+?»)\)", "\g<dec>", of_fmla)  # Correct "(«.+?»)" error.
    print(of_fmla, end="\n\n")
    # Instantiate all variables.
    if of_fmla[-1] == ":":
        return False
    while ":" in of_fmla:
        col_cntA = of_fmla.count(":")
        # Get the rightmost slice of the formula.
        right_slice = str()
        for c in range(len(of_fmla) - 1, -1, -1):
            if (of_fmla[c] in ["∀", "∃"]) and (of_fmla[c + 1:].count(":") == 1):
                right_slice = of_fmla[c:]
                break
        if len(right_slice) < 4:  # The scope must be more than just a quantifier statement.
            return False
        if (right_slice[2] != ":") or (right_slice[1] not in list("uvwxyzUVWXYZφχψ")):  # Only one variable allowed.
            return False
        # Find and lop off the portion of the formula that does not fall under right_slice's scope to get quant_sub.
        quant_subfmla = str()
        for d in range(4, len(right_slice)):
            if (right_slice[0:d].count("(") == right_slice[0:d].count(")")) and (right_slice[0:d].count("(") > 0):
                quant_subfmla = right_slice[0:d]
                break
        if len([a for a in list(quant_subfmla) if a == quant_subfmla[1]]) < 2:  # Instantiation must occur.
            return False
        print(quant_subfmla)
        inst_subfmla: str = str()
        if quant_subfmla[1] in list("uvwxyz"):
            inst_subfmla = quant_subfmla[3:].replace(quant_subfmla[1], "a")
        elif quant_subfmla[1] in list("UVWXYZφχψ"):
            inst_subfmla = quant_subfmla[3:].replace(quant_subfmla[1], "A")
        print(inst_subfmla)
        of_fmla = inst_subfmla.join(of_fmla.rsplit(quant_subfmla, 1))
        # /questions/2556108/rreplace-how-to-replace-the-last-occurrence-of-an-expression-in-a-string
        print(of_fmla, end="\n\n")
        col_cntB = of_fmla.count(":")
        if col_cntA == col_cntB:  # Every loop must register an instantiation.
            return False
    # Reduce the proposition to "A".
    while of_fmla != "A":
        fmla_len_a = len(of_fmla)
        of_fmla = re.sub("Aa*", "A", of_fmla)  # Replace atomic predicates with "A".
        of_fmla = re.sub("a=a", "A", of_fmla)  # Replace "a=a" with "A".
        of_fmla = re.sub("[□◇¬]+A", "A", of_fmla)  # Replace unary leads to predicates with "A".
        of_fmla = re.sub("\(A[∨∧→↔]A\)", "A", of_fmla)  # Replace binary sentences in parens with "A".
        of_fmla = of_fmla.replace("«A»", "a").replace("(A)", "A")  # Replace declared atomics with "a"...
        # ... and atomics in parens with "A".
        print(of_fmla)
        fmla_len_b = len(of_fmla)
        if fmla_len_a == fmla_len_b:
            return False
        elif of_fmla == "A":
            return True


def clean(fmla: str) -> str:
    paren_depths = [fmla[0:a + 1].count("(") - fmla[0:a + 1].count(")") for a in range(0, len(fmla))]
    if max(paren_depths) == 0:
        return fmla
    # Begin populating a dictionary.
    sub_dict = dict()
    while max(paren_depths) > 0:
        max_left = paren_depths.index(max(paren_depths))
        max_right = max_left + paren_depths[max_left:].index(max(paren_depths) - 1) + 1
        subfmla = fmla[max_left:max_right]
        fmla = fmla.replace(subfmla, f"Φ{len(sub_dict)}")
        sub_dict[f"Φ{len(sub_dict)}"] = subfmla
        paren_depths = [fmla[0:a + 1].count("(") - fmla[0:a + 1].count(")") for a in range(0, len(fmla))]
    # Remove excess parentheses from any sub_dict value that contains no binary operator.
    for k in sub_dict.keys():
        if len(re.split("[∨∧→↔]", sub_dict[k])) == 1:
            sub_dict[k] = sub_dict[k].replace("(", "").replace(")", "")
    # Rebuild the fmla with their respective sub_dict entries.
    for k in range(len(sub_dict) - 1, -1, -1):
        fmla = fmla.replace(f"Φ{k}", sub_dict[f"Φ{k}"])
    # Handle the absolute outermost parentheses.
    paren_depths = [fmla[0:a + 1].count("(") - fmla[0:a + 1].count(")") for a in range(0, len(fmla))]
    if len(paren_depths) > 0:
        while paren_depths.index(0) == len(paren_depths) - 1:
            fmla = fmla[1:len(fmla) - 1]
            paren_depths = [fmla[0:a + 1].count("(") - fmla[0:a + 1].count(")") for a in range(0, len(fmla))]
    return fmla


def main_op(of_fmla: str) -> tuple:
    paren_depths = [of_fmla[0:a + 1].count("(") - of_fmla[0:a + 1].count(")") for a in range(0, len(of_fmla))]
    valencies = [2 if a in list("∨∧→↔") else 1 if a in list("¬∀∃□◇") else 0.5 if a == "=" else 0
                 for a in list(of_fmla)]
    op_tuples = list(zip(paren_depths, valencies, [a for a in range(0, len(of_fmla))]))
    op_tuples.sort(key=lambda i: (i[0], -i[1], i[2]))
    return of_fmla, of_fmla[op_tuples[0][2]], op_tuples[0][2]


def break_down(fmla: str) -> list:
    mo = main_op(fmla)
    if mo[1] in list("∨∧→↔"):
        return [fmla, mo[1], clean(fmla[0:mo[2]]), clean(fmla[mo[2] + 1:])]
    elif mo[1] in list("¬□◇"):
        return [fmla, mo[1], clean(fmla[1:])]
    elif mo[1] in list("∀∃"):
        return [fmla, fmla[mo[2]:mo[2] + 2], clean(fmla[2:])]
    else:
        return [fmla, mo[1], str()]


'''All of the E-rules, I-rules, and their related D-rules or C-rules go here.'''


def get_consts(from_fmlae: list, arb: bool) -> list:
    char_list = list("".join(from_fmlae))
    consts = list("abcdefghijklmnopqrst")
    if not arb:
        spec_consts = list(set([a for a in char_list if a in consts]))
        spec_consts.sort()
        return spec_consts
    else:
        arb_consts = list(set([a for a in consts if a not in char_list]))
        arb_consts.sort()
        return arb_consts


def instantiate(this_fmla: str, with_const: str) -> str:
    this_var = this_fmla[1]
    this_fmla = this_fmla[2:]
    # If there are internal scopes with the same variable, sub those in with phi props to be subbed out later.
    sub_dict = dict()
    while len(re.split(f"[∀∃]{this_var}", this_fmla)) > 1:
        split_fmla = re.split(f"[∀∃]{this_var}", this_fmla)
        right_subfmla = this_fmla[len("__".join(split_fmla[:-1])):]
        if right_subfmla[2] == "(":
            # Tally the parens to 0, replace the true sub-formula with the sub_dict key, and populate sub_dict.
            right_ind = int()
            paren_tally = 0
            for c in range(2, len(right_subfmla)):
                if right_subfmla[c] == "(":
                    paren_tally += 1
                elif right_subfmla[c] == ")":
                    paren_tally -= 1
                if paren_tally == 0:
                    right_ind = c + 1
                    break
            this_fmla = this_fmla.replace(right_subfmla[0:right_ind], f"Φ{len(sub_dict)}")
            sub_dict[f"Φ{len(sub_dict)}"] = right_subfmla[0:right_ind]
        elif ")" in right_subfmla:
            right_ind = list(right_subfmla).index(")")
            this_fmla = this_fmla.replace(right_subfmla[0:right_ind], f"Φ{len(sub_dict)}")
            sub_dict[f"Φ{len(sub_dict)}"] = right_subfmla[0:right_ind]
        else:
            this_fmla = this_fmla.replace(right_subfmla, f"Φ{len(sub_dict)}")
            sub_dict[f"Φ{len(sub_dict)}"] = right_subfmla
    # Replace the correctly subbed formula with the constant.
    this_fmla = this_fmla.replace(this_var, with_const)
    # Rebuild this_fmla with their respective sub_dict entries.
    for k in range(len(sub_dict) - 1, -1, -1):
        this_fmla = this_fmla.replace(f"Φ{k}", sub_dict[f"Φ{k}"])
    return clean(this_fmla)


def generalize(this_fmla: str, this_const: str, to_var: str, q_type: str = "∀") -> list:
    generalizations = list()
    if q_type == "∃":  # Build a power set of all matching constants in the proposition.
        gen_inds = [a for a in range(0, len(this_fmla)) if this_fmla[a] == this_const]
        gen_inds_len = len(gen_inds)
        gen_inds_poset = list()
        for i in range(1, 1 << gen_inds_len):
            gen_inds_poset.append([gen_inds[a] for a in range(gen_inds_len) if (i & (1 << a))])
        for gip in gen_inds_poset:
            new_gen = ''.join([to_var if a in gip else this_fmla[a] for a in range(0, len(this_fmla))])
            generalizations.append(clean(f"∃{to_var}({new_gen})"))
    elif q_type == "∀":
        generalizations = [clean(f"∀{to_var}({this_fmla.replace(this_const, to_var)})")]
    return generalizations


def try_falsum_elim(on_ln: list, in_proof: list) -> list:
    # This proof needs one premise, the on_ln.
    # If the falsum is the stated target for an SM line, don't do ⊥E.
    sm_lns = [a for a in in_proof if ("SM" in a[3]) and (not a[5])]
    if sm_lns != list():
        if sm_lns[-1][4][0] == "⊥":
            return in_proof
    if in_proof[-1][7] != list():
        props = [a[1] for a in in_proof[-1][7][0] if is_unique(a[1], in_proof) and (a[1] != "⊥")]
        if props != list():
            ll = in_proof[-1]
            in_proof.append([ll[0] + 1, ll[1], props[0], "⊥E", [on_ln[0]], ll[5], ll[6], ll[7]])
            return in_proof
    return in_proof


def try_falsum_intro(for_goal: tuple, in_proof: list) -> list:
    # This proof needs two premises.
    if is_unique(for_goal[1], in_proof):
        srts = [a[2] for a in in_proof if not a[5]]
        indices = [a[0] for a in in_proof if not a[5]]
        neg_indices = [indices[srts.index(clean(f"¬({a})"))] if clean(f"¬({a})") in srts else -1 for a in srts]
        cont_inds = [a for a in list(zip(indices, neg_indices)) if -1 not in a]
        cont_inds.sort(key=lambda i: max(i))
        if cont_inds != list():
            prem_1_lines = [a for a in in_proof if (a[0] == cont_inds[0][0]) and (not a[5])]
            prem_2_lines = [a for a in in_proof if (a[0] == cont_inds[0][1]) and (not a[5])]
            if (prem_1_lines != list()) and (prem_2_lines != list()):
                ll = in_proof[-1]
                jst_lns = [prem_1_lines[0][0], prem_2_lines[0][0]]
                in_proof.append([ll[0] + 1, ll[1], for_goal[1], "⊥I", jst_lns, ll[5], ll[6], ll[7]])
                return in_proof
    # If ⊥I fails, set targets based on available lines.
    for tgt in [(a[0], break_down(a[2])[2]) if main_op(a[2])[1] == "¬" else (a[0], clean(f"¬({a[2]})"))
                for a in in_proof if not a[5]]:
        if in_proof[-1][7] != list():
            new_tree = build_tree(from_prop=tgt[1], start_val=f"C_{in_proof[-1][1]}_0|{tgt[0]}|⊥I", sms=False)
            in_proof[-1][7][0] = in_proof[-1][7][0] + [a for a in new_tree if a not in in_proof[-1][7][0]]
    return in_proof


def try_not_elim(on_ln: list, in_proof: list, intn: bool) -> list:
    # This proof needs one premise, the on_ln.
    bk = break_down(on_ln[2])
    sbk = break_down(bk[2])
    if intn:
        if len(on_ln[2]) > 3:
            if (bk[1] == "¬") and (on_ln[2][0:3] == "¬¬¬"):
                prop = break_down(bk[2])[2]
                if is_unique(prop, in_proof):
                    ll = in_proof[-1]
                    in_proof.append([ll[0] + 1, ll[1], prop, "¬E", [on_ln[0]], ll[5], ll[6], ll[7]])
                    return in_proof
    elif not intn:
        if (bk[1] == "¬") and (sbk[1] == "¬"):
            prop = break_down(bk[2])[2]
            if is_unique(prop, in_proof):
                ll = in_proof[-1]
                in_proof.append([ll[0] + 1, ll[1], prop, "¬E", [on_ln[0]], ll[5], ll[6], ll[7]])
                return in_proof
    # If ¬E fails, set intuitionistic decompositions as targets.
    if in_proof[-1][7] != list():
        dec_trees = list()
        # Decompose single negations.
        if sbk[1] == "∨":  # Handle: ¬(A∨B) ⊢ ¬A, ¬B
            tgt_d = clean(f"¬({sbk[2]})")
            if is_unique(tgt_d, in_proof):
                new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬∨D(1)")
                dec_trees.append(new_tree)
            tgt_d = clean(f"¬({sbk[3]})")
            if is_unique(tgt_d, in_proof):
                new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬∨D(2)")
                dec_trees.append(new_tree)
        elif sbk[1] == "∧":  # Handle: ¬(A∧B) ⊢ A→¬B, B→¬A
            tgt_d = clean(f"({sbk[2]})→¬({sbk[3]})")
            if is_unique(tgt_d, in_proof):
                new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬∧D(1)")
                dec_trees.append(new_tree)
            tgt_d = clean(f"({sbk[3]})→¬({sbk[2]})")
            if is_unique(tgt_d, in_proof):
                new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬∧D(2)")
                dec_trees.append(new_tree)
        elif sbk[1] == "→":  # Handle: ¬(A→B) ⊢ ¬¬A, ¬B
            tgt_d = clean(f"¬¬({sbk[2]})")
            if is_unique(tgt_d, in_proof):
                new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬→D(1)")
                dec_trees.append(new_tree)
            tgt_d = clean(f"¬({sbk[3]})")
            if is_unique(tgt_d, in_proof):
                new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬→D(2)")
                dec_trees.append(new_tree)
        elif sbk[1] == "↔":  # Handle: ¬(A↔B) ⊢ A→¬B, B→¬A, ¬A→¬¬B, ¬B→¬¬A
            tgt_d = clean(f"({sbk[2]})→¬({sbk[3]})")
            if is_unique(tgt_d, in_proof):
                new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬↔D(1)")
                dec_trees.append(new_tree)
            tgt_d = clean(f"({sbk[3]})→¬({sbk[2]})")
            if is_unique(tgt_d, in_proof):
                new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬↔D(2)")
                dec_trees.append(new_tree)
            tgt_d = clean(f"¬({sbk[2]})→¬¬({sbk[3]})")
            if is_unique(tgt_d, in_proof):
                new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬↔D(3)")
                dec_trees.append(new_tree)
            tgt_d = clean(f"¬({sbk[3]})→¬¬({sbk[2]})")
            if is_unique(tgt_d, in_proof):
                new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬↔D(4)")
                dec_trees.append(new_tree)
        elif "∃" in sbk[1]:  # Handle: ¬∃xAx ⊢ ∀x¬Ax
            if get_consts(from_fmlae=[a[2] for a in in_proof if not a[5]], arb=True) != list():
                ac = get_consts(from_fmlae=[a[2] for a in in_proof if not a[5]], arb=True)[0]
                inst = instantiate(this_fmla=bk[2], with_const=ac)
                tgt_d = generalize(this_fmla=clean(f"¬({inst})"), this_const=ac, to_var=sbk[1][1], q_type="∀")[0]
                if is_unique(tgt_d, in_proof):
                    new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬∃D")
                    dec_trees.append(new_tree)
        elif sbk[1] == "¬":  # Decompose double negations.
            s_sbk = break_down(sbk[2])
            if s_sbk[1] == "∨":  # Handle: ¬¬(A∨B) ⊢ ¬A→¬¬B, ¬B→¬¬A
                tgt_d = clean(f"¬({s_sbk[2]})→¬¬({s_sbk[3]})")
                if is_unique(tgt_d, in_proof):
                    new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬¬∨D(1)")
                    dec_trees.append(new_tree)
                tgt_d = clean(f"¬({s_sbk[3]})→¬¬({s_sbk[2]})")
                if is_unique(tgt_d, in_proof):
                    new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬¬∨D(2)")
                    dec_trees.append(new_tree)
            elif s_sbk[1] == "∧":  # Handle: ¬¬(A∧B) ⊢ ¬¬A, ¬¬B
                tgt_d = clean(f"¬¬({s_sbk[2]})")
                if is_unique(tgt_d, in_proof):
                    new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬¬∧D(1)")
                    dec_trees.append(new_tree)
                tgt_d = clean(f"¬¬({s_sbk[3]})")
                if is_unique(tgt_d, in_proof):
                    new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬¬∧D(2)")
                    dec_trees.append(new_tree)
            elif s_sbk[1] == "→":  # Handle: ¬¬(A→B) ⊢ ¬B→¬A
                tgt_d = clean(f"¬({s_sbk[3]})→¬({s_sbk[2]})")
                if is_unique(tgt_d, in_proof):
                    new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬¬→D")
                    dec_trees.append(new_tree)
            elif s_sbk[1] == "↔":  # Handle: ¬¬(A↔B) ⊢ ¬B→¬A, ¬A→¬B
                tgt_d = clean(f"(¬({s_sbk[3]})→¬({s_sbk[2]}))")
                if is_unique(tgt_d, in_proof):
                    new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬¬↔D(1)")
                    dec_trees.append(new_tree)
                tgt_d = clean(f"(¬({s_sbk[2]})→¬({s_sbk[3]}))")
                if is_unique(tgt_d, in_proof):
                    new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬¬↔D(2)")
                    dec_trees.append(new_tree)
            elif "∃" in s_sbk[1]:  # Handle: ¬¬∃xAx ⊢ ¬∀x¬Ax
                if get_consts(from_fmlae=[a[2] for a in in_proof if not a[5]], arb=True) != list():
                    ac = get_consts(from_fmlae=[a[2] for a in in_proof if not a[5]], arb=True)[0]
                    inst = instantiate(this_fmla=sbk[2], with_const=ac)
                    neg = clean(f"¬({inst})")
                    gen = generalize(this_fmla=neg, this_const=ac, to_var=s_sbk[1][1], q_type="∀")[0]
                    tgt_d = clean(f"¬({gen})")
                    if is_unique(tgt_d, in_proof):
                        new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬¬∃D")
                        dec_trees.append(new_tree)
            elif "∀" in s_sbk[1]:  # Handle: ¬¬∀xAx ⊢ ∀x¬¬Ax
                if get_consts(from_fmlae=[a[2] for a in in_proof if not a[5]], arb=True) != list():
                    ac = get_consts(from_fmlae=[a[2] for a in in_proof if not a[5]], arb=True)[0]
                    inst = instantiate(this_fmla=sbk[2], with_const=ac)
                    d_neg = clean(f"¬¬({inst})")
                    tgt_d = generalize(this_fmla=d_neg, this_const=ac, to_var=s_sbk[1][1], q_type="∀")[0]
                    if is_unique(tgt_d, in_proof):
                        new_tree = build_tree(from_prop=tgt_d, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|¬¬∀D")
                        dec_trees.append(new_tree)
        if dec_trees != list():
            new_tgts_ids = ["|".join(a[0].split("|")[1:]) for a in flatten_targets(in_proof) if "|" in a[0]]
            dec_id = "|".join(dec_trees[0][0][0].split("|")[1:])
            if dec_id not in new_tgts_ids:
                in_proof[-1][7] = dec_trees + in_proof[-1][7]
    return in_proof


def try_not_intro(for_goal: tuple, in_proof: list) -> list:
    # This proof needs two premises.
    # Check the ¬I derivation if the SM to discharge is the correct one: [A ... ⊥] ⊢ ¬A
    bk = break_down(for_goal[1])
    sm_lns = [a for a in in_proof if ("SM" in a[3]) and (not a[5])]
    if sm_lns != list():
        if (clean(f"¬({sm_lns[-1][2]})") == for_goal[1]) and (sm_lns[-1][3] == "SM¬I"):
            prem_1_ln = sm_lns[-1]  # Now verified, the first premise just is the last SM line.
            # The second premise is an open falsum that can serve as the discharge line.
            dch_lns = [a for a in in_proof if (a[2] == "⊥") and (not a[5])]
            if dch_lns != list():
                prem_2_ln = dch_lns[0]  # An open falsum above the SM means the discharge is two lines, so dch_lns[0].
                # The bk[3] has to be reiterated if it's at or above the SM line.
                if prem_2_ln[0] <= prem_1_ln[0]:
                    ll = in_proof[-1]
                    in_proof.append([ll[0] + 1, ll[1], "⊥", "R", [prem_2_ln[0]], ll[5], ll[6], ll[7]])
                    prem_2_ln = in_proof[-1]
                # All lines at or below the discharge line must be discharged.
                for ip_ln in in_proof:
                    if ip_ln[0] >= prem_1_ln[0]:
                        ip_ln[5] = True
                ll = in_proof[-1]
                jst_lns = [prem_1_ln[0], prem_2_ln[0]]
                ll[7] = [a for a in ll[7] if int(re.findall("_[0-9]+_", a[0][0])[0].replace("_", "")) <= ll[1]]
                in_proof.append([ll[0] + 1, ll[1] - 1, for_goal[1], "¬I", jst_lns, False, ll[6], ll[7]])
                return in_proof
    # Make SM and build targets for the following if ¬I fails: [A ... ⊥] ⊢ ¬A
    if not for_goal[2]:  # Don't run a ¬I proof on unpermitted goals.
        return in_proof
    if not is_unique(for_goal[1], in_proof):  # Don't run a ¬I proof if the goal or its double negation already exists.
        return in_proof
    if bk[2] in [a[2] for a in in_proof if not a[5]]:  # Don't run a ¬I proof if the assertion is already below it.
        return in_proof
    if is_contradicted(for_goal[1], in_proof):  # Don't run a ¬I proof if the goal is already contradicted somewhere.
        return in_proof
    if [a for a in in_proof if (a[2] == bk[2]) and (a[3] in ["SM¬I", "P"]) and (not a[5])] == list():
        in_proof[-1][7].insert(0, build_tree(from_prop=for_goal[1], start_val=f"C_{in_proof[-1][1] + 1}_"))
        ll = in_proof[-1]
        in_proof.append([ll[0] + 1, ll[1] + 1, bk[2], "SM¬I", [for_goal[1]], ll[5], ll[6], ll[7]])
        return in_proof
    return in_proof


def try_then_elim(on_ln: list, in_proof: list) -> list:
    # This proof needs two premises. on_ln is the major one.
    bk = break_down(on_ln[2])
    prem_2 = bk[2]
    prem_2_lns = [a for a in in_proof if (a[2] == prem_2) and (not a[5])]
    if prem_2_lns != list():
        prop = bk[3]
        if is_unique(prop, in_proof):
            ll = in_proof[-1]
            in_proof.append([ll[0] + 1, ll[1], prop, "→E", [on_ln[0], prem_2_lns[0][0]], ll[5], ll[6], ll[7]])
            return in_proof
    if on_ln[3] == "→I":  # Don't build targets for →E if the line, itself, resulted from →I.
        return in_proof
    # If →E fails, set the target.
    # If the negated consequent is present, the target is the negated consequent. Otherwise, it's the antecedent.
    if in_proof[-1][7] != list():
        if is_contradicted(bk[3], in_proof) or (bk[3] == "⊥") or are_contradictory(bk[2], bk[3]):
            tgt = clean(f"¬({bk[2]})")
            if is_unique(tgt, in_proof):
                new_tree = build_tree(from_prop=tgt, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|→E", sms=True)
                in_proof[-1][7] = [new_tree] + in_proof[-1][7]
        if is_unique(bk[2], in_proof):
            new_tree = build_tree(from_prop=bk[2], start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|→E", sms=False)
            in_proof[-1][7][0] = in_proof[-1][7][0] + [a for a in new_tree if a not in in_proof[-1][7][0]
                                                       if (a not in in_proof[-1][7][0]) and is_unique(a[1], in_proof)]
    return in_proof


def try_then_intro(for_goal: tuple, in_proof: list) -> list:
    # This proof needs two premises.
    # The first premise the last SM line, but only if its contained proposition's negation matches for_goal[1].
    # Check the →I derivation if the SM to discharge is the correct one: |A ... |B ⊢ A→B
    bk = break_down(for_goal[1])
    sm_lns = [a for a in in_proof if ("SM" in a[3]) and (not a[5])]
    if sm_lns != list():
        # Unlike ¬I, →I requires a target ID match, not just a string match.
        if (sm_lns[-1][3] == "SM→I") and (sm_lns[-1][4] == [for_goal[1]]):
            prem_1_ln = sm_lns[-1]  # Now verified, the first premise just is the last SM line.
            # The second premise is an open consequent that can serve as the discharge line.
            dch_lns = [a for a in in_proof if (a[2] == bk[3]) and (not a[5])]
            if dch_lns != list():
                prem_2_ln = dch_lns[0]  # An open bk[3] above the SM means the discharge is two lines, so dch_lns[0].
                # The bk[3] has to be reiterated if it's at or above the SM line.
                if prem_2_ln[0] <= prem_1_ln[0]:
                    ll = in_proof[-1]
                    in_proof.append([ll[0] + 1, ll[1], bk[3], "R", [prem_2_ln[0]], ll[5], ll[6], ll[7]])
                    prem_2_ln = in_proof[-1]
                # All lines at or below the discharge line must be discharged.
                for ip_ln in in_proof:
                    if ip_ln[0] >= prem_1_ln[0]:
                        ip_ln[5] = True
                ll = in_proof[-1]
                jst_lns = [prem_1_ln[0], prem_2_ln[0]]
                ll[7] = [a for a in ll[7] if int(re.findall("_[0-9]+_", a[0][0])[0].replace("_", "")) < ll[1]]
                in_proof.append([ll[0] + 1, ll[1] - 1, for_goal[1], "→I", jst_lns, False, ll[6], ll[7]])
                return in_proof
    if not is_unique(for_goal[1], in_proof):  # Don't run a →I proof if the goal already exists.
        return in_proof
    # Force →I proofs in certain cases, even if for_goal[2] is False.
    if not is_unique(bk[3], in_proof) and (for_goal[1] not in [a[4][0] for a in sm_lns if a[3] == "SM→I"]):
        # Handle: B ⊢ A→B (Weakening)
        in_proof[-1][7].insert(0, build_tree(from_prop=bk[3], start_val=f"C_{in_proof[-1][1] + 1}_"))
        ll = in_proof[-1]
        in_proof.append([ll[0] + 1, ll[1] + 1, bk[2], "SM→I", [for_goal[1]], ll[5], ll[6], ll[7]])
        return in_proof
    elif is_contradicted(bk[2], in_proof) and (for_goal[1] not in [a[4][0] for a in sm_lns if a[3] == "SM→I"]):
        # Handle: ¬A ⊢ A→B (Strengthening)
        in_proof[-1][7].insert(0, build_tree(from_prop=bk[3], start_val=f"C_{in_proof[-1][1] + 1}_"))
        ll = in_proof[-1]
        in_proof.append([ll[0] + 1, ll[1] + 1, bk[2], "SM→I", [for_goal[1]], ll[5], ll[6], ll[7]])
        return in_proof
    # Make SM and build targets for the following if →I fails: [A ... B] ⊢ A→B
    if not for_goal[2]:  # Don't run a →I proof on unpermitted goals.
        return in_proof
    # Handle: ¬A∨B ⊢ ¬A→(A→B), B→(A→B) ⊢ A→B (Material Implication)
    mi_tgts = [set(break_down(a)[2:]) for a in mine_props(in_proof, by_op="∨")]
    if {clean(f"¬({bk[2]})"), bk[3]} in mi_tgts:
        tgt_1 = clean(f"¬({bk[2]})→({for_goal[1]})")
        if is_unique(tgt_1, in_proof) and (tgt_1 not in [a[1] for a in flatten_targets(in_proof)]):
            in_proof[-1][7].insert(0, build_tree(from_prop=tgt_1, start_val=f"C_{in_proof[-1][1] + 1}_"))
            ll = in_proof[-1]
            in_proof.append([ll[0] + 1, ll[1] + 1, clean(f"¬({bk[2]})"), "SM→I", [tgt_1], ll[5], ll[6], ll[7]])
            in_proof[-1][7].insert(0, build_tree(from_prop=for_goal[1], start_val=f"C_{in_proof[-1][1] + 2}_"))
            ll = in_proof[-1]
            in_proof.append([ll[0] + 1, ll[1] + 1, bk[2], "SM→I", [for_goal[1]], ll[5], ll[6], ll[7]])
            return in_proof
        tgt_2 = clean(f"({bk[3]})→({for_goal[1]})")
        if is_unique(tgt_2, in_proof) and not is_unique(tgt_1, in_proof):
            in_proof[-1][7].insert(0, build_tree(from_prop=tgt_2, start_val=f"C_{in_proof[-1][1] + 1}_"))
            ll = in_proof[-1]
            in_proof.append([ll[0] + 1, ll[1] + 1, bk[3], "SM→I", [tgt_2], ll[5], ll[6], ll[7]])
            in_proof[-1][7].insert(0, build_tree(from_prop=for_goal[1], start_val=f"C_{in_proof[-1][1] + 2}_"))
            ll = in_proof[-1]
            in_proof.append([ll[0] + 1, ll[1] + 1, bk[2], "SM→I", [for_goal[1]], ll[5], ll[6], ll[7]])
            return in_proof
    if int(re.findall("_[0-9]+_", in_proof[-1][7][0][0][0])[0].replace("_", "")) < in_proof[-1][1]:
        # Don't run a →I proof if the target level is below the current level.
        return in_proof
    if bk[2] in [a[2] for a in in_proof if not a[5]]:  # Do not add an antecedent that's already established.
        return in_proof
    if "|" in for_goal[0]:  # If the SM would be to build conditionals on an already discharged line, don't start →I for it.
        fg_ln_num = int(for_goal[0].split("|")[1])
        if in_proof[fg_ln_num - 1][5]:
            return in_proof
    if [a for a in in_proof if (a[2] == bk[2]) and (a[3] == "SM→I") and (a[4] == [for_goal[1]]) and (not a[5])] == list():
        in_proof[-1][7].insert(0, build_tree(from_prop=bk[3], start_val=f"C_{in_proof[-1][1] + 1}_"))
        ll = in_proof[-1]
        in_proof.append([ll[0] + 1, ll[1] + 1, bk[2], "SM→I", [for_goal[1]], ll[5], ll[6], ll[7]])
        return in_proof
    return in_proof


def try_or_elim(on_ln: list, in_proof: list) -> list:
    bk = break_down(on_ln[2])
    sbk_l = break_down(bk[2])
    sbk_r = break_down(bk[3])
    conditionals = [a for a in in_proof if (main_op(a[2])[1] == "→") and (not a[5])]
    # The second and third premises rely first on a matching antecedent, and then a coincident consequent.
    prem_2_lns = [a for a in conditionals if break_down(a[2])[2] == bk[2]]
    prem_3_lns = [a for a in conditionals if break_down(a[2])[2] == bk[3]]
    prem_2_cnsqs = [break_down(a[2])[3] for a in prem_2_lns]
    prem_3_cnsqs = [break_down(a[2])[3] for a in prem_3_lns]
    if set(prem_2_cnsqs).intersection(set(prem_3_cnsqs)) != set():
        for p_c in list(set(prem_2_cnsqs).intersection(set(prem_3_cnsqs))):
            prop = p_c
            prem_2_jst_ln = [a for a in prem_2_lns if break_down(a[2])[3] == p_c][0]
            prem_3_jst_ln = [a for a in prem_3_lns if break_down(a[2])[3] == p_c][0]
            jst_lns = [on_ln[0], prem_2_jst_ln[0], prem_3_jst_ln[0]]
            if is_unique(prop, in_proof):
                ll = in_proof[-1]
                in_proof.append([ll[0] + 1, ll[1], prop, "∨E", jst_lns, ll[5], ll[6], ll[7]])
                return in_proof
    # If ∨E fails, the conditionals are needed as the targets.
    if in_proof[-1][7] != list():
        if "D" in in_proof[-1][7][0][0][0]:  # Do not admit ∨E for decompositions.
            return in_proof
        if is_contradicted(bk[2], in_proof) or is_contradicted(bk[3], in_proof):
            if is_contradicted(bk[2], in_proof):
                tgt_1 = clean(f"({bk[2]})→({bk[3]})")
                tgt_2 = clean(f"({bk[3]})→({bk[3]})")
            else:
                tgt_1 = clean(f"({bk[2]})→({bk[2]})")
                tgt_2 = clean(f"({bk[3]})→({bk[2]})")
        else:
            if [a for a in in_proof if (a[3] == "SM¬I") and (not a[5])] == list():
                tgt_consq = in_proof[-1][7][0][0][1]
            else:
                tgt_consq = "⊥"
            tgt_1 = clean(f"({bk[2]})→({tgt_consq})")
            tgt_2 = clean(f"({bk[3]})→({tgt_consq})")
        if is_unique(tgt_1, in_proof):
            new_tree = build_tree(from_prop=tgt_1, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|∨E(p2)")
            in_proof[-1][7][0] = in_proof[-1][7][0] + [a for a in new_tree if a not in in_proof[-1][7][0]]
            return in_proof
        if is_unique(tgt_2, in_proof):
            new_tree = build_tree(from_prop=tgt_2, start_val=f"C_{in_proof[-1][1]}_0|{on_ln[0]}|∨E(p3)")
            in_proof[-1][7][0] = in_proof[-1][7][0] + [a for a in new_tree if a not in in_proof[-1][7][0]]
            return in_proof
    return in_proof


def try_or_intro(for_goal: tuple, in_proof: list) -> list:
    # This proof needs one premise.
    bk = break_down(for_goal[1])
    if is_unique(for_goal[1], in_proof):
        prem_1_lines = [a for a in in_proof if (a[2] in bk[2:4]) and (not a[5])]
        if prem_1_lines != list():
            ll = in_proof[-1]
            in_proof.append([ll[0] + 1, ll[1], for_goal[1], "∨I", [prem_1_lines[0][0]], ll[5], ll[6], ll[7]])
            return in_proof
    return in_proof


def try_and_elim(on_ln: list, in_proof: list) -> list:
    # If the reason for the conjunction is, itself, ∧I, then it was in service of a goal, so ∧E should not happen.
    if on_ln[3] == "∧I":
        return in_proof
    # This proof needs one premise, the on_ln.
    bk = break_down(on_ln[2])
    prop_1 = bk[2]
    prop_2 = bk[3]
    if is_unique(prop_1, in_proof):
        ll = in_proof[-1]
        in_proof.append([ll[0] + 1, ll[1], prop_1, "∧E", [on_ln[0]], ll[5], ll[6], ll[7]])
    if is_unique(prop_2, in_proof):
        ll = in_proof[-1]
        in_proof.append([ll[0] + 1, ll[1], prop_2, "∧E", [on_ln[0]], ll[5], ll[6], ll[7]])
    return in_proof


def try_and_intro(for_goal: tuple, in_proof: list) -> list:
    # This proof needs two premises.
    bk = break_down(for_goal[1])
    if is_unique(for_goal[1], in_proof):
        prem_1_lines = [a for a in in_proof if (a[2] == bk[2]) and (not a[5])]
        prem_2_lines = [a for a in in_proof if (a[2] == bk[3]) and (not a[5])]
        if (prem_1_lines != list()) and (prem_2_lines != list()):
            ll = in_proof[-1]
            jst_lns = [prem_1_lines[0][0], prem_2_lines[0][0]]
            in_proof.append([ll[0] + 1, ll[1], for_goal[1], "∧I", jst_lns, ll[5], ll[6], ll[7]])
            return in_proof
    return in_proof


def try_iff_elim(on_ln: list, in_proof: list) -> list:
    # This proof needs one premise, the on_ln.
    bk = break_down(on_ln[2])
    prop_1 = clean(f"({bk[2]})→({bk[3]})")
    prop_2 = clean(f"({bk[3]})→({bk[2]})")
    if is_unique(prop_1, in_proof):
        ll = in_proof[-1]
        in_proof.append([ll[0] + 1, ll[1], prop_1, "↔E", [on_ln[0]], ll[5], ll[6], ll[7]])
    if is_unique(prop_2, in_proof):
        ll = in_proof[-1]
        in_proof.append([ll[0] + 1, ll[1], prop_2, "↔E", [on_ln[0]], ll[5], ll[6], ll[7]])
    return in_proof


def try_iff_intro(for_goal: tuple, in_proof: list) -> list:
    # This proof needs two premises.
    if is_unique(for_goal[1], in_proof):
        bk = break_down(for_goal[1])
        prem_1_lines = [a for a in in_proof if (a[2] == clean(f"({bk[2]})→({bk[3]})")) and (not a[5])]
        prem_2_lines = [a for a in in_proof if (a[2] == clean(f"({bk[3]})→({bk[2]})")) and (not a[5])]
        if (prem_1_lines != list()) and (prem_2_lines != list()):
            ll = in_proof[-1]
            jst_lns = [prem_1_lines[0][0], prem_2_lines[0][0]]
            in_proof.append([ll[0] + 1, ll[1], for_goal[1], "↔I", jst_lns, ll[5], ll[6], ll[7]])
    return in_proof


def try_all_elim(on_ln: list, in_proof: list) -> list:
    # This proof needs one premise, the on_ln.
    # Start with eliminations to match premise-lines' constants.
    consts = get_consts(from_fmlae=[a[2] for a in in_proof if not a[5]], arb=False)
    if consts != list():
        for c in consts:
            prop = instantiate(on_ln[2], with_const=c)
            if is_unique(prop, in_proof):
                ll = in_proof[-1]
                in_proof.append([ll[0] + 1, ll[1], prop, "∀E", [on_ln[0]], ll[5], ll[6], ll[7]])
    # Continue with elimination from targets' constants.
    tgt_consts = list()
    if in_proof[-1][7] != list():
        tgt_props = [a[1] for a in flatten_targets(in_proof) if a[2]]
        tgt_consts = get_consts(from_fmlae=tgt_props, arb=False)
        if tgt_consts != list():
            for tc in tgt_consts:
                prop = instantiate(on_ln[2], with_const=tc)
                if is_unique(prop, in_proof):
                    ll = in_proof[-1]
                    in_proof.append([ll[0] + 1, ll[1], prop, "∀E", [on_ln[0]], ll[5], ll[6], ll[7]])
    # If no constants are to be found, and no universal is in the targets and no open existential is in the proof,
    # then just use the first constant to get the ball rolling.
    tgt_univs = list()
    tgt_neg_exists = list()
    if in_proof[-1][7] != list():
        tgt_univs = [a for a in in_proof[-1][7][0] if main_op(a[1])[1][0] == "∀" and a[2]]
        tgt_neg_exists = [a for a in in_proof[-1][7][0] if (main_op(cut_negs(off_prop=a[1]))[1][0] == "∃")
                          and are_contradictory(cut_negs(off_prop=a[1]), a[1])]
    ip_exists = [a for a in in_proof if (main_op(a[2])[1][0] == "∃") and (not a[5])]
    if consts + tgt_consts + tgt_univs + ip_exists + tgt_neg_exists == list():
        prop = instantiate(on_ln[2], with_const="a")
        ll = in_proof[-1]
        in_proof.append([ll[0] + 1, ll[1], prop, "∀E", [on_ln[0]], ll[5], ll[6], ll[7]])
    return in_proof


def try_all_intro(for_goal: tuple, in_proof: list) -> list:
    # This proof needs two premises.
    sm_lns = [a for a in in_proof if ("SM" in a[3]) and (not a[5])]
    if sm_lns != list():
        if sm_lns[-1][3] == "SM∀I":
            prem_1_ln = sm_lns[-1]  # Now verified, the first premise just is the last SM line.
            # The second premise is the instantiated version of the goal.
            inst_prop = instantiate(this_fmla=for_goal[1], with_const=prem_1_ln[2])
            dch_lns = [a for a in in_proof if (a[0] > prem_1_ln[0]) and (a[2] == inst_prop) and (not a[5])]
            if dch_lns != list():
                prem_2_ln = dch_lns[0]
                # All lines at or below the discharge line must be discharged.
                for ip_ln in in_proof:
                    if ip_ln[0] >= prem_1_ln[0]:
                        ip_ln[5] = True
                ll = in_proof[-1]
                jst_lns = [prem_1_ln[0], prem_2_ln[0]]
                ll[7] = [a for a in ll[7] if int(re.findall("_[0-9]+_", a[0][0])[0].replace("_", "")) < ll[1]]
                in_proof.append([ll[0] + 1, ll[1] - 1, for_goal[1], "∀I", jst_lns, False, ll[6][:-1], ll[7]])
                return in_proof
    # Make SM and build targets for the following if ∀I fails: [a ... Aa] ⊢ ∀xAx
    if not for_goal[2]:  # Don't run a ∀I proof on unpermitted goals.
        return in_proof
    if not is_unique(for_goal[1], in_proof):  # Don't run a ∀I proof if the goal already exists.
        return in_proof
    arb_consts = get_consts(from_fmlae=[a[2] for a in in_proof if not a[5]], arb=True)
    inst = instantiate(for_goal[1], with_const=arb_consts[0])
    if [a for a in in_proof if (a[3] == "SM∀I") and (a[4] == [for_goal[1]]) and (not a[5])] == list():
        in_proof[-1][7].insert(0, build_tree(from_prop=inst, start_val=f"C_{in_proof[-1][1] + 1}_"))
        ll = in_proof[-1]
        ll[6] = ll[6] + [arb_consts[0]]
        in_proof.append([ll[0] + 1, ll[1] + 1, arb_consts[0], "SM∀I", [for_goal[1]], ll[5], ll[6], ll[7]])
        return in_proof
    return in_proof


def try_some_elim(on_ln: list, in_proof: list, sms: bool) -> list:
    # This proof needs three premises.
    # The first premise is just on_ln.
    # The second premise the last SM line, but only if it's of kind SM∃E.
    bk = break_down(on_ln[2])
    sbk = break_down(bk[2])
    sm_lns = [a for a in in_proof if ("SM" in a[3]) and (not a[5])]
    if (sm_lns != list()) and (in_proof[-1][6] != list()):
        inst_match = instantiate(on_ln[2], with_const=in_proof[-1][6][-1])
        if (sm_lns[-1][2] == inst_match) and (sm_lns[-1][3] == "SM∃E"):
            prem_2_ln = sm_lns[-1]  # Now verified, the second premise just is the last SM line.
            # the prem_3_ln is the sought conclusion present after the prem_2_ln.
            prem_3_lns = [a for a in in_proof[prem_2_ln[0]:] if (a[2] in [prem_2_ln[4][0], "⊥"]) and (not a[5])]
            if prem_3_lns != list():
                prem_3_ln = prem_3_lns[-1]
                # All lines at or below the discharge line must be discharged.
                for ip_ln in in_proof:
                    if ip_ln[0] >= prem_2_ln[0]:
                        ip_ln[5] = True
                ll = in_proof[-1]
                jst_lns = [on_ln[0], prem_2_ln[0], prem_3_ln[0]]
                ll[7] = [a for a in ll[7] if int(re.findall("_[0-9]+_", a[0][0])[0].replace("_", "")) < ll[1]]
                in_proof.append([ll[0] + 1, ll[1] - 1, prem_3_ln[2], "∃E", jst_lns, False, ll[6][:-1], ll[7]])
                return in_proof
    if not sms:
        return in_proof
    # If ∃E fails, an instantiation is needed as a target.
    if on_ln[3] == "∃I":  # Don't build targets for ∃E if the line, itself, resulted from ∃I.
        return in_proof
    if not is_unique("⊥", in_proof):  # Don't build targets for ∃E if there's an open falsum.
        return in_proof
    # If an arbitrary instantiation already exists, don't bother doing another one.
    for ac in in_proof[-1][6]:
        if not is_unique(instantiate(on_ln[2], with_const=ac), in_proof):
            return in_proof
    # If there's more than one instance of the same prop from the same rule arising, don't open another SM line.
    if len([a for a in in_proof if (main_op(a[2])[1][0] == "∃") and (a[3:4] == on_ln[3:4]) and (not a[5])]) > 1:
        return in_proof
    # If an identical SM line has been discharged by ∃E, don't open another SM line.
    if [a for a in [b for b in in_proof if b[3] == "∃E"] if a[4][0] == on_ln[0]] != list():
        return in_proof
    # If there are still decompositions to do at the immediate depth, stall on the ∃E SM line.
    if [a for a in in_proof[-1][7][0] if "D" in a[0]] != list():
        return in_proof
    arb_consts = get_consts(from_fmlae=[a[2] for a in in_proof if not a[5]], arb=True)
    inst = instantiate(on_ln[2], with_const=arb_consts[0])
    if in_proof[-1][7] != list():
        sm_tgt = in_proof[-1][7][0][0][1]
        if [a for a in in_proof if
            (a[2] == inst) and (a[3] == "SM∃E") and (a[4] == [sm_tgt]) and (not a[5])] == list():
            ll = in_proof[-1]
            ll[6] = ll[6] + [arb_consts[0]]
            in_proof.append([ll[0] + 1, ll[1] + 1, inst, "SM∃E", [sm_tgt], ll[5], ll[6], ll[7]])
            tgt_bk = break_down(sm_tgt)
            if tgt_bk[1][0] in ["∃", "∀"]:
                new_tgt = instantiate(sm_tgt, with_const=arb_consts[0])
            else:
                new_tgt = sm_tgt
            new_tree = build_tree(from_prop=new_tgt, start_val=f"C_{in_proof[-1][1]}_0", sms=True)
            in_proof[-1][7] = [new_tree] + in_proof[-1][7]
            return in_proof
    return in_proof


def try_some_intro(for_goal: tuple, in_proof: list) -> list:
    if not is_unique(for_goal[1], in_proof):  # This happens when ∃I is a part of ∃E.
        return in_proof
    # This proof needs one premise.
    bk = break_down(for_goal[1])
    for ip_ln in [a for a in in_proof if not a[5]]:
        consts = get_consts(from_fmlae=[ip_ln[2]], arb=False)
        for c in consts:
            props = generalize(this_fmla=ip_ln[2], this_const=c, to_var=bk[1][1], q_type="∃")
            if for_goal[1] in props:
                ll = in_proof[-1]
                in_proof.append([ll[0] + 1, ll[1], for_goal[1], "∃I", [ip_ln[0]], ll[5], ll[6], ll[7]])
    return in_proof


def try_nec_elim(on_ln: list, in_proof: list) -> list:
    return in_proof


def try_nec_intro(for_goal: tuple, in_proof: list) -> list:
    return in_proof


def try_pos_elim(on_ln: list, in_proof: list, sms: bool) -> list:
    return in_proof


def try_pos_intro(for_goal: tuple, in_proof: list) -> list:
    return in_proof


def try_equals_elim(on_ln: list, in_proof: list) -> list:
    return in_proof


def try_equals_intro(for_goal: tuple, in_proof: list) -> list:
    return in_proof


def try_elim(on_ln: list, in_proof: list, intn: bool, sms: bool) -> list:
    if on_ln[5]:  # Do nothing with discharged lines.
        return in_proof
    if can_do_discharge(in_proof):  # If an SM is ready for discharge, only allow the matching target through.
        #print("DISCHARGE DOABLE (AS OF E CYCLE)")
        last_sm = [a for a in in_proof if ("SM" in a[3]) and (not a[5])][-1]
        if last_sm[3] == "SM∃E":
            match_lns = [a for a in in_proof if (a[1] < last_sm[1]) and (main_op(a[2])[1][0] == "∃") and (not a[5])]
            match_lns = [a for a in match_lns if instantiate(a[2], with_const=last_sm[6][-1]) == last_sm[2]]
            if match_lns != list():
                on_ln = match_lns[0]
            else:
                return in_proof
        else:
            return in_proof
    len_start = len(in_proof)
    mo = main_op(of_fmla=on_ln[2])[1]
    if (mo not in ["⊥", "∃", "◇"]) \
            and ("⊥" in [a[2] for a in in_proof if not a[5]]):  # Only allow ⊥E, ∃E, or ◇E with falsum.
        return in_proof
    if mo == "⊥":
        in_proof = try_falsum_elim(on_ln=on_ln, in_proof=in_proof)
    elif mo == "¬":
        in_proof = try_not_elim(on_ln=on_ln, in_proof=in_proof, intn=intn)
    elif mo == "→":
        in_proof = try_then_elim(on_ln=on_ln, in_proof=in_proof)
    elif mo == "∧":
        in_proof = try_and_elim(on_ln=on_ln, in_proof=in_proof)
    elif mo == "∨":
        in_proof = try_or_elim(on_ln=on_ln, in_proof=in_proof)
    elif mo == "↔":
        in_proof = try_iff_elim(on_ln=on_ln, in_proof=in_proof)
    elif mo == "∀":
        in_proof = try_all_elim(on_ln=on_ln, in_proof=in_proof)
    elif mo == "∃":
        in_proof = try_some_elim(on_ln=on_ln, in_proof=in_proof, sms=sms)
    elif mo == "□":
        in_proof = try_nec_elim(on_ln=on_ln, in_proof=in_proof)
    elif mo == "◇":
        in_proof = try_pos_elim(on_ln=on_ln, in_proof=in_proof, sms=sms)
    elif mo == "=":
        in_proof = try_equals_elim(on_ln=on_ln, in_proof=in_proof)
    len_end = len(in_proof)
    if len_start < len_end:
        for ip_ln in in_proof[len_start:]:
            print(ip_ln)
        # Grant permission to do: ∨I, ∧I, ↔I, ⊥I, ∃I, and ◇I:
        low_risk_tgts = [a for a in flatten_targets(in_proof)
                         if main_op(a[1])[1][0] in ["∨", "∧", "↔", "⊥", "∃", "◇"]]
        len_restart = len(in_proof)
        for lrt in low_risk_tgts:
            in_proof = try_intro(for_goal=lrt, in_proof=in_proof, intn=intn)
        len_reend = len(in_proof)
        if len_restart < len_reend:
            return in_proof
        in_proof = cull_targets(from_proof=in_proof)
        print(f"TARGETS AFTER {mo}E (LN {on_ln[0]}) "
              f"({sum([len(a) for a in in_proof[-1][7]])}:{len(in_proof[-1][7])}): {in_proof[-1][7]}")
    return in_proof


def try_intro(for_goal: tuple, in_proof: list, intn: bool) -> list:
    mo = main_op(of_fmla=for_goal[1])[1]
    if can_do_discharge(in_proof):  # If an SM is ready for discharge, only allow the matching target through.
        #print("DISCHARGE DOABLE (AS OF I CYCLE)")
        last_sm = [a for a in in_proof if ("SM" in a[3]) and (not a[5])][-1]
        for_goal = (f"DCH_{in_proof[-1][1]}_0", last_sm[4][0], False)
        mo = main_op(of_fmla=for_goal[1])[1]
    len_start = len(in_proof)
    if mo == "⊥":
        in_proof = try_falsum_intro(for_goal=for_goal, in_proof=in_proof)
    elif mo == "¬":
        in_proof = try_not_intro(for_goal=for_goal, in_proof=in_proof)
    elif mo == "→":
        in_proof = try_then_intro(for_goal=for_goal, in_proof=in_proof)
    elif mo == "∧":
        in_proof = try_and_intro(for_goal=for_goal, in_proof=in_proof)
    elif mo == "∨":
        in_proof = try_or_intro(for_goal=for_goal, in_proof=in_proof)
    elif mo == "↔":
        in_proof = try_iff_intro(for_goal=for_goal, in_proof=in_proof)
    elif mo[0] == "∀":
        in_proof = try_all_intro(for_goal=for_goal, in_proof=in_proof)
    elif mo[0] == "∃":
        in_proof = try_some_intro(for_goal=for_goal, in_proof=in_proof)
    elif mo == "□":
        in_proof = try_nec_intro(for_goal=for_goal, in_proof=in_proof)
    elif mo == "◇":
        in_proof = try_pos_intro(for_goal=for_goal, in_proof=in_proof)
    elif mo == "=":
        in_proof = try_equals_intro(for_goal=for_goal, in_proof=in_proof)
    len_end = len(in_proof)
    if len_start < len_end:
        for ip_ln in in_proof[len_start:]:
            print(ip_ln)
        # Grant permission to do: ∨E, ∧E, →E, ↔E, ¬E, ⊥E, ∀E, and □E:
        low_risk_lns = [a for a in in_proof if main_op(a[2])[1][0] in ["∨", "∧", "→", "↔", "¬", "⊥", "∀", "□"]]
        len_restart = len(in_proof)
        for lrl in low_risk_lns:
            in_proof = try_elim(on_ln=lrl, in_proof=in_proof, intn=intn, sms=False)
        len_reend = len(in_proof)
        if len_restart < len_reend:
            return in_proof
        in_proof = cull_targets(from_proof=in_proof)
        print(f"TARGETS AFTER {mo}I (ID {for_goal[0]}) "
              f"({sum([len(a) for a in in_proof[-1][7]])}:{len(in_proof[-1][7])}): {in_proof[-1][7]}")
    return in_proof


'''
All of the functions for setting up the body of the proof go here.
The universal line construction for proofs is as follows:
[ln_num, sm_depth, prop, jst, jst_lns, dchd, arb_items, targets]
'''


def build_tree(from_prop: str, start_val: str = "t", sms: bool = True, classical: bool = False) -> list:
    # Every tree node is a triple (ID, node prop, allow SM)
    tree = [(f"{start_val}0", from_prop, sms)]
    n = 0
    arb_cnt = -1
    while n < len(tree):
        bk = break_down(tree[n][1])
        if bk[1] == "⊥":
            n += 0  # Falsum ends a branch.
        if bk[1] == "¬":
            tree.append((f"{tree[n][0]}1", "⊥", False))
        elif bk[1] == "→":
            tree.append((f"{tree[n][0]}1", bk[2], False))
            tree.append((f"{tree[n][0]}2", bk[3], tree[n][2]))
        elif bk[1] == "∨":
            tree.append((f"{tree[n][0]}1", bk[2], False))
            tree.append((f"{tree[n][0]}2", bk[3], False))
            if classical:
                tree.append((f"{tree[n][0]}3", clean(f"¬¬({bk[0]})"), tree[n][2]))
        elif bk[1] == "∧":
            tree.append((f"{tree[n][0]}1", bk[2], tree[n][2]))
            tree.append((f"{tree[n][0]}2", bk[3], tree[n][2]))
        elif bk[1] == "↔":
            tree.append((f"{tree[n][0]}1", clean(f"({bk[2]})→({bk[3]})"), tree[n][2]))
            tree.append((f"{tree[n][0]}2", clean(f"({bk[3]})→({bk[2]})"), tree[n][2]))
        elif bk[1][0] == "∃":
            chars = list("abcdefghijklmnopqrst")
            for m in range(0, len(chars)):
                tree.append((f"{tree[n][0]}1", instantiate(bk[0], with_const=f"{chars[m]}"), False))
            if classical:
                tree.append((f"{tree[n][0]}1", clean(f"¬¬({bk[0]})"), tree[n][2]))
        elif bk[1][0] == "∀":
            arb_cnt += 1
            #tree.append((f"{tree[n][0]}1", instantiate(bk[0], with_const=f"|{arb_cnt}|"), tree[n][2]))
        elif (bk[2] == str()) and (bk[0] != "⊥"):
            tree.append((f"{tree[n][0]}1", clean(f"¬¬({bk[0]})"), tree[n][2]))
        n += 1
    tree = list(set(tree))
    tree.sort(key=lambda i: float(i[0].replace(start_val, ".", 1)))
    return tree


def prune_tree(this_tree: list, of_val: str) -> list:
    return [a for a in this_tree if of_val not in a[0]]


def is_unique(this_prop: str, in_proof: list) -> bool:
    if len(in_proof) == 0:
        return True
    else:
        return [a for a in in_proof if (a[2] == this_prop) and (not a[5])] == list()


def is_proven(this_prop: str, in_proof: list) -> bool:
    if len(in_proof) == 0:
        return False
    else:
        return [a for a in in_proof if (a[1] == 0) and (a[2] == this_prop)] != list()


def is_contradicted(this_prop: str, in_proof: list) -> bool:
    open_props = list(set([a[2] for a in in_proof if not a[5]]))
    tp_neg_cnt = 0
    tp_bk = break_down(this_prop)
    while tp_bk[1] == "¬":
        tp_neg_cnt += 1
        tp_bk = break_down(tp_bk[2])
        if tp_bk[1] == "→":
            if tp_bk[3] == "⊥":
                tp_neg_cnt += 1
                tp_bk = break_down(tp_bk[2])
    op_tups = list()
    for op in open_props:
        op_bk = break_down(op)
        op_neg_cnt = 0
        while op_bk[1] == "¬":
            op_neg_cnt += 1
            op_bk = break_down(op_bk[2])
            if tp_bk[1] == "→":
                if tp_bk[3] == "⊥":
                    tp_neg_cnt += 1
                    tp_bk = break_down(tp_bk[2])
        op_tups.append((op_bk[0], op_neg_cnt % 2))
    return (tp_bk[0], abs((tp_neg_cnt % 2) - 1)) in op_tups


def are_contradictory(prop_1: str, prop_2: str) -> bool:
    p1_neg_cnt = 0
    p1_bk = break_down(prop_1)
    while p1_bk[1] == "¬":
        p1_neg_cnt += 1
        p1_bk = break_down(p1_bk[2])
        if p1_bk[1] == "→":
            if p1_bk[3] == "⊥":
                p1_neg_cnt += 1
                p1_bk = break_down(p1_bk[2])
    p2_neg_cnt = 0
    p2_bk = break_down(prop_2)
    while p2_bk[1] == "¬":
        p2_neg_cnt += 1
        p2_bk = break_down(p2_bk[2])
        if p2_bk[1] == "→":
            if p2_bk[3] == "⊥":
                p2_neg_cnt += 1
                p2_bk = break_down(p2_bk[2])
    return (p1_bk[0] == p2_bk[0]) and ((p1_neg_cnt % 2) != (p2_neg_cnt % 2))


def cut_negs(off_prop: str) -> str:
    pbk = break_down(off_prop)
    if pbk[1] == "¬":
        pbk = break_down(pbk[2])
    return pbk[0]


def can_do_discharge(in_proof: list) -> bool:
    sm_lns = [a for a in in_proof if ("SM" in a[3]) and (not a[5])]
    open_props = [a[2] for a in in_proof if not a[5]]
    if sm_lns != list():
        last_sm = sm_lns[-1]
        if "→" in last_sm[3]:
            return break_down(last_sm[4][0])[3] in open_props
        if "∃" in last_sm[3]:
            return (last_sm[4][0] in open_props) or ("⊥" in open_props)
        if "∀" in last_sm[3]:
            return instantiate(last_sm[4][0], with_const=in_proof[-1][6][-1]) in open_props
        if "¬" not in last_sm[3]:
            return last_sm[4][0] in open_props
        else:
            return "⊥" in open_props
    else:
        return False


def mine_props(in_proof: list, by_op: str) -> list:
    return [a[2] for a in in_proof if (by_op in main_op(a[2])[1]) and (not a[5])]


def flatten_targets(in_proof: list) -> list:
    tgts = in_proof[-1][7]
    flattened = [a for b in tgts for a in b]
    return flattened


def classicalize(these_tgts: list) -> list:
    for n in range(0, len(these_tgts)):
        new_trees = list()
        for base in [a for a in these_tgts[n] if a[0][-1] == "0"]:
            new_trees = new_trees + build_tree(from_prop=base[1], start_val=base[0][:-1], classical=True)
        these_tgts[n] = new_trees
    return these_tgts


def cull_targets(from_proof: list) -> list:
    open_props = [a[2] for a in from_proof if not a[5]]
    while from_proof[-1][7] != list():
        depth = int(from_proof[-1][7][0][0][0].split("_")[1])
        if depth > from_proof[-1][1]:
            from_proof[-1][7].pop(0)
        elif depth == from_proof[-1][1]:
            tgt_cnt_a = len(from_proof[-1][7][0])
            for n in range(len(from_proof[-1][7][0]) - 1, -1, -1):
                if n >= len(from_proof[-1][7][0]):
                    continue
                if from_proof[-1][7][0][n][1] in open_props:
                    from_proof[-1][7][0] = prune_tree(this_tree=from_proof[-1][7][0], of_val=from_proof[-1][7][0][n][0])
            tgt_cnt_b = len(from_proof[-1][7][0])
            if from_proof[-1][7][0] == list():
                from_proof[-1][7].pop(0)
            elif [a for a in from_proof[-1][7][0] if ("|" not in a[0]) or ("D" in a[0])] == list():
                from_proof[-1][7].pop(0)
            elif tgt_cnt_a == tgt_cnt_b:
                break
        else:
            break
    return from_proof


def simplify(this_proof: list, to_conc: str) -> list:
    # Officially, SM lines have no justification lines, so clear them.
    for ln in this_proof:
        if "SM" in ln[3]:
            ln[4] = []
    conc_ln_lists = [[a[0]] for a in this_proof if a[2] == to_conc]
    simp_proof = list()
    for cll in conc_ln_lists:
        n = 0
        while n < len(cll):
            cll = cll + this_proof[cll[n] - 1][4]
            n += 1
        cll = list(set(cll))
        cll.sort()
        proof_snippet = [this_proof[a - 1] for a in cll]
        net_depth = sum([1 if ("SM" in ln[3]) else -1 if ln[3] in ["¬I", "→I", "∃E", "∀I", "◇E", "□I"] else 0
                         for ln in proof_snippet])
        print(f"PROOF {cll}: NET DEPTH = {net_depth}")
        if net_depth == 0:
            simp_proof = [a for a in proof_snippet]
            break
    # Renumber the complete proof found.
    if simp_proof != list():
        renumbering_dict = dict(zip([a[0] for a in simp_proof], [a + 1 for a in range(0, len(simp_proof))]))
        for sp_ln in simp_proof:
            sp_ln[0] = renumbering_dict[sp_ln[0]]
            sp_ln[4] = [renumbering_dict[a] for a in sp_ln[4]]
    # Reassess the assumption depths.
    sp_depth = 0
    for sp_ln in simp_proof:
        if "SM" in sp_ln[3]:
            sp_depth += 1
            sp_ln[1] = sp_depth
        elif sp_ln[3] in ["¬I", "→I", "∃E", "∀I", "◇E", "□I"]:
            sp_depth -= 1
            sp_ln[1] = sp_depth
        else:
            sp_ln[1] = sp_depth
    return simp_proof


def build_prems(from_props: list, classical: bool = False) -> list:
    conc = from_props[-1]
    c_tree = build_tree(from_prop=conc, start_val="C_0_", classical=classical)
    if len(from_props) > 1:
        prems = [[a + 1, 0, from_props[a], "P", [], False, [], [c_tree]] for a in range(0, len(from_props) - 1)]
    else:  # Make the sole premise the vacuous "¬⊥".
        prems = [[1, 0, "¬⊥", "P", [], False, [], [c_tree]]]
    for p in prems:
        print(p)
    return prems


def count_open_sms(in_proof: list) -> int:
    return len([a for a in in_proof if ("SM" in a[3]) and (not a[5])])


def try_derivation(from_props: list, provisional: bool = False) -> list:
    if from_props == list():
        return list()
    proof = build_prems(from_props=from_props)
    '''
    - Stage 1: (w/ SM): Do E-rules. If new lines, restart the loop. If new SM line or new tree, Stage 1.
    - Stage 2: (w/ SM): Do I-rules. If new lines, restart the loop. If new SM line, Stage 1.
    - Stage 3: Turn off intn_on.
    '''
    intn_on = True
    dns_on = False
    while not is_proven(from_props[-1], in_proof=proof):
        len_start = len(proof)
        # - Stage 1: (w/ SM): Do E-rules. If new lines, restart the loop. If new SM line, Stage 1. If new tree, Stage 2.
        n = 0
        e_sms_on = False
        while True:
            len_c = len(proof)
            sm_cnt_c = count_open_sms(in_proof=proof)
            tree_cnt_c = len(proof[-1][7])
            while n < len(proof):
                len_a = len(proof)
                tree_cnt_a = len(proof[-1][7])
                sm_cnt_a = count_open_sms(in_proof=proof)
                proof = try_elim(on_ln=proof[n], in_proof=proof, intn=intn_on, sms=e_sms_on)
                len_b = len(proof)
                tree_cnt_b = len(proof[-1][7])
                sm_cnt_b = count_open_sms(in_proof=proof)
                if (sm_cnt_a != sm_cnt_b) or (tree_cnt_a != tree_cnt_b):
                    break
                if len_a < len_b:
                    n = 0
                else:
                    n += 1
            len_d = len(proof)
            sm_cnt_d = count_open_sms(in_proof=proof)
            tree_cnt_d = len(proof[-1][7])
            if not e_sms_on:
                if (sm_cnt_c != sm_cnt_d) or (tree_cnt_c != tree_cnt_d) or (len_c < len_d):
                    break
                else:
                    print("SM∃E AND SM◇E NOW ALLOWED")
                    e_sms_on = True
                    n = 0
            else:
                break
        len_end = len(proof)
        if (len_start < len_end) and (not e_sms_on):
            continue
        # - Stage 2: (w/ SM): Do I-rules. If new lines, restart the loop. If new SM line, Stage 1.
        if proof[-1][7] == list():
            break
        elif dns_on:  # Rather than pushing the dns_on paremeter everywhere, just rebuild all trees classically.
            proof[-1][7] = classicalize(these_tgts=proof[-1][7])
            proof = cull_targets(from_proof=proof)
        n = 0
        while n < len(proof[-1][7][0]):
            len_a = len(proof)
            sm_cnt_a = count_open_sms(in_proof=proof)
            proof = try_intro(for_goal=proof[-1][7][0][n], in_proof=proof, intn=intn_on)
            len_b = len(proof)
            sm_cnt_b = count_open_sms(in_proof=proof)
            if sm_cnt_a != sm_cnt_b:
                break
            if proof[-1][7] == list():
                break
            if len_a < len_b:
                n = 0
            else:
                n += 1
        len_end = len(proof)
        if (len_start < len_end) or ("⊥" in [a[2] for a in proof if not a[5]]):
            continue
        if not provisional:
            no_sm_tgts = [a[1] for a in proof[-1][7][0]
                          if (("|" not in a[0]) or ("→E" in a[0]))
                          and (main_op(a[1])[1][0] in ["¬", "→", "∀", "□"]) and (not a[2])]
            passed = False
            for nst in no_sm_tgts:
                print(f"PROVISIONALLY PROOFING FOR {nst}")
                prov_props = [a[2] for a in proof if not a[5]] + [nst]
                if nst in prov_props[:-1]:
                    continue
                prov_proof = try_derivation(from_props=prov_props, provisional=True)
                if is_proven(nst, in_proof=prov_proof):
                    proof[-1][7].insert(0, build_tree(from_prop=nst, start_val=f"C_{proof[-1][1]}_"))
                    print(f"{nst} GOTTEN")
                    passed = True
                    break
            if passed:
                continue
        if intn_on:
            print("INTUITIONISM CONSTRAINT REMOVED")
            intn_on = False
            continue
        if not dns_on:
            print("CLASSICAL DN DERIVATIONS ALLOWED")
            dns_on = True
            # Build double negation targets for disjuncts and existentials.
            last_zero_ln = [a for a in proof if a[1] == 0][-1]
            proof = proof[0:last_zero_ln[0]]
            proof[-1][7] = [build_tree(from_prop=from_props[-1], start_val="C_0_", classical=True)]
            continue
        print(f"({len(flatten_targets(in_proof=proof))}:{len(proof[-1][7])}): {proof[-1][7]}")
        break
    if is_proven(from_props[-1], in_proof=proof) and (not provisional):
        proof = simplify(proof, to_conc=from_props[-1])
    return proof


def textify(this_drv: list) -> str:
    if this_drv == list():
        return str()
    else:
        zf_val = len(str(this_drv[-1][0]))
        return "\n".join([f"{str(a[0]).zfill(zf_val)}.{'|' * a[1]}{a[2]} : {a[3]} "
                          f"({','.join([str(b).zfill(zf_val) for b in a[4]])})" for a in this_drv])


#drv_attempt = try_derivation(from_props=["∀x(Fxxx→∃x∃y∃zFxyz)"], provisional=True)
#print(textify(drv_attempt))
#Failed: ["¬∃xFx↔∀yGy", "∀y¬Fy", "∃yGy"]
#Failed: ["∃x∃yFxy→∃y∃xFyx"]
#Failed: ["∃xFxxx", "∃x∃y∃zFxyz"]

'''
Challenges for the program:
["∃x(Fx→∀yFy)"] // Overlong
["¬¬¬¬¬(A∧¬A)"] // Reason to simply make the for_goal when discharge is available.
["(A∨B)↔¬(¬A∧¬B)"] // Reason to cull targets after classicalization.
["∃x∀yFxy→∃x∃yFxy"]
["∀x(Fa→Fx)↔(Fa→∀xFx)"]
["(∀xFx→Ga)↔∃x(Fx→Ga)"]
["¬((¬C∨¬¬C)∨¬¬C)", "⊥"]
["(A∨(B↔C))↔(A∨(¬B↔¬C))"] // Uses provisional proofing.
["((A∧B)→C)↔(¬(A→C)→¬B)"]
["((A∨B)∨C)↔(¬A→(¬B→C))"]
["(A∧(B∨C))↔((B∧A)∨(C∧A))"]
["(¬A↔¬A)↔(¬(¬A→A)↔(A→¬A))"] // Reason to apply are_contradictory() to then_elim.
["(H∧G)→(L∨K)", "G∧H", "K∨L"]
["∀x(Fx→∃yGxy)↔∀x∃y(Fx→Gxy)"]
["(¬A→(¬B→C))→((A∨B)∨(¬¬B∨C))"]
["∀x(Fx↔Gx)", "∃y(Fy∧¬Gy)", "⊥"]
["(A∨(B→(A→B)))↔(A∨((¬A∨B)∨B))"] // Uses provisional proofing.
["D→E", "E→(Z∧W)", "¬Z∨¬W", "¬D"]
["(A→(B↔C))↔(A→((¬B∨C)∧(¬C∨B)))"] // Reason to simply make the for_goal when discharge is available.
["¬Y→¬Z", "¬Z→¬X", "¬X→¬Y", "Y↔Z"]
["(M∨B)∨(C∨G)", "¬B∧(¬G∧¬M)", "C"]
["F→(¬G∨H)", "F→G", "¬(H∨I)", "F→J"]
["(F∧G)∨(H∧¬I)", "I→¬(F∧D)", "I→¬D"] // Reason to keep "|" targets with "D" ID's protected from "|" target deletion.
["F→(G→H)", "¬I→(F∨H)", "F→G", "I∨H"]
["¬L∨(¬Z∨¬U)", "(U∧G)∨H", "Z", "L→H"]
["∀x(∃yLxy→∀zLzx)", "Lta", "∀x∀yLxy"]
["G→(H∧¬K)", "¬I→(F∨H)", "F→G", "I∨H"]
["((K∧J)∨I)∨¬Y", "Y∧((I∨K)→F)", "F∨N"]
["(¬A∧¬B)∨(¬A∧¬C)", "(E∧D)→A", "¬E∨¬D"] // Reason for the classical parameter and dns_on value.
["∀x∀y(Hxy→¬Hyx)", "∀x∃yHxy", "∀x∃y¬Hxy"] // Reason to introduce e_sms_on and the sms parameter, and for lrt check.
["¬(W∧(Z∨Y))", "(Z→Y)→Z", "(Y→Z)→W", "⊥"] // Reason to allow weakening and strengthening, regardless of tgt sm status.
["(W→S)∧¬M", "(¬W→H)∨M", "(¬S→H)→K", "K"]
["∀z(Hz→∃yGzy)", "∃wHw", "∀x¬∃yGxy", "⊥"]
["∀x(∃zFxz→∀yFxy)", "∃x∃yFxy", "∃x∀wFxw"] // Reason to have e_sms_on not activate if the proof is deriving new lines.
["B∧(H∨Z)", "¬Z→K", "(B↔Z)→¬Z", "¬K", "⊥"]
["((X∧Z)∧Y)∨(¬X→¬Y)", "X→Z", "Z→Y", "X↔Y"]
["¬(A→B)∧(C∧¬D)", "(B∨¬A)∨((C∧E)→D)", "¬E"]
["((F→G)∨(¬F→G))→H", "(A∧H)→¬A", "A∨¬H", "⊥"] // Reason for restricting weak. and stren. to novel SM→I's.
["∃xHx", "∀x(Hx→Rx)", "∃xRx→∀xGx", "∀x(Fx→Gx)"]
["M∧L", "(L∧(M∧¬S))→K", "¬K∨¬S", "¬(K↔¬S)", "⊥"]
["((E∧F)∨¬¬G)→M", "¬(((G∨E)∧(F∨G))→(M∧M))", "⊥"]
["J→(K∨(L∨H))", "((K∨L)∨H)→((M∨G)∨I)", "J→(M∨(G∨I))"] // Helped program restrictions on "|" targets.
["((A∧B)∨((C∧D)∨A))↔((((C∨A)∧(C∨B))∧((D∨A)∧(D∨B)))∨A)"]
'''