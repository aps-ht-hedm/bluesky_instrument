#!/usr/bin/env python

"""
This module contains motors customized for APS-MPE group.

EXAMPLE::

    tomostage = StageAero("", name='tomostage')
    psofly = EnsemblePSOFlyDevice("PV_PREFIX:", name="psofly")

TODO:
* The motor controls here also include those defined through FPGA.
* Additional work is required once the actual PVs are knwon.
"""


from ophyd import Component
from ophyd import Device
from ophyd import EpicsMotor
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import MotorBundle


class MyMotorBundle(MotorBundle):
    """Apply local enhancements."""

    @property
    def wh(self):
        """
        wh -- where: Return table of motors, PVs, and current positions.
        
        Re-named from ``status`` to avoid confusion with ophyd's Status
        objects.
        """
        import pyRestTable

        table = pyRestTable.Table()
        table.labels = "name PV position".split()
        for nm in self.component_names:
            try:
                motor = getattr(self, nm)
                v = motor.position  # excepts here if not a motor
                row = [nm,]
                if "pvname" in dir(motor):
                    row.append(motor.pvname)
                else:
                    row.append(motor.prefix)
                row.append(v)
                table.addRow(row)
            except AttributeError:
                continue
        return table

    def cache_position(self):
        """
        Cache current motor positions.
        
        Build dictionary from component that are EpicsMotor subclass
        (or override in subclass).
        """
        positions_now = {
            nm: getattr(self, nm).position
            for nm in self.component_names
            if "position" in dir(getattr(self, nm))
        }
        # TODO: Consider what to do if there is mismatch between
        #   self._position_cache and positions_now.
        #   Could happen when a motor is moved manually.
        self._position_cache = positions_now

    def resume_position(self):
        """Move motors to cached position."""
        if "position_cached" not in dir(self):
            raise AttributeError(
                "Cannot resume. Must first call 'cache_position()'"
            )

        # Move all positioners to cached positions.
        all_status = None  # watch all moves with ``AndStatus`` object
        for nm, v in self._position_cache.items():
            motor = getattr(self, nm)
            st = motor.move(v, wait=False)
            if all_status is None:
                all_status = st
            else:
                all_status = all_status.__and__(st)  # AndStatus

        # Wait for all motions to end or timeout.
        if all_status is not None:
            all_status.wait()


class TomoCamStage(MyMotorBundle):
    """
    Motor stacks used for Tomo Camera

        _____________
        |   Tomo Y  |
        =============
        |   Tomo X  |
        =============
        |   Tomo Z  |
        -------------

    """
    tomoy = Component(EpicsMotor, "6idhedm:m48", name='tomoy')  # x motion with kohzu stage
    tomox = Component(EpicsMotor, "6idhedm:m45", name='tomox')  # y motion with kohzu stage
    tomoz = Component(EpicsMotor, "6idhedm:m46", name='tomoz')  # z motion with kohzu stage


# NOTE:
# The NFCamStage should have similar structure of the Tomo stage


class FFCamStage(MyMotorBundle):
    """
    Motor stacks used for Tomo Camera

        ___________
        |   FF Y  |
        ===========
        |   FF X  |
        ===========
        |   FF Z  |
        -----------

    """
    # ffy = Component(EpicsMotor, "6idhedm:m48", name='ffy')  # x motion with kohzu stage
    # FIXME: PV names unknown here
    ffx = Component(EpicsMotor, "6idhedm:m$$", name='ffz')  # y motion with kohzu stage
    ffz = Component(EpicsMotor, "6idhedm:m$$", name='ffz')  # z motion with kohzu stage


class AeroEpicsMotor(EpicsMotor):
    dial_readback = Component(EpicsSignalRO, '.DRBV', kind='hinted',auto_monitor=True)
    dial_setpoint = Component(EpicsSignal, '.DVAL', limits=True)


class StageAero(MyMotorBundle):
    """
    Motor stacks used for HT-HEDM

        ___________________________________
        |   fine translation:  kx,ky,kz   |
        |   fine tilt: kx_tilt, kz_tilt   |
        ===================================
        |    air-bearing rotation: rot    |
        ===================================
        |  coarse translation below Aero: |
        |     x_base, y_base, z_base      |
        -----------------------------------

    """

    kx          = Component(EpicsMotor, "6idhedm:m41", name='kx_trans')  # x motion with kohzu stage
    ky          = Component(EpicsMotor, "6idhedm:m40", name='ky_trans')  # y motion with kohzu stage
    kz          = Component(EpicsMotor, "6idhedm:m42", name='kz_trans')  # z motion with kohzu stage
    kx_tilt     = Component(EpicsMotor, "6idhedm:m44", name='kx_tilt')   # kohzu tilt motion along x
    kz_tilt     = Component(EpicsMotor, "6idhedm:m43", name='kz_tilt')   # kohzu tilt motion along z

    rot         = Component(AeroEpicsMotor, "6idhedms1:m1",  name='rot_y'  )    # rotation with aero stage

    x_base      = Component(EpicsMotor, "6idhedm:m37",  name='x_trans')    # x motion below aero stage
    tiltx_base  = Component(EpicsMotor, "6idhedm:m38",  name='tiltx_base')    # y motion below aero stage
    tiltz_base  = Component(EpicsMotor, "6idhedm:m39",  name='tiltz_base')    # z motion below aero stage


class SimStageAero(MyMotorBundle):
    """
    Simulated Motor stacks used for HT-HEDM (6iddSIM:m1)

    Sim motors assigned as follows::

        kx          = m1
        ky          = m2
        kz          = m3
        rot         = m4

        kx_tilt     = m16
        kz_tilt     = m16
        x_base      = m16
        tiltx_base  = m16
        tiltz_base  = m16

        ___________________________________
        |   fine translation:  kx,ky,kz   |
        |   fine tilt: kx_tilt, kz_tilt   |
        ===================================
        |    air-bearing rotation: rot    |
        ===================================
        |  coarse translation below Aero: |
        |  x_base, tiltx_base, tiltz_base |
        -----------------------------------

    """

    # TODO: update with actual PV
    kx          = Component(EpicsMotor, "6iddSIM:m1", name='kx_trans')  # x motion with kohzu stage
    ky          = Component(EpicsMotor, "6iddSIM:m2", name='ky_trans')  # y motion with kohzu stage
    kz          = Component(EpicsMotor, "6iddSIM:m3", name='kz_trans')  # z motion with kohzu stage
    kx_tilt     = Component(EpicsMotor, "6iddSIM:m16", name='kx_tilt')   # kohzu tilt motion along x
    kz_tilt     = Component(EpicsMotor, "6iddSIM:m16", name='kz_tilt')   # kohzu tilt motion along z

    rot         = Component(EpicsMotor, "6iddSIM:m4",  name='rot_y'  )    # rotation with aero stage

    x_base      = Component(EpicsMotor, "6iddSIM:m16",  name='x_trans')    # x motion below aero stage
    tiltx_base  = Component(EpicsMotor, "6iddSIM:m16",  name='tiltx_trans')    # y motion below aero stage
    tiltz_base  = Component(EpicsMotor, "6iddSIM:m16",  name='tiltz_trans')    # z motion below aero stage


class TaxiFlyScanDevice(Device):
    """
    BlueSky Device for APS taxi & fly scans

    Some EPICS fly scans at APS are triggered by a pair of
    EPICS busy records. The busy record is set, which triggers
    the external controls to do the fly scan and then reset
    the busy record.

    The first busy is called taxi and is responsible for
    preparing the hardware to fly.
    The second busy performs the actual fly scan.
    In a third (optional) phase, data is collected
    from hardware and written to a file.
    """

    taxi    = Component(EpicsSignal, "taxi", put_complete=True)
    fly     = Component(EpicsSignal, "fly",  put_complete=True)

    reset_fpga = EpicsSignal("6idMZ1:SG:BUFFER-1_IN_Signal.PROC", put_complete=True, name = 'reset_fpga')
    pso_state  = EpicsSignal("6idMZ1:SG:AND-1_IN1_Signal",        put_complete=True, name = 'pso_state')  # only accept str as its input

    fi1_signal = EpicsSignal("6idMZ1:SG:FI1_Signal", put_complete=True, name = 'fi1_signal')
    fi2_signal = EpicsSignal("6idMZ1:SG:FI2_Signal", put_complete=True, name = 'fi2_signal')
    fi3_signal = EpicsSignal("6idMZ1:SG:FI3_Signal", put_complete=True, name = 'fi3_signal')
    fi4_signal = EpicsSignal("6idMZ1:SG:FI4_Signal", put_complete=True, name = 'fi4_signal')
    fi5_signal = EpicsSignal("6idMZ1:SG:FI5_Signal", put_complete=True, name = 'fi5_signal')

    def plan(self):
        import bluesky.plan_stubs as bps

        yield from bps.mv(self.taxi, self.taxi.enum_strs[1])
        yield from bps.mv(self.fly, self.fly.enum_strs[1])


class EnsemblePSOFlyDevice(TaxiFlyScanDevice):
    """Aerotech Ensemble PSOfly control wrapper."""
    motor_pv_name = Component(EpicsSignalRO, "motorName")
    start         = Component(EpicsSignal,   "startPos")
    end           = Component(EpicsSignal,   "endPos")
    slew_speed    = Component(EpicsSignal,   "slewSpeed")

    # scan_delta: output a trigger pulse when motor moves this increment
    scan_delta = Component(EpicsSignal, "scanDelta")

    # advanced controls
    delta_time          = Component(EpicsSignalRO, "deltaTime"   )
    detector_setup_time = Component(EpicsSignal,   "detSetupTime")
    pulse_type          = Component(EpicsSignal,   "pulseType"   )
    scan_control        = Component(EpicsSignal,   "scanControl" )
