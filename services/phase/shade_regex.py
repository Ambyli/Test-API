import re

# takes a list of steps and converts it to a shade
# this needs to be turned into a dyanmic version


def gen_shade(steps, delimiter=";"):
    shade = []

    # pull simple steps out of steps and into shade
    shade.extend(pull_basic(steps))

    # combine like steps
    steps = combine_like_term(steps)

    # find unique suffix's
    suffix_list = []
    # pattern list for possible suffix types
    # anchored at start of step
    # ex. U01 -> '', U01R -> 'R', U500DDDDDD^1313123 -> 'DDDDDD^1313123'
    pattern_list = [r"^(U|L)\D+(\^\d+|)$", r"^(U|L)\d+(\D+(\^\d+|)|(\^\d+))$"]
    for step in steps:  # go through step by step
        # check if one of the patterns is a match for current step
        for i in range(0, len(pattern_list)):
            result = re.search(pattern_list[i], step)
            if result is not None:  # if we have a match with a pattern
                if i == 0:
                    # check if it already exists in suffix_list
                    if result.group(0)[1:] not in suffix_list:
                        # append ignoring prefix
                        suffix_list.append(result.group(0)[1:])
                        break  # stop pattern loop, we found a pattern already and added it
                elif i == 1:
                    temp = result.group(0).replace(
                        re.search(r"^(U|L)\d+", result.group(0)).group(0), ""
                    )  # remove prefix and step number
                    if (
                        temp not in suffix_list
                    ):  # check if it already exists in suffix_list
                        # append ignoring prefix and step number
                        suffix_list.append(temp)
                        break  # stop pattern loop, we found a pattern already and added it

    # NO SUFFIX STEPS
    # upper, get uppers and sort ignoring prefix 'U'
    norm_steps = sorted(
        split_like_term(steps, prefixes=["U"], ignore=suffix_list),
        key=lambda x: int(x[1:]),
    )
    # lower, get lowers and sort ignoring prefix 'L'
    norm_steps.extend(
        sorted(
            split_like_term(steps, prefixes=["L"], ignore=suffix_list),
            key=lambda x: int(x[1:]),
        )
    )
    # combine U and L steps into shade
    shade.extend(combine_range(combine_UL(norm_steps)))

    # SUFFIX STEPS
    current = steps
    # extrax suffixes from length greatest to least
    suffix_list = sorted(suffix_list, key=lambda x: len(x), reverse=True)
    for suffix in suffix_list:
        # upper, get uppers and sort ignoring prefix 'U'
        # we sort steps by replacing suffix with 0 and we ignore prefix
        # ex. U01R -> 010U|L;U01^5;L03-12R^2
        custom = sorted(
            split_like_term(current, prefixes=["U"], suffixes=[suffix]),
            key=lambda x: int(x.replace(suffix, "0")[1:]),
        )
        # lower, get lowers and sort ignoring prefix 'L'
        # we sort steps by replacing suffix with 0 and we ignore prefix
        # ex. U01R -> 010
        custom.extend(
            sorted(
                split_like_term(current, prefixes=["L"], suffixes=[suffix]),
                key=lambda x: int(x.replace(suffix, "0")[1:]),
            )
        )
        # remove already combined steps from current
        for step in custom:
            if step in current:
                current.remove(step)
        # combine U and L steps into shade
        shade.extend(combine_range(combine_UL(custom), suffixes=[suffix]))

    return delimiter.join(shade)


# takes a list of steps by reference, removes simple 'U' and 'L' steps
# then provides a shade based on number of simple 'U' and 'L' steps
# this is required because later functions won't understand simple steps


def pull_basic(steps):
    shade = []

    # calculate number of 'U' and 'L' in steps
    upperlower = 0
    upper = 0
    lower = 0
    while "U" in steps or "L" in steps:
        if "U" in steps and "L" in steps:
            steps.remove("U")
            steps.remove("L")
            upperlower += 1
        elif "U" in steps:
            steps.remove("U")
            upper += 1
        elif "L" in steps:
            steps.remove("L")
            lower += 1

    # append ul's to shade
    if upperlower > 0:
        if upperlower > 1:
            shade.append("U|L^" + str(upperlower))
        else:
            shade.append("U|L")
    # append u's to shade
    if upper > 0:
        if upper > 1:
            shade.append("U^" + str(upper))
        else:
            shade.append("U")
    # append l's to shade
    if lower > 0:
        if lower > 1:
            shade.append("L^" + str(lower))
        else:
            shade.append("L")

    # return complete shade
    return shade


# takes a list of steps and combines like steps with the carrot ^
# ex. [U01,U01,U02,U01^2] -> [U01^4,U02]


def combine_like_term(steps):
    new_steps = []
    while len(steps) != 0:
        step = steps.pop(0)
        i = 0
        while i < len(steps):
            # we found a duplicate item
            if re.search(r"^\w+", step).group(0) == steps[i]:
                x = re.search(r"\^\d+", step)  # check for existing pattern
                if x is not None:  # if patter was found, increment by 1
                    # increment existing pattern by 1
                    step = step.replace(
                        x.group(0),
                        r"^" + str(int(re.search(r"\d+", x.group(0)).group(0)) + 1),
                    )
                    steps.remove(steps[i])
                    i -= 1
                else:  # pattern not found, first instance
                    step += "^2"  # append carrot and 2 to indicate a copy was found
                    steps.remove(steps[i])
                    i -= 1
            i += 1
        new_steps.append(step)
    return new_steps


# DEPRECATED
# takes a list of steps and splits with like prefix
# ex. [U01,U02,L02,L03,U01R,U02R,L02R], ['U'] -> [U01,U02,U01R,U02R]
# ex. [U01,U02,L02,L03,U01R,U02R,L02R], ['R'] -> [U01R,U02R,L02R]
# ex. [U01,U02,L02,L03,U01R,U02R,L02R], ['U'], ['R'] -> [U01,U02]
# you can either include a prefix you'd like to find or a list of prefix you want to ignore


def old_split_like_term(steps, terms=[""], ignore=[""]):
    for step in steps:
        # check if step has whats in terms and doesnt have whats in ignore
        if len(list(_ for _ in terms if _ in step)) > len(terms) - 1 and (
            ignore == [""] or len(list(_ for _ in ignore if _ in step)) == 0
        ):
            yield step  # yield step if prefix is the same
    return


# takes a list of steps and splits with like prefix
# ex. [U01,U02,L02,L03,U01R,U02R,L02R], ['U'] -> [U01,U02,U01R,U02R]
# ex. [U01,U02,L02,L03,U01R,U02R,L02R], [''], ['R'] -> [U01R,U02R,L02R]
# ex. [U01,U02,L02,L03,U01R,U02R,L02R], ['U'], [''], ['R'] -> [U01,U02]
# ex. [U01^25,U01R^25], ['U'], ['^25'] -> [U01^25,U01R^25]
# ex. [U01^25,U01R^25], ['U'], ['^25'] ['R'] -> [U01^25]
# you can either include a prefix you'd like to find or a list of prefix you want to ignore


def split_like_term(steps, prefixes=[""], suffixes=[""], ignore=[""]):
    for step in steps:
        # see if a prefix provided are in step
        prefix = get_prefix(step, prefixes)
        # see if a suffix provided are in step
        suffix = get_suffix(step, suffixes)

        # check if prefix was found
        # check if suffix was found
        # check if ignore wasn't found
        if (
            (prefixes == [""] or len(prefix) != 0)
            and (suffixes == [""] or len(suffix) != 0)
            and (ignore == [""] or len(list(_ for _ in ignore if _ in step)) == 0)
        ):
            # print(step)
            yield step  # yield step if prefix is the same
    return


# combines like steps numbers


def combine_UL(steps, divider="|"):
    new_steps = []  # holds list of new steps

    # make sure we have at least 1 step U01, and if U01 is at least 2 characters long
    if len(steps) <= 1:
        return steps

    # [U01,U02,L01R,...] -> U01
    while len(steps) != 0:
        # set the new active_step
        active_step = steps[0]
        # if active step is less than 2 ex. U or '', minimum is UA or UR
        if len(active_step) < 2:
            # then ignore that false step and check the next
            steps.remove(active_step)  # remove false active step
            continue
        # remove active step from steps, so len(steps) becomes len(steps)-1
        steps.remove(active_step)  # len(steps)-1
        # U01 -> U
        active_prefix = active_step[0]  # grab the active steps prefix
        # U01R -> 01R
        active_suffix = active_step[1:]  # grab the active steps suffix

        # track if an item has been added into the new_steps
        old_len = len(new_steps)

        # [U01,L01,L01R,...] -> [U|L01,L01R,...]
        for step in steps:
            # if we find a successful match ex. U01 and L01
            if step != active_step and step[1:] == active_suffix:
                # get the prefix of the step with a matching suffix
                # L01 -> L
                found_prefix = step[0]  # grab the found steps prefix
                # then remove it from the list
                steps.remove(step)  # len(steps)-1
                # and add the new step form into the new_steps array
                new_steps.append(active_prefix + divider + found_prefix + active_suffix)
                # we made item combo, so leave loop
                break

        # if we didnt add a new item from the above for loop
        if len(new_steps) == old_len:
            # then we didnt find a matching step ex. U01 and L01
            # we must have no matches, append normal step
            new_steps.append(active_step)

    return new_steps


# gets a steps prefix from a set of possibilities


def get_prefix(step, prefixes=[r"U|L", "U", "L"]):
    # set active prefix for current step
    for prefix in prefixes:
        try:
            # we use regular expression instead of join so we can have a prefix and suffix of the same type not be combined
            # need to make characters literal for pattern matching
            # "".join(_ for _ in steps[i] if _ in prefix else break) #makes "" if cant find
            active_prefix = re.search(prefix.replace(r"|", r"\|"), step).group(0)
            # compare found prefix in step
            # ex. L01U -> 'U' found -> 'U' index 3 != 0
            # ex. U01 -> 'U' found -> 'U' index 0 == 0
            # remove active_prefix and check to see if pattern matches
            # ex. prefix = 'U' -> U|L01R -> |L01R does not match '^\d+(\D|)' pattern
            # ex. prefix = 'L' -> L01R -> 01R does match '^\d+(\D|)' pattern
            # ex. prefix = 'L' -> L01 -> 01 does match '^\d+(\D|)' pattern
            if (
                step.rfind(active_prefix) == 0
                and re.search(
                    r"^(\d+|)(\D+\^\d+|\^\d+|\D+|)$", step.replace(active_prefix, "")
                )
                is not None
            ):  # check if suffix is good
                break  # we found a match, leave loop
            else:
                active_prefix = ""  # makes "" if cant find
        except Exception:
            active_prefix = ""  # makes "" if cant find
    return active_prefix


# gets a steps suffix from a set of possibilities
# suffix must have fufilled length of step
# ex. suffix R -> U01R != U01RQ even though R is found in both


def get_suffix(step, suffixes=[""]):
    # set active suffix for current step
    for suffix in suffixes:
        try:
            # we use regular expression instead of join so we can have a prefix and suffix of the same type not be combined
            # need to make characters literal for pattern matching
            # "".join(_ for _ in steps[i] if _ in suffix else break) #makes "" if cant find
            active_suffix = re.search(suffix.replace(r"^", r"\^"), step).group(0)
            # compare found suffix in step
            # ex. U01R^2 with suffix check 'R'
            # U01R^2 -> 'R' found -> U01R^2[:3+1-1] -> len(U01R) != len(U01R^2)
            if len(step[: step.find(suffix) + len(suffix)]) == len(
                step
            ):  # check if suffix is good
                break  # we found a match, leave loop
            else:
                active_suffix = ""  # makes "" if cant find
        except Exception:
            active_suffix = ""  # makes "" if cant find
    return active_suffix


# convert a list of numbers into a range
# must be sorted


def combine_range(steps, prefixes=[r"U|L", "U", "L"], suffixes=[""]):
    # yield 2-tuple ranges or 1-tuple single elements from list of increasing ints
    length = len(steps)
    i = 0
    while i < length:
        # set active prefix for current step
        active_prefix = get_prefix(steps[i], prefixes)
        active_suffix = get_suffix(steps[i], suffixes)

        # set low
        try:
            # int("".join(_ for _ in steps[i] if _ in "0123456789")) #set low integer
            low_step = int(
                re.search(r"\d+", steps[i].replace(active_suffix, "")).group(0)
            )
        except Exception:  # if low_step has no digit
            i += 1  # iterate past step with no digit
            # then yield prefix and suffix, there is no range
            yield active_prefix + active_suffix
            continue

        # find high
        while i < length - 1:
            try:
                current_step = (
                    int(re.search(r"\d+", steps[i].replace(active_suffix, "")).group(0))
                    + 1
                )
            except Exception:  # if we find a steps[i + 1] that has no digit
                i += 1  # iterate past step with no digit
                yield active_prefix + active_suffix  # also yield the step with no digit
                continue  # then continue the function leaving the while loop
            try:
                next_step = int(
                    re.search(r"\d+", steps[i + 1].replace(active_suffix, "")).group(0)
                )
                # "".join(_ for _ in steps[i] if (_ in active_prefix and len(_) != len(active_prefix)) else break)
                current_prefix = get_prefix(steps[i], [active_prefix])
                # "".join(_ for _ in steps[i+1] if (_ in active_prefix and len(_) != len(active_prefix)) else break)
                next_prefix = get_prefix(steps[i + 1], [current_prefix])
                # "".join(_ for _ in steps[i] if (_ in active_suffix and len(_) != len(active_suffix)) else break)
                current_suffix = get_suffix(steps[i], [active_suffix])
                # "".join(_ for _ in steps[i+1] if (_ in active_suffix and len(_) != len(active_suffix)) else break)
                next_suffix = get_suffix(steps[i + 1], [current_suffix])

                if (
                    current_step == next_step
                    and current_prefix == next_prefix
                    and current_suffix == next_suffix
                ):
                    # if step[i]+1 == steps[i+1] and step[i].prefix == step[i+1].prefix and step[i].suffix == step[i+1].suffix
                    i += 1  # move high by +1
                else:
                    break
            except (
                Exception
            ):  # if we find a steps[i + 1] that has a different prefix suffix
                break
        # set high
        # int("".join(_ for _ in steps[i] if _ in "0123456789")) #set high integer
        high_step = int(re.search(r"\d+", steps[i].replace(active_suffix, "")).group(0))

        # check if range or single step for high and low
        if high_step - low_step >= 1:
            # if ex. 10 - 7 = 3 > 2 -> then we have a range and not a single number
            yield active_prefix + str("{:02d}".format(low_step)) + "-" + str(
                "{:02d}".format(high_step)
            ) + active_suffix
        else:
            # we dont have a high that is > low
            yield active_prefix + str("{:02d}".format(low_step)) + active_suffix

        i += 1  # check next iteration after the old high value
    return


# takes a shade and converts it to the individual steps


def gen_steps(shade, delimiter=";"):
    step_list = []
    try:
        steps_array = shade.split(delimiter)
        for i in range(0, len(steps_array)):
            step_list.extend(check_step(steps_array[i]))
    except Exception as e:
        return step_list

    return step_list


# helper function for gen_steps function
# comments for process is given in the equivalent C# code


def check_step(step):
    step_list = []

    carrot = -1
    dash = -1
    prefix = ""
    suffix = ""
    numsteps = -1
    start = -1
    end = -1
    length = len(step)

    pattern_list = [
        r"\^\d+",
        r"^\D$",
        r"^\D\D$",
        r"^\D\d+$",
        r"^\D\d+\D$",
        r"^\D\d+-\d+$",
        r"^\D\d+-\d+\D$",
        r"^\D\|\D",
    ]

    for i in range(0, len(pattern_list)):
        x = re.search(pattern_list[i], step)
        if x is not None:
            if i == 0:
                carrot = step.find("^")
                numsteps = int(step[carrot + 1 : length])
                rest = step[:carrot]  # everything before carrot

                for j in range(0, numsteps):
                    step_list.extend(check_step(rest))
            # ^\D\D$ or ^\D$ or ^\D\d+$ or ^\D\d+\D
            if i == 1 or i == 2 or i == 3 or i == 4:
                step_list.append(step)
            # ^\D\d+-\d+$
            elif i == 5:
                prefix = step[0]
                dash = step.find("-")
                start = int(step[1:dash])
                # length cause we have no carrot or suffix
                end = int(step[dash + 1 : length])

                stepnum = start
                while stepnum <= end:
                    step_list.append(prefix + "{0:0=2d}".format(stepnum))
                    stepnum += 1
            # ^\D\d+-\d+\D$
            elif i == 6:
                prefix = step[0]
                suffix = step[length - 1]
                dash = step.find("-")
                start = int(step[1:dash])
                # length - 1 because we have suffix
                end = int(step[dash + 1 : length - 1])

                stepnum = start
                while stepnum <= end:
                    step_list.append(prefix + "{0:0=2d}".format(stepnum) + suffix)
                    stepnum += 1
            # ^\D\|\D
            elif (
                i == 7
            ):  # this is a special case where two prefixes are listed, the function recursively divides them into two seperate instances
                divider = step.find("|")  # location of |
                prefix1 = step[0:divider]  # first prefix ex: U|L -> U
                # second prefix ex: U|L -> L
                prefix2 = step[divider + 1 : divider + 2]
                rest = step[divider + 2 : len(step)]  # everything after prefixes

                step_list.extend(check_step(prefix1 + rest))
                step_list.extend(check_step(prefix2 + rest))
            break
        else:
            continue
    return step_list


def main():
    # shade = "U|L01-16;U|LA;U|L01-03R;U16"
    shade = "U|LT^20;U|L01^25;U|LR^25;U09A;U09"
    steps = gen_steps(shade)
    possible_result = [
        "U01R",
        "U02R",
        "U03R",
        "L01R",
        "L02R",
        "L03R",
        "U01R",
        "U01X",
        "U02X",
        "U03X",
        "U01Q",
        "U01Q",
        "U01Q",
        "U01",
        "UR",
        "UA",
    ]
    # steps = gen_steps("U|L89-91A^2;LAAAAAA;LA^2;UT;UT^2;U01;asdfa;U0AAA;U78^4;U09-13A^2;U09-13A^A")
    # possible_result = ['U89A', 'U90A', 'U91A', 'U89A', 'U90A', 'U91A', 'L89A', 'L90A', 'L91A', 'L89A', 'L90A', 'L91A', 'LA', 'LA', 'UT', 'UT', 'UT', 'U01', 'U78', 'U78', 'U78', 'U78', 'U09A', 'U10A', 'U11A', 'U12A', 'U13A', 'U09A', 'U10A', 'U11A', 'U12A', 'U13A']
    print(shade)
    print(steps)
    print(possible_result)
    print(sorted(steps) == sorted(possible_result))
    print("------------------------")

    print(shade)
    new_shade = gen_shade(steps)
    new_steps = gen_steps(new_shade)
    # remake steps, it was deleted due to reference made in combine_like_terms
    steps = gen_steps(shade)
    print(sorted(steps))
    print(new_shade)
    print(sorted(new_steps))
    print(sorted(steps) == sorted(new_steps))
    # print(combine_UL(['U01', 'U01', 'L01']))


if __name__ == "__main__":
    main()
