from datetime import timedelta
from typing import List, Sequence, cast

import mechwolf as mw


def validate_peptide(peptide: Sequence) -> List[str]:
    one_to_three_letter_aa_code = {
        "A": "ala",
        "C": "cys",
        "D": "asp",
        "E": "glu",
        "F": "phe",
        "G": "gly",
        "H": "his",
        "I": "ile",
        "K": "lys",
        "L": "leu",
        "M": "met",
        "N": "asn",
        "P": "pro",
        "Q": "gln",
        "R": "arg",
        "S": "ser",
        "T": "thr",
        "V": "val",
        "W": "trp",
        "Y": "tyr",
    }

    if isinstance(peptide, str):
        peptide = [one_to_three_letter_aa_code[aa] for aa in peptide]
    elif isinstance(peptide, list):
        _peptide = []
        for aa in peptide:
            if len(aa) == 1:
                _peptide.append(one_to_three_letter_aa_code[aa.upper()])
            elif len(aa) == 3:
                _peptide.append(aa.lower())
            else:
                raise ValueError("Must provide either one or three letter AA code.")
        peptide = _peptide

    return cast(List[str], peptide)


def create_apparatus(
    valve1: mw.Valve = mw.Valve(),
    valve2: mw.Valve = mw.Valve(),
    valve3: mw.Valve = mw.Valve(),
    pump1: mw.Pump = mw.Pump(),
    pump2: mw.Pump = mw.Pump(),
    pump3: mw.Pump = mw.Pump(),
) -> mw.Apparatus:

    aa_vessels = {
        "ala": mw.Vessel(name="ala", description="FmocAla"),
        "arg": mw.Vessel(name="arg", description="FmocArg_Pbf"),
        "asn": mw.Vessel(name="asn", description="FmocAsn_Trt"),
        "asp": mw.Vessel(name="asp", description="FmocAsp_tBu"),
        "cys": mw.Vessel(name="cys", description="FmocCys_Trt"),
        "gln": mw.Vessel(name="gln", description="FmocGln_Trt"),
        "glu": mw.Vessel(name="glu", description="FmocGlu_tBu"),
        "gly": mw.Vessel(name="gly", description="FmocGly"),
        "his": mw.Vessel(name="his", description="FmocHis_Trt"),
        "ile": mw.Vessel(name="ile", description="FmocIle"),
        "leu": mw.Vessel(name="leu", description="FmocLeu"),
        "lys": mw.Vessel(name="lys", description="FmocLys_Boc"),
        "met": mw.Vessel(name="met", description="FmocMet"),
        "phe": mw.Vessel(name="phe", description="FmocPhe"),
        "pro": mw.Vessel(name="pro", description="FmocPro"),
        "ser": mw.Vessel(name="ser", description="FmocSer_tBu"),
        "thr": mw.Vessel(name="thr", description="FmocThr_tBu"),
        "trp": mw.Vessel(name="trp", description="FmocTrp_Boc"),
        "tyr": mw.Vessel(name="tyr", description="FmocTyr_tBu"),
        "val": mw.Vessel(name="val", description="FmocVal"),
    }

    # other vessels
    solvent = mw.Vessel("Solvent", name="solvent")
    deprotection = mw.Vessel("20% Piperdine", name="deprotection")
    coupling_agent = mw.Vessel("HATU", name="coupling_agent")
    coupling_base = mw.Vessel("NMM", name="coupling_base")
    output = mw.Vessel("waste", name="output")

    valve1.mapping = {
        aa_vessels["ala"]: 1,
        aa_vessels["cys"]: 2,
        aa_vessels["asp"]: 3,
        aa_vessels["glu"]: 4,
        aa_vessels["phe"]: 5,
        aa_vessels["gly"]: 6,
        aa_vessels["his"]: 7,
        coupling_agent: 8,
        coupling_base: 9,
        solvent: 10,
    }
    valve2.mapping = {
        aa_vessels["leu"]: 1,
        aa_vessels["met"]: 2,
        aa_vessels["asn"]: 3,
        aa_vessels["pro"]: 4,
        aa_vessels["gln"]: 5,
        aa_vessels["arg"]: 6,
        aa_vessels["ser"]: 7,
        coupling_agent: 8,
        coupling_base: 9,
        solvent: 10,
    }
    valve3.mapping = {
        aa_vessels["thr"]: 1,
        aa_vessels["trp"]: 2,
        aa_vessels["ile"]: 3,
        aa_vessels["lys"]: 4,
        aa_vessels["tyr"]: 5,
        aa_vessels["val"]: 6,
        deprotection: 7,
        coupling_agent: 8,
        coupling_base: 9,
        solvent: 10,
    }

    # tubes and mixer
    fat_short_tube = mw.Tube(length="1 foot", ID="1/16 in", OD="1/8 in", material="PFA")
    thin_short_tube = mw.Tube(length="1 ft", ID="0.04 in", OD="1/16 in", material="PFA")
    thin_rxn_tube = mw.Tube(length="50 ft", ID="0.04 in", OD="1/16 in", material="PFA")

    mixer = mw.CrossMixer(name="Cross mixer")

    # define apparatus
    A = mw.Apparatus("Generic peptide synthesizer")

    A.add(valve1.mapping, valve1, fat_short_tube)
    A.add(valve1, pump1, fat_short_tube)
    A.add(pump1, mixer, thin_short_tube)

    A.add(valve2.mapping, valve2, fat_short_tube)
    A.add(valve2, pump2, fat_short_tube)
    A.add(pump2, mixer, thin_short_tube)

    A.add(valve3.mapping, valve3, fat_short_tube)
    A.add(valve3, pump3, fat_short_tube)
    A.add(pump3, mixer, thin_short_tube)

    A.add(mixer, output, thin_rxn_tube)

    A._validate()  # just an extra safety check (ya never know)

    return A


def create_protocol(peptide: Sequence, apparatus: mw.Apparatus) -> mw.Protocol:

    peptide = validate_peptide(peptide)

    P = mw.Protocol(apparatus)

    start = timedelta(seconds=0)
    deprotection_duration = timedelta(seconds=60)
    wash_duration = timedelta(seconds=30)
    coupling_duration = timedelta(seconds=60)
    # how much time to leave the pumps off before and after switching the valve
    # should be 2 seconds minimum
    switching_duration = timedelta(seconds=2)

    valve_mapping = {}
    for component in apparatus[mw.Valve]:
        for vessel in component.mapping:
            valve_mapping[vessel.name] = component

    pump_mapping = {}
    for connection in apparatus.network:
        if isinstance(connection.to_component, mw.Pump):
            pump_mapping[connection.from_component] = connection.to_component

    for amino_acid in peptide:

        # Deprotection
        P.add(
            valve_mapping["deprotection"],
            start=start + (switching_duration / 2),
            duration=deprotection_duration + switching_duration,
            setting="deprotection",
        )
        P.add(
            pump_mapping[valve_mapping["deprotection"]],
            start=start + switching_duration,
            duration=deprotection_duration,
            rate="5ml/min",
        )

        start += deprotection_duration + switching_duration

        # Wash
        P.add(
            valve_mapping["deprotection"],
            start=start + (switching_duration / 2),
            duration=wash_duration + switching_duration,
            setting="solvent",
        )
        P.add(
            pump_mapping[valve_mapping["deprotection"]],
            start=start + switching_duration,
            duration=wash_duration,
            rate="5ml/min",
        )

        start += wash_duration + switching_duration

        # Coupling
        P.add(
            valve_mapping[amino_acid],
            start=start + (switching_duration / 2),
            duration=coupling_duration + switching_duration,
            setting=amino_acid,
        )
        other_valves = [
            valve
            for valve in apparatus[mw.Valve]
            if valve is not valve_mapping[amino_acid]
        ]
        P.add(
            other_valves[0],
            start=start + (switching_duration / 2),
            duration=coupling_duration + switching_duration,
            setting="coupling_agent",
        )
        P.add(
            other_valves[1],
            start=start + (switching_duration / 2),
            duration=coupling_duration + switching_duration,
            setting="coupling_base",
        )

        P.add(
            apparatus[mw.Pump],
            start=start + switching_duration,
            duration=coupling_duration,
            rate="5ml/min",
        )

        start += coupling_duration + switching_duration

        # # Wash
        # P.add(
        #     valve3,
        #     start=start + (switching_duration / 2),
        #     duration=wash_duration + switching_duration,
        #     setting="solvent",
        # )
        # P.add(
        #     pump3,
        #     start=start + switching_duration,
        #     duration=wash_duration,
        #     rate="5ml/min",
        # )

        start += wash_duration + switching_duration

    return P
