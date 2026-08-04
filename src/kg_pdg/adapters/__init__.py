"""Domain adapters for KG-PDG."""
from kg_pdg.adapters.base import BaseAdapter
from kg_pdg.adapters.medical import MedicalAdapter

__all__ = ["BaseAdapter", "MedicalAdapter"]
