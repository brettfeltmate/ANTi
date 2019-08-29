from klibs.KLIndependentVariable import IndependentVariableSet

ANTi_ind_vars = IndependentVariableSet()
ANTi_ind_vars.add_variable('cue_type', str, ['invalid', 'valid', 'none'])
ANTi_ind_vars.add_variable('congruent', bool, [True, False])
ANTi_ind_vars.add_variable('tone_trial', bool, [True, False])
ANTi_ind_vars.add_variable('target_location', str, ['above', 'below'])