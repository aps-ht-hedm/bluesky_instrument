#!/usr/bin/env python

"""
Detectors customized for APS-MPE group.

EXAMPLE::

    # example on how to make an instance of the PointGrey detector
    det = PointGreyDetector("IOC_PREFIX:", name='det')

Additional setup might be necessary to use the ``dxchange`` format for
HDF5 output.  For more details, see:
https://github.com/BCDA-APS/bluesky_training/blob/main/.wip/images_darks_flats.ipynb

NOTE: This document URL may change.  If above document is not found, search with:
https://github.com/search?q=repo%3ABCDA-APS%2Fbluesky_training%20darks&type=code

NOTE:
* Retiga area detector is not readily available in Ophyd
* Retiga area detector camera needs to be either setup here or PR to ophyd
* Changed to PointGrey Detectors in this example
"""

from ophyd import ADComponent
from ophyd import AreaDetector
from ophyd import CamBase
from ophyd import EpicsSignal
from ophyd import EpicsSignalWithRBV
from ophyd import HDF5Plugin
from ophyd import ImagePlugin
from ophyd import PerkinElmerDetectorCam
from ophyd import PointGreyDetectorCam
from ophyd import ProcessPlugin
from ophyd import SingleTrigger
from ophyd import TIFFPlugin
from ophyd import TransformPlugin


class MyADEnhancements:
    """Common enhancements mixin class to area detector support here."""
    # TODO: access additional PVs as property,for interactive use as needed

    @property
    def status(self):
        """List all related PVs and corresponding values"""
        return "Not implemented yet"  # TODO:

    @property
    def help(self):
        """Return quick summary of the actual specs of the detector"""

    @property
    def position(self):
        """return the area detector position from the associated motor"""
        pass

    @position.setter
    def position(self, new_pos):
        """move the detector to the new location"""
        # NOTE:
        #   This is for interactive control only, cannot be used in scan plan
        pass


class HDF5Plugin6IDD(HDF5Plugin):
    """AD HDF5 plugin customizations (properties)"""
    xml_file_name = ADComponent(EpicsSignalWithRBV, "XMLFileName")


class GEDetector(SingleTrigger, AreaDetector):
    """
    Generic detector abstraction for GE.

    Example::

        det = GEDetector("GE2:", name='det')
    """
    # TODO:  we might need to switch to raw
    cam1  = ADComponent(CamBase, suffix="cam1:")
    proc1 = ADComponent(ProcessPlugin, suffix="Proc1:")
    tiff1 = ADComponent(TIFFPlugin, suffix="TIFF1:")


class VarexTransformPlugin(TransformPlugin):
    """Add Types handle"""
    transformation_type = ADComponent(EpicsSignal, "Type")


class Varex4343CTCAM6IDD(PerkinElmerDetectorCam):
    """Varex 4343CT cam plugin customizations based on PerkinElmerDetectorCam(properties)"""
    # TODO:  Add fields when needed
    # image_mode           = ADComponent(EpicsSignalWithRBV, "ImageMode")
    # acquire_time         = ADComponent(EpicsSignalWithRBV, "AcquireTime")
    # pe_gain              = ADComponent(EpicsSignalWithRBV, "PEGain")
    # num_images           = ADComponent(EpicsSignalWithRBV, "NumImages")
    # trigger_mode         = ADComponent(EpicsSignalWithRBV, "TriggerMode")
    # acquire              = ADComponent(EpicsSignalWithRBV, "Acquire")
    # wait_for_plugins     = ADComponent(EpicsSignalWithRBV, "WaitForPlugins")
    # pe_skip_frames       = ADComponent(EpicsSignalWithRBV, "PESkipFrames")
    pass


class Varex4343CT(MyADEnhancements, SingleTrigger, AreaDetector):
    """Varex 4343CT Detector used at 6-ID-D@APS for ff-HEDM"""
    # TODO: verify all these
    cam1   = ADComponent(Varex4343CTCAM6IDD,       suffix="cam1:"  )  # camera
    proc1  = ADComponent(ProcessPlugin,            suffix="Proc1:" )  # processing
    tiff1  = ADComponent(TIFFPlugin,               suffix="TIFF1:" )  # tiff output
    hdf1   = ADComponent(HDF5Plugin6IDD,           suffix="HDF1:"  )  # HDF5 output
    trans1 = ADComponent(VarexTransformPlugin,     suffix="Trans1:")  # Transform images
    image1 = ADComponent(ImagePlugin,              suffix="image1:")  # Image plugin, rarely used in plan

    def cont_acq(self, _exp, _nframes = -1):
        """
        Continuous image acquisition.

        EXAMPLE:

            det.cont_acq(0.1, 10)

        PARAMETERS

        _exp *float* :
            exposure time (seconds) per image
        _nframes *int* :
            number of images to acquire
            (default: -1 which will continue acquiring until manual interruption)
        """
        from time import sleep

        self.cam1.acquire_time.put(_exp)
        self.cam1.image_mode.put("Continuous")  # To be checked
        if _nframes <= 0:
            # do infinite number of frames....
            print(f"Start taking images with {_exp} seconds of exposure\n")
            print(f"Press \"Stop\" on 6IDFF:cam1 to stop acquisition.\n")
            sleep(0.5)
        else:
            self.cam1.image_mode.put("Multiple")
            print(f"Start taking {_nframes} images with {_exp} seconds of exposure\n")
            print(f"Press \"Stop\" on 6IDFF:cam1 to stop acquisition.\n")
            self.cam1.num_images.put(_nframes)
            sleep(0.5) # To be updated
        self.cam1.acquire.put(1)


class PointGreyDetectorCam6IDD(PointGreyDetectorCam):
    """PointGrey Grasshopper3 cam plugin customizations (properties)"""
    auto_exposure_on_off    = ADComponent(EpicsSignalWithRBV, "AutoExposureOnOff")
    auto_exposure_auto_mode = ADComponent(EpicsSignalWithRBV, "AutoExposureAutoMode")
    sharpness_on_off        = ADComponent(EpicsSignalWithRBV, "SharpnessOnOff")
    sharpness_auto_mode     = ADComponent(EpicsSignalWithRBV, "SharpnessAutoMode")
    gamma_on_off            = ADComponent(EpicsSignalWithRBV, "GammaOnOff")
    shutter_auto_mode       = ADComponent(EpicsSignalWithRBV, "ShutterAutoMode")
    gain_auto_mode          = ADComponent(EpicsSignalWithRBV, "GainAutoMode")
    trigger_mode_on_off     = ADComponent(EpicsSignalWithRBV, "TriggerModeOnOff")
    trigger_mode_auto_mode  = ADComponent(EpicsSignalWithRBV, "TriggerModeAutoMode")
    trigger_delay_on_off    = ADComponent(EpicsSignalWithRBV, "TriggerDelayOnOff")
    frame_rate_on_off       = ADComponent(EpicsSignalWithRBV, "FrameRateOnOff")
    frame_rate_auto_mode    = ADComponent(EpicsSignalWithRBV, "FrameRateAutoMode")


class PointGreyDetector(MyADEnhancements, SingleTrigger, AreaDetector):
    """PointGrey Detector used at 6-ID-D@APS for tomo and nf-HEDM"""

    cam1   = ADComponent(PointGreyDetectorCam6IDD, suffix="cam1:"  )  # camera
    proc1  = ADComponent(ProcessPlugin,            suffix="Proc1:" )  # processing
    tiff1  = ADComponent(TIFFPlugin,               suffix="TIFF1:" )  # tiff output
    hdf1   = ADComponent(HDF5Plugin6IDD,           suffix="HDF1:"  )  # HDF5 output
    trans1 = ADComponent(TransformPlugin,          suffix="Trans1:")  # Transform images
    image1 = ADComponent(ImagePlugin,              suffix="image1:")  # Image plugin, rarely used in plan

    def cont_acq(self, _exp, _period, _nframes = -1):
        """
        Continuous image acquisition.

        EXAMPLE:

            det.cont_acq(0.1, 0.5, 10)

        PARAMETERS

        _exp *float* :
            exposure time (seconds) per image
        _period *float* :
            time (seconds) between image starts
        _nframes *int* :
            number of images to acquire
            (default: -1 which will continue acquiring until manual interruption)
        """
        from time import sleep
        self.cam1.acquire_time.put(_exp)
        self.cam1.acquire_period.put(_period)
        self.cam1.image_mode.put("Continuous")  # To be checked
        if _nframes <= 0:
            # do infinite number of frames....
            print(f"Start taking images with {_exp} seconds of exposure\n")
            print(f"Press \"Stop\" on 1idPG4:cam1 to stop acquisition.\n")
            sleep(0.5)
        else:
            self.cam1.image_mode.put("Multiple")
            print(f"Start taking {_nframes} images with {_exp} seconds of exposure\n")
            print(f"Press \"Stop\" on 1idPG4:cam1 to stop acquisition.\n")
            self.cam1.n_images.put(_nframes)
            sleep(0.5) # To be updated
        self.cam1.acquire.put(1)


class SimDetectorCam6IDD(PointGreyDetectorCam):
    """
    Using SimDetector as PointGrey:
    cam plugin customizations (properties)
    """
    auto_exposure_on_off    = ADComponent(EpicsSignalWithRBV, "AutoExposureOnOff")
    auto_exposure_auto_mode = ADComponent(EpicsSignalWithRBV, "AutoExposureAutoMode")
    sharpness_on_off        = ADComponent(EpicsSignalWithRBV, "SharpnessOnOff")
    sharpness_auto_mode     = ADComponent(EpicsSignalWithRBV, "SharpnessAutoMode")
    gamma_on_off            = ADComponent(EpicsSignalWithRBV, "GammaOnOff")
    shutter_auto_mode       = ADComponent(EpicsSignalWithRBV, "ShutterAutoMode")
    gain_auto_mode          = ADComponent(EpicsSignalWithRBV, "GainAutoMode")
    trigger_mode_on_off     = ADComponent(EpicsSignalWithRBV, "TriggerModeOnOff")
    trigger_mode_auto_mode  = ADComponent(EpicsSignalWithRBV, "TriggerModeAutoMode")
    trigger_delay_on_off    = ADComponent(EpicsSignalWithRBV, "TriggerDelayOnOff")
    frame_rate_on_off       = ADComponent(EpicsSignalWithRBV, "FrameRateOnOff")
    frame_rate_auto_mode    = ADComponent(EpicsSignalWithRBV, "FrameRateAutoMode")


class SimDetector(MyADEnhancements, SingleTrigger, AreaDetector):
    """
    Simulated Detector used at 6-ID-D@APS, based on the Point Grey detector.
    """

    cam1  = ADComponent(SimDetectorCam6IDD, suffix="cam1:" )  # camera
    proc1 = ADComponent(ProcessPlugin,      suffix="Proc1:")  # processing
    tiff1 = ADComponent(TIFFPlugin,         suffix="TIFF1:")  # tiff output
    hdf1  = ADComponent(HDF5Plugin6IDD,     suffix="HDF1:" )  # HDF5 output
