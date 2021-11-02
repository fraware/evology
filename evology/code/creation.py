from sampling import *

def generate_creation_func(wealth_coordinates):

    def gen_rd_ind(wealth_coordinates):
        PROBA_NT = wealth_coordinates[0]
        PROBA_VI = wealth_coordinates[1]
        PROBA_TF = wealth_coordinates[2]

        rd = random.random()
        if rd <= PROBA_NT:
            return toolbox.gen_nt_ind()
        elif rd > PROBA_NT and rd <= PROBA_NT + PROBA_VI:
            return toolbox.gen_vi_ind()
        elif rd > PROBA_NT + PROBA_VI and rd <= PROBA_TF + PROBA_VI + PROBA_NT:
            return toolbox.gen_tf_ind()

    toolbox.register("gen_rd_ind", gen_rd_ind, wealth_coordinates)
    toolbox.register("gen_rd_pop", tools.initRepeat, list, toolbox.gen_rd_ind)


    def create_pop(mode, POPULATION_SIZE):
        if POPULATION_SIZE == 3 and mode == "between":
            # Create a Scholl et al. like population
            pop = adjust_mode(toolbox.gen_ref_pop(), mode)
            count_tf, count_vi, count_nt = 0, 0, 0
            for ind in pop:
                if ind.type == "tf":
                    count_tf += 1
                if ind.type == "vi":
                    count_vi += 1
                if ind.type == "nt":
                    count_nt += 1
            if count_tf == 1 and count_nt == 1 and count_vi == 1:
                pass
            else:
                raise ValueError('Population of 3 from Scholl et al. is not balanced.')
        if POPULATION_SIZE != 3 and mode == "between":
            # Create a random population with unique strategy per type
            pop = adjust_mode(toolbox.gen_rd_pop(n=POPULATION_SIZE), mode)
        if POPULATION_SIZE != 3 and mode != "between":
            # Create a random population with diversity within each type
            pop = toolbox.gen_rd_pop(n=POPULATION_SIZE)

        for ind in pop:
            if ind.type == 'tf':
                ind.leverage = LAMBDA_TF
            if ind.type == 'vi':
                ind.leverage = LAMBDA_VI
            if ind.type == 'nt':
                ind.leverage = LAMBDA_NT

        return pop
    return create_pop
