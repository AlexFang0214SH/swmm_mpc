import unittest
from swmm_mpc import evaluate
from swmm_mpc.rpt_ele import rpt_ele


class test_evaluate(unittest.TestCase):
    rpt_file = "example.rpt"
    rpt = rpt_ele(rpt_file)

    def test_get_flood_cost_no_dict(self):
        node_fld_wgt_dict = None
        cost = evaluate.get_flood_cost(self.rpt, node_fld_wgt_dict)
        self.assertEqual(cost, 0.320)

    def test_get_flood_cost_dict(self):
        node_fld_wgt_dict = {"J3":1, "St1":1, "St2":1}
        cost = evaluate.get_flood_cost(self.rpt, node_fld_wgt_dict)
        self.assertEqual(cost, 0.640)

    def test_gene_to_policy_dict(self):
        gene = [1, 0, 1, 1, 1, 0, 0, 1]
        n_ctl_steps = 2
        ctl_str_ids = ["ORIFICE r1", "PUMP p1"]
        policy = evaluate.gene_to_policy_dict(gene, ctl_str_ids, n_ctl_steps)
        # print (policy)
        self.assertEqual(policy, {'ORIFICE r1': [0.714, 0.857],
                                  'PUMP p1': ['OFF', 'ON']})

    def test_bits_to_perc(self):
        bits = [1, 1, 0, 1]
        perc = evaluate.bits_to_perc(bits)
        self.assertEqual(perc, 0.867)

    def test_bits_to_decimal(self):
        bits = [1, 0, 1, 1]
        dec = evaluate.bits_to_decimal(bits)
        self.assertEqual(dec, 11)

    def test_bits_max_val(self):
        bit_len = 8
        max_val = evaluate.bits_max_val(bit_len)
        self.assertEqual(max_val, 255)


if __name__ == '__main__':
        unittest.main()
