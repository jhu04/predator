import time
import z3
import xlsxwriter


def z3_min(a, b):
    return z3.If(a < b, a, b)


def name(i: int, j: int) -> str:
    """Variable name for state with i deficit and j rolls remaining."""
    return f"{i} {j}"


def main():
    start = time.time()  # Too lazy to use perf_counter

    probabilities = [0.85, 0.10, 0.05]

    # We ignore the time for the plane bosses, plane 2 respite, and plane 3 transaction domains as we assume we hit them so
    # rarely that they play a negligible role.
    reset_time = 51
    combat_time = 17

    # Assuming we hit 2 elites in first plane, 3 elites in second plane, 1 elite in third plane
    rolls = 16
    deficit = 12

    # Too many variables causes z3 to take a long time to solve
    print("SOLVING SYSTEM OF", (rolls + 1) * (deficit + 1), "VARIABLES WITH", rolls, "ROLLS AND", deficit, "DEFICITS")

    z3.set_option(rational_to_decimal=True, precision=5)

    solver = z3.Solver()

    # states[i][j] = expected rolls to flip at least i heads with j flips remaining
    states = [[z3.Real(name(i, j)) for j in range(rolls + 1)] for i in range(deficit + 1)]

    solver.add(states[0][0] == 0)

    # naive reset: only reset when all flips have been flipped
    for i in range(1, deficit + 1):
        solver.add(states[i][0] == states[deficit][rolls])

    # if there is zero deficit, it is always optimal to keep rolling as you are guaranteed a win
    # for i in range(1, rolls + 1):
    #     solver.add(states[0][i] == 1 + states[0][i - 1])

    for i in range(deficit + 1):
        for j in range(1, rolls + 1):
            if i != deficit or j != rolls:
                solver.add(states[i][j] == z3_min(
                    states[deficit][rolls],
                    combat_time + z3.Sum(tuple(p * states[max(i - di, 0)][j - 1] for di, p in enumerate(probabilities)))
                    # TOOD: account for different domain times
                ))
            else:
                # assume it is never optimal to reset on the first domain
                solver.add(states[i][j] == reset_time + z3.Sum(
                    tuple(p * states[max(i - di, 0)][j - 1] for di, p in enumerate(probabilities))))

    print("CHECK:", solver.check())
    model = solver.model()
    print("MODEL:", model)

    with xlsxwriter.Workbook(f"out/{deficit}-deficit-{rolls}-rolls.xlsx") as workbook:
        worksheet = workbook.add_worksheet()

        for d in range(deficit + 1):
            for r in range(rolls + 1):
                print(f"{d} DEFICIT AND {r} ROLLS EXPECTED: {model[states[d][r]]}")

                worksheet.write_number(d, r, model[states[d][r]].as_fraction())

        init = model[states[deficit][rolls]].as_fraction()
        worksheet.conditional_format(0, 0, deficit, rolls, {
            "type": "cell",
            "criteria": "=",
            "value": init,
            "format": workbook.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})
        })
        worksheet.conditional_format(0, 0, deficit, rolls, {
            "type": "cell",
            "criteria": "!=",
            "value": init,
            "format": workbook.add_format({"bg_color": "#C6EFCE", "font_color": "#0006100"})
        })

    print("EXPECTED TIME TO GET ACHIEVEMENT:", model[states[deficit][rolls]])
    print("COMPUTE TIME TAKEN:", time.time() - start)


if __name__ == '__main__':
    main()
