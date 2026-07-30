"""Auto-detect entities for dual battery setup."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


def _score(priority: int, *conditions: bool) -> int:
    return priority * 10 + sum(1 for c in conditions if c)


def _pick_best(entities: list[dict], *, domain: str | None = None, name_like: str | None = None, device_class: str | None = None) -> str | None:
    scored: list[tuple[int, str]] = []
    for e in entities:
        ent = e["entity_id"]
        score = 0
        if ent.startswith("number.") if domain == "number" else (ent.startswith("sensor.") if domain in (None, "sensor") else False):
            score += 10
        if domain and ent.startswith(f"{domain}."):
            score += 20
        if name_like and name_like in e.get("name", "").lower():
            score += 30
        if name_like and name_like in ent.lower():
            score += 15
        if device_class and e.get("device_class") == device_class:
            score += 25
        if score > 0:
            scored.append((score, ent))
    scored.sort(reverse=True)
    return scored[0][1] if scored else None


def _build_mapping(groups: dict[str, list[dict]]) -> dict:
    """Build entity mapping from entity groups keyed by inverter prefix."""
    mapping = {"a": {}, "b": {}}
    sorted_prefixes = sorted(groups.keys())
    if not sorted_prefixes:
        return mapping
    label_map = {"a": sorted_prefixes[0], "b": sorted_prefixes[1]} if len(sorted_prefixes) >= 2 else {"a": sorted_prefixes[0]}
    for key, prefix in label_map.items():
        ents = groups[prefix]
        mapping[key]["soc"] = _pick_best(ents, name_like="battery_capacity") or _pick_best(ents, name_like="soc")
        mapping[key]["power"] = _pick_best(ents, name_like="battery_power")
        mapping[key]["current_limit"] = _pick_best(ents, domain="number", name_like="battery_charge_max_current") or _pick_best(ents, domain="number", name_like="charge_max_current") or _pick_best(ents, domain="number", name_like="current_limit")
        mapping[key]["house_load"] = _pick_best(ents, name_like="house_load")
    return mapping


def _prefix_for(eid: str) -> str | None:
    """Extract inverter prefix like 'tock_solax1' from entity id."""
    eid = eid.split(".")[-1]
    import re
    for m in re.finditer(r"(tock_solax[12]|solax[12]|inverter[12])", eid):
        return m.group(0)
    return None


async def async_detect_entities(hass: HomeAssistant) -> dict:
    """Scan Home Assistant and return detected entity map for Battery A and B.

    Returns a dict like:
      { "a": { "soc": "...", "power": "...", "current_limit": "...", "house_load": "..." },
        "b": { ... } }
    """
    states = hass.states.async_all()
    solax_entities = []
    for state in states:
        eid = state.entity_id
        if "solax" in eid.lower() or "inverter" in eid.lower():
            solax_entities.append({
                "entity_id": eid,
                "name": (state.attributes.get("friendly_name") or eid).lower(),
                "device_class": state.attributes.get("device_class"),
            })

    groups: dict[str, list[dict]] = {}
    for e in solax_entities:
        prefix = _prefix_for(e["entity_id"])
        if prefix:
            groups.setdefault(prefix, []).append(e)

    mapping = _build_mapping(groups)

    result = {}
    label_map = {"a": "A", "b": "B"}
    for key in mapping:
        if any(mapping[key].values()):
            result[key] = mapping[key]
    return result


async def async_build_defaults(hass: HomeAssistant) -> dict:
    """Build defaults dict for the config flow, keyed by CONF_ constants."""
    detected = await async_detect_entities(hass)
    from .const import (
        CONF_BATTERY_A_CURRENT_LIMIT,
        CONF_BATTERY_A_HOUSE_LOAD,
        CONF_BATTERY_A_NAME,
        CONF_BATTERY_A_POWER,
        CONF_BATTERY_A_SOC,
        CONF_BATTERY_B_CURRENT_LIMIT,
        CONF_BATTERY_B_HOUSE_LOAD,
        CONF_BATTERY_B_NAME,
        CONF_BATTERY_B_POWER,
        CONF_BATTERY_B_SOC,
    )
    defaults = {}
    if "a" in detected:
        defaults[CONF_BATTERY_A_NAME] = "Battery A"
        defaults[CONF_BATTERY_A_SOC] = detected["a"].get("soc") or ""
        defaults[CONF_BATTERY_A_POWER] = detected["a"].get("power") or ""
        defaults[CONF_BATTERY_A_CURRENT_LIMIT] = detected["a"].get("current_limit") or ""
        defaults[CONF_BATTERY_A_HOUSE_LOAD] = detected["a"].get("house_load") or ""
    if "b" in detected:
        defaults[CONF_BATTERY_B_NAME] = "Battery B"
        defaults[CONF_BATTERY_B_SOC] = detected["b"].get("soc") or ""
        defaults[CONF_BATTERY_B_POWER] = detected["b"].get("power") or ""
        defaults[CONF_BATTERY_B_CURRENT_LIMIT] = detected["b"].get("current_limit") or ""
        defaults[CONF_BATTERY_B_HOUSE_LOAD] = detected["b"].get("house_load") or ""
    return defaults
