"use strict";

// Plain words for the tiers and safety states, so a reader never has to guess what a label means.
// The label itself is always shown too: these explain a tier, they never replace or raise it.
const plainTiers = {
  'drafted': 'A computer program wrote this. No cook has checked it yet, which is why your eyes help.',
  'sourced': 'Taken from a named reference that a person can open. No cook has approved it yet.',
  'reviewed': 'Approved by a reviewer who knows this cuisine.',
  'verified': 'Approved, then confirmed a second time by another reviewer or a test cook.',
  'cook-tested': 'Backed by results from real cooks.',
  'unverified': 'No person has checked these safety answers against a trusted source yet.'
};

function plainTier(tier) {
  return plainTiers[tier] || 'No plain explanation is recorded for this label.';
}
