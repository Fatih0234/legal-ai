from app.adapters import (
    bundesportal,
    berlin_service,
    nrw_service,
    elster,
    dguv,
    geoportal,
    handelsregister,
    sozialversicherung,
)
from app.schemas import ActionStep, Procedure, RiskFlag


def test_bundesportal_trade_registration():
    proc = bundesportal.get_trade_registration("Berlin", "Berlin")
    assert isinstance(proc, Procedure)
    assert proc.title
    assert proc.steps
    assert proc.source_url.startswith("https://")
    assert proc.source_name == "SDG Portal"


def test_bundesportal_food_registration():
    proc = bundesportal.get_food_business_registration("Berlin", "Berlin")
    assert isinstance(proc, Procedure)
    assert "Lebensmittel" in proc.title or "Food" in proc.title
    assert proc.source_url


def test_bundesportal_ifsg():
    proc = bundesportal.get_ifsg_instruction("Berlin", "Berlin")
    assert isinstance(proc, Procedure)
    assert proc.steps
    assert proc.source_url


def test_berlin_restaurant_permit_alcohol():
    proc = berlin_service.get_restaurant_permit("Berlin", "Berlin", serves_alcohol=True)
    assert isinstance(proc, Procedure)
    assert "Gaststättenerlaubnis" in proc.title
    assert proc.steps
    assert proc.source_url


def test_berlin_restaurant_permit_no_alcohol():
    proc = berlin_service.get_restaurant_permit(
        "Berlin", "Berlin", serves_alcohol=False
    )
    assert isinstance(proc, Procedure)
    assert len(proc.steps) > 0


def test_berlin_ihk_alcohol():
    proc = berlin_service.get_ihk_instruction("Berlin", "Berlin", serves_alcohol=True)
    assert isinstance(proc, Procedure)
    assert "IHK" in proc.title
    assert proc.steps


def test_berlin_ihk_no_alcohol():
    proc = berlin_service.get_ihk_instruction("Berlin", "Berlin", serves_alcohol=False)
    assert isinstance(proc, Procedure)
    assert len(proc.steps) == 0


def test_nrw_business_registration():
    proc = nrw_service.get_business_registration("NRW", "Köln")
    assert isinstance(proc, Procedure)
    assert proc.steps
    assert proc.state_specific is True


def test_nrw_restaurant_permit_alcohol():
    proc = nrw_service.get_restaurant_permit("NRW", "Köln", serves_alcohol=True)
    assert isinstance(proc, Procedure)
    assert proc.steps


def test_nrw_restaurant_permit_no_alcohol():
    proc = nrw_service.get_restaurant_permit("NRW", "Köln", serves_alcohol=False)
    assert isinstance(proc, Procedure)


def test_elster_sole_proprietor():
    step = elster.get_tax_registration_step("sole proprietor")
    assert isinstance(step, ActionStep)
    assert step.action_url
    assert step.source_url


def test_elster_ug():
    step = elster.get_tax_registration_step("UG")
    assert isinstance(step, ActionStep)
    assert "UG" in step.title or "GmbH" in step.title


def test_elster_gmbh():
    step = elster.get_tax_registration_step("GmbH")
    assert isinstance(step, ActionStep)


def test_handelsregister_ug():
    step = handelsregister.get_handelsregister_step("UG")
    assert isinstance(step, ActionStep)
    assert "UG" in step.title
    assert step.source_url.startswith("https://")
    assert step.action_url.startswith("https://")
    assert "€1" in step.description


def test_handelsregister_gmbh():
    step = handelsregister.get_handelsregister_step("GmbH")
    assert isinstance(step, ActionStep)
    assert "GmbH" in step.title
    assert step.source_url.startswith("https://")
    assert "25.000" in step.description


def test_dguv_registration():
    step = dguv.get_dguv_registration_step()
    assert isinstance(step, ActionStep)
    assert step.action_type == "insurance"
    assert step.source_url


def test_sozialversicherung_registration():
    step = sozialversicherung.get_social_insurance_registration_step()
    assert isinstance(step, ActionStep)
    assert step.action_type == "registration"
    assert step.source_url
    assert "Sozialversicherung" in step.title or "Mitarbeiter" in step.title


def test_geoportal_sources():
    sources = geoportal.find_geo_sources("Berlin", "Berlin")
    assert isinstance(sources, list)
    assert len(sources) >= 2
    urls = [s["url"] for s in sources]
    assert any("geoportal.de" in u for u in urls)
    # Berlin should have FIS-Broker
    assert any("fbinter" in u for u in urls)


def test_geoportal_nrw():
    sources = geoportal.find_geo_sources("NRW", "Köln")
    assert any("geoportal.nrw" in s["url"] for s in sources)


def test_geoportal_location_risk_existing():
    from app.schemas import PremisesType
    risks = geoportal.flag_location_risk(PremisesType.EXISTING_GASTRONOMY)
    assert isinstance(risks, list)
    assert len(risks) == 1
    assert risks[0].severity == "info"


def test_geoportal_location_risk_new():
    from app.schemas import PremisesType
    risks = geoportal.flag_location_risk(PremisesType.NEW_NON_GASTRO)
    assert isinstance(risks, list)
    assert len(risks) == 2
    assert any(r.severity == "warning" for r in risks)


def test_geoportal_location_risk_change_of_use():
    from app.schemas import PremisesType
    risks = geoportal.flag_location_risk(PremisesType.CHANGE_OF_USE)
    assert isinstance(risks, list)
    assert len(risks) == 2
    assert any(r.category == "Nutzungsänderung" for r in risks)
    assert any(r.severity == "warning" for r in risks)


def test_geoportal_location_risk_takeover():
    from app.schemas import PremisesType
    risks = geoportal.flag_location_risk(PremisesType.TAKEOVER)
    assert isinstance(risks, list)
    assert len(risks) == 1
    assert risks[0].category == "Übernahme Gaststätte"
    assert risks[0].severity == "warning"


def test_geoportal_location_risk_public_terrace():
    from app.schemas import PremisesType
    risks = geoportal.flag_location_risk(PremisesType.EXISTING_GASTRONOMY, has_public_terrace=True)
    assert len(risks) == 2
    assert any(r.category == "Außenbereich / Terrasse" for r in risks)
