"""Systematic uncertainty calculations"""

import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class SystematicUncertainties:
    """Propagate experimental uncertainties"""
    
    @staticmethod
    def lepton_scale_uncertainty(mass, lepton_type='muon'):
        """Scale uncertainty on lepton pT measurement"""
        if lepton_type == 'muon':
            scale_unc = 0.001  # 0.1% for muons
        elif lepton_type == 'electron':
            scale_unc = 0.005  # 0.5% for electrons
        else:
            scale_unc = 0
        
        return mass * scale_unc
    
    @staticmethod
    def lepton_resolution_uncertainty(pt):
        """Resolution on lepton pT"""
        # CMS: 1-2% depending on pt
        return 0.01 * pt + 0.001 * (pt ** 2)
    
    @staticmethod
    def jet_energy_scale(energy):
        """JES uncertainty"""
        return 0.02 * energy  # 2% for jets
    
    @staticmethod
    def pile_up_uncertainty(n_interactions):
        """Pile-up reweighting uncertainty"""
        return 0.05 * np.sqrt(n_interactions)
    
    @staticmethod
    def compute_total_uncertainty(signal_yield, **uncertainties):
        """Combine systematic uncertainties in quadrature"""
        total_unc_sq = sum(u**2 for u in uncertainties.values())
        total_unc = np.sqrt(total_unc_sq)
        return {
            'total': total_unc,
            'relative': total_unc / signal_yield if signal_yield > 0 else 0,
            'breakdown': uncertainties
        }


def compute_uncertainties(df):
    """Add uncertainty columns to dataframe"""
    
    df_copy = df.copy()
    
    # Lepton pT resolution
    if 'Muon_pt' in df.columns:
        df_copy['lepton_pt_unc'] = df['Muon_pt'].apply(
            SystematicUncertainties.lepton_resolution_uncertainty
        )
    else:
        df_copy['lepton_pt_unc'] = 0
    
    # Jet energy
    if 'Jet_energy' in df.columns:
        df_copy['jet_energy_unc'] = df['Jet_energy'].apply(
            SystematicUncertainties.jet_energy_scale
        )
    else:
        df_copy['jet_energy_unc'] = 0
    
    # Combined mass uncertainty
    df_copy['mass_unc'] = np.sqrt(
        (0.01 * df.get('invariant_mass', 125))**2 +  # Scale
        (0.02 * df.get('invariant_mass', 125))**2 +  # Resolution
        (0.005 * df.get('invariant_mass', 125))**2   # Trigger
    )
    
    return df_copy


def main():
    """Example: compute uncertainties"""
    logging.basicConfig(level=logging.INFO)
    
    logger.info("Computing systematic uncertainties...")
    
    # Example signal yield
    signal_yield = 100
    
    # Breakdown of uncertainties
    uncertainties = {
        'lepton_scale': 2.0,      # 2 events
        'jet_energy': 1.5,        # 1.5 events
        'resolution': 3.0,        # 3 events
        'trigger': 0.5,           # 0.5 events
        'pileup': 1.0,            # 1 event
    }
    
    # Compute total
    result = SystematicUncertainties.compute_total_uncertainty(
        signal_yield, **uncertainties
    )
    
    logger.info(f"\nSignal yield: {signal_yield}")
    logger.info(f"Total uncertainty: ±{result['total']:.2f} events")
    logger.info(f"Relative uncertainty: ±{result['relative']*100:.1f}%")
    logger.info(f"\nBreakdown:")
    for source, value in result['breakdown'].items():
        logger.info(f"  {source:15} ±{value:.2f}")
    
    # Apply to mock data
    logger.info("\n" + "="*50)
    logger.info("Applying to mock dataset...")
    
    df = pd.DataFrame({
        'event': range(100),
        'Muon_pt': np.random.normal(50, 20, 100),
        'invariant_mass': np.random.normal(125, 10, 100),
    })
    
    df_with_unc = compute_uncertainties(df)
    
    logger.info(f"Mean mass uncertainty: ±{df_with_unc['mass_unc'].mean():.2f} GeV")
    logger.info("✓ Uncertainties computed!")


if __name__ == "__main__":
    main()