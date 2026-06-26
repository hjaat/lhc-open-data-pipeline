"""
physics.py - Particle physics calculations and event reconstruction
Handles 4-vector math, invariant masses, selection cuts
"""

import numpy as np
import pandas as pd
import logging
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ============================================================================
# 4-VECTOR MATHEMATICS
# ============================================================================

@dataclass
class LorentzVector:
    """4-vector representation of particle (E, px, py, pz)"""
    
    pt: float  # Transverse momentum
    eta: float  # Pseudorapidity
    phi: float  # Azimuthal angle
    mass: float  # Invariant mass
    
    def to_cartesian(self) -> Tuple[float, float, float, float]:
        """Convert (pt, eta, phi, mass) → (E, px, py, pz)"""
        px = self.pt * np.cos(self.phi)
        py = self.pt * np.sin(self.phi)
        pz = self.pt * np.sinh(self.eta)
        
        # Energy from momentum and mass: E = sqrt(p^2 + m^2)
        p_mag_sq = self.pt**2 + pz**2
        energy = np.sqrt(p_mag_sq + self.mass**2)
        
        return energy, px, py, pz
    
    @staticmethod
    def from_cartesian(energy: float, px: float, py: float, pz: float) -> 'LorentzVector':
        """Convert (E, px, py, pz) → (pt, eta, phi, mass)"""
        pt = np.sqrt(px**2 + py**2)
        phi = np.arctan2(py, px)
        eta = np.arcsinh(pz / pt) if pt > 0 else 0
        
        # Mass from energy-momentum: m = sqrt(E^2 - p^2)
        p_mag_sq = px**2 + py**2 + pz**2
        mass_sq = energy**2 - p_mag_sq
        mass = np.sqrt(max(0, mass_sq))
        
        return LorentzVector(pt=pt, eta=eta, phi=phi, mass=mass)


class FourVectorMath:
    """Utilities for 4-vector operations"""
    
    @staticmethod
    def invariant_mass(particles: List[LorentzVector]) -> float:
        """
        Calculate invariant mass of particle system
        M = sqrt((Σ E)^2 - (Σ p)^2)
        """
        total_energy = 0
        total_px = 0
        total_py = 0
        total_pz = 0
        
        for particle in particles:
            E, px, py, pz = particle.to_cartesian()
            total_energy += E
            total_px += px
            total_py += py
            total_pz += pz
        
        total_p_sq = total_px**2 + total_py**2 + total_pz**2
        mass_sq = total_energy**2 - total_p_sq
        
        return np.sqrt(max(0, mass_sq))
    
    @staticmethod
    def delta_r(eta1: float, phi1: float, eta2: float, phi2: float) -> float:
        """
        Angular distance between two particles
        ΔR = sqrt(Δη^2 + Δφ^2)
        """
        delta_eta = eta1 - eta2
        delta_phi = phi1 - phi2
        
        # Wrap phi difference to [-π, π]
        delta_phi = np.arctan2(np.sin(delta_phi), np.cos(delta_phi))
        
        return np.sqrt(delta_eta**2 + delta_phi**2)
    
    @staticmethod
    def transverse_mass(pt1: float, phi1: float, pt2: float, phi2: float) -> float:
        """
        Transverse mass of two-particle system
        MT = sqrt((E1T + E2T)^2 - (pT1 + pT2)^2)
        """
        # Assume massless particles for MET calculation
        e1t = pt1
        e2t = pt2
        
        px_total = pt1 * np.cos(phi1) + pt2 * np.cos(phi2)
        py_total = pt1 * np.sin(phi1) + pt2 * np.sin(phi2)
        p_total = np.sqrt(px_total**2 + py_total**2)
        
        return np.sqrt((e1t + e2t)**2 - p_total**2)


# ============================================================================
# EVENT SELECTION & RECONSTRUCTION
# ============================================================================

class EventSelector:
    """Apply selection cuts and event filters"""
    
    @staticmethod
    def select_muons(
        df: pd.DataFrame,
        pt_min: float = 20.0,
        eta_range: Tuple[float, float] = (-2.4, 2.4),
        iso_max: float = 0.2
    ) -> pd.DataFrame:
        """
        Select tight muons
        Applies pT, η, and isolation cuts
        """
        mask = (
            (df['Muon_pt'] > pt_min) &
            (df['Muon_eta'] >= eta_range[0]) &
            (df['Muon_eta'] <= eta_range[1]) &
            (df['Muon_pfRelIso03_all'] < iso_max)  # Relative isolation
        )
        return df[mask].copy()
    
    @staticmethod
    def select_electrons(
        df: pd.DataFrame,
        pt_min: float = 20.0,
        eta_max: float = 2.5,
        iso_max: float = 0.15
    ) -> pd.DataFrame:
        """
        Select tight electrons
        Applies pT, η, and isolation cuts
        """
        mask = (
            (df['Electron_pt'] > pt_min) &
            (np.abs(df['Electron_eta']) < eta_max) &
            (df['Electron_pfRelIso03_all'] < iso_max)
        )
        return df[mask].copy()
    
    @staticmethod
    def select_jets(
        df: pd.DataFrame,
        pt_min: float = 30.0,
        eta_max: float = 4.7
    ) -> pd.DataFrame:
        """Select jets with kinematic cuts"""
        mask = (
            (df['Jet_pt'] > pt_min) &
            (np.abs(df['Jet_eta']) < eta_max)
        )
        return df[mask].copy()
    
    @staticmethod
    def trigger_selection(df: pd.DataFrame) -> pd.DataFrame:
        """Apply trigger requirements for data/MC consistency"""
        # Example: Require at least one passing trigger
        mask = (
            (df['HLT_Mu30'] == 1) |
            (df['HLT_Ele27_WP80'] == 1) |
            (df['HLT_QuadMu8'] == 1)
        )
        return df[mask].copy()
    
    @staticmethod
    def vertex_selection(df: pd.DataFrame) -> pd.DataFrame:
        """Select events with good primary vertex"""
        mask = (
            (df['PV_npvsGood'] >= 1) &
            (np.abs(df['PV_z']) < 24.0) &
            (np.sqrt(df['PV_x']**2 + df['PV_y']**2) < 2.0)
        )
        return df[mask].copy()


# ============================================================================
# CHANNEL-SPECIFIC RECONSTRUCTION
# ============================================================================

class HiggsReconstruction:
    """Reconstruct Higgs boson from decay products"""
    
    @staticmethod
    def reconstruct_four_lepton(df: pd.DataFrame) -> pd.DataFrame:
        """
        Reconstruct H→ZZ→4l events
        Find two Z bosons from 4-lepton combinations
        """
        logger.info("Reconstructing 4-lepton channel (H→ZZ→4l)")
        
        results = []
        
        # This would be vectorized for production
        # For clarity, shown as loop logic
        for idx, row in df.iterrows():
            n_muons = row.get('nMuon', 0)
            n_electrons = row.get('nElectron', 0)
            
            # Need exactly 4 leptons
            if n_muons + n_electrons != 4:
                continue
            
            # Find best Z pair combination
            best_mass_product = float('inf')
            best_result = None
            
            # (Implementation: try all lepton pairings, find 2 Z combinations)
            # For now, simplified placeholder
            
            if best_result:
                results.append({
                    'event': idx,
                    'higgs_mass': best_result['higgs_mass'],
                    'z1_mass': best_result['z1_mass'],
                    'z2_mass': best_result['z2_mass'],
                    'leptons': best_result['leptons']
                })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def reconstruct_two_jet(
        df: pd.DataFrame,
        mass_window: Tuple[float, float] = (120, 130)
    ) -> pd.DataFrame:
        """
        Reconstruct H→bb from two jets
        Find dijet pairs consistent with Higgs mass
        """
        logger.info("Reconstructing dijet channel (H→bb)")
        
        results = []
        
        for idx, row in df.iterrows():
            n_jets = row.get('nJet', 0)
            if n_jets < 2:
                continue
            
            # Get top 2 jets by pT
            jet_pts = row['Jet_pt'][:2]
            jet_etas = row['Jet_eta'][:2]
            jet_phis = row['Jet_phi'][:2]
            jet_masses = row['Jet_mass'][:2]
            
            # Reconstruct dijet mass
            j1 = LorentzVector(pt=jet_pts[0], eta=jet_etas[0], 
                             phi=jet_phis[0], mass=jet_masses[0])
            j2 = LorentzVector(pt=jet_pts[1], eta=jet_etas[1], 
                             phi=jet_phis[1], mass=jet_masses[1])
            
            dijet_mass = FourVectorMath.invariant_mass([j1, j2])