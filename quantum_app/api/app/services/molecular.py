from dataclasses import dataclass

from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, Lipinski, rdMolDescriptors


@dataclass(frozen=True)
class Candidate:
    id: str
    smiles: str
    profile: tuple[float, ...]
    safety: float


CANDIDATES = (
    Candidate("MV-QA17", "CCOc1ccc(CN)cc1", (0.72, 0.81, 0.38, 0.44), 0.76),
    Candidate("MV-NX04", "CCN(CC)Cc1ccccc1", (0.58, 0.74, 0.69, 0.62), 0.68),
    Candidate("MV-SR22", "COc1ccc(CCN)cc1O", (0.83, 0.57, 0.51, 0.35), 0.82),
    Candidate("MV-KT09", "CN1CCC(c2ccccc2)CC1", (0.46, 0.66, 0.77, 0.71), 0.72),
    Candidate("MV-PL31", "CC(C)NCC(O)c1ccccc1", (0.64, 0.78, 0.61, 0.55), 0.79),
)


def calculate_descriptors(smiles: str) -> dict[str, float | int]:
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        raise ValueError("candidate contains invalid SMILES")
    return {
        "molecular_weight": round(Descriptors.MolWt(molecule), 3),
        "log_p": round(Crippen.MolLogP(molecule), 3),
        "h_bond_donors": int(Lipinski.NumHDonors(molecule)),
        "polar_surface_area": round(rdMolDescriptors.CalcTPSA(molecule), 3),
    }


def molecular_suitability(descriptors: dict[str, float | int]) -> float:
    molecular_weight = float(descriptors["molecular_weight"])
    log_p = float(descriptors["log_p"])
    polar_surface_area = float(descriptors["polar_surface_area"])
    weight_score = max(0.0, 1 - abs(molecular_weight - 300) / 300)
    log_p_score = max(0.0, 1 - abs(log_p - 2.0) / 4.0)
    surface_score = max(0.0, 1 - abs(polar_surface_area - 60) / 100)
    return (weight_score + log_p_score + surface_score) / 3
