import qt
import numpy as np

from measurement.lib.measurement2.adwin_ssro import ssro, pulsar_mbi_espin
from measurement.scripts.teleportation import parameters

def prepare(m, sil_name, yellow = False):
    # m.params.from_dict(qt.cfgman.get('samples/'+sil_name))
    # m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO'))
    # m.params.from_dict(qt.cfgman.get('protocols/'+sil_name+'-default/AdwinSSRO'))
    # m.params.from_dict(qt.cfgman.get('protocols/'+sil_name+'-default/AdwinSSRO-integrated'))
    # m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO+MBI'))
    # m.params.from_dict(qt.cfgman.get('protocols/'+sil_name+'-default/AdwinSSRO+MBI'))
    # m.params.from_dict(qt.cfgman.get('protocols/'+sil_name+'-default/pulses'))
    # # m.params.from_dict(qt.cfgman.get('protocols/hans-sil4-default/BSM'))

    for k in tparams.params.parameters:
        self.params[k] = tparams.params[k]

    for k in tparams.params_lt1.parameters:
        self.params_lt1[k] = tparams.params_lt1[k]

    # ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    # m.params['repump_duration']=m.params['greem_repump_duration']
    # m.params['repump_amplitude']=m.params['green_repump_amplitude']
    # m.params['CR_repump']=m.params['greem_CR_repump']

    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration']=m.params_lt1['repump_duration']
    m.params['repump_amplitude']=m.params_lt1['repump_amplitude']
    m.params['CR_repump']=m.params_lt1['CR_repump']

def finish(m, upload=True, debug=False):
    m.autoconfig()

    m.params['A_SP_durations'] = [m.params_lt1['repump_after_MBI_duration']]
    m.params['A_SP_amplitudes'] = [m.params_lt1['repump_after_MBI_amplitude']]
    m.params['E_RO_durations'] = [m.params_lt1['SSRO1_duration']]
    m.params['E_RO_amplitudes'] = [m.params_lt1['Ey_RO_amplitude']]
    m.params['send_AWG_start'] = [1]
    m.params['sequence_wait_time'] = [0]

    # m.params['A_SP_durations'] = [m.params['repump_after_MBI_duration']]
    # m.params['A_SP_amplitudes'] = [m.params['repump_after_MBI_amplitude']]
    # m.params['E_RO_durations'] = [m.params['SSRO_duration']]
    # m.params['E_RO_amplitudes'] = [m.params['Ex_RO_amplitude']]
    # m.params['send_AWG_start'] = [1]
    # m.params['sequence_wait_time'] = [0]
    
    m.generate_sequence(upload=upload)
    
    if not debug:
        m.setup()
        m.run()
        m.save()
        m.finish()