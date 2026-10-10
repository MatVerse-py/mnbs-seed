"""MatVerse seed policy evaluator (not a production authorizer).

Security correction: metrics MUST be supplied and are never fabricated.
An eligible decision never implies an effect or a trusted authorization.
This module has no network, shell or provider adapter side effects.
"""
from __future__ import annotations
import hashlib
import json
import math
import time
from typing import Mapping

THRESHOLDS = {'psi_min': 0.85, 'omega_min': 0.85, 'cvar_max': 0.05}

class GravFieldSeed:
    """A fail-closed policy *candidate* evaluator without execution privileges."""

    def __init__(self):
        self.ledger = []

    @staticmethod
    def _metric(value):
        if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError('METRIC_INVALID: finite numeric [0,1] required')
        return float(value)

    def potential(self, psi, omega, cvar):
        psi, omega, cvar = (self._metric(x) for x in (psi, omega, cvar))
        return 1.2 * psi - 1.5 * cvar + omega

    def gate(self, psi, omega, cvar):
        psi, omega, cvar = (self._metric(x) for x in (psi, omega, cvar))
        return psi >= THRESHOLDS['psi_min'] and cvar <= THRESHOLDS['cvar_max'] and omega >= THRESHOLDS['omega_min']

    def build_event(self, input_data, *, metrics=None, measurement_ref=None):
        """Metrics are external observations; a hash/source ref is not trusted authority."""
        if not isinstance(metrics, Mapping) or not isinstance(measurement_ref, str) or not measurement_ref.strip():
            raise ValueError('MEASUREMENTS_REQUIRED: provide metrics and independent source ref')
        if set(metrics) != {'psi', 'omega', 'cvar'}:
            raise ValueError('MEASUREMENT_SCHEMA_MISMATCH')
        values = {k:self._metric(metrics[k]) for k in ('psi', 'omega', 'cvar')}
        try:
            json.dumps(input_data, allow_nan=False, sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise ValueError('INPUT_NOT_CANONICAL_JSON') from exc
        return {'data':input_data, **values, 'measurement_ref':measurement_ref.strip(), 'ts':time.time_ns()}

    def execute(self, input_data, *, metrics=None, measurement_ref=None):
        """Legacy name; evaluates policy only. No action is ever executed."""
        try:
            event = self.build_event(input_data, metrics=metrics, measurement_ref=measurement_ref)
        except ValueError as exc:
            return {'status':'BLOCK', 'reason':str(exc), 'effect_applied':False}
        psi, omega, cvar = (event[k] for k in ('psi', 'omega', 'cvar'))
        eligible = self.gate(psi, omega, cvar)
        result={'eligible':eligible, 'phi':self.potential(psi, omega, cvar),
                'effect_applied':False, 'authority_bound':False,
                'decision_status':'CANDIDATE_ONLY' if eligible else 'BLOCK'}
        payload=json.dumps({'event':event,'result':result},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
        digest=hashlib.sha256(payload.encode('utf-8')).hexdigest()
        self.ledger.append({'event':event,'decision':result,'digest':digest})
        return {'status':'HOLD_AUTHORITY' if eligible else 'BLOCK', 'reason':
                'PROVIDER_AUTHORITY_UNBOUND' if eligible else 'THRESHOLD_REJECTED',
                'result':result,'digest':digest,'effect_applied':False,
                'ledger_size':len(self.ledger)}
