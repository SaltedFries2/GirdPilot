"""Small SCL/ICD DataSet reader (not a full IEC 61850 SCL implementation)."""
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


@dataclass(frozen=True)
class Fcda:
    ld_inst: str
    prefix: str
    ln_class: str
    ln_inst: str
    do_name: str
    fc: str

    @property
    def reference(self) -> str:
        return f"{self.ld_inst}/{self.prefix}{self.ln_class}{self.ln_inst}.{self.do_name}[{self.fc}]"


def read_datasets(path: str | Path) -> dict[str, list[Fcda]]:
    """Return DataSet members in declared order, keyed by dataset name."""
    root = ET.parse(path).getroot()
    datasets: dict[str, list[Fcda]] = {}
    for dataset in root.iter():
        if dataset.tag.split("}")[-1] != "DataSet":
            continue
        name = dataset.attrib.get("name", "")
        if not name:
            continue
        if name in datasets:
            raise ValueError(f"Ambiguous duplicate DataSet name: {name}")
        fields: list[Fcda] = []
        for child in dataset:
            if child.tag.split("}")[-1] != "FCDA":
                continue
            a = child.attrib
            fields.append(Fcda(a.get("ldInst", ""), a.get("prefix", ""),
                               a.get("lnClass", ""), a.get("lnInst", ""),
                               a.get("doName", ""), a.get("fc", "")))
        datasets[name] = fields
    return datasets
