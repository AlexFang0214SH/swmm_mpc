import string
import random
import os
from shutil import copyfile
import subprocess
from rpt_ele import rpt_ele
import update_process_model_input_file as up
from swmm_mpc import inp_process_file_inp, inp_process_file_base,\
    control_time_step, control_str_ids, inp_file_dir, fmt_control_policies,\
    n_control_steps, node_flood_weight_dict, target_depth_dict


def evaluate(individual):
    FNULL = open(os.devnull, 'w')
    # make process model tmp file
    rand_string = ''.join(random.choice(
        string.ascii_lowercase + string.digits) for _ in range(9))
    inp_tmp_process_file_base = inp_process_file_base + '_tmp' + rand_string
    inp_tmp_process_inp = os.path.join(inp_file_dir,
                                       inp_tmp_process_file_base + '.inp')
    inp_tmp_process_rpt = os.path.join(inp_file_dir,
                                       inp_tmp_process_file_base + '.rpt')
    copyfile(inp_process_file_inp, inp_tmp_process_inp)

    # make copy of hs file
    hs_filename = up.read_hs_filename(inp_process_file_inp)
    tmp_hs_file_name = hs_filename.replace('.hsf',
                                           '_tmp_{}.hsf'.format(rand_string))
    tmp_hs_file = os.path.join(inp_file_dir, tmp_hs_file_name)
    copyfile(os.path.join(inp_file_dir, hs_filename), tmp_hs_file)

    # convert individual to percentages
    indivi_percentage = [setting/10. for setting in individual]
    policies = fmt_control_policies(indivi_percentage, control_str_ids,
                                    n_control_steps)

    # update controls
    up.update_controls_and_hotstart(inp_tmp_process_inp, control_time_step,
                                    policies, tmp_hs_file)

    # run the swmm model
    cmd = 'swmm5 {0}.inp {0}.rpt'.format(inp_tmp_process_file_base)
    subprocess.call(cmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

    # read the output file
    rpt = rpt_ele('{}.rpt'.format(inp_tmp_process_file_base))
    node_flood_costs = []

    # get flooding costs
    if not rpt.flooding_df.empty and node_flood_weight_dict:
        for nodeid, weight in node_flood_weight_dict.iteritems():
            # try/except used here in case there is no flooding for one or
            # more of the nodes
            try:
                # flood volume is in column, 5
                node_flood_volume = float(rpt.flooding_df.loc[nodeid, 5])
                node_flood_cost = (weight*node_flood_volume)
                node_flood_costs.append(node_flood_cost)
            except:
                pass
    else:
        node_flood_costs.append(rpt.total_flooding)

    # get deviation costs
    node_deviation_costs = []
    if target_depth_dict:
        for nodeid, data in target_depth_dict.iteritems():
            avg_dev = abs(data['target'] - float(rpt.depth_df.loc[nodeid, 2]))
            weighted_deviation = avg_dev*data['weight']
            node_deviation_costs.append(weighted_deviation)

    # convert the contents of the output file into a cost
    cost = sum(node_flood_costs) + sum(node_deviation_costs)
    os.remove(inp_tmp_process_inp)
    os.remove(inp_tmp_process_rpt)
    os.remove(tmp_hs_file)
    return cost,
