import unittest
from kernel.seed import GravFieldSeed

class SeedFailClosedTests(unittest.TestCase):
    def setUp(self):
        self.seed = GravFieldSeed()

    def test_missing_metrics_never_pass(self):
        self.assertEqual(self.seed.execute({'hello':'world'})['status'], 'BLOCK')
        self.assertEqual(len(self.seed.ledger), 0)

    def test_missing_measurement_source_never_pass(self):
        self.assertEqual(self.seed.execute({}, metrics={'psi':.95,'omega':.95,'cvar':.01})['status'], 'BLOCK')

    def test_valid_candidate_requires_external_authority(self):
        r = self.seed.execute({}, metrics={'psi':.95,'omega':.95,'cvar':.01}, measurement_ref='example-measurement')
        self.assertEqual(r['status'], 'HOLD_AUTHORITY')
        self.assertFalse(r['effect_applied'])

    def test_rejected_threshold(self):
        r = self.seed.execute({}, metrics={'psi':.3,'omega':.95,'cvar':.01}, measurement_ref='example')
        self.assertEqual(r['status'], 'BLOCK')

    def test_nonfinite_invalid_and_boolean_metric(self):
        for value in [float('nan'),float('inf'),True]:
            r = self.seed.execute({}, metrics={'psi':value,'omega':.95,'cvar':.01}, measurement_ref='example')
            self.assertEqual(r['status'], 'BLOCK')

    def test_unserializable_inputs_block(self):
        r = self.seed.execute({'v':object()},metrics={'psi':.95,'omega':.95,'cvar':.01},measurement_ref='example')
        self.assertEqual(r['status'], 'BLOCK')

if __name__ == '__main__':
    unittest.main()
