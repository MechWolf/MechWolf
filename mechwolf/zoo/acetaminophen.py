from .. import Apparatus, Protocol, Pump, TMixer, Tube, Vessel


def create_protocol(pump_1: Pump, pump_2: Pump) -> Protocol:
    # define the vessels
    aminophenol = Vessel("15 mL 4-aminophenol")
    acetic_anhydride = Vessel("15 mL acetic anhydride")
    acetaminophen = Vessel("acetaminophen")

    # define the mixer
    mixer = TMixer()

    # same tube specs for all tubes
    tube = Tube(length="1 m", ID="1/16 in", OD="2/16 in", material="PVC")

    # create the Apparatus object
    A = Apparatus(name="Acetaminophen synthesizer")
    A.add(from_component=aminophenol, to_component=pump_1, tube=tube)
    A.add(acetic_anhydride, pump_2, tube)
    A.add([pump_1, pump_2], mixer, tube)
    A.add(mixer, acetaminophen, tube)

    # create the protocol
    P = Protocol(A, name="acetaminophen synthesis")
    P.add([pump_1, pump_2], duration="15 mins", rate="1 mL/min")
    return P
