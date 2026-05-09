"""Tests for core/rights_mapper.py — domain → rights mapping."""

import pytest
from core.rights_mapper import map_rights, RightsMap, Right


class TestMapRightsUK:
    def test_returns_rights_map(self):
        result = map_rights("housing", "UK")
        assert isinstance(result, RightsMap)

    def test_correct_domain_and_jurisdiction(self):
        result = map_rights("employment", "UK")
        assert result.domain == "employment"
        assert result.jurisdiction == "UK"

    def test_has_rights_list(self):
        result = map_rights("benefits", "UK")
        assert isinstance(result.rights, list)
        assert len(result.rights) > 0

    def test_rights_are_right_objects(self):
        result = map_rights("credit", "UK")
        for right in result.rights:
            assert isinstance(right, Right)
            assert right.name
            assert right.source
            assert right.action

    def test_uk_default_jurisdiction(self):
        result = map_rights("consumer")
        assert result.jurisdiction == "UK"

    def test_jurisdiction_normalised_to_uppercase(self):
        result = map_rights("housing", "uk")
        assert result.jurisdiction == "UK"

    def test_uk_enforcement_includes_gdpr(self):
        result = map_rights("enforcement", "UK")
        sources = [r.source for r in result.rights]
        assert any("GDPR" in s for s in sources)

    def test_uk_enforcement_includes_equality_act(self):
        result = map_rights("enforcement", "UK")
        sources = [r.source for r in result.rights]
        assert any("Equality Act" in s for s in sources)

    def test_uk_housing_includes_protection_from_eviction(self):
        result = map_rights("housing", "UK")
        sources = [r.source for r in result.rights]
        assert any("Housing Act" in s for s in sources)

    def test_notes_present(self):
        result = map_rights("consumer", "UK")
        assert isinstance(result.notes, str)
        assert len(result.notes) > 0

    def test_all_domains_return_rights(self):
        from core.conversation import DOMAINS
        for domain in DOMAINS:
            result = map_rights(domain, "UK")
            assert len(result.rights) > 0, f"No rights found for domain: {domain}"

    def test_medical_includes_device_and_accessibility_rights(self):
        result = map_rights("medical", "UK")
        combined = " ".join(f"{right.name} {right.source}" for right in result.rights)
        assert "device data" in combined.lower() or "Health or Device Data" in combined
        assert "UK GDPR Article 22" in combined
        assert "Equality Act 2010" in combined


class TestMapRightsInternational:
    def test_non_uk_returns_rights_map(self):
        result = map_rights("enforcement", "US")
        assert isinstance(result, RightsMap)

    def test_non_uk_jurisdiction_stored(self):
        result = map_rights("consumer", "AU")
        assert result.jurisdiction == "AU"

    def test_non_uk_includes_note_about_jurisdiction(self):
        result = map_rights("housing", "DE")
        assert "DE" in result.notes or "Mirror does not yet" in result.notes

    def test_non_uk_still_returns_some_rights(self):
        result = map_rights("consumer", "FR")
        assert len(result.rights) > 0
