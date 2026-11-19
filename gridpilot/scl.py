"""Small SCL/ICD reader (not a full IEC 61850 SCL implementation)."""
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET


def _local(tag: str) -> str:
    """Strip an XML namespace, if present."""
    return tag.split("}")[-1]


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

    @property
    def ln_reference(self) -> str:
        """Reference of the logical node this FCDA points at, e.g. BRANCH1/GGIO1."""
        return f"{self.ld_inst}/{self.prefix}{self.ln_class}{self.ln_inst}"


@dataclass(frozen=True)
class LogicalNode:
    ld_inst: str
    prefix: str
    ln_class: str
    ln_inst: str

    @property
    def reference(self) -> str:
        return f"{self.ld_inst}/{self.prefix}{self.ln_class}{self.ln_inst}"


@dataclass(frozen=True)
class SclModel:
    """IED names, logical devices, logical nodes and datasets of one SCL file."""
    ied_names: list[str] = field(default_factory=list)
    logical_devices: list[str] = field(default_factory=list)
    logical_nodes: list[LogicalNode] = field(default_factory=list)
    datasets: dict[str, list[Fcda]] = field(default_factory=dict)

    def has_logical_node(self, ln_reference: str) -> bool:
        return any(ln.reference == ln_reference for ln in self.logical_nodes)


def read_datasets(path: str | Path) -> dict[str, list[Fcda]]:
    """Return DataSet members in declared order, keyed by dataset name."""
    return read_model(path).datasets


def read_model(path: str | Path) -> SclModel:
    """Parse IED names, logical devices, logical nodes and DataSets from an SCL/ICD file."""
    root = ET.parse(path).getroot()
    return _walk(root, SclModel())


def _walk(root: ET.Element, model: SclModel) -> SclModel:
    """Iterate with explicit LDevice context to resolve LN references."""
    def visit(element: ET.Element, ld_inst: str) -> None:
        tag = _local(element.tag)
        if tag == "LDevice":
            ld_inst = element.attrib.get("inst", "")
            if ld_inst and ld_inst not in model.logical_devices:
                model.logical_devices.append(ld_inst)
        elif tag == "IED":
            name = element.attrib.get("name", "")
            if name and name not in model.ied_names:
                model.ied_names.append(name)
        elif tag in ("LN", "LN0"):
            ln = LogicalNode(ld_inst, element.attrib.get("prefix", ""),
                             element.attrib.get("lnClass", ""), element.attrib.get("inst", ""))
            if ln.reference not in {n.reference for n in model.logical_nodes}:
                model.logical_nodes.append(ln)
        elif tag == "DataSet":
            name = element.attrib.get("name", "")
            if name and name in model.datasets:
                raise ValueError(f"Ambiguous duplicate DataSet name: {name}")
            if name:
                fields: list[Fcda] = []
                for child in element:
                    if _local(child.tag) == "FCDA":
                        a = child.attrib
                        fields.append(Fcda(a.get("ldInst", ld_inst), a.get("prefix", ""),
                                           a.get("lnClass", ""), a.get("lnInst", ""),
                                           a.get("doName", ""), a.get("fc", "")))
                model.datasets[name] = fields
        for child in element:
            visit(child, ld_inst)

    visit(root, "")
    return model
