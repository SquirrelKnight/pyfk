from os.path import join, dirname

import numpy as np
import obspy

from pyfk.config.config import Config, SeisModel, SourceModel
from pyfk.gf.gf import calculate_gf
from pyfk.sync.sync import calculate_sync, generate_source_time_function
from pyfk.tests.taup.test_taup import TestFunctionTaup


class TestFunctionCalculateSync(object):
    @staticmethod
    def test_prem():
        model_data = TestFunctionTaup.gen_test_model("prem")
        model_prem = SeisModel(model=model_data)
        source_prem = SourceModel(sdep=16.5)
        # * note, use larger distance will integrate more, the waveform of only calculating 10km and calculating to 100km will be grealy different
        config_prem = Config(
            model=model_prem,
            source=source_prem,
            npt=512,
            dt=0.1,
            receiver_distance=np.arange(10, 20, 10))
        gf = calculate_gf(config_prem)
        # # * calculate sync_prem_gcmt for the event
        event = obspy.read_events(
            join(
                dirname(__file__),
                "../data/sync_prem_gcmt/test_gcmt"))[0]
        source_prem.update_source_mechanism(event)
        # # * generate a source time function
        source_time_function = generate_source_time_function(
            4, 0.5, gf[0][0].stats.delta)
        sync_result = calculate_sync(gf, config_prem, 30, source_time_function)
        # * test if the cc value is large enough
        for index, component in enumerate(["z", "r", "t"]):
            sac_path = join(dirname(__file__),
                            f"../data/sync_prem_gcmt/prem.{component}")
            sac_wave = obspy.read(sac_path)[0].data
            coef = np.corrcoef(
                sac_wave,
                sync_result[0][index].data,
            )[0, 1]
            assert coef > 0.9999
